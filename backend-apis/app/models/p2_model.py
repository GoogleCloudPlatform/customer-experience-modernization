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
Persona 2 body model
"""

from pydantic import BaseModel


# ---------------------------------Models--------------------------------------#
class Product(BaseModel):
    """
    ### Representation of a product
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
    """

    title: str
    description: str
    image_urls: list[str]
    labels: list[str]
    features: list[str]
    categories: list[str]


class Service(BaseModel):
    """
    ### Representation of a service
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
    """

    title: str
    description: str
    image_urls: list[str]
    labels: list[str]
    features: list[str]
    categories: list[str]


# ---------------------------------POST---------------------------------------#
# @route.post(path="/detect-product-categories")
class DetectProductCategoriesRequest(BaseModel):
    """
    ### Request body for detect-product-categories
    **images_names**: *list[string]*
    - List of images names from Cloud Storage to extract categories from
    """

    images_names: list[str]


class DetectProductCategoriesResponse(BaseModel):
    """
    ### Response body for detect-product-categories
    **vision_labels**: *list*
    - List of labes from Vision API

    **images_features**: *list*
    - List of features from Imagen Captions and PaLM

    **images_categories**: *list*
    - List of categories from Imagen Captions and PaLM

    **similar_products**: *list*
    - List of similar products ids from Vertex Vector Search
    """

    vision_labels: list[str]
    images_features: list
    images_categories: list
    similar_products: list


# @router.post(path="/edit-image")
class EditImageRequest(BaseModel):
    """
    ### Request body for edit-image
    **prompt**: *string*
    - Prompt for editing the image

    **base_image_name**: *string*
    - Base image name to be collected from Google Cloud Storage /images

    **mask_image_name**: *string* = ""
    - Mask image name to be collected from Google Cloud Storage /images

    **number_of_images**: *int* = 1
    - Number of images to generate
    """

    prompt: str  # prompt
    base_image_name: str
    mask_image_name: str = ""
    number_of_images: int = 1
    negative_prompt: str = ""


# @router.post(path="/generate-image")
class GenerateImageRequest(BaseModel):
    """
    ### Request body for generate-image
    **prompt**: *string*
    - Prompt to generate image

    **number_of_images**: *int* = 1
    - Number of images to generate

    **negative_prompt**: *string* = ""
    - Negative prompt to generate image
    """

    prompt: str
    number_of_images: int = 1
    negative_prompt: str = ""


class GenerateOrEditImageResponse(BaseModel):
    """
    ### Response body for generate-image and edit-image

    **generated_images**: *list[GeneratedImage]*

    ### GeneratedImage
    **image_name**: *string*
    - Name of the image in Cloud Storage

    **image_size**: *tuple(int, int)*
    - Size of the generated image

    **images_parameters**: *dict*
    - Parameters used to generate the image
    """

    class GeneratedImage(BaseModel):
        """
        ### Generated Image for generate-image and edit-image
        **image_name**: *string*
        - Name of the image in Cloud Storage

        **image_size**: *tuple(int, int)*
        - Size of the generated image

        **images_parameters**: *dict*
        - Parameters used to generate the image
        """

        image_name: str
        image_size: tuple
        image_parameters: dict

    generated_images: list[GeneratedImage]


# @router.post(path="/generate-title-description")
class GenerateTitleDescriptionRequest(BaseModel):
    """
    ### Request body for generate-title-description
    **product_categories**: *list*
    - List of product categories

    **context**: *string* = ""
    - Context for the title and description
    """

    product_categories: list
    context: str = ""


class GenerateTitleDescriptionResponse(BaseModel):
    """
    ### Response body for generate-title-description
    **title**: *string*
    - Generated title

    **description**: *string*
    - Generated description
    """

    title: str
    description: str
