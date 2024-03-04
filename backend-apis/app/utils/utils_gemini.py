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
Utils module for Vertex AI Gemini
"""

from vertexai.generative_models._generative_models import GenerationResponse
from vertexai.preview.generative_models import GenerativeModel

gemini_pro_vision = GenerativeModel("gemini-pro-vision")
gemini_pro_text = GenerativeModel("gemini-pro")


def generate_gemini_pro_vision(contents: list) -> GenerationResponse:
    """

    Args:
        contents:

    Returns:

    """
    response = gemini_pro_vision.generate_content(
        contents=contents
    )

    if isinstance(response, GenerationResponse):
        return response

    response_iterator = iter(response)
    return next(response_iterator)


def generate_gemini_pro_text(
        prompt: str,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
        top_k: int = 40,
        top_p: float = 0.9,
        candidate_count: int = 1
) -> str:
    """
    Args:
        prompt:

    Returns:
        LLM response
    """
    response = gemini_pro_text.generate_content(
        contents=[prompt],
        generation_config={
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "candidate_count": candidate_count,
            "max_output_tokens": max_output_tokens,
        }
    )

    return response.text