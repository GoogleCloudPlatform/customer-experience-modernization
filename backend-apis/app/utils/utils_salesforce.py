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
Utils for Salesforce
"""

import base64
import binascii
import json
import tomllib

import numpy as np
from fastapi.exceptions import HTTPException
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore, translate_v2
from google.cloud.discoveryengine_v1beta.types.conversation import Conversation
from proto import Message

from app.models.p1_model import SalesforceEmailSupportRequest
from app.utils import (
    utils_cloud_sql,
    utils_palm,
    utils_search,
    utils_vertex_vector,
    utils_workspace,
)

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

project_id = config["global"]["project_id"]
location = config["global"]["location"]
multimodal_model = config["multimodal"]["multimodal_model"]
index_endpoint_id = config["multimodal"]["index_endpoint_id"]
deployed_index_id = config["multimodal"]["deployed_index_id"]
vector_api_endpoint = config["multimodal"]["vector_api_endpoint"]

prompt_questions = config["salesforce"]["prompt_email_support"]

datastore_location = config["global"]["datastore_location"]
email_datastore_id = config["website_search"]["website_datastore_id"]

translate_client = translate_v2.Client()
embeddings_client = utils_palm.EmbeddingPredictionClient(project=project_id)
db = firestore.Client()


def results_from_questions(questions: list, conversation_id: str) -> list:
    """Search for results from questions.

    Args:
        questions:
            Questions to be searched

    Returns:
        list
            List of dict representations of results
    """
    results = []
    for question in questions:
        if (
            "image" in question.lower()
            or "picture" in question.lower()
            or "attach" in question.lower()
        ):
            continue

        try:
            search_results = utils_search.vertexai_search_multiturn(
                search_query=question,
                conversation_id=conversation_id,
                summary_result_count=2,
                datastore_id=config["website_search"]["website_datastore_id"],
            )
            search_results_dict = Message.to_dict(search_results)
        except GoogleAPICallError as e:
            print(e)
            continue

        result = {}
        result["question"] = question
        result["summary_text"] = search_results_dict.get("reply", {}).get(
            "reply", ""
        )
        result["links"] = []

        for i, r in enumerate(search_results_dict.get("search_results", [])):
            if i == 2:
                break
            result["links"].append(
                config["salesforce"]["website_uri"] + r["id"]
            )
        results.append(result)

    return results


def set_docs_id(case_number: str, docs_id: str):
    """Set the Case Google Docs id in Firestore

    Args:
        case_number: str
            The case number. Used as the document id in Firestore.
        docs_id:
            The case Google Docs id.
    """
    document = db.collection("salesforce_cases").document(case_number)
    document.set({"docs_id": docs_id}, merge=True)


def translate_email(email_content: str, email_response: str) -> str:
    """Translate email response to the email content language
       using Google Translation API.

    Args:
        email_content: str
            Email content
        email_response: str
            Email response
    Returns:
        str
            Translated email response to the email content language

    """
    # Translate email
    target_language = translate_client.detect_language(email_content)[
        "language"
    ]
    translated_email = email_response
    if target_language != "en":
        results = []
        email_response_split = email_response.split()
        i = 0
        while i * 128 < len(email_response_split):
            result = translate_client.translate(
                " ".join(email_response_split[i * 128 : i * 128 + 128]),
                target_language=target_language,
                source_language="en",
            )
            results.append(result)
            i += 1
        for r in results:
            translated_email += r["translatedText"].replace("> ", ">")

        email_response = translated_email
    return translated_email


def get_resources(
    data: SalesforceEmailSupportRequest,
) -> tuple[dict, dict, Conversation]:
    """Get salesforce resources in Firestore.
       Try to create resources if they don't exist.

    Args:
        data: SalesforceEmailSupporRequest
            The email support request

    Raises:
        HTTPException:
            If it is not possible to get the thread id

    Returns:
        tuple
            case_dict, email_content and Conversation
    """
    case_document = db.collection("salesforce_cases").document(
        data.case_number
    )
    case_document_snapshot = case_document.get()
    case_dict = case_document_snapshot.to_dict() or {
        "user_email_address": data.email_address,
        "subject": data.subject,
        "user_name": data.user_name,
        "salesforce_thread_id": data.salesforce_thread_id,
    }

    if case_document_snapshot.exists and case_dict:
        email_thread = utils_workspace.get_gmail_thread(
            user_id=config["salesforce"]["user_id"],
            internal_thread_id=case_dict["internal_thread_id"],
        )
        case_dict["email_message_id"] = utils_workspace.get_last_message_id(
            email_thread
        )
        case_dict["internal_message_id"] = email_thread["messages"][0]["id"]

        conversation = utils_search.get_search_conversation(
            conversation_resource=case_dict["conversation_resource"]
        )

    else:
        case_dict["docs_id"] = ""
        # Create a new conversation
        conversation = utils_search.create_new_conversation(
            datastore_id=email_datastore_id,
            user_pseudo_id=data.email_address,
        )
        case_dict["conversation_resource"] = conversation.name

        # Retrieve thread_id from Gmail
        emails = utils_workspace.list_gmail_threads(
            user_id=config["salesforce"]["user_id"],
            email_address=data.email_address,
            subject=data.subject,
        )

        try:
            case_dict["internal_thread_id"] = emails["threads"][0]["id"]
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"{str(e)}. Could not get thread id."
            ) from e

        email_thread = utils_workspace.get_gmail_thread(
            user_id=config["salesforce"]["user_id"],
            internal_thread_id=case_dict["internal_thread_id"],
        )
        case_dict["internal_message_id"] = email_thread["messages"][0]["id"]

        (
            case_dict["email_thread_id"],
            case_dict["email_message_id"],
        ) = utils_workspace.get_email_thread_id(email_thread)

    case_document.set(case_dict)

    return case_dict, email_thread, conversation


def salesforce_multimodal(
    attachments: list,
    internal_message_id: str,
    conversation: Conversation,
    questions: list,
) -> dict:
    """Try to answer multimodal questions from the email.

    Args:
        attachments: list
            Attachments from the email
        internal_message_id: str
            Internal message id
        email_content: str
            Email content
        conversation: Conversation
            Current conversation resource

    Returns:
        dict
            A dict representing the result

    """
    # Extract embedding for each image
    images_embeddings = []  # Embeddings of all images

    for attachment in attachments:
        try:
            email_attachment = utils_workspace.get_attachment(
                attachment_id=attachment,
                internal_message_id=internal_message_id,
                user_id=config["salesforce"]["user_id"],
            )
            # Replace the characters in the base64 string
            image_bytes = (
                email_attachment["data"]
                .replace("_", "/")
                .replace("-", "+")
                .replace(" ", "")
            )
            image_bytes = base64.b64decode(image_bytes)
        except binascii.Error as e:
            print(e)
            continue
        else:
            images_embeddings.append(
                embeddings_client.get_embedding(
                    image_bytes=image_bytes
                ).image_embedding
            )
    if images_embeddings:
        image_embedding = list(np.sum(np.array(images_embeddings), axis=0))
        return embeddings_search(
            image_embedding=image_embedding,
            conversation=conversation,
            questions=questions,
        )
    return {}


def get_questions_from_email(email_content: str) -> list:
    """Get questions from email using GenAI.

    Args:
        email_content: str
            Email content
        multimodal: bool
            Whether to use multimodal prompt or not.

    Returns:
        dict
            A dict of questions found by GenAI

    """
    questions_dict = {}
    try:
        questions = utils_palm.text_generation(
            prompt=prompt_questions.format(email_content)
        )
        questions = questions.replace("```json", "")
        questions = questions.replace("```", "")
        questions_dict = json.loads(questions)
    except (json.JSONDecodeError, GoogleAPICallError) as e:
        print(e)

    questions = questions_dict.get("questions_inquiries_orders", [])

    return questions


def is_human_needed(email_content: str) -> bool:
    """Check if customer wants to talk to a human agent.

    Args:
        email_content: str
            Email content

    Returns:
        bool
            If human is needed

    """
    is_human_talking_palm = utils_palm.text_generation(
        prompt=config["salesforce"]["prompt_talk_to_human"].format(
            email_content
        ),
    )
    if "true" not in is_human_talking_palm.lower():
        return False
    return True


def embeddings_search(
    image_embedding: list[float], conversation: Conversation, questions: list
) -> dict:
    """Search multimodal questions from email

    Args:
        image_embedding: list[float]
            Attached image embedding
        email_content: str
            Email content
        conversation: Conversation
            Current conversation resource

    Returns:
        dict
            A dict representing the result
    """
    # This means the parsing succeeded and there are questions
    multimodal_questions = []
    for question in questions:
        if (
            "image" in question.lower()
            or "picture" in question.lower()
            or "attach" in question.lower()
        ):
            multimodal_questions.append(question)

    if multimodal_questions:
        # Extract embedding for each text
        text_embeddings = []
        for question in multimodal_questions:
            text_embeddings.append(
                embeddings_client.get_embedding(text=question).text_embedding
            )

        # Combine embeddings: Texts + Images
        multimodal_embedding = utils_palm.reduce_embedding_dimension(
            vector_text=list(np.sum(np.array(text_embeddings), axis=0)),
            vector_image=image_embedding,
        )
    else:
        # Combine embeddings: Images
        multimodal_embedding = utils_palm.reduce_embedding_dimension(
            vector_image=image_embedding
        )

    neighbors = utils_vertex_vector.find_neighbor(
        feature_vector=multimodal_embedding,
        neighbor_count=2,
    )

    append_to_conversation = {}
    if multimodal_questions:
        append_to_conversation["input"] = " \n".join(multimodal_questions)
    else:
        append_to_conversation[
            "input"
        ] = "Show products similar to the attached image."

    neighbors_result = {}
    neighbors_result["question"] = append_to_conversation["input"]
    neighbors_result["links"] = []
    neighbors_result["snapshots"] = []
    for n in neighbors.nearest_neighbors[0].neighbors:
        neighbors_result["links"].append(
            config["salesforce"]["website_uri"] + n.datapoint.datapoint_id
        )
        product = utils_cloud_sql.get_product(int(n.datapoint.datapoint_id))
        if product:
            snapshot = utils_cloud_sql.convert_product_to_dict(product)
            neighbors_result["snapshots"].append(snapshot)

    references = json.dumps(
        {
            f"{i+1}": snapshot
            for i, snapshot in enumerate(neighbors_result["snapshots"])
        }
    )
    append_to_conversation["reply"] = utils_palm.text_generation(
        prompt=config["salesforce"]["prompt_generate_reply"].format(
            references=references
        ),
    )
    neighbors_result["summary_text"] = append_to_conversation["reply"]

    # Append to current Conversation
    utils_search.update_search_conversation(
        conversation=conversation,
        append_to_conversation=append_to_conversation,
    )
    return neighbors_result

