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
Persona 6 body model
"""

from typing import Literal

from pydantic import BaseModel
from typing_extensions import TypedDict


# ---------------------------------Models--------------------------------------#
class Timestamp(TypedDict):
    """
    ### Timestamp
    **seconds**: *int*
    - Seconds since Unix epoch 1970-01-01T00:00:00Z

    **nanoseconds**: *int*
    - Nanoseconds for the timestamp

    """

    seconds: int
    nanoseconds: int


class AgentActivity(BaseModel):
    """
    ### Representation of an agent activity
    **title**: *string*
    - Title

    **description**: *string*
    - Description

    **customer_id**: *string*
    - Customer Id

    **timestamp**: *Timestamp*
    - Timestamp for the activity since Unix epoch 1970-01-01T00:00:00Z

    ### Timestamp
    **seconds**: *int*
    - Seconds since Unix epoch 1970-01-01T00:00:00Z

    **nanoseconds**: *int*
    - Nanoseconds for the timestamp

    """

    title: str
    description: str
    customer_id: str
    timestamp: Timestamp
    status: Literal["Open", "In progress", "Completed"] = "Open"


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
# @router.post(path="/ask-image-gemini")
class AskImageRequest(BaseModel):
    """
    ### Request body for ask-image-gemini
    **image_name**: *string*
    - Image name to be collected from Google Cloud Storage /images

    **user_query**: *string*
    - User query
    """

    image_name: str
    user_query: str


class AskImageResponse(BaseModel):
    """
    ### Response body for ask-image-gemini
    **response**: *string*
    - Gemini response
    """

    response: str


# @router.post(path="/generate-agent-activity/{user-id}")
class GenerateAgentActivityRequest(BaseModel):
    """
    ### Request body for generate-agent-activity
    **user_id**: *string*
    - User id

    **customer_id**: *string*
    - Customer id

    **conversation**: *string*
    - Chat conversation with virtual agent

    **timestamp**: *int*
    - Timestamp for the activity in milliseconds since Unix epoch 1970-01-01T00:00:00Z
    """

    user_id: str
    customer_id: str
    conversation: str
    timestamp: Timestamp


# @router.post(path="/generate-conversations-insights")
class GenerateConversationsInsightsRequest(BaseModel):
    """
    ### Request Body for generate-conversations-insights
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


# @router.post(path="/search-manuals")
class SearchManualsRequest(BaseModel):
    """
    ### Request body for search-manuals
    **query**: *string*
    - Query

    **user_pseudo_id**: *string*
    - User pseudo id

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
    """

    query: str
    user_pseudo_id: str
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


class SearchManualsResponse(BaseModel):
    """
    ### Response body for search-manuals
    **responses**: *dict*
    - Responses
    """

    responses: dict


# @router.post(path="/schedule-event")
class ScheduleEventRequest(BaseModel):
    """
    ### Request body for schedule-event
    **event_summary**: *string*
    - Event summary

    **attendees**: *list*
    - List of attendees

    **start_time**: *string*
    - Start time

    **end_time**: *string*
    - End time
    """

    attendees: list[str]
    start_time: str  # ISO format. Sample: "2023-12-26T16:00:00+01:00"


class ScheduleEventResponse(BaseModel):
    """
    ### Response body for schedule-event
    **conference_call_link**: *string*
    - Conference call link

    **icon_url**: *string*
    - Icon URL

    **start_time_iso**: *string*
    - Start time ISO

    **end_time_iso**: *string*
    - End time ISO

    """

    conference_call_link: str
    calendar_link: str
    icon_url: str
    start_time_iso: str
    end_time_iso: str
