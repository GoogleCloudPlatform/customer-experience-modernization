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
Utils for Recommendations Service

"""

import tomllib
from typing import Literal

from google.cloud import discoveryengine_v1alpha as discoveryengine
from proto import Message

recommender_client = discoveryengine.RecommendationServiceClient()
document_client = discoveryengine.DocumentServiceClient()
event_client = discoveryengine.UserEventServiceClient()
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)
    rec_config = config["recommendations"]

project_id = config["global"]["project_id"]
datastore_location = config["global"]["datastore_location"]


def format_user_event(
    event_type: Literal[
        "search",
        "view-item",
        "view-item-list",
        "view-home-page",
        "view-category-page",
        "add-to-cart",
        "purchase",
        "media-play",
        "media-complete",
    ],
    user_pseudo_id: str,
    documents: list | None = None,
    optional_user_event_fields: dict | None = None,
) -> discoveryengine.UserEvent:
    """

    Args:
        event_type:
        user_pseudo_id:
        documents:
        optional_user_event_fields:

    Returns:

    """
    user_event = discoveryengine.UserEvent()
    user_event.event_type = event_type
    user_event.user_pseudo_id = user_pseudo_id

    if documents:
        user_event.documents = [
            discoveryengine.DocumentInfo(id=document_id)
            for document_id in documents
        ]

    if optional_user_event_fields:
        for key in optional_user_event_fields:
            try:
                setattr(user_event, key, optional_user_event_fields[key])
            except (AttributeError, TypeError) as e:
                print(e)

    return user_event


def get_recommendations(
    recommendations_type: Literal[
        "recommended-for-you",
        "others-you-may-like",
        "more-like-this",
        "most-popular-items",
    ],
    event_type: Literal[
        "search",
        "view-item",
        "view-item-list",
        "view-home-page",
        "view-category-page",
        "add-to-cart",
        "purchase",
        "media-play",
        "media-complete",
    ],
    user_pseudo_id: str,
    documents: list | None = None,
    optional_user_event_fields: dict | None = None,
):
    """

    Args:
        recommendations_type:
        event_type:
        user_pseudo_id:
        project_id:
        documents:
        optional_user_event_fields:

    Returns:

    """

    user_event = format_user_event(
        event_type, user_pseudo_id, documents, optional_user_event_fields
    )

    serving_config = (
        f"projects/{project_id}/locations/global/collections/"
        "default_collection/dataStores/"
        f"{rec_config['media_rec_datastore_id']}/servingConfigs/"
        f"{rec_config['media_rec_app_id'][recommendations_type]}"
    )

    request = discoveryengine.RecommendRequest(
        serving_config=serving_config,
        user_event=user_event,
    )

    return recommender_client.recommend(request=request)


def collect_events(
    event_type: Literal[
        "search",
        "view-item",
        "view-item-list",
        "view-home-page",
        "view-category-page",
        "add-to-cart",
        "purchase",
        "media-play",
        "media-complete",
    ],
    user_pseudo_id: str,
    documents: list | None = None,
    optional_user_event_fields: dict | None = None,
):
    """

    Args:
        event_type:
        user_pseudo_id:
        url:
        timestamp_milisseconds:
        documents:
        optional_user_event_fields:
    """
    user_event = format_user_event(
        event_type, user_pseudo_id, documents, optional_user_event_fields
    )
    request = discoveryengine.WriteUserEventRequest(
        parent=(
            f"projects/{project_id}/locations/global/collections/"
            "default_collection/dataStores/"
            f"{rec_config['media_rec_datastore_id']}"
        ),
        user_event=user_event,
    )
    event_client.write_user_event(request)


def get_document_datastore(
    document: str,
    branch: str = "default_branch",
):
    """

    Args:
        project_id:
        document:
        datastore_location:
        branch:

    Returns:

    """
    document_ref = document_client.document_path(
        project=project_id,
        location=datastore_location,
        data_store=rec_config["media_rec_datastore_id"],
        branch=branch,
        document=document,
    )

    doc_request = discoveryengine.GetDocumentRequest(name=document_ref)
    doc = document_client.get_document(request=doc_request)

    return Message.to_dict(doc.content)
