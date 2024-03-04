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
Persona 5 body model
"""

from typing import Literal

from pydantic import BaseModel


# -------------------------------Models---------------------------------------#
# @router.get(path="/customer")
class Customer(BaseModel):
    """
    ### Representation of a customer
    **conversations**: *list*
    - List of all the conversations that customer had with the Call Center

    **reviews**: *list*
    - List of all the reviews submited by that customer

    **customer_info**: *dict*
    - Information about that customer extracted from the CDP
    """

    conversations: list
    reviews: list
    customer_info: dict


# ---------------------------------POST---------------------------------------#
# @router.post(path="/generate-conversations-insights")
class GenerateConversationsInsightsRequest(BaseModel):
    """
    ## Request Body for generate-conversations-insights
    **conversations**: *list*
    - Conversations to generate the insights from
    """

    conversations: list[dict]


class GenerateConversationsInsightsResponse(BaseModel):
    """
    ### Response Body for generate-conversations-insights
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

    summary: str
    entities: list
    insights: str
    pending_tasks: str
    next_best_action: str


# @router.post(path="/generate-reviews-insights")
class GenerateReviewsInsightsRequest(BaseModel):
    """
    ### Request body for generate-reviews-insights
    **reviews**: *list*
    - Reviews to generate the insights from
    """

    reviews: list[dict]


class GenerateReviewsInsightsResponse(BaseModel):
    """
    ### Response Body for generate-reviews-insights
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

    summary: str
    entities: list
    insights: str
    pending_tasks: str
    next_best_action: str


# @router.post(path="/search-conversations")
class SearchConversationsRequest(BaseModel):
    """
    ### Request Body for search-conversations
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
    """

    query: str
    user_pseudo_id: str
    conversation_id: str = ""
    agent_id: str = ""
    customer_id: str = ""
    product_id: str = ""
    rating: list[Literal["1", "2", "3", "4", "5"]] = []
    status: list[Literal["resolved", "not resolved"]] = []
    sentiment: list[Literal["positive", "negative", "neutral"]] = []
    category: list[
        Literal[
            "Bath Robe",
            "Bath Towel Set",
            "Bed",
            "Bookcase",
            "Chair",
            "Console Table",
            "Dining Table",
            "Game Table",
            "Grill",
            "Office Chair",
            "Ottoman",
            "Outdoor Heater",
            "Pool",
            "Sofa",
            "Tool Cabinet",
        ]
    ] = []


class SearchConversationsResponse(BaseModel):
    """
    ### Response Body for search-conversations
    **responses**: *dictionary*
    - Search results, including information about the conversation

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation

    """

    responses: dict
    conversation_id: str


# @router.post(path="/search-reviews")
class SearchReviewsRequest(BaseModel):
    """
    ### Request Body for search-reviews
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
    """

    query: str
    user_pseudo_id: str
    conversation_id: str = ""
    customer_id: str = ""
    product_id: str = ""
    rating: list[Literal["1", "2", "3", "4", "5"]] = []
    sentiment: list[Literal["positive", "negative", "neutral"]] = []
    category: list[
        Literal[
            "Bath Robe",
            "Bath Towel Set",
            "Bed",
            "Bookcase",
            "Chair",
            "Console Table",
            "Dining Table",
            "Game Table",
            "Grill",
            "Office Chair",
            "Ottoman",
            "Outdoor Heater",
            "Pool",
            "Sofa",
            "Tool Cabinet",
        ]
    ] = []


class SearchReviewsResponse(BaseModel):
    """
    ### Response Body for search-reviews
    **responses**: *dictionary*
    - Search results, including information about the review

    **conversation_id**: *string*
    - ID of the Vertex AI Search Conversation
    """

    responses: dict
    conversation_id: str


# @router.post(path="/vector-find-similar")
class VectorFindNeighborRequest(BaseModel):
    """
    ### Request Body for vector-find-similar
    **input_text**: *string*
    - Input text that will be used as the reference to search
    similar documents.

    **user_journey**: *string*
    - Identifier for conversations or reviews
    - Allowed values:
      - conversations
      - reviews

    """

    input_text: str
    user_journey: Literal["conversations", "reviews"] = "conversations"


class VectorFindNeighborResponse(BaseModel):
    """
    ### Response Body for vector-find-similar
    **similar_vectors**: *list*
    - List of similar documents and their metadata

    """

    similar_vectors: list
