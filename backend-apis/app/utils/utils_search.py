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
Utility module for Vertex AI Search API
"""
import json
import tomllib
from copy import deepcopy
from typing import List

from fastapi import HTTPException
from google.api_core import protobuf_helpers
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
from google.cloud.discoveryengine_v1beta.services.search_service.pagers import (
    SearchPager,
)
from google.cloud.discoveryengine_v1beta.types.conversation import Conversation
from proto import Message
from vertexai.preview.language_models import TextGenerationModel

from app.utils import utils_cloud_sql, utils_palm, utils_vertex_vector

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

# Global configurations
project_id = config["global"]["project_id"]
location = config["global"]["location"]

# Vertex Search configurations
datastore_location = config["global"]["datastore_location"]
serving_config_id = config["global"]["serving_config_id"]
images_bucket_name = config["global"]["images_bucket_name"]
project_number = config["global"]["project_number"]

p1_website_datastore_id = config["website_search"]["website_datastore_id"]
multimodal_model = config["multimodal"]["multimodal_model"]
index_endpoint_id = config["multimodal"]["index_endpoint_id"]
deployed_index_id = config["multimodal"]["deployed_index_id"]
vector_api_endpoint = config["multimodal"]["vector_api_endpoint"]

search_client = discoveryengine.SearchServiceClient()
converse_client = discoveryengine.ConversationalSearchServiceClient()
embeddings_client = utils_palm.EmbeddingPredictionClient(project=project_id)
user_event_client = discoveryengine.UserEventServiceClient()
storage_client = storage.Client()

text_gen_client = TextGenerationModel.from_pretrained(model_name="text-bison")
bucket = storage_client.bucket(images_bucket_name)


def get_search_conversation(conversation_resource: str) -> Conversation:
    """

    Args:
        conversation_resource:

    Returns:
        Conversation
    """
    request = discoveryengine.GetConversationRequest(
        name=conversation_resource
    )
    return converse_client.get_conversation(request=request)


def create_new_conversation(
    datastore_id: str, user_pseudo_id: str
) -> discoveryengine.Conversation:
    """

    Args:
        email_address ():
        project_id:
        datastore_location:
        email_datastore_id:

    Raises:
        HTTPException:

    Returns:

    """
    try:
        converse_request = discoveryengine.CreateConversationRequest(
            parent=(
                f"projects/{project_id}/"
                f"locations/{datastore_location}/"
                "collections/default_collection/"
                f"dataStores/{datastore_id}"
            ),
            conversation=discoveryengine.Conversation(
                user_pseudo_id=user_pseudo_id
            ),
        )
        conversation = converse_client.create_conversation(
            request=converse_request
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return conversation


def update_search_conversation(
    conversation: discoveryengine.Conversation, append_to_conversation: dict
):
    """

    Args:
        conversation:
        append_to_conversation:

    Raises:
        HTTPException:
    """
    try:
        original_conversation = discoveryengine.Conversation()
        discoveryengine.Conversation.copy_from(
            instance=original_conversation, other=conversation
        )

        conversation.messages.append(
            discoveryengine.ConversationMessage(
                user_input=discoveryengine.TextInput(
                    input=append_to_conversation["input"]
                )
            )
        )
        conversation.messages.append(
            discoveryengine.ConversationMessage(
                reply=discoveryengine.Reply(
                    summary=discoveryengine.SearchResponse.Summary(
                        summary_text=append_to_conversation["reply"]
                    )
                )
            )
        )
        converse_client.update_conversation(
            conversation=conversation,
            update_mask=protobuf_helpers.field_mask(
                original=original_conversation._pb,  # pylint: disable=protected-access
                modified=conversation._pb,  # pylint: disable=protected-access
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def generate_conversation_history(  # pylint: disable=too-many-statements, too-many-branches, too-many-locals
    message_dict: dict,
    search_doc_dict: dict,
    datastore_id: str = p1_website_datastore_id,
) -> list:
    """

    Args:
        search_doc_dict ():
        message_dict:

    Raises:
        HTTPException:
        HTTPException:
        HTTPException:

    Returns:

    """
    conversation_history = []
    if not message_dict["image"]:
        try:
            response = vertexai_search_multiturn(
                search_query=message_dict["query"],
                conversation_id=search_doc_dict.get("conversation_id", ""),
                datastore_id=datastore_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Could not retrieve search results. " + str(e),
            ) from e

        try:
            results = []
            for i, result in enumerate(response.search_results):
                search_result_dict = Message.to_dict(result)
                document = search_result_dict.get("document", {})
                product_id = document.get("id", "")
                product = utils_cloud_sql.get_product(product_id)
                snapshot = {}
                if product:
                    snapshot = utils_cloud_sql.convert_product_to_dict(product)

                    result = {"id": product_id, "snapshot": snapshot}
                    results.append(result)

                if i == 9 or (
                    len(response.search_results) < 10
                    and i == len(response.search_results) - 1
                ):
                    break

            conversation = Message.to_dict(response.conversation).get(
                "messages"
            )
            conversation_history = []
            if search_doc_dict:
                conversation_history = deepcopy(
                    search_doc_dict.get("conversation", [])
                )

            conversation_history.append(
                {
                    "author": "system",
                    "message": conversation[-1]["reply"]["reply"],
                    "results": results,
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail="Error parsing data from search results. " + str(e),
            ) from e

    else:
        # Multimodal search
        try:
            blob = bucket.blob(f"images/{message_dict['image']}")
            image_contents = blob.download_as_string()
            user_query = message_dict["query"]

            feature_vector = embeddings_client.get_embedding(
                text=user_query, image_bytes=image_contents
            )

            reduced_vector = utils_palm.reduce_embedding_dimension(
                vector_image=feature_vector.image_embedding,
                vector_text=feature_vector.text_embedding,
            )

            neighbors = utils_vertex_vector.find_neighbor(
                feature_vector=reduced_vector,
            )

            num_responses = len(neighbors.nearest_neighbors[0].neighbors)
            results = []
            for i, n in enumerate(neighbors.nearest_neighbors[0].neighbors):
                product = utils_cloud_sql.get_product(
                    int(n.datapoint.datapoint_id)
                )
                snapshot = {}

                if product:
                    snapshot = utils_cloud_sql.convert_product_to_dict(product)
                result = {"id": n.datapoint.datapoint_id, "snapshot": snapshot}
                results.append(result)

                if i == 9 or (num_responses < 10 and i == num_responses - 1):
                    break

            conversation_history = []
            if search_doc_dict:
                conversation_history = deepcopy(
                    search_doc_dict.get("conversation", [])
                )
            system_answer = ""

            references = json.dumps(
                {
                    f"{i+1}": result.get("snapshot", "")
                    for i, result in enumerate(results[:3])
                }
            )

            prompt = ""

            if user_query == "Show items similar to this image.":
                prompt = config["multimodal"]["prompt_without_query"].format(
                    history=json.dumps(conversation_history),
                    results=references,
                )

            else:
                prompt = config["multimodal"]["prompt_with_query"].format(
                    history=json.dumps(conversation_history),
                    results=references,
                    question=user_query,
                )
            system_answer = text_gen_client.predict(
                prompt,
                max_output_tokens=1024,
                temperature=0.2,
                top_k=40,
                top_p=0.8,
            ).text

            conversation_history.append(
                {
                    "author": "system",
                    "message": system_answer,
                    "results": results,
                }
            )

            past_conversations = converse_client.get_conversation(
                name=search_doc_dict.get("conversation_id", "")
            )
            original_conversation = discoveryengine.Conversation()
            discoveryengine.Conversation.copy_from(
                instance=original_conversation, other=past_conversations
            )

            past_conversations.messages.append(
                discoveryengine.ConversationMessage(
                    user_input=discoveryengine.TextInput(
                        input=message_dict["query"]
                    )
                )
            )
            past_conversations.messages.append(
                discoveryengine.ConversationMessage(
                    reply=discoveryengine.Reply(
                        summary=discoveryengine.SearchResponse.Summary(
                            summary_text="Showing relevant items ..."
                        )
                    )
                )
            )
            converse_client.update_conversation(
                conversation=past_conversations,
                update_mask=protobuf_helpers.field_mask(
                    original=original_conversation._pb,  # pylint: disable=protected-access
                    modified=past_conversations._pb,  # pylint: disable=protected-access
                ),
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return conversation_history


def write_vertex_search_user_event(
    search_query: str,
    event_type: str,
    user_pseudo_id: str,
    documents: List,
    datastore_parent: str,
) -> discoveryengine.UserEvent:
    """

    Args:
        search_query:
        event_type:
        user_pseudo_id:
        documents:
        datastore_parent:

    Returns:

    """
    user_event = discoveryengine.UserEvent()
    user_event.event_type = event_type
    user_event.user_pseudo_id = user_pseudo_id
    user_event.search_info.search_query = search_query
    user_event.documents = [
        discoveryengine.DocumentInfo(id=document_id)
        for document_id in documents
    ]
    request = discoveryengine.WriteUserEventRequest(
        parent=datastore_parent, user_event=user_event
    )
    return user_event_client.write_user_event(request=request)


def vertexai_search_oneturn(  # pylint: disable=too-many-arguments, too-many-locals
    search_query: str,
    include_content_spec: bool = True,
    include_citations: bool = True,
    summary_result_count: int = 3,
    return_snippet: bool = True,
    page_size: int = 20,
    search_filter: str = "",
    user_email: str = "user@example.com",
    datastore_id: str = p1_website_datastore_id,
    write_user_events: bool = True,
) -> SearchPager:
    """
    Args:
        search_query: str
            The search query.
        return_snippet: bool
            Whether to return the snippet of the document. Default is True.
        summary_result_count: int
            The number of summary results to return. Default is 3.
        include_citations: bool
            Whether to include citations. Default is True.

    Returns:
        search_service.pagers.SearchPager
            Response message for [SearchService.Search] method.

            Iterating over this object will yield results and resolve
            additional pages automatically.
    """
    serving_config = search_client.serving_config_path(
        project=project_id,
        location=datastore_location,
        data_store=datastore_id,
        serving_config=serving_config_id,
    )

    content_spec = None
    if include_content_spec:
        snippet_spec = (
            discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=return_snippet
            )
        )
        summary_spec = (
            discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=summary_result_count,
                include_citations=include_citations,
            )
        )
        content_spec = discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=snippet_spec, summary_spec=summary_spec
        )

    request = discoveryengine.SearchRequest(
        content_search_spec=content_spec,
        serving_config=serving_config,
        query=search_query,
        page_size=page_size,
        filter=search_filter,
    )

    response = search_client.search(request)

    if write_user_events:
        search_results_documents = []
        for result in response.results:
            search_results_documents.append(result.id)

        write_vertex_search_user_event(
            event_type="search",
            user_pseudo_id=user_email,
            datastore_parent=config["search"]["datastore_parent"].format(
                project_id, datastore_id
            ),
            search_query=search_query,
            documents=search_results_documents,
        )

    return response


def vertexai_search_multiturn(  # pylint: disable=too-many-arguments
    search_query: str,
    conversation_id: str,
    include_citations: bool = True,
    summary_result_count: int = 5,
    datastore_id: str = p1_website_datastore_id,
    user_email: str = "user@example.com",
    write_user_events: bool = True,
    # search_filter: str = ""   # Uncomment when available in Proto
) -> discoveryengine.ConverseConversationResponse:
    """Searches for documents on Vertex AI Search using a conversational
    interface.

    Args:
        search_query (str):
            User query
        conversation_id (str):
            Vertex AI Search conversation identifier
        include_citations (bool):
            Include or not citations
            Default: True
        summary_result_count (int):
            Number of summary results to return
            Default: 5
        datastore_id (str):
            Datastore identifier
            Default: p1_website_datastore_id
        user_email (str):
            User email
            Default: "user@example.com"
        write_user_events (bool):
            Write user events
            Default: True
        search_filter (str):
            Search filter
            Default: ""
    Returns:
        (discoveryengine.ConverseConversationResponse)
        Response for the query.
    """
    serving_config = converse_client.serving_config_path(
        project=project_id,
        location=datastore_location,
        data_store=datastore_id,
        serving_config=serving_config_id,
    )

    summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        include_citations=include_citations,
        summary_result_count=summary_result_count,
    )

    request = discoveryengine.ConverseConversationRequest(
        name=conversation_id,
        query=discoveryengine.TextInput(input=search_query),
        serving_config=serving_config,
        summary_spec=summary_spec,
        # search_filter=search_filter,  # Uncomment when available in Proto
    )

    response = converse_client.converse_conversation(request)

    if write_user_events:
        search_results_documents = []
        for result in response.search_results:
            search_results_documents.append(result.id)

        write_vertex_search_user_event(
            event_type="search",
            user_pseudo_id=user_email,
            datastore_parent=config["search"]["datastore_parent"].format(
                project_id, datastore_id
            ),
            search_query=search_query,
            documents=search_results_documents,
        )

    return response
