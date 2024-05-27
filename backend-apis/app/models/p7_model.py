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
Persona 7 body model
"""
from typing import Literal

from pydantic import BaseModel


# ---------------------------------Models-------------------------------------#
class ReturnMetadata(BaseModel):
    """
    Return Metadta if Item is returned

    **ai_validation_reason**: *string*
    - Reasoning provided by LLM

    **image_uploaded**: *string*
    - image url

    **is_valid**: *bool*
    - True if valid return

    **return_status**: *string*
    - Return Status

    **return_type**: *string*
    - Short Return reason

    **returned_date**: *string*
    - Date returned

    **video_uploaded**: *string*
    - GCS URL of video
    """

    ai_validation_reason: str
    image_uploaded: str = ""
    is_valid: bool
    return_status: Literal["under review", "accept", "reject", "completed"]
    return_type: str
    returned_date: str
    video_uploaded: str = ""


class OrderItem(BaseModel):
    """
    Representation of Order Item
    **id**: *int*
    - Product id

    **title**: *string*
    - Product title

    **description** : *string*
    - Product description

    **image**: *string*
    - Product image

    **features**: *list*
    - Product features

    **categories**: *list*
    - Product categories

    **price**: *float*
    - Product price

    **quantity**: *int*
    - Product quantity

    **is_returned**: *bool"
    - True if Returned

    **return_metadata**: *dict*
    - Return Metadata
    """

    id: int
    title: str
    description: str
    image: str
    features: list
    categories: list
    price: float
    quantity: int
    is_returned: bool = False
    return_metadata: ReturnMetadata | None = None


class Order(BaseModel):
    """
    ### Representation of an order
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
    """

    order_date: str
    order_status: Literal["Inititated", "Fulfilled"]
    order_items: list[OrderItem]
    user_id: str
    email: str
    total_amount: float
    is_delivery: bool
    is_pickup: bool
    pickup_datetime: str


# ---------------------------------POST---------------------------------------#
class ReturnValidationRequest(BaseModel):
    """
    ### Representation of an Validation Request
    **product_url**: *string*
    - Product URL

    **return_image**: *string*
    - Return Image

    **return_video_url**: *string*
    - Return Video URL

    """

    product_url: str
    return_image: str | None = None
    return_video_url: str | None = None


class ReturnValidationResponse(BaseModel):
    """
    ### Representation of an Validation Response
    **valid**: *bool*
    - Valid

    **return_type**: *string
    - Return type

    **reasoning**: *string*
    - model reasoning
    """

    valid: bool
    return_type: str
    reasoning: str


class SearchSimilarRequest(BaseModel):
    """
    ### Representation of an Search Request
    **image**: *string*
    - Image URL

    **query**: *string*
    - Search Query
    """

    image: str
    query: str


class SearchSimilarResponse(BaseModel):
    """
    ###Represnetation of Search Response
    **results**: *list*
    """

    results: list
