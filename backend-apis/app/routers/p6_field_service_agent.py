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
Persona 6 routers - Field Service Agent
"""

import json
import tomllib
from datetime import datetime, timedelta  # , timezone

from fastapi import APIRouter, HTTPException
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore_v1 as firestore
from google.cloud.exceptions import NotFound
from google.cloud.firestore_v1.base_query import FieldFilter
from google.protobuf import timestamp_pb2
from proto import Message
from vertexai.preview.generative_models import Image

from app.models.p6_model import (
    AgentActivity,
    AskImageRequest,
    AskImageResponse,
    Customer,
    GenerateAgentActivityRequest,
    GenerateConversationsInsightsRequest,
    GenerateConversationsInsightsResponse,
    ScheduleEventRequest,
    ScheduleEventResponse,
    SearchManualsRequest,
    SearchManualsResponse,
)
from app.utils import (
    utils_cloud_nlp,
    utils_gemini,
    utils_imagen,
    utils_palm,
    utils_search,
    utils_workspace,
)

# Load configuration file
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

firestore_client = firestore.Client()

router = APIRouter(prefix="/p6", tags=["P6 - Field Service Agent"])


# ---------------------------------DELETE-------------------------------------#
@router.delete(path="/agent-activity/{user_id}/{activity_id}")
def delete_agent_activity(user_id: str, activity_id: str) -> str:
    """
    # Delete user activity

    ## Path parameters
    **user_id**: *string*
    - User id

    **activity_id**: *string*
    - Activity id

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error deleting in Firestore
    - Firestore could not delete the activity

    """

    try:
        firestore_client.collection("field-agent").document(
            user_id
        ).collection("activities").document(activity_id).delete()
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error deleting in Firestore" + str(e)
        ) from e

    return "ok"


# ---------------------------------GET----------------------------------------#
@router.get(path="/customer/{customer_id}")
def get_customer_info(customer_id: str) -> Customer:
    """
    # Retrieve customer information from Firestore
     - CDP data
     - Conversations
     - Reviews

    ## Request Parameters:
    **customer_id**: *string*
    - Unique identifier of the customer

    ## Customer:
    **conversations**: *list*
    - List of all the conversations that customer had with the Call Center

    **reviews**: *list*
    - List of all the reviews submited by that customer

    **customer_info**: *dict*
    - Information about that customer extracted from the CDP
    """
    customer_info_snapshot = (
        firestore_client.collection(
            config["search-persona5"]["firestore_customers"]
        )
        .document(customer_id)
        .get()
    )

    if customer_info_snapshot:
        customer_info = customer_info_snapshot.to_dict() or {}
    else:
        raise HTTPException(status_code=400, detail="Customer ID not found.")

    conversations = (
        firestore_client.collection(
            config["search-persona5"]["firestore_conversations"]
        )
        .where(filter=FieldFilter("customer_id", "==", customer_id))
        .get()
    )
    conversations_list = []
    for conversation in conversations:
        conversations_list.append(conversation.to_dict())

    reviews = (
        firestore_client.collection(
            config["search-persona5"]["firestore_reviews"]
        )
        .where(filter=FieldFilter("customer_id", "==", customer_id))
        .get()
    )
    reviews_list = []
    for review in reviews:
        reviews_list.append(review.to_dict())

    return Customer(
        conversations=conversations_list,
        reviews=reviews_list,
        customer_info=customer_info,
    )


# ---------------------------------POST---------------------------------------#
@router.post(path="/agent-activity/{user_id}")
def add_agent_activity(user_id: str, activity: AgentActivity) -> str:
    """
    # add agent activity

    ## path parameters
    **user_id**: *string*
    - user id

    ## agentactivity
    **title**: *string*
    - title of the activity

    **description**: *string*
    - description of the activity

    **customer_id**: *string*
    - customer id

    ## returns
    - ok

    ## raises
    **httpexception** - *400* - error setting in firestore
    - firestore could not set the activity

    """
    try:
        firestore_client.collection("field-agent").document(
            user_id
        ).collection("activities").document().set(
            {
                **activity.model_dump(),
                "timestamp": DatetimeWithNanoseconds.from_timestamp_pb(
                    timestamp_pb2.Timestamp(
                        seconds=activity.timestamp["seconds"],
                        nanos=activity.timestamp["nanoseconds"],
                    )
                ),
            }
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"


@router.post(path="/ask-image-gemini")
def ask_image_gemini(data: AskImageRequest) -> AskImageResponse:
    """
    # Multimodal generate with text and image

    ## Request body [AskImageRequest]
    **image_name**: *string*
    - Image name to be collected from Google Cloud Storage /images

    **user_query**: *string*
    - User query

    ## Response body [AskImageResponse]
    **response**: *str*
    - Generated text

    ## Raises

    **HTTPException** - *400* - Image name not provided
    **HTTPException** - *400* - Image not found in Cloud Storage
    **HTTPException** - *400* - Error generating response from Gemini
    """

    if not data.image_name:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one image to generate the categories.",
        )

    try:
        base_image = Image.from_bytes(
            data=utils_imagen.image_name_to_bytes(image_name=data.image_name)
        )
    except NotFound as e:
        raise HTTPException(
            status_code=404,
            detail="Image not found in Cloud Storage " + str(e),
        ) from e

    try:
        gemini_response = utils_gemini.generate_gemini_pro_vision(
            [data.user_query, base_image]
        )
        response = gemini_response.candidates[0].content.parts[0].text
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error generating response from Gemini " + str(e),
        ) from e

    return AskImageResponse(response=response)


@router.post(path="/generate-agent-activity")
def generate_agent_activity(data: GenerateAgentActivityRequest) -> str:
    """
    # Generate agent activity

    ## Request body [GenerateActivityRequest]
    **user_id**: *string*
    - User id

    **customer_id**: *string*
    - Customer id

    **conversation**: *string*
    - Chat conversation with virtual agent

    **date_time**: *string*
    - Date time for the activity

    ## Returns
    - ok
    """
    try:
        response_palm = utils_palm.text_generation(
            prompt=config["field_service_agent"][
                "prompt_agent_activity"
            ].format(data.conversation)
        ).replace("</output>", "")
        print(response_palm)
        response = json.loads(response_palm)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error generating title / description with PaLM" + str(e),
        ) from e

    agent_activity = AgentActivity(
        title=response["title"],
        description=response["description"],
        customer_id=data.customer_id,
        timestamp=data.timestamp,
    )
    return add_agent_activity(data.user_id, agent_activity)


@router.post(path="/generate-conversations-insights")
def generate_insights_conversations(
    data: GenerateConversationsInsightsRequest,
) -> GenerateConversationsInsightsResponse:
    """
    # Generate insights from conversations.
     - Summary
     - Insights (what went good/not good)
     - Pending tasks
     - Next best action

    ## Request Body [GenerateConversationsInsightsRequest]:
    **conversations**: *list*
    - Conversations to generate the insights from

    ## Response Body [GenerateConversationsInsightsResponse]:
    **summary**: *string*
    - Summary of the conversations

    **entities**: *list*
    - Entities extracted with Cloud NL API

    **insights**: *string*
    - Insights from the conversations

    **pending_tasks**: *string*
    - Pending tasks from the conversations

    **next_best_action**: *string*
    - Next best action extracted from the conversations
    """
    if len(data.conversations) > 1:
        prompt_summary = config["search-persona5"][
            "prompt_summary_multi_conversations"
        ]
        prompt_insights = config["search-persona5"][
            "prompt_insights_multi_conversations"
        ]
        prompt_tasks = config["search-persona5"][
            "prompt_pending_tasks_multi_conversations"
        ]
        prompt_nbs = config["search-persona5"][
            "prompt_nbs_multi_conversations"
        ]
    else:
        prompt_summary = config["search-persona5"][
            "prompt_summary_conversation"
        ]
        prompt_insights = config["search-persona5"][
            "prompt_insights_conversation"
        ]
        prompt_tasks = config["search-persona5"][
            "prompt_pending_tasks_conversation"
        ]
        prompt_nbs = config["search-persona5"]["prompt_nbs_conversation"]

    input_text = json.dumps({"conversations": data.conversations})

    try:
        summary = utils_palm.text_generation(
            prompt=prompt_summary.format(input_text)
        )
        insights = utils_palm.text_generation(
            prompt=prompt_insights.format(input_text)
        )
        pending_tasks = utils_palm.text_generation(
            prompt=prompt_tasks.format(input_text)
        )
        next_best_action = utils_palm.text_generation(
            prompt=prompt_nbs.format(input_text)
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling Vertex AI PaLM API. " f"{str(e)}",
        ) from e

    try:
        entities = utils_cloud_nlp.nlp_analyze_entities(input_text)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling Google Cloud NL API. " f"{str(e)}",
        ) from e

    return GenerateConversationsInsightsResponse(
        summary=summary,
        entities=entities,
        insights=insights,
        pending_tasks=pending_tasks,
        next_best_action=next_best_action,
    )


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

    """
    try:
        event_summary = "Cymbal Support: Your Event Has Been Scheduled!"

        start_date = datetime.fromisoformat(data.start_time)
        end_date = (
            datetime.fromisoformat(data.start_time) + timedelta(minutes=60)
        ).isoformat()

        result_dict = utils_workspace.create_calendar_event(
            event_summary=event_summary,
            attendees=data.attendees,
            start_date=start_date.isoformat(),
            end_date=end_date,
        )
    except Exception as e:
        print(f"ERROR : Calendar Event Creation Failed : {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    calendar_link = (
        "https://calendar.google.com/"
        f"calendar/u/0/r/day/{start_date.year}/"
        f"{start_date.month}/{start_date.day}"
    )

    email_response_html = f"""<html><body><p>Dear Customer,</p>
        <p>Thank you for contacting the support team.</p>
        <p>Your event has been scheduled, and one of our experts 
        will be at your location on the date and time indicated below.</p>

        <p><b>Date: </b>{start_date.strftime('%m/%d/%Y, %H:%M:%S')} UTC</p>
        <p>Link to your calendar appointment: \
            <a href="{calendar_link}">Calendar</a></p>

        <p>Best Regards,<br>You support team</p>"""

    for attendee in data.attendees:
        try:
            utils_workspace.send_email_single_thread(
                email_response_html=email_response_html,
                destination_email_address=attendee,
                email_subject=event_summary,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400, detail="Could not send the email. " + str(e)
            ) from e

    return ScheduleEventResponse(
        conference_call_link=result_dict["hangoutLink"],
        calendar_link=calendar_link,
        icon_url=result_dict["conferenceData"]["conferenceSolution"][
            "iconUri"
        ],
        start_time_iso=result_dict["start"]["dateTime"],
        end_time_iso=result_dict["end"]["dateTime"],
    )


@router.put("/agent-activity/{user_id}/{activity_id}")
def put_agent_activity(
    user_id: str, activity_id: str, activity: AgentActivity
) -> str:
    """
    # Put agent activity

    ## path parameters
    **user_id**: *string*
    - user id

    **activity_id**: *string*
    - activity id

    ## agentactivity
    **title**: *string*
    - title of the activity

    **description**: *string*
    - description of the activity

    **customer_id**: *string*
    - customer id

    ## returns
    - ok

    ## raises
    **httpexception** - *400* - error setting in firestore
    - firestore could not set the activity

    """

    try:
        firestore_client.collection("field-agent").document(
            user_id
        ).collection("activities").document(activity_id).set(
            {
                **activity.model_dump(),
                "timestamp": DatetimeWithNanoseconds.from_timestamp_pb(
                    timestamp_pb2.Timestamp(
                        seconds=activity.timestamp["seconds"],
                        nanos=activity.timestamp["nanoseconds"],
                    )
                ),
            }
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"
