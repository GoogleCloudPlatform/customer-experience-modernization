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
Utils for PaLM

"""


import asyncio
import base64
import functools
import typing

import numpy as np
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import aiplatform
from google.protobuf import struct_pb2
from google.protobuf.json_format import MessageToDict
from vertexai.preview.language_models import (
    TextEmbeddingInput,
    TextEmbeddingModel,
    TextGenerationModel,
)

model = TextGenerationModel.from_pretrained(model_name="text-bison@002")
text_embedding_model = TextEmbeddingModel.from_pretrained(
    "textembedding-gecko@003"
)


def text_generation(
    prompt: str,
    max_output_tokens: int = 1024,
    temperature: float = 0.2,
    top_k: int = 40,
    top_p: float = 0.8,
) -> str:
    """

    Args:
        model:
        prompt:
        max_output_tokens:
        temperature:
        top_k:
        top_p:

    Returns:

    """
    return model.predict(
        prompt=prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
    ).text


class EmbeddingResponse(typing.NamedTuple):
    """Embedding Response"""

    text_embedding: list[float]
    image_embedding: list[float]


class EmbeddingPredictionClient:
    """Wrapper around Prediction Service Client."""

    def __init__(
        self,
        project: str,
        location: str = "us-central1",
        api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com",
    ):
        self.location = location
        self.project = project
        self.set_client_options(api_regional_endpoint)

    def set_client_options(self, api_endpoint: str):
        """

        Args:
            api_endpoint:
        """
        client_options = {"api_endpoint": api_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=client_options
        )

    def get_embedding(self, text: str = "", image_bytes: bytes = b""):
        """

        Args:
            text:
            image_bytes:

        Raises:
            ValueError:

        Returns:

        """
        if not text and not image_bytes:
            raise ValueError(
                "At least one of text or image_bytes must be specified."
            )

        instance = struct_pb2.Value()
        if text:
            instance.struct_value.update({"text": text})

        if image_bytes:
            encoded_content = base64.b64encode(image_bytes).decode("utf-8")
            instance.struct_value.update(
                {"image": {"bytesBase64Encoded": encoded_content}}
            )

        instances = [instance]
        endpoint = (
            f"projects/{self.project}/locations/{self.location}"
            "/publishers/google/models/multimodalembedding@001"
        )
        response = self.client.predict(endpoint=endpoint, instances=instances)
        response_dict = MessageToDict(
            response._pb  # pylint: disable=protected-access
        )
        text_embedding = []
        if text:
            text_emb_value = response_dict["predictions"][0]["textEmbedding"]
            text_embedding = [float(v) for v in text_emb_value]

        image_embedding = []
        if image_bytes:
            image_emb_value = response_dict["predictions"][0]["imageEmbedding"]
            image_embedding = [float(v) for v in image_emb_value]

        return EmbeddingResponse(
            text_embedding=text_embedding, image_embedding=image_embedding
        )


def reduce_embedding_dimension(
    vector_text: list[float] | None = None,
    vector_image: list[float] | None = None,
) -> list:
    """

    Args:
        vector_text:
        vector_image:

    Returns:

    """
    if vector_image and vector_text:
        matrix = np.array([vector_text, vector_image])
        max_pooled_rows = np.sum(matrix, axis=0)
    else:
        max_pooled_rows = np.array(vector_text or vector_image)

    return list(max_pooled_rows)


async def async_predict_text_llm(
    prompt: str,
    max_output_tokens: int = 1024,
    temperature: float = 0.2,
    top_k: int = 40,
    top_p: float = 0.8,
) -> str:
    """

    Args:
        model:
        prompt:
        max_output_tokens:
        temperature:
        top_k:
        top_p:

    Returns:

    """
    loop = asyncio.get_running_loop()
    generated_response = None
    try:
        generated_response = await loop.run_in_executor(
            None,
            functools.partial(
                model.predict,
                prompt=prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_k=top_k,
                top_p=top_p,
            ),
        )
    except GoogleAPICallError as e:
        print(e)
        return ""

    if generated_response and generated_response.text:
        generated_response = generated_response.text.replace("```json", "")
        generated_response = generated_response.replace("```JSON", "")
        generated_response = generated_response.replace("```", "")
        return generated_response
    return ""


async def run_predict_text_llm(
    prompts: list, temperature: float = 0.2
) -> list:
    """

    Args:
        prompts:
        model:
        temperature:

    Returns:

    """
    tasks = [
        async_predict_text_llm(prompt=prompt, temperature=temperature)
        for prompt in prompts
    ]
    results = await asyncio.gather(*tasks)
    return results


def get_text_embeddings(input_text: str) -> list:
    """

    Args:
        input_text:

    Returns:

    """
    text_input = TextEmbeddingInput(text=input_text, task_type="CLUSTERING")

    embeddings = text_embedding_model.get_embeddings(texts=[text_input])[
        0
    ].values

    return embeddings
