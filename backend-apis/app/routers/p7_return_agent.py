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
Persona 7 routers - Return Agent
"""

import base64
import http.client
import json
import tomllib
import typing
import urllib.request

from fastapi import APIRouter, HTTPException
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore_v1 as firestore
from google.cloud import storage
from vertexai.preview.generative_models import Image, Part

from app.models.p7_model import (
    Order,
    ReturnValidationRequest,
    ReturnValidationResponse,
    SearchSimilarRequest,
    SearchSimilarResponse,
)
from app.utils import (
    utils_cloud_sql,
    utils_gemini,
    utils_palm,
    utils_vertex_vector,
)

# Load configuration file
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)
# Global configurations
project_id = config["global"]["project_id"]
images_bucket_name = config["global"]["images_bucket_name"]
embeddings_client = utils_palm.EmbeddingPredictionClient(project=project_id)

storage_client = storage.Client()

firestore_client = firestore.Client()

router = APIRouter(prefix="/p7", tags=["P7 - Return Agent"])


# ---------------------------------POST-------------------------------------#
@router.post(path="/order-update/{order_id}")
def order_update(order_id: str, data: Order) -> str:
    """
    Updates the Order dictionary for order id provided in parameter
    ## Path parameters
    **order_id**: *string*
    - Order id

    ## data [Order]
    **order_date**: *string*
    - Date of Order

    **order_status** : *string*
    - Order Status

    **order_items**: *list*
    - List of items ordered

    **user_id**: *string*
    - User who ordered

    **email**: *string*
    - user email

    **total_amount**: *float*
    - Amount of order

    **is_delivery**: *boolean*
    - Home delivery

    **is_pickup**: *boolean*
    - Pickup from the store

    **pickup_datetime**: *string*
    - scheduled pickup time

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error updating in Firestore
    - Firestore could not update the order

    """

    try:
        firestore_client.collection("orders").document(order_id).set(
            data.model_dump()
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error deleting in Firestore" + str(e)
        ) from e

    return "ok"


# ---------------------------------POST----------------------------------------#
@router.post(path="/return-validation")
def return_validation(
    data: ReturnValidationRequest,
) -> ReturnValidationResponse:
    """
    Validation of return based on product image in catalogue as original Image
    and uploaded Image or Video, this function excepts image base64 string or
    Video gcs path
    ### Representation of an Validation Request
    **product_url**: *string*
    - Product URL - Catalogue Public Image URL

    **return_image**: *string*
    - Return Image in base64

    **return_video_url**: *string*
    - GCS Video URL of returning item

    Returns:
    ### Representation of an Validation Response
    **valid**: *bool*
    - Valid
    **return_type**: *string*
    - returning reason in audio mapped to type
    **reasoning**: *string*
    - model reasoning
    """

    def get_image_bytes_from_url(image_url: str) -> bytes:
        with urllib.request.urlopen(image_url) as response:
            response = typing.cast(http.client.HTTPResponse, response)
            image_bytes = response.read()
        return image_bytes

    image_bytes = get_image_bytes_from_url(
        str(data.product_url).replace(" ", "%20")
    )

    product_image = Image.from_bytes(image_bytes)

    return_type = "No Longer Needed"
    instructions = ""
    prompt1 = ""
    prompt2 = ""
    return_media = None
    prompt3 = ""

    if data.return_image:
        return_bytes = base64.b64decode(data.return_image)
        return_media = Image.from_bytes(return_bytes)

        instructions = """Instructions: Consider yourself a order return agent,
        you will be provided with two images one of original product and one of return item.
        You need to compare the product items in the images and validate the return."""
        prompt1 = "Original Product Image:"
        prompt2 = "Return Product Image:"
        prompt3 = """
        Compare the product item in the images and validate the return. Provide response as a json with keys
        is_valid:boolean and reasoning:string
        """

    if data.return_video_url:
        return_media = Part.from_uri(
            data.return_video_url, mime_type="video/mp4"
        )

        instructions = """Instructions: Consider yourself a order return agent,
        you will be provided with a image of original product and one video of return item.
        You need to compare the item in image and product in video and validate the return."""
        prompt1 = "Original Product Image:"
        prompt2 = "Return Product Video:"
        prompt3 = """
        Compare item in image and item in video and validate the return.
        Check if any resoning provided in audio as well and append it to reasoning if provided.
        Based on the audio determine return_type among 'Found Better Price' , 'Defective', 'No Longer Needed'. If not determined default to 'No Longer Needed'
        Provide response as a json with keys is_valid:boolean, return_type:string and reasoning:string
        """

    contents = [
        instructions,
        prompt1,
        product_image,
        prompt2,
        return_media,
        prompt3,
    ]

    try:
        response = utils_gemini.generate_gemini_pro_vision(contents).text

        response = json.loads(
            response.replace("```json", "").replace("```", "")
        )

        if "return_type" in response.keys():
            return_type = response["return_type"]

    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error generating response from Gemini " + str(e),
        ) from e

    return ReturnValidationResponse(
        valid=response["is_valid"],
        return_type=return_type,
        reasoning=response["reasoning"],
    )


# ---------------------------------POST----------------------------------------#
@router.post(path="/search-similar")
def search_similar(data: SearchSimilarRequest) -> SearchSimilarResponse:
    """
    Searches for the similar product options for the returning product
    based on image and category

    ### Representation of an Search Request
    **image**: *string*
    - Image URL - bucket/path/to/img

    **query**: *string*
    - Search Query

    Returns:
    ### Representation of an Search Response
    **results**: *list*
    - List of Similar Products

    """
    # Multimodal search
    try:
        image_path = data.image.split("/", 1)
        bucket = storage_client.bucket(image_path[0])
        blob = bucket.blob(f"{image_path[1]}")
        image_contents = blob.download_as_string()

        feature_vector = embeddings_client.get_embedding(
            text=data.query, image_bytes=image_contents
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
            results.append(
                {"id": n.datapoint.datapoint_id, "snapshot": snapshot}
            )

            if i == 9 or (num_responses < 10 and i == num_responses - 1):
                break
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return SearchSimilarResponse(results=results)
