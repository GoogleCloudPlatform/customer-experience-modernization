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
Utils for Cloud PubSub
"""


import json
import re

from google.cloud import pubsub_v1


def publish_message(
    topic_name: str, project_id: str, message_body: str
) -> str:
    """

    Args:
        topic_name:
        project_id:
        message_body:

    Returns:

    """
    topic_path = f"projects/{project_id}/topics/{topic_name}"

    publisher = pubsub_v1.PublisherClient()
    future = publisher.publish(topic_path, message_body.encode("utf-8"))

    return future.result()


def create_case_summary_message(
    user_email: str,
    start_time: str,
    case_summary: str,
    conversation_id: str,
    chat_summary: str,
) -> str:
    """
    TODO: Use LLM to extract from the summarization any document links (in cloud run)?
            Or look into Search history to pull relevant links (in cloud run) ? (we need matrics)
    """

    # Sentimental Analysis
    sentimental_matches = re.search(
        r'"sentimental_score": (10|[1-9])', chat_summary
    )
    chat_sentimental_matches = ""
    if sentimental_matches:
        original_sentimental_matches = sentimental_matches.group(1)
        escaped_sentimental_matches = original_sentimental_matches.replace(
            '"', r"\""
        )
        chat_sentimental_matches = escaped_sentimental_matches.replace(
            original_sentimental_matches, escaped_sentimental_matches
        )
    else:
        print("[Sentimental Analys]No sentimental_score found.")
    # End Sentimental Analysis
    if chat_sentimental_matches != "":
        message = {
            "user_email": user_email,
            "start_time": start_time,
            "case_summary": case_summary,
            "conversation_id": conversation_id,
            "sentimental_score": int(chat_sentimental_matches),
        }
    else:
        message = {
            "user_email": user_email,
            "start_time": start_time,
            "case_summary": case_summary,
            "conversation_id": conversation_id,
            "sentimental_score": 5,
        }
    return json.dumps(message, default=str)
