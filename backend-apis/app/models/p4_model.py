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
Persona 2 body model
"""

from typing import Literal

from pydantic import BaseModel


# ---------------------------------Models--------------------------------------#
class ChatMessage(BaseModel):
    """
    ### Representation of a chat message
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
    """

    text: str
    author: Literal["User", "Agent", "System"] = "User"
    language: str = "en-US"
    link: str = ""
    iconURL: str = ""


# ---------------------------------GET---------------------------------------#
# @router.post(path="/conversation-summary-and-title")
class ConversationSummaryAndTitleResponse(BaseModel):
    """
    ### Response body for conversation-summary-and-title
    **summary**: *string*
    - Conversation Summary

    **title** *string*
    - Conversation Title
    """

    summary: str
    title: str


# ---------------------------------POST---------------------------------------#
# @router.post(path="/send-message/{user_id}/{conversation_id}")
class AddMessageResponse(BaseModel):
    """
    ### Response body for send-message
    **conversation_id**: *string*
    - Conversation Id
    """

    conversation_id: str


# @router.post(path="/rephrase-text")
class RephraseTextRequest(BaseModel):
    """
    ### Request body for rephrase-text
    **rephrase_text_input**: *string*
    - Text to rephrase
    """

    rephrase_text_input: str


class RephraseTextResponse(BaseModel):
    """
    ### Response body for rephrase-text
    **rephrase_text_output**: *string*
    - Rephrased text
    """

    rephrase_text_output: str


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

    event_summary: str
    attendees: list[str]
    start_time: str
    end_time: str


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
    icon_url: str
    start_time_iso: str
    end_time_iso: str


# @router.post(path="/search-conversations")
class SearchConversationsRequest(BaseModel):
    """
    ### Request body for search-conversations
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
    """

    query: str
    user_pseudo_id: str
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
    ### Response body for search-conversations
    **responses**: *dict*
    - Search results, including information about the conversation
    """

    responses: dict


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


# @router.post(path="/translate")
class TranslateRequest(BaseModel):
    """
    ### Request body for translate
    **input_text**: *string*
    - Text to translate

    **target_language**: *string*
    - Target language
    """

    input_text: str
    target_language: str = "en-us"


class TranslateResponse(BaseModel):
    """
    ### Response body for translate
    **output_text**: *string*
    - Translated text
    """

    output_text: str

# @router.post(path="/auto-suggest-query")
class AutoSuggestRequest(BaseModel):
    """
    ### Request body of Conversation text
    **input_text**: *string*
    - Text to translate
    """

    input_text: str


class AutoSuggestResponse(BaseModel):
    """
    ### Response body for Auto Suggest
    **output_text**: *string*
    - Suggested Query text
    """

    output_text: str