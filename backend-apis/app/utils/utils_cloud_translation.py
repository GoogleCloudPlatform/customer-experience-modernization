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
Utils for Cloud Translation API
"""

from google.cloud import translate_v2 as translate

translate_client = translate.Client()


def translate_text_cloud_api(
    input_text: str, target_language: str = "en-us"
) -> str:
    """

    Args:
        input_text:
        target_language:

    Returns:
        str
            Translated text

    """
    result = translate_client.translate(
        input_text, target_language=target_language
    )

    if result and "translatedText" in result:
        return result["translatedText"]
    return ""
