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
Persona 2 routers - Content Creator
"""

import asyncio
import json
import tomllib

import numpy as np
from fastapi import APIRouter, HTTPException
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore
from google.cloud.exceptions import NotFound
from vertexai.vision_models import Image

from app.models.p2_model import (
    DetectProductCategoriesRequest,
    DetectProductCategoriesResponse,
    EditImageRequest,
    GenerateImageRequest,
    GenerateOrEditImageResponse,
    GenerateTitleDescriptionRequest,
    GenerateTitleDescriptionResponse,
    Product,
    Service,
)
from app.utils import utils_imagen, utils_palm, utils_vertex_vector

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

project_id = config["global"]["project_id"]

# ----------------------------------------------------------------------------#

db = firestore.Client()

# ----------------------------------------------------------------------------#
# Vertex Vector multimodal search
embeddings_client = utils_palm.EmbeddingPredictionClient(project=project_id)
index_endpoint_id = config["multimodal"]["index_endpoint_id"]
deployed_index_id = config["multimodal"]["deployed_index_id"]
vector_api_endpoint = config["multimodal"]["vector_api_endpoint"]
# ----------------------------------------------------------------------------#

router = APIRouter(prefix="/p2", tags=["P2 - Content Creator"])


# -------------------------------DELETE---------------------------------------#
@router.delete(path="/user-product/{user_id}/{product_id}")
def delete_user_product(user_id: str, product_id: str) -> str:
    """
    # Delete user product

    ## Path parameters
    **user_id**: *string*
    - User id

    **product_id**: *string*
    - Product id

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error deleting in Firestore
    - Firestore could not delete the product

    """

    try:
        db.collection("content-creator").document(user_id).collection(
            "products"
        ).document(product_id).delete()
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error deleting in Firestore" + str(e)
        ) from e

    return "ok"


@router.delete(path="/user-service/{user_id}/{service_id}")
def delete_user_service(user_id: str, service_id: str) -> str:
    """
    # Delete user service

    ## Path parameters
    **user_id**: *string*
    - User id

    **service_id**: *string*
    - Service id

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error deleting in Firestore
    - Firestore could not delete the service

    """

    try:
        db.collection("content-creator").document(user_id).collection(
            "services"
        ).document(service_id).delete()
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error deleting in Firestore" + str(e)
        ) from e

    return "ok"


# ---------------------------------POST---------------------------------------#
@router.post(path="/user-product/{user_id}")
def add_user_product(user_id: str, product: Product) -> str:
    """
    # Add user product

    ## Path Parameters [AddUserProductRequest]
    **user_id**: *string*
    - User id

    ## Product
    **title**: *string*
    - Title of the product

    **description**: *string*
    - Description of the product

    **image_urls**: *list[string]*
    - List of image urls of the product

    **labels**: *list[string]*
    - List of labels of the product

    **features**: *list[string]*
    - List of features of the product

    **categories**: *list[string]*
    - List of categories of the product

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error setting in Firestore
    - Firestore could not set the product

    """
    try:
        db.collection("content-creator").document(user_id).collection(
            "products"
        ).document().set(product.model_dump())
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"


@router.post(path="/user-service/{user_id}")
def add_user_service(user_id: str, service: Service) -> str:
    """
    # Add User Service

    ### Request body [AddUserServiceRequest]
    **user_id**: *string*
    - User id

    **service**: *Service*
    - Service to be added

    ### Service
    **title**: *string*
    - Title of the service

    **description**: *string*
    - Description of the service

    **image_urls**: *list[string]*
    - List of image urls of the service

    **labels**: *list[string]*
    - List of labels of the service

    **features**: *list[string]*
    - List of features of the service

    **categories**: *list[string]*
    - List of categories of the service

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error setting in Firestore
    - Firestore could not set the service

    """
    try:
        db.collection("content-creator").document(user_id).collection(
            "services"
        ).document().set(service.model_dump())
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"


@router.post(path="/detect-product-categories")
def detect_product_categories(
    data: DetectProductCategoriesRequest,
) -> DetectProductCategoriesResponse:
    """
    # Detect Product Categories with Vision API

    ## Request body [DetectProductCategoriesRequest]
    **images_uri**: *list*
    - List of image uri

    ## Response body [DetectProductCategoriesResponse]
    **vision_labels**: *list*
    - List of labes from Vision API

    **images_features**: *list*
    - List of features from Imagen Captions and PaLM

    **images_categories**: *list*
    - List of categories from Imagen Captions and PaLM

    **similar_products**: *list*
    - List of similar products ids from Vertex Vector Search

    ## Raises

    **HTTPException** - *400* - Error annotating images with Vision API

    **HTTPException** - *400* - Error extracting captions

    **HTTPException** - *400* - Error extracting features and categories

    **HTTPException** - *400* - Error getting images embeddings

    **HTTPException** - *400* - Error getting similar products

    """
    if not data.images_names:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one image to generate the categories.",
        )

    try:
        vision_labels = utils_imagen.annotate_image_names(data.images_names)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error annotating images with Vision API" + str(e),
        ) from e

    try:
        images_bytes = [
            utils_imagen.image_name_to_bytes(image_name)
            for image_name in data.images_names
        ]
        # Extract labels with Imagen Captioning
        imagen_captions = asyncio.run(
            utils_imagen.run_image_captions(
                images_bytes=images_bytes,
            )
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error extracting captions" + str(e)
        ) from e

    try:
        images_feat_cat = asyncio.run(
            utils_palm.run_predict_text_llm(
                prompts=[
                    config["content_creation"]["prompt_features"].format(
                        "\n".join(imagen_captions)
                    ),
                    config["content_creation"]["prompt_categories"].format(
                        "\n".join(imagen_captions)
                    ),
                ],
            )
        )
        images_feat_cat[0] = images_feat_cat[0].replace("</output>", "")
        images_feat_cat[0] = images_feat_cat[0].replace("```json", "")
        images_feat_cat[0] = images_feat_cat[0].replace("```", "")

        images_feat_cat[1] = images_feat_cat[1].replace("</output>", "")
        images_feat_cat[1] = images_feat_cat[1].replace("```json", "")
        images_feat_cat[1] = images_feat_cat[1].replace("```", "")

        images_features = json.loads(images_feat_cat[0])
        images_categories = json.loads(images_feat_cat[1])
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error extracting features and categories" + str(e),
        ) from e

    images_embeddings = []
    try:
        # Get similar products and retrieve their labels from Firestore
        for image_bytes in images_bytes:
            images_embeddings.append(
                embeddings_client.get_embedding(
                    image_bytes=image_bytes
                ).image_embedding
            )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error getting images embeddings" + str(e)
        ) from e

    image_embedding = list(np.sum(np.array(images_embeddings), axis=0))
    try:
        neighbors = utils_vertex_vector.find_neighbor(
            feature_vector=image_embedding,
            neighbor_count=2,
        )

        similar_products = [
            i.datapoint.datapoint_id
            for i in neighbors.nearest_neighbors[0].neighbors
        ]
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Error getting similar products" + str(e)
        ) from e

    return DetectProductCategoriesResponse(
        vision_labels=list(vision_labels),
        images_features=images_features["product_features"],
        images_categories=images_categories["product_categories"],
        similar_products=similar_products,
    )


@router.post(path="/edit-image")
def image_edit(data: EditImageRequest) -> GenerateOrEditImageResponse:
    """
    # Image editing with Imagen

    ## Request body [EditImageRequest]:
    **prompt**: *string*
    - Prompt for editing the image

    **base_image_name**: *string*
    - Base image name to be collected from Google Cloud Storage /images

    **mask_image_name**: *string* = ""
    - Mask image name to be collected from Google Cloud Storage /images

    **number_of_images**: *int* = 1
    - Number of images to generate

    **negative_prompt**: *string* = ""
    - Negative prompt for editing the image

    ## Response body [GenerateOrEditImageResponse]:
    **generated_images**: *list[GeneratedImage]*

    ## GeneratedImage:
    **image_name**: *string*
    - Name of the image in Cloud Storage

    **image_size**: *tuple(int, int)*
    - Size of the generated image

    **images_parameters**: *dict*
    - Parameters used to generate the image

    ## Raises
    **HTTPException** - *404* - Image not found in Cloud Storage

    **HTTPException** - *400* - Error editing image with Imagen

    """
    try:
        if not data.mask_image_name:
            mask = None
        else:
            mask = Image(
                image_bytes=utils_imagen.image_name_to_bytes(
                    data.mask_image_name
                )
            )
        base_image = Image(
            image_bytes=utils_imagen.image_name_to_bytes(data.base_image_name)
        )
    except NotFound as e:
        raise HTTPException(
            status_code=404,
            detail="Image not found in Cloud Storage " + str(e),
        ) from e
    try:
        imagen_responses = utils_imagen.image_generate_model.edit_image(
            prompt=data.prompt,
            base_image=base_image,
            mask=mask,
            number_of_images=data.number_of_images,
            negative_prompt=data.negative_prompt,
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error editing image with Imagen " + str(e)
        ) from e
    generated_images = []
    for image in imagen_responses:
        image_name = utils_imagen.upload_image_to_storage(
            image._image_bytes  # pylint:  disable=protected-access
        )
        generated_images.append(
            GenerateOrEditImageResponse.GeneratedImage(
                image_name=image_name,
                image_size=image._size,  # pylint:  disable=protected-access
                image_parameters=image.generation_parameters,
            )
        )

    return GenerateOrEditImageResponse(generated_images=generated_images)


@router.post(path="/generate-image")
def image_generate(
    data: GenerateImageRequest,
) -> GenerateOrEditImageResponse:
    """
    # Image generation with Imagen

    ## Request body [EditImageRequest]:
    **prompt**: *string*
    - Prompt for editing the image

    **number_of_images**: *int* = 1
    - Number of images to generate

    **negative_prompt**: *string* = ""
    - Negative prompt for editing the image

    ## Response body [GenerateOrEditImageResponse]:
    **generated_images**: *list[GeneratedImage]*

    ## GeneratedImage:
    **image_name**: *string*
    - Name of the image in Cloud Storage

    **image_size**: *tuple(int, int)*
    - Size of the generated image

    **images_parameters**: *dict*
    - Parameters used to generate the image

    ## Raises
    **HTTPException** - *400* - Error generating image with Imagen

    """
    try:
        imagen_responses = utils_imagen.image_generate_model.generate_images(
            prompt=data.prompt,
            number_of_images=data.number_of_images,
            negative_prompt=data.negative_prompt,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error generating image with Imagen " + str(e),
        ) from e
    generated_images = []
    for image in imagen_responses:
        image_name = utils_imagen.upload_image_to_storage(
            image._image_bytes  # pylint:  disable=protected-access
        )
        generated_images.append(
            GenerateOrEditImageResponse.GeneratedImage(
                image_name=image_name,
                image_size=image._size,  # pylint:  disable=protected-access
                image_parameters=image.generation_parameters,
            )
        )

    return GenerateOrEditImageResponse(generated_images=generated_images)


@router.post(path="/generate-title-description")
def generate_title_description(
    data: GenerateTitleDescriptionRequest,
) -> GenerateTitleDescriptionResponse:
    """
    # Generate Title and Description with PaLM

    ## Request body [GenerateTitleDescriptionRequest]
    **product_categories**: *list*
    - List of product categories

    **context**: *string* = ""
    - Context for the title and description

    ## Response body [GenerateTitleDescriptionResponse]
    **title**: *string*
    - Generated title

    **description**: *string*
    - Generated description

    ## Raises
    **HTTPException** - *400* - Error generating title / description with PaLM

    """
    try:
        response = utils_palm.text_generation(
            prompt=config["content_creation"][
                "prompt_title_description"
            ].format(data.product_categories, data.context),
        )
        response = response.replace("</output>", "")
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = json.loads(response)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error generating title / description with PaLM" + str(e),
        ) from e

    return GenerateTitleDescriptionResponse(
        title=response["title"], description=response["description"]
    )


# ----------------------------------PUT---------------------------------------#
@router.put("/user-product/{user_id}/{product_id}")
def put_user_product(user_id: str, product_id: str, product: Product) -> str:
    """
    # Put user product

    ## Path parameters
    **user_id**: *string*
    - User id

    **product_id**: *string*
    - Product id

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error setting in Firestore
    - Firestore could not set the product

    """

    try:
        db.collection("content-creator").document(user_id).collection(
            "products"
        ).document(product_id).set(product.model_dump())
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"


@router.put("/user-service/{user_id}/{service_id}")
def put_user_service(user_id: str, service_id: str, service: Service) -> str:
    """
    # Put user service

    ## Path parameters
    **user_id**: *string*
    - User id

    **service_id**: *string*
    - Service id

    ## Returns
    - ok

    ## Raises
    **HTTPException** - *400* - Error setting in Firestore
    - Firestore could not set the service

    """

    try:
        db.collection("content-creator").document(user_id).collection(
            "services"
        ).document(service_id).set(service.model_dump())
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"
