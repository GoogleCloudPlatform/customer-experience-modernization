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
Persona 5 routers - Contact Center Analyst
"""

import json
import tomllib

from fastapi import APIRouter, HTTPException
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from proto import Message

from app.models.p5_model import (
    Customer,
    GenerateConversationsInsightsRequest,
    GenerateConversationsInsightsResponse,
    GenerateReviewsInsightsRequest,
    GenerateReviewsInsightsResponse,
    SearchConversationsRequest,
    SearchConversationsResponse,
    SearchReviewsRequest,
    SearchReviewsResponse,
    VectorFindNeighborRequest,
    VectorFindNeighborResponse,
)
from app.utils import (
    utils_cloud_nlp,
    utils_palm,
    utils_search,
    utils_vertex_vector,
)

# Load configuration file
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

db = firestore.Client()


router = APIRouter(prefix="/p5", tags=["P5 - Contact Center Analyst"])


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
    customer_info = (
        db.collection(config["search-persona5"]["firestore_customers"])
        .document(customer_id)
        .get()
    )

    if customer_info:
        customer_info = customer_info.to_dict() or {}
    else:
        raise HTTPException(status_code=400, detail="Customer ID not found.")

    conversations = (
        db.collection(config["search-persona5"]["firestore_conversations"])
        .where(filter=FieldFilter("customer_id", "==", customer_id))
        .get()
    )
    conversations_list = []
    for conversation in conversations:
        conversations_list.append(conversation.to_dict())

    reviews = (
        db.collection(config["search-persona5"]["firestore_reviews"])
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


@router.post(path="/generate-reviews-insights")
def generate_insights_reviews(
    data: GenerateReviewsInsightsRequest,
) -> GenerateReviewsInsightsResponse:
    """
    # Generate insights from reviews.
     - Summary
     - Insights (what went good/not good)
     - Pending tasks
     - Next best action
     - Entities

    ## Request Body [GenerateReviewsInsightsRequest]:
    **reviews**: *list*
    - Reviews to generate the insights from

    ## Response Body [GenerateReviewsInsightsResponse]:
    **summary**: *string*
    - Summary of the reviews

    **entities**: *list*
    - Entities extracted with Cloud NL API

    **insights**: *string*
    - Insights from the reviews

    **pending_tasks**: *string*
    - Pending tasks from the reviews

    **next_best_action**: *string*
    - Next best action extracted from the reviews
    """
    prompt_summary = config["search-persona5"]["prompt_summary_reviews"]
    prompt_insights = config["search-persona5"]["prompt_insights_reviews"]
    prompt_tasks = config["search-persona5"]["prompt_pending_tasks_reviews"]
    prompt_nbs = config["search-persona5"]["prompt_nbs_reviews"]

    input_text = json.dumps({"reviews": data.reviews})
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

    return GenerateReviewsInsightsResponse(
        summary=summary,
        entities=entities,
        insights=insights,
        pending_tasks=pending_tasks,
        next_best_action=next_best_action,
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

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation

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

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation
    """

    if not data.conversation_id:
        try:
            conversation_id = utils_search.create_new_conversation(
                user_pseudo_id=data.user_pseudo_id,
                datastore_id=config["search-persona5"][
                    "conversations_datastore_id"
                ],
            ).name
        except GoogleAPICallError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error creating a Vertex AI Conversation session. "
                f"{str(e)}",
            ) from e
    else:
        conversation_id = data.conversation_id

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
        results = utils_search.vertexai_search_multiturn(
            search_query=data.query,
            conversation_id=conversation_id,
            # search_filter=search_filter,  # Uncomment when available
            datastore_id=config["search-persona5"][
                "conversations_datastore_id"
            ],
        )
        results = Message.to_dict(results)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching Vertex AI datatore. " f"{str(e)}",
        ) from e

    responses = {}

    reply = results.get("reply", "")
    summary = reply.get("summary", "")
    summary_text = summary.get("summary_text", "")
    responses["summary"] = summary_text
    responses["user_input"] = data.query

    responses["search_results"] = []
    search_results = results.get("search_results", "")
    for i in search_results:
        document = i.get("document", "")
        struct_data = document.get("struct_data", "")
        responses["search_results"].append(
            {
                "id": i["id"],
                "sentiment": struct_data["sentiment"],
                "agent_id": struct_data["agent_id"],
                "customer_id": struct_data["customer_id"],
                "customer_email": struct_data["customer_email"],
                "product_id": struct_data["product_id"],
                "category": struct_data["category"],
                "rating": struct_data["rating"],
                "title": struct_data["title"],
                "agent_email": struct_data["agent_email"],
                "status": struct_data["status"],
                "conversation": struct_data["conversation"],
            }
        )

    return SearchConversationsResponse(
        responses=responses, conversation_id=conversation_id
    )


