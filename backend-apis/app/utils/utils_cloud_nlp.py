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
Utils for Cloud NLP API
"""

from google.cloud import language_v2

client = language_v2.LanguageServiceClient()


def nlp_analyze_entities(input_text: str) -> list:
    """
    Analyzes Entities in a string.

    Args:
      text_content: The text content to analyze
    """
    # Available types: PLAIN_TEXT, HTML
    document_type_in_plain_text = language_v2.Document.Type.PLAIN_TEXT

    language_code = "en"
    document = {
        "content": input_text,
        "type_": document_type_in_plain_text,
        "language_code": language_code,
    }

    encoding_type = language_v2.EncodingType.UTF8
    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )

    results = []
    for entity in response.entities:
        result = {}
        result["name"] = entity.name
        result["entity_type"] = language_v2.Entity.Type(entity.type_).name

        result["metadata"] = []
        for metadata_name, metadata_value in entity.metadata.items():
            result["metadata"].append({metadata_name: metadata_value})

        result["mentions"] = []
        for mention in entity.mentions:
            result["mentions"].append(
                {
                    "text": mention.text.content,
                    "type": language_v2.EntityMention.Type(mention.type_).name,
                    "probability": mention.probability,
                }
            )

        results.append(result)

    return results
