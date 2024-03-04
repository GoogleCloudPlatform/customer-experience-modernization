# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Persona 4 routers - Customer Service Agent
"""
import asyncio
import json
import tomllib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore
from google.protobuf import timestamp_pb2
from proto import Message

from app.models.p4_model import (
    AddMessageResponse,
    ChatMessage,
    ConversationSummaryAndTitleResponse,
    RephraseTextRequest,
    RephraseTextResponse,
    ScheduleEventRequest,
    ScheduleEventResponse,
    SearchConversationsRequest,
    SearchConversationsResponse,
    SearchManualsRequest,
    SearchManualsResponse,
    TranslateRequest,
    TranslateResponse,
    AutoSuggestRequest,
    AutoSuggestResponse,
)
from app.utils import (
    utils_cloud_translation,
    utils_palm,
    utils_search,
    utils_workspace,
)

# Imports the Google Cloud language client library
from google.cloud import language_v1

# Instantiates a client
lang_client = language_v1.LanguageServiceClient()

# Load configuration file
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

# Global configuration
project_id = config["global"]["project_id"]

# Prompts for Salesforce
sf_summarize_prompt_template = config["salesforce"][
    "sf_summarize_prompt_template"
]
chat_summarize_prompt_template = config["salesforce"][
    "chat_summarize_prompt_template"
]
chat_title_prompt_template = config["salesforce"]["chat_title_prompt_template"]

rephrase_prompt_template = config["salesforce"]["rephrase_prompt_template"]

auto_suggest_prompt_template = config["salesforce"]["auto_suggest_prompt_template"]

router = APIRouter(prefix="/p4", tags=["P4 - Customer Service Agent"])

db = firestore.Client()


# ---------------------------------GET---------------------------------------#
@router.get(path="/conversation_summary_and_title/{user_id}/{conversation_id}")
def conversation_summary_and_title(
    user_id: str, conversation_id: str
) -> ConversationSummaryAndTitleResponse:
    """
    # End conversation and create summary

    ## Request parameters
    **user_id**: *string*
    - User Id

    **conversation_id**: *string*
    - Conversation Id

    ## Response body [ConversationSummaryAndTitleResponse]
     **summary**: *string*
    - Conversation Summary

    **title** *string*
    - Conversation Title

    ## Raises
    **HTTPException** - *500* - Error
    - Query conversation error

    **HTTPException** - *404* - Error
    - No conversation found

    **HTTPException** - *500* - Error
    - Summarization error

    """
    try:
        conversation_messages_snapshot = [
            message_snapshot.to_dict()
            for message_snapshot in db.collection("p4-conversations")
            .document(user_id)
            .collection("conversations")
            .document(conversation_id)
            .collection("messages")
            .get()
        ]
    except GoogleAPICallError as e:
        print(f"[Error]query_conversation:{e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    summary = "Empty conversation."
    title = "Empty conversation."

    if conversation_messages_snapshot:
        try:
            conversation_str = json.dumps(
                {"messages": conversation_messages_snapshot},
                default=str,
            )
            summary, title = asyncio.run(
                utils_palm.run_predict_text_llm(
                    prompts=[
                        chat_summarize_prompt_template.format(
                            conversation_str
                        ),
                        chat_title_prompt_template.format(conversation_str),
                    ]
                )
            )

            if not summary:
                summary = "Closed case"
            if not title:
                title = "Closed case"

        except GoogleAPICallError as e:
            print(f"[Error]VertexSummarizeChat:{e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    try:
        db.collection("p4-conversations").document(user_id).collection(
            "conversations"
        ).document(conversation_id).update(
            {"title": title, "summary": summary}
        )
    except GoogleAPICallError as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e

    return ConversationSummaryAndTitleResponse(summary=summary, title=title)


# ---------------------------------POST---------------------------------------#
@router.post(path="/message/{user_id}/{conversation_id}")
def add_message(
    user_id: str, conversation_id: str, message: ChatMessage
) -> AddMessageResponse:
    """
    # Add message to conversation

    ## Path parameters
    **user_id**: *string*
    - Conversation Id

    **conversation_id**: *string*
    - Conversation Id
    - If "new", creates a new conversation id


    ## ChatMessage
    **text**: *string*
    - Text to send

    **author**: *string*
    - Author
    - Allowed values
      - User
      - Agent
      - System

    **language**: *string*
    - Language

    ## Response body for send-message
    **conversation_id**: *string*
    - Conversation Id

    """
    if conversation_id == "new":
        try:
            conversation_doc: tuple[
                timestamp_pb2.Timestamp, firestore.DocumentReference
            ] = (
                db.collection("p4-conversations")
                .document(user_id)
                .collection("conversations")
                .add({"timestamp": datetime.now(tz=timezone.utc)})
            )
        except GoogleAPICallError as e:
            raise HTTPException(
                status_code=400, detail="Error setting in Firestore" + str(e)
            ) from e
        conversation_id = conversation_doc[1].id

    try:
        document = language_v1.types.Document(
        content=message.text, type_=language_v1.types.Document.Type.PLAIN_TEXT
        )

        # Detects the sentiment of the text
        sentiment = lang_client.analyze_sentiment(
            request={"document": document}
        ).document_sentiment
        sentiment_score = sentiment.score
        sentiment_magnitude = sentiment.magnitude
    except:
        sentiment_score = 0
        sentiment_magnitude = 0

    db.collection("p4-conversations").document(user_id).collection(
        "conversations"
    ).document(conversation_id).collection("messages").add(
        {
            "author": message.author,
            "text": message.text,
            "timestamp": datetime.now(tz=timezone.utc),
            "language": message.language,
            "link": message.link,
            "iconURL": message.iconURL,
            "sentiment_score":sentiment_score,
            "sentiment_magnitude": sentiment_magnitude
        }
    )

    return AddMessageResponse(conversation_id=conversation_id)

# ---------------------------------DELETE---------------------------------------#
@router.delete(path="/clear_conversations/{user_id}")
def clear_all_conversations(
    user_id: str
):
    """
    # Add message to conversation

    ## Path parameters
    **user_id**: *string*

    """

    conv_ref = db.collection("p4-conversations").document(user_id).collection(
        "conversations"
    )
    conv_docs = conv_ref.list_documents()

    for doc in conv_docs:
        msg_docs = doc.collection("messages").list_documents()
        for msg in msg_docs:
            msg.delete()
        print("Deleting Conversation)")
        doc.delete() 

    return JSONResponse(
        content={'message': 'Successfully Deleted Conversations'},
        status_code=200
        )

@router.post(path="/auto-suggest-query")
def auto_suggest_query_text(
    data: AutoSuggestRequest,
) -> AutoSuggestResponse:
    """
    # Form Query for a given text.

    ## Request body for given-text
    **input_text**: *string*
    - Conversation Text

    ## Response body for query-text
    **output_text**: *string*
    - Query text

    """
    try:
        llm_response = utils_palm.text_generation(
            prompt=auto_suggest_prompt_template.format(data.input_text)
        )
    except:
        llm_response = "No suggestions for now"

    return AutoSuggestResponse(output_text=llm_response)

@router.post(path="/rephrase-text")
def rephrase_text(
    data: RephraseTextRequest,
) -> RephraseTextResponse:
    """
    # Rephrase a given text.

    ## Request body for rephrase-text
    **rephrase_text_input**: *string*
    - Text to rephrase

    ## Response body for rephrase-text
    **rephrase_text_output**: *string*
    - Rephrased text

    """

    llm_response = utils_palm.text_generation(
        prompt=rephrase_prompt_template.format(data.rephrase_text_input)
    )

    return RephraseTextResponse(rephrase_text_output=llm_response)


@router.post(path="/schedule-event")
def schedule_event(data: ScheduleEventRequest) -> ScheduleEventResponse:
    """
    # Creates an event using Calendar API with Google Meet

    ## Request body for schedule-event
    **event_summary**: *string*
    - Event summary

    **attendees**: *list*
    - List of attendees

    **start_time**: *string*
    - Start time

    **end_time**: *string*
    - End time

    ## Response body for schedule-event
    **conference_call_link**: *string*
    - Conference call link

    **icon_url**: *string*
    - Icon URL

    **start_time_iso**: *string*
    - Start time ISO

    **end_time_iso**: *string*
    - End time ISO

    ## Raises
    **HTTPException** - *400* - Error
    - Calendar Event Creation Failed

    """
    try:
        start_date = datetime.fromisoformat(data.start_time).isoformat()

        end_date = (
            datetime.fromisoformat(data.start_time) + timedelta(minutes=30)
        ).isoformat()

        result_dict = utils_workspace.create_calendar_event(
            event_summary=data.event_summary,
            attendees=data.attendees,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        print(f"ERROR : Calendar Event Creation Failed : {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ScheduleEventResponse(
        conference_call_link=result_dict["hangoutLink"],
        icon_url=result_dict["conferenceData"]["conferenceSolution"][
            "iconUri"
        ],
        start_time_iso=result_dict["start"]["dateTime"],
        end_time_iso=result_dict["end"]["dateTime"],
    )


@router.post(path="/search-conversations")
def search_conversations(
    data: SearchConversationsRequest,
) -> SearchConversationsResponse:
    """
    # Search for conversations on Vertex AI Search Datastore

    ## Request Body [SearchConversationsRequest]:
    **query**: *string*
    - User input to search the datastore

    **user_pseudo_id**: *string*
    - User unique ID

    **rating**: *list*
    - Filter field for conversation rating
    - Allowed values
      - 1
      - 2
      - 3
      - 4
      - 5

    **status**: *list*
    - Filter field for conversation status
    - Allowed values
      - resolved
      - not resolved

    **sentiment**: *list*
    - Filter field for conversation sentiment
    - Allowed values
      - positive
      - negative
      - neutral

    **category**: *list*
    - Filter field for conversation category
    - Allowed values
      - Bath Robe
      - Bath Towel Set
      - Bed
      - Bookcase
      - Chair
      - Console Table
      - Dining Table
      - Game Table
      - Grill
      - Office Chair
      - Ottoman
      - Outdoor Heater
      - Pool
      - Sofa
      - Tool Cabinet

    **agent_id**: *string*
    - Filter field for conversation agent_id

    **customer_id**: *string*
    - Filter field for conversation customer_id

    **product_id**: *string*
    - Filter field for conversation product_id

    ## Response Body [SearchConversationsResponse]:
    **responses**: *dictionary*
    - Search results, including information about the conversation

    """
    search_filter = ""

    if data.rating:
        search_filter += 'rating: ANY("'
        search_filter += '","'.join(data.rating)
        search_filter += '") '
    if data.status:
        if search_filter:
            search_filter += " AND "
        search_filter += 'status: ANY("'
        search_filter += '","'.join(data.status)
        search_filter += '") '
    if data.sentiment:
        if search_filter:
            search_filter += " AND "
        search_filter += 'sentiment: ANY("'
        search_filter += '","'.join(data.sentiment)
        search_filter += '") '
    if data.category:
        if search_filter:
            search_filter += " AND "
        search_filter += 'category: ANY("'
        search_filter += '","'.join(data.category)
        search_filter += '") '
    if data.agent_id:
        if search_filter:
            search_filter += " AND "
        search_filter += f'agent_id: ANY("{data.agent_id}") '
    if data.customer_id:
        if search_filter:
            search_filter += " AND "
        search_filter += f'customer_id: ANY("{data.customer_id}") '
    if data.product_id:
        if search_filter:
            search_filter += " AND "
        search_filter += f'product_id: ANY("{data.product_id}") '

    try:
        search_response = utils_search.vertexai_search_oneturn(
            search_query=data.query,
            summary_result_count=5,
            search_filter=search_filter,
            datastore_id=config["search-persona5"][
                "conversations_datastore_id"
            ],
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching Vertex AI datatore. " f"{str(e)}",
        ) from e

    responses = {}
    responses["summary"] = search_response.summary.summary_text
    responses["user_input"] = data.query

    responses["search_results"] = []
    for result in search_response.results:
        search_result_dict = Message.to_dict(result)
        document = search_result_dict.get("document", {})
        derived_struct_data = document.get("derived_struct_data", {})

        if len(derived_struct_data.get("snippets", [])) > 0:
            struct_data = document.get("struct_data", {})
            responses["search_results"].append(
                {
                    "snippet": derived_struct_data["snippets"][0]["snippet"],
                    "link": derived_struct_data["link"],
                    "id": search_result_dict.get("id"),
                    "title": struct_data["title"],
                    "status": struct_data["status"],
                    "sentiment": struct_data["sentiment"],
                    "rating": struct_data["rating"],
                    "product_id": struct_data["product_id"],
                    "customer_id": struct_data["customer_id"],
                    "customer_email": struct_data["customer_email"],
                    "conversation": struct_data["conversation"],
                    "category": struct_data["category"],
                    "agent_id": struct_data["agent_id"],
                    "agent_email": struct_data["agent_email"],
                }
            )

    return SearchConversationsResponse(responses=responses)


@router.post(path="/search-manuals")
def search_manuals(
    data: SearchManualsRequest,
) -> SearchManualsResponse:
    """
    # Search for conversations on Vertex AI Search Datastore

    ## Request Body [SearchConversationsRequest]:
    **query**: *string*
    - User input to search the datastore

    **user_pseudo_id**: *string*
    - User unique ID

    **category**: *list*
    - Filter field for manuals category
    - Allowed values
      - Bath Robe
      - Bath Towel Set
      - Bed
      - Bookcase
      - Chair
      - Console Table
      - Dining Table
      - Game Table
      - Grill
      - Office Chair
      - Ottoman
      - Outdoor Heater
      - Pool
      - Sofa
      - Tool Cabinet

    ## Response Body [SearchConversationsResponse]:
    **responses**: *dictionary*
    - Search results, including information about the conversation
    """
    search_filter = ""
    if data.category:
        search_filter += 'category: ANY("'
        search_filter += '","'.join(data.category)
        search_filter += '") '

    try:
        search_response = utils_search.vertexai_search_oneturn(
            search_query=data.query,
            summary_result_count=5,
            search_filter=search_filter,
            datastore_id=config["search-persona5"][
                "product_manuals_datastore_id"
            ],
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching Vertex AI datatore. " f"{str(e)}",
        ) from e

    responses = {}
    responses["summary"] = search_response.summary.summary_text
    responses["user_input"] = data.query

    responses["search_results"] = []
    for result in search_response.results:
        search_result_dict = Message.to_dict(result)
        document = search_result_dict.get("document", {})
        derived_struct_data = document.get("derived_struct_data", {})

        if len(derived_struct_data.get("snippets", [])) > 0:
            struct_data = document.get("struct_data", {})
            responses["search_results"].append(
                {
                    "id": search_result_dict.get("id"),
                    "snippet": derived_struct_data["snippets"][0]["snippet"],
                    "link": derived_struct_data["link"],
                    "title": struct_data["title"],
                    "category": struct_data["category"],
                    "manual": struct_data["manual"],
                }
            )

    return SearchManualsResponse(responses=responses)


@router.post(path="/translate")
def translate(data: TranslateRequest) -> TranslateResponse:
    """
    # Translate text using Cloud Translation API

    ## Request body for translate
    **input_text**: *string*
    - Text to translate

    **target_language**: *string*
    - Target language

    ## Response body for translate
    **output_text**: *string*
    - Translated text

    """
    translated_text = utils_cloud_translation.translate_text_cloud_api(
        input_text=data.input_text, target_language=data.target_language
    )
    return TranslateResponse(output_text=translated_text)
