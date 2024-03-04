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

import argparse
import asyncio
import base64
import json
import typing
import numpy as np
import os
import random
import requests
import time

from google.cloud import aiplatform
from google.cloud import storage
from google.protobuf import struct_pb2


class EmbeddingResponse(typing.NamedTuple):
    text_embedding: typing.Sequence[float]
    image_embedding: typing.Sequence[float]


class EmbeddingPredictionClient:
    """Wrapper around Prediction Service Client."""
    def __init__(self, project : str,
        location : str = "us-central1",
        api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com"):
        client_options = {"api_endpoint": api_regional_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)  
        self.location = location
        self.project = project

    def get_embedding(self, text : str = None, image_bytes : bytes = None):
        if not text and not image_bytes:
            raise ValueError('At least one of text or image_bytes must be specified.')

        instance = struct_pb2.Struct()
        if text:
            instance.fields['text'].string_value = text

        if image_bytes:
            encoded_content = base64.b64encode(image_bytes).decode("utf-8")
            image_struct = instance.fields['image'].struct_value
            image_struct.fields['bytesBase64Encoded'].string_value = encoded_content

        instances = [instance]
        endpoint = (f"projects/{self.project}/locations/{self.location}"
            "/publishers/google/models/multimodalembedding@001")
        response = self.client.predict(endpoint=endpoint, instances=instances)

        text_embedding = None
        if text:    
            text_emb_value = response.predictions[0]['textEmbedding']
            text_embedding = [v for v in text_emb_value]

        image_embedding = None
        if image_bytes:    
            image_emb_value = response.predictions[0]['imageEmbedding']
            image_embedding = [v for v in image_emb_value]

        return EmbeddingResponse(
            text_embedding=text_embedding,
            image_embedding=image_embedding)
    

def reduce_embedding_dimesion(
        vector_text: list = [],
        vector_image: list = [],
) -> list:
    if vector_image and vector_text:
        matrix = np.array([vector_text, vector_image])
        max_pooled_rows = np.sum(matrix, axis=0)
    else:
        max_pooled_rows = np.array(vector_text or vector_image)

    return list(max_pooled_rows)


def image_text_to_embedding(text: str, image_uri: str) -> list:
    image_contents = requests.get(image_uri).content
    response = embeddings_client.get_embedding(
        text=text[:1020],
        image_bytes=image_contents)

    reduced_vector = reduce_embedding_dimesion(
        vector_image=response.image_embedding,
        vector_text=response.text_embedding)

    return reduced_vector


def generate_metadata_upsert(
        input_dir: str,
        output_dir: str
):
    with open(
        os.path.join(input_dir, "images_title_description.jsonl"), "r"
    ) as f:
        products = [json.loads(p) for p in f.readlines()]

    metadata = {"datapoints": []}
    for product in products:
        id = product['id'] if product['id'] != "0" else "1000"
        print(id)

        feature_vector = image_text_to_embedding(
            text=product["title"] + " " + product["description"],
            image_uri=product["uri"]
        )

        metadata["datapoints"].append(
            {"datapoint_id":id,
             "feature_vector":feature_vector})

    with open(
        os.path.join(output_dir, "vector_metadata.json"), "a"
    ) as f:
        f.write(json.dumps(metadata))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name")
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    
    embeddings_client = EmbeddingPredictionClient(project=args.project_name)
    storage_client = storage.Client()

    generate_metadata_upsert(
        input_dir = args.input_dir,
        output_dir = args.output_dir
    )