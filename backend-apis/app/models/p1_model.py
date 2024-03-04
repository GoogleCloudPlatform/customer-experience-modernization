# Copyrightll 2023 Google LLC
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
Persona 1 body model
"""

from typing import Literal

from pydantic import BaseModel
from typing_extensions import TypedDict


# ----------------------------------GET---------------------------------------#
# @router.get(path="/get-product/{product_id}")
class GetProductResponse(BaseModel):
    """
    ### Response body for get-product
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
    """

    id: int
    title: str
    description: str
    image: str
    features: list
    categories: list
    price: float
    quantity: int


# @router.get(path="/get-reviews/{product_id}")
class GetReviewsResponse(BaseModel):
    """
    ### Response body for get-reviews
    **reviews**: *list[ReviewDoc]*
    - List of reviews for the product

    ### ReviewDoc
    **review**: *string*
    - Product review

    **sentiment**: *string*
    - Review sentiment

    **stars**: *int*
    - Review stars for the product

    """

    class ReviewDoc(TypedDict):
        """
        ### A dict representing a review document for Firestore
        **review**: *string*
        - Product review

        **sentiment**: *string*
        - Review sentiment

        **stars**: *int*
        - Review stars for the product
        """

        review: str
        sentiment: Literal["positive", "negative", "neutral"]
        stars: int

    reviews: list[ReviewDoc]


# @router.get(path="/get-reviews-summary/{product_id}")
class GetReviewsSummaryResponse(BaseModel):
    """
    ### Response body for get-reviews-summary
    **reviews_summary**: *string*
    - Reviews summary for the product
    """

    reviews_summary: str


# @router.get(path="/get-reviews-summary/{product_id}")
class GetProductSummaryResponse(BaseModel):
    """
    ### Response body for get-product-summary
    **product_summary**: *string*
    - Product summary for the product
    """

    product_summary: str


# ---------------------------------POST---------------------------------------#
# @route.post(path="/collect-recommendations-events")
class CollectRecommendationsEventsRequest(BaseModel):
    """
    ### Request body for collect-recommendations-events
    **event_type**: *string*
    - Event type
    - Valid types:
        - search
        - view-item
        - view-item-list
        - view-home-page
        - view-category-page
        - add-to-cart
        - purchase
        - media-play
        - media-complete

    **user_pseudo_id**: *string*
    - User pseudo id

    **documents**: *list[string]*
    - List of documents ids

    **optional_user_event_fields**: *dict*
    - Optional user event fields
    """

    event_type: Literal[
        "search",
        "view-item",
        "view-item-list",
        "view-home-page",
        "view-category-page",
        "add-to-cart",
        "purchase",
        "media-play",
        "media-complete",
    ]
    user_pseudo_id: str
    documents: list = []
    optional_user_event_fields: dict = {}


# @route.post(path="/compare-products")
class CompareProductsRequest(BaseModel):
    """
    ### Request body for compare-products
    **products**: *list[string]*
    - List of products ids
    """

    products: list[str]


# @route.post(path="/initiate-vertexai-recommendations")
class InitiateVertexAIRecommendationsRequest(BaseModel):
    """
    ### Request body for initiate-vertexai-recommendations
    **recommendation_type**: *string*
    - Recommendation type
    - Valid types:
        - recommended-for-you
        - others-you-may-like
        - more-like-this
        - most-popular-items
        - new-and-featured

    **event_type**: *string*
    - Event type
    - Valid types:
        - search
        - view-item
        - view-item-list
        - view-home-page
        - view-category-page
        - add-to-cart
        - purchase
        - media-play
        - media-complete

    **user_pseudo_id**: *string*
    - User pseudo-id

    **documents**: *list[string]*
    - List of document ids

    **optional_user_event_fields**: *dict*
    - Optional user event fields
    """

    recommendation_type: Literal[
        "recommended-for-you",
        "others-you-may-like",
        "more-like-this",
        "most-popular-items",
        "new-and-featured",
    ]
    event_type: Literal[
        "search",
        "view-item",
        "view-item-list",
        "view-home-page",
        "view-category-page",
        "add-to-cart",
        "purchase",
        "media-play",
        "media-complete",
    ]
    user_pseudo_id: str
    documents: list = []
    optional_user_event_fields: dict = {}


class InitiateVertexAIRecommendationsResponse(BaseModel):
    """
    ### Response body for initiate-vertexai-recommendations
    **recommendations_doc_id**: *string*
    - Firestore document id for recommendations
    """

    recommendations_doc_id: str


# @route.post(path="/initiate-vertexai-search")
class InitiateVertexAISearchRequest(BaseModel):
    """
    ### Request body for initiate-vertexai-search
    **visitor_id**: *string*
    - Visitor id

    **query**: *string*
    - Search query

    **image**: *string*
    - Image url

    **search_doc_id**: *string*
    - Firestore document id for search.
    - If it is the first interaction, this is empty.

    **user_id**: *string*
    - User id
    """

    visitor_id: str
    query: str = ""
    image: str = ""
    search_doc_id: str = ""
    user_id: str = ""


class InitiateVertexAISearchResponse(BaseModel):
    """
    ### Response body for initiate-vertexai-search
    **search_doc_id**: *string*
    - Firestore document id for search
    """

    document_id: str


# @route.post(path="/salesforce-email-support")
class SalesforceEmailSupportRequest(BaseModel):
    """
    ### Request body for support-email-support
    **email_content**: *string*
    - Email content

    **email_html**: *string*
    - Email html

    **email_address**: *string*
    - Email address

    **user_name**: *string*
    - User name

    **subject**: *string*
    - Email subject

    **case_number**: *string*
    - Case number

    **salesforce_thread_id**: *string*
    - Salesforce thread id

    **is_human_talking**: *bool*
    - Whether a human should answer instead of the AI model
    """

    email_content: str
    email_html: str
    email_address: str
    user_name: str
    subject: str
    case_number: str
    salesforce_thread_id: str
    is_human_talking: bool


class SalesforceEmailSupportResponse(BaseModel):
    """
    ### Response body for support-email-response
    **email_response**: *string*
    - Email response

    **is_human_talking**: *bool*
    - Whether a human should answer instead of the AI model

    **docs_id**: *string*
    - Google Docs Id for the human response
    """

    email_response: str
    is_human_talking: bool
    docs_id: str


# @route.post(path="/send-email-from-docs")
class SendEmailFromDocsRequest(BaseModel):
    """
    ### Request body for send-email-from-docs
    ** docs_id**: *string*
    - Google Docs Id to get the email from
    """

    docs_id: str


# @route.post(path="/translate-text")
class TranslateTextRequest(BaseModel):
    """
    ### Request body for translate-text
    **text**: *list[string]*
    - List of strings representing the text to translate

    **target_language**: *string*
    - Target language

    **source_language**: *string*
    - Source language
    """

    text: list
    target_language: str
    source_language: str = "en"


class TranslateTextResponse(BaseModel):
    """
    ### Response body for translate-text
    **translation**: *list[string]*
    - List of strings representing the translated text
    """

    translation: list


# @route.post(path="/trigger-unstructured-recommendations")
class TriggerUnstructuredRecommendationsRequest(BaseModel):
    """
    ### Request body for trigger-unstructured-recommendations
    **message**: *dict*
    - Pubsub message representing the recommendations request
    """

    message: dict


# @route.post(path="/trigger-unstructured-search")
class TriggerUnstructuredSearchRequest(BaseModel):
    """
    ### Request body for trigger-unstructured-search
    **message**: *dict*
    - Pubsub message representing the search request
    """

    message: dict

# @route.post(path="/add-order")
class OrderRequest(BaseModel):
    """
    ### Request body of order placed

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
    order_status: str
    order_items: list
    user_id: str
    email: str
    total_amount: float
    is_delivery: bool
    is_pickup: bool
    pickup_datetime: str

# @route.post(path="/trigger-recommendation-email")
class TriggerRecommendationEmailRequest(BaseModel):
    """
    ### Request body for trigger-recommendation-email
    **message**: *dict*
    - Pubsub message representing the recommendations request
    """

    message: dict