@router.post(path="/search-reviews")
def search_reviews(data: SearchReviewsRequest) -> SearchReviewsResponse:
    """
    # Search for reviews on Vertex AI Search Datastore

    ## Request Body [SearchReviewsRequest]:
    **query**: *string*
    - User input to search the datastore

    **user_pseudo_id**: *string*
    - User unique ID

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation

    **rating**: *list*
    - Filter field for conversation rating
    - Allowed values
      - 1
      - 2
      - 3
      - 4
      - 5

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

    **customer_id**: *string*
    - Filter field for review customer_id

    **product_id**: *string*
    - Filter field for review product_id

    ## Response Body [SearchReviewsResponse]:
    **responses**: *dictionary*
    - Search results, including information about the review

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation
    """
    if not data.conversation_id:
        try:
            conversation_id = utils_search.create_new_conversation(
                user_pseudo_id=data.user_pseudo_id,
                datastore_id=config["search-persona5"]["reviews_datastore_id"],
            ).name
        except GoogleAPICallError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error creating a Vertex AI Conversation session. "
                f"{str(e)}",
            ) from e
    else:
        conversation_id = data.conversation_id

    search_filter = ""
    if data.customer_id:
        search_filter += f'customer_id: ANY("{data.customer_id}") '
    if data.product_id:
        search_filter += f'product_id: ANY("{data.product_id}") '
    if data.rating:
        search_filter += 'rating: ANY("'
        search_filter += '","'.join(data.rating)
        search_filter += '") '
    if data.sentiment:
        search_filter += 'sentiment: ANY("'
        search_filter += '","'.join(data.sentiment)
        search_filter += '") '
    if data.category:
        search_filter += 'category: ANY("'
        search_filter += '","'.join(data.category)
        search_filter += '") '

    try:
        results = utils_search.vertexai_search_multiturn(
            search_query=data.query,
            conversation_id=conversation_id,
            # search_filter=search_filter,    # Uncomment when available
            datastore_id=config["search-persona5"]["reviews_datastore_id"],
        )
        results = Message.to_dict(results)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error searching Vertex AI datatore. " f"{str(e)}",
        ) from e

    responses = {}

    reply = results.get("reply", "")
    summary = reply.get("summary", "")
    summary_text = summary.get("summary_text", "")
    responses["summary"] = summary_text
    responses["user_input"] = data.query

    responses["search_results"] = []
    search_results = results.get("search_results", "")

    for i in search_results:
        document = i.get("document", "")
        struct_data = document.get("struct_data", "")
        responses["search_results"].append(
            {
                "id": i["id"],
                "sentiment": struct_data["sentiment"],
                "customer_id": struct_data["customer_id"],
                "customer_email": struct_data["customer_email"],
                "product_id": struct_data["product_id"],
                "category": struct_data["category"],
                "rating": struct_data["rating"],
                "title": struct_data["title"],
                "review": struct_data["review"],
            }
        )

    return SearchReviewsResponse(
        responses=responses, conversation_id=conversation_id
    )


@router.post(path="/vector-find-similar")
def vector_find_similar(
    data: VectorFindNeighborRequest,
) -> VectorFindNeighborResponse:
    """
    # Find Similar documents using embeddings and Vector Search

    ## Request Body [VectorFindNeighborRequest]:
    **input_text**: *string*
    - Input text that will be used as the reference to search
    similar documents.

    **user_journey**: *string*
    - Identifier for conversations or reviews
    - Allowed values:
      - conversations
      - reviews

    ## Response Body [VectorFindNeighborResponse]:
    **similar_vectors**: *list*
    - List of similar documents and their metadata
    """
    try:
        embeddings = utils_palm.get_text_embeddings(data.input_text)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting embeddings from input text. "
            f"{str(e)}",
        ) from e

    try:
        similar_vectors = utils_vertex_vector.find_neighbor(
            feature_vector=embeddings,
            persona=5,
            user_journey=data.user_journey,
        )
        similar_vectors = Message.to_dict(similar_vectors)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calling Vertex AI Vector Search. " f"{str(e)}",
        ) from e

    nearest_neighbors = similar_vectors.get("nearest_neighbors", "")
    neighbors = nearest_neighbors[0].get("neighbors")

    results = []

    firebase_collection = ""
    if data.user_journey == "conversations":
        firebase_collection = "p5-conversations"
    else:
        firebase_collection = "p5-reviews"

    for i in neighbors:
        document = (
            db.collection(firebase_collection)
            .document(i["datapoint"]["datapoint_id"])
            .get()
            .to_dict()
        )
        results.append(document)

    return VectorFindNeighborResponse(similar_vectors=results)
