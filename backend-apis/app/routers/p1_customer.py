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
Persona 1 routers - Customer
"""

import base64
import json
import tomllib

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import firestore, pubsub_v1
from google.cloud import translate_v2 as translate
from proto import Message

from app.models.p1_model import (
    CollectRecommendationsEventsRequest,
    CompareProductsRequest,
    GetProductResponse,
    GetProductSummaryResponse,
    GetReviewsResponse,
    GetReviewsSummaryResponse,
    InitiateVertexAIRecommendationsRequest,
    InitiateVertexAIRecommendationsResponse,
    InitiateVertexAISearchRequest,
    InitiateVertexAISearchResponse,
    SalesforceEmailSupportRequest,
    SalesforceEmailSupportResponse,
    SendEmailFromDocsRequest,
    TranslateTextRequest,
    TranslateTextResponse,
    TriggerUnstructuredRecommendationsRequest,
    TriggerUnstructuredSearchRequest,
    OrderRequest,
    TriggerRecommendationEmailRequest
)
from app.utils import (
    utils_cloud_sql,
    utils_gemini,
    utils_palm,
    utils_recommendations,
    utils_salesforce,
    utils_search,
    utils_workspace,
)

# ----------------------------------------------------------------------------#
# Load configuration file (config.toml) and global configs
with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

# ----------------------------------------------------------------------------#

# ----------------------------------------------------------------------------#
# Clients
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
translate_client = translate.Client()

# ----------------------------------------------------------------------------#

# ----------------------------------------------------------------------------#
# Pubsub Topics
project_id = config["global"]["project_id"]
website_topic_id = config["website_search"]["website_topic_id"]
website_topic_path = publisher.topic_path(project_id, website_topic_id)
recommendations_topic_id = config["recommendations"][
    "recommendations_topic_id"
]
recommendations_topic_path = publisher.topic_path(
    project_id, recommendations_topic_id
)
# ----------------------------------------------------------------------------#

router = APIRouter(prefix="/p1", tags=["P1 - Customer"])


# ----------------------------------GET---------------------------------------#
@router.get(
    path="/get-product/{product_id}", response_model=GetProductResponse
)
def get_product(product_id: int) -> dict:
    """
    # Get Product

    ## Path parameters
    **product_id**: *string*
    - Product id

    ## Response body [GetProductResponse]
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

    ## Raises
    **HTTPException** - *400* - Cloud SQL Error
    - Error connecting to Cloud SQL

    **HTTPException** - *404* - Product not found
    - Product was not found in the Cloud SQL database

    """
    try:
        product = utils_cloud_sql.get_product(product_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Cloud SQL error.") from e

    if product:
        return utils_cloud_sql.convert_product_to_dict(product)
    raise HTTPException(status_code=404, detail="Product not found.")


@router.get(
    path="/get-reviews/{product_id}", response_model=GetReviewsResponse
)
def get_reviews(product_id: str) -> GetReviewsResponse:
    """
    # Get Reviews

    ## Path parameters
    **product_id**: *string*
    - Product id to get the reviews

    ## Response body [GetReviewsResponse]
    **reviews**: *list[ReviewDoc]*
    - List of reviews for the product

    ## ReviewDoc
    **review**: *string*
    - Product review

    **sentiment**: *string*
    - Review sentiment

    **stars**: *int*
    - Review stars for the product

    ## Raises
    **HTTPException** - *400* - Error getting from Firestore
    - Firestore could not return the reviews

    """
    try:
        reviews: list[GetReviewsResponse.ReviewDoc] = [
            review_snapshot.to_dict()
            for review_snapshot in db.collection("website_reviews")
            .document(product_id)
            .collection("reviews")
            .get()
        ]
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error getting from Firestore" + str(e)
        ) from e

    return GetReviewsResponse(reviews=reviews)


@router.get(
    path="/get-reviews-summary/{product_id}",
    response_model=GetReviewsSummaryResponse,
)
def get_reviews_summary(product_id: int) -> GetReviewsSummaryResponse:
    """
    # Get reviews summary

    ## Path parameters
    **product_id**: *string*
    - Product id to get the reviews

    ## Response body [GetReviewsSummaryResponse]
    **reviews_summary**: *string*
    - Reviews summary for the product

    ## Raises
    **HTTPException** - *400* - Cloud SQL Error
    - Error connecting to Cloud SQL

    **HTTPException** - *404* - Product not found
    - Product was not found in the Cloud SQL database

    **HTTPException** - 400 - Error getting reviews
    - Firestore could not return the reviews

    **HTTPException** - 400 - Error generating reviews summary
    - PaLM could not generate the summary

    """
    try:
        product = utils_cloud_sql.get_product(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cloud SQL error." + str(e)
        ) from e
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product_dict = utils_cloud_sql.convert_product_to_dict(product)

    try:
        reviews: list[GetReviewsResponse.ReviewDoc] = [
            review_snapshot.to_dict()
            for review_snapshot in db.collection("website_reviews")
            .document(str(product_id))
            .collection("reviews")
            .get()
        ]
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error getting reviews " + str(e)
        ) from e

    summary = "No reviews yet."
    if reviews:
        reviews_json = json.dumps(
            {
                "product": product_dict,
                "reviews": reviews,
            }
        )
        try:
            summary = utils_palm.text_generation(
                prompt=config["summary"]["prompt_reviews"].format(
                    reviews=reviews_json
                ),
                max_output_tokens=1024,
                temperature=0.2,
                top_k=40,
                top_p=0.8,
            )

        except GoogleAPICallError as e:
            raise HTTPException(
                status_code=400,
                detail="Error generating reviews summary" + str(e),
            ) from e
    return GetReviewsSummaryResponse(reviews_summary=summary)


@router.get(
    path="/get-product-summary/{product_id}",
    response_model=GetProductSummaryResponse,
)
def get_product_summary(product_id: int) -> GetProductSummaryResponse:
    """
    # Get Product Summary

    ## Path parameters
    **product_id**: *string*
    - Product id

    ## Response body for [GetProductSummaryResponse]
    **product_summary**: *string*
    - Product summary for the product

    ## Raises
    **HTTPException** - *400* - Cloud SQL Error
    - Error connecting to Cloud SQL

    **HTTPException** - *404* - Product not found
    - Product was not found in the Cloud SQL database

    **HTTPException** - *400* - Error generating the summary
    - PaLM could not generate the summary


    """
    try:
        product = utils_cloud_sql.get_product(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cloud SQL error." + str(e)
        ) from e
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product_dict = utils_cloud_sql.convert_product_to_dict(product)

    try:
        product_json = json.dumps(product_dict)
        summary = utils_palm.text_generation(
            prompt=config["summary"]["prompt_product"].format(
                product=product_json
            ),
            max_output_tokens=1024,
            temperature=0.2,
            top_k=40,
            top_p=0.8,
        )
        return GetProductSummaryResponse(product_summary=summary)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Error generating the summary " + str(e)
        ) from e


# ---------------------------------POST---------------------------------------#
@router.post(path="/collect-recommendations-events")
def collect_recommendations_events(data: CollectRecommendationsEventsRequest):
    """
    # Collect recommendations events

    ## Request body [CollectRecommendationsEventsRequest]
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

     ## Raises
    **HTTPException** - *400* - Error collecting event
    - Error collecting event to recommendations

    """
    try:
        utils_recommendations.collect_events(
            data.event_type,
            data.user_pseudo_id,
            data.documents,
            data.optional_user_event_fields,
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error collecting event. " + str(e),
        ) from e

    return "ok"


@router.post(path="/compare-products", response_class=HTMLResponse)
def compare_products(data: CompareProductsRequest) -> HTMLResponse:
    """
    # Compare Products

    ## Request body [CompareProductsRequest]
    **products**: *list[string]*
    - List of products ids

    ## Returns:
    **HTMLResponse**
    - A HTML comparison table

    ## Raises:
    **HTTPException** - *400* - Error Generating the table
    - PaLM got an error generating the table

    """
    try:
        for i in data.products:
            print("Product Description------")
            print(i)

        product_1 = json.loads(data.products[0])
        del product_1["image"]
        del product_1["quantity"]
        del product_1["id"]
        del product_1["features"]
        del product_1["categories"]

        product_2 = json.loads(data.products[1])
        del product_2["image"]
        del product_2["quantity"]
        del product_2["id"]
        del product_2["features"]
        del product_2["categories"]

        comparison = utils_gemini.generate_gemini_pro_text(
            prompt=config["compare"]["prompt_compare"].format(
                product_title_1=product_1["title"],
                product_description_1=product_1["description"],
                product_title_2=product_2["title"],
                product_description_2=product_2["description"]
            ),
            temperature=0.2,
            top_k=40,
            top_p=0.8
        )
        return HTMLResponse(content=comparison)
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error generating the HTML. " + str(e)
        ) from e


@router.post(path="/initiate-vertexai-recommendations")
def initiate_vertexai_recommendations(
    data: InitiateVertexAIRecommendationsRequest,
) -> InitiateVertexAIRecommendationsResponse:
    """
    # Initiate Vertex AI Recommendations

    ## Request body [InitiateVertexAIRecommendationsRequest]
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

    ## Response body [InitiateVertexAIRecommendationsResponse]
    **recommendations_doc_id**: *string*
    - Firestore document id for recommendations

    ## Raises:
    **HTTPException** - *400* - Error creating firestore document

    **HTTPException** - *400* - Error publishing message to Pubsub
    """
    try:
        recommendations_doc = db.collection(
            "website_recommendations"
        ).document()
        recommendations_doc.set(
            {
                "event_type": data.event_type,
                "user_pseudo_id": data.user_pseudo_id,
                "documents": data.documents,
                "recommendations_type": data.recommendation_type,
                "optional_user_event_fields": data.optional_user_event_fields,
                "recommendations": [],
            }
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error creating Firestore document. " + str(e),
        ) from e

    try:
        payload = json.dumps(
            {
                "event_type": data.event_type,
                "user_pseudo_id": data.user_pseudo_id,
                "documents": data.documents,
                "recommendations_type": data.recommendation_type,
                "optional_user_event_fields": data.optional_user_event_fields,
                "recommendations_doc_id": recommendations_doc.id,
            }
        ).encode("utf-8")
        future = publisher.publish(recommendations_topic_path, payload)
        future.result()
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error publishing the message to pubsub. " + str(e),
        ) from e

    return InitiateVertexAIRecommendationsResponse(
        recommendations_doc_id=recommendations_doc.id
    )


@router.post(path="/initiate-vertexai-search")
def initiate_vertexai_search(
    data: InitiateVertexAISearchRequest,
) -> InitiateVertexAISearchResponse:
    """
    # Initiate Vertex AI Search

    ## Request body [InitiateVertexAISearchRequest]
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

    ## Response body [InitiateVertexAISearchResponse]
    **search_doc_id**: *string*
    - Firestore document id for search


    ## Raises:
    **HTTPException** - *400* - Provide a text and/or an image to search

    **HTTPException** - *400* - Error creating firestore document

    **HTTPException** - *400* - Error publishing message to Pubsub


    """
    if not data.image and not data.query:
        raise HTTPException(
            status_code=400, detail="Provide a text and/or an image to search."
        )
    user_query = ""
    if data.query and data.image:
        user_query = (
            f"Show items similar to this image and description. "
            f"Description: {data.query}"
        )
    elif not data.query and data.image:
        user_query = "Show items similar to this image."
    elif data.query and not data.image:
        user_query = data.query

    try:
        search_doc = db.collection("website_search").document(
            data.search_doc_id or None
        )

        if not data.search_doc_id:
            search_doc.set(
                {
                    "conversation": [],
                    "visitor_id": data.visitor_id,
                    "user_id": data.user_id,
                }
            )
        user_id = data.user_id or (search_doc.get().to_dict() or {}).get(
            "user_id", ""
        )

        search_doc.update(
            {
                "conversation": firestore.ArrayUnion(
                    [{"author": "user", "message": user_query}]
                ),
                "user_id": user_id,
            }
        )
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error creating Firestore document. " + str(e),
        ) from e

    try:
        payload = json.dumps(
            {
                "query": data.query,
                "visitor_id": data.visitor_id,
                "search_doc_id": search_doc.id,
                "image": data.image,
            }
        ).encode("utf-8")
        future = publisher.publish(website_topic_path, payload)
        future.result()
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400,
            detail="Error publishing the message to pubsub. " + str(e),
        ) from e

    return InitiateVertexAISearchResponse(document_id=search_doc.id)


@router.post(path="/salesforce-email-support")
def salesforce_email_support(
    data: SalesforceEmailSupportRequest,
) -> SalesforceEmailSupportResponse:
    """
    # Salesforce email support

    ## Request body [SalesforceEmailSupportRequest]
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

    ## Response body for [SalesforceEmailSupportResponse]
    **email_response**: *string*
    - Email response

    **is_human_talking**: *bool*
    - Whether a human should answer instead of the AI model

    **docs_id**: *string*
    - Google Docs Id for the human response

    ## Raises:
    **HTTPException** - *400* - Error

    """
    # Retrieve or create Vertex AI Search conversation
    (
        case_dict,
        email_thread,
        conversation,
    ) = utils_salesforce.get_resources(data)
    # Remove old messages
    email_content = data.email_content.split("wrote:")[0]

    # Retrieve questions from email
    questions = utils_salesforce.get_questions_from_email(email_content)

    # Remove questions with "agent" or "human" words in it
    filtered_questions = []
    for q in questions:
        if not ("human" in q.lower() or "agent" in q.lower()):
            filtered_questions.append(q)
    questions = filtered_questions

    # Check if customer wants to talk to a human agent
    is_human_talking = data.is_human_talking
    if not is_human_talking:
        is_human_talking = utils_salesforce.is_human_needed(email_content)

    results_multimodal = []
    results = []

    # Check if there are attachments and get attachmentId
    attachments = utils_workspace.get_attachment_ids(email_thread)
    # If there are attachments
    if attachments:
        results_multimodal.append(
            utils_salesforce.salesforce_multimodal(
                attachments=attachments,
                internal_message_id=case_dict["internal_message_id"],
                conversation=conversation,
                questions=questions,
            )
        )
    else:
        results = utils_salesforce.results_from_questions(
            questions=questions, conversation_id=conversation.name
        )

    email_response = utils_workspace.create_salesforce_email_body(
        results=results,
        results_multimodal=results_multimodal,
        user_name=data.user_name,
        is_human_talking=is_human_talking,
    )

    # Translate email
    email_response = utils_salesforce.translate_email(
        email_content, email_response
    )

    # Create and send the email
    case_dict["docs_id"] = utils_workspace.send_salesforce_email_with_reply(
        email_response=email_response,
        request=data,
        case_dict=case_dict,
        is_human_talking=is_human_talking,
    )
    utils_salesforce.set_docs_id(data.case_number, case_dict["docs_id"])

    return SalesforceEmailSupportResponse(
        email_response=email_response,
        is_human_talking=is_human_talking,
        docs_id=case_dict["docs_id"],
    )


@router.post(path="/send-email-from-docs")
def send_email_from_docs(data: SendEmailFromDocsRequest) -> str:
    """
    # Send email from Google Docs

    ## Request body [SendEmailFromDocsRequest]
    ** docs_id**: *string*
    - Google Docs Id to get the email from

    ## Raises:
    **HTTPException** - *404* - Case document not found

    ## Returns:
    - ok

    """
    case_number, email_response = utils_workspace.get_email_from_docs(
        data.docs_id
    )
    document = db.collection("salesforce_cases").document(case_number)
    document_snapshot = document.get()
    document_dict = document_snapshot.to_dict()

    if document_snapshot.exists and document_dict:
        utils_workspace.send_human_email(
            email_response=email_response,
            user_email_address=document_dict.get("user_email_address", ""),
            subject=document_dict.get("subject", ""),
            email_thread_id=document_dict.get("email_thread_id", ""),
            email_message_id=document_dict.get("email_message_id", ""),
            salesforce_thread_id=document_dict.get("salesforce_thread_id", ""),
            internal_thread_id=document_dict.get("internal_thread_id", ""),
        )
        return "ok"
    raise HTTPException(status_code=404, detail="Case document not found.")


@router.post(path="/translate-text")
def translate_text(data: TranslateTextRequest) -> TranslateTextResponse:
    """
    # Translate text

    ## Request body [TranslateTextRequest]
    **text**: *list[string]*
    - List of strings representing the text to translate

    **target_language**: *string*
    - Target language

    **source_language**: *string*
    - Source language

    ## Response body [TranslateTextResponse]
    **translation**: *list[string]*
    - List of strings representing the translated text

    ## Raises:
    **HTTPException** - *400* - Error

    """
    try:
        results = []
        i = 0
        while i * 128 < len(data.text):
            result = translate_client.translate(
                data.text[i * 128 : i * 128 + 128],
                target_language=data.target_language,
                source_language=data.source_language,
            )
            results.extend(result)
            i += 1
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Something went wrong. Please try again. " + str(e),
        ) from e

    return TranslateTextResponse(translation=results)


@router.post(path="/trigger-unstructured-recommendations")
def trigger_unstructured_recommendations(
    data: TriggerUnstructuredRecommendationsRequest,
) -> str:
    """
    # Trigger Unstructured Recommendations (PubSub)

    ## Request body [TriggerUnstructuredRecommendationsRequest]
    **message**: *dict*
    - Pubsub message representing the recommendations request

    ## Raises:
    **HTTPException** - *400* - Could not load pubsub message

    **HTTPException** - *400* - Error writing document to Firestore

    ## Returns:
    - ok

    """
    try:
        message = base64.b64decode(data.message["data"]).decode("utf-8")
        message_dict = json.loads(message)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Could not load pubsub message. " + str(e)
        ) from e

    if (
        message_dict["event_type"] == "view-item"
        and not message_dict["documents"]
    ):
        return "ok"

    results = []
    if message_dict["recommendations_type"] == "new-and-featured":
        results = utils_cloud_sql.get_random_products(size=10)
    else:
        try:
            documents = utils_recommendations.get_recommendations(
                recommendations_type=message_dict["recommendations_type"],
                event_type=message_dict["event_type"],
                user_pseudo_id=message_dict["user_pseudo_id"],
                documents=message_dict["documents"],
                optional_user_event_fields=message_dict[
                    "optional_user_event_fields"
                ],
            )
            documents_dict = Message.to_dict(documents).get("results")

            if not documents_dict:
                raise FileNotFoundError("No documents returned")
        except (FileNotFoundError, GoogleAPICallError) as e:
            print(e)
            results = utils_cloud_sql.get_random_products(size=10)
        else:
            results = utils_cloud_sql.get_products(
                [doc["id"] for doc in documents_dict]
            )

    try:
        db.collection("website_recommendations").document(
            message_dict["recommendations_doc_id"]
        ).set({"recommendations": results}, merge=True)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error writing document to Firestore. " + str(e),
        ) from e

    return "ok"


@router.post(path="/trigger-unstructured-search")
def trigger_unstructured_search(
    data: TriggerUnstructuredSearchRequest,
) -> str:
    """

    ### Request body [TriggerUnstructuredSearchRequest]
    **message**: *dict*
    - Pubsub message representing the search request

    ## Raises:
    **HTTPException** - *400* - Could not load pubsub message

    **HTTPException** - *400* - Error writing document to Firestore

    ## Returns:
    - ok

    """
    try:
        message = base64.b64decode(data.message["data"]).decode("utf-8")
        message_dict = json.loads(message)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Could not load pubsub message. " + str(e)
        ) from e

    search_doc = db.collection("website_search").document(
        message_dict["search_doc_id"]
    )
    search_doc_dict = search_doc.get().to_dict() or {}
    conversation_id = search_doc_dict.get("conversation_id", "")
    if not conversation_id:
        conversation_id = utils_search.create_new_conversation(
            datastore_id=config["website_search"]["website_datastore_id"],
            user_pseudo_id=message_dict["visitor_id"],
        ).name
        search_doc.update({"conversation_id": conversation_id})
        search_doc_dict = search_doc.get().to_dict() or {}

    conversation_history = utils_search.generate_conversation_history(
        message_dict, search_doc_dict
    )

    try:
        firestore_payload = {
            "conversation": conversation_history,
        }

        search_doc.set(firestore_payload, merge=True)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error writing document to Firestore. " + str(e),
        ) from e

    return "ok"

# ---------------------------------POST---------------------------------------#
@router.post(path="/add-order")
def add_order(order: OrderRequest) -> str:
    """
    # Add user order

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
    **HTTPException** - *400* - Error setting in Firestore
    - Firestore could not set the order

    """
    try:
        db.collection("orders").document().set(order.model_dump())
    except GoogleAPICallError as e:
        raise HTTPException(
            status_code=400, detail="Error setting in Firestore" + str(e)
        ) from e

    return "ok"

@router.post(path="/trigger-recommendation-email")
def trigger_recommendation_email(
    data: TriggerRecommendationEmailRequest,
) -> str:
    """
    # Trigger Recommendation Email (PubSub)

    ## Request body [TriggerRecommendationEmailRequest]
    **message**: *dict*
    - Pubsub message representing the recommendations request

    ## Raises:
    **HTTPException** - *400* - Could not load pubsub message

    **HTTPException** - *400* - Error writing document to Firestore

    ## Returns:
    - ok

    """
    try:
        message = base64.b64decode(data.message["data"]).decode("utf-8")
        message_dict = json.loads(message)
        print(message_dict)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Could not load pubsub message. " + str(e)
        ) from e

    if (
        message_dict["event_type"] == "view-item"
        and not message_dict["documents"]
    ):
        return "ok"

    results = []
    if 1 == 1:
        print("if 1=1")
    else:
        try:
            documents = utils_recommendations.get_recommendations(
                recommendations_type="others-you-may-like",
                event_type='purchase',
                user_pseudo_id=message_dict["user_id"],
                documents=message_dict["documents"],
                optional_user_event_fields=message_dict[
                    "optional_user_event_fields"
                ],
            )
            documents_dict = Message.to_dict(documents).get("results")

            if not documents_dict:
                raise FileNotFoundError("No documents returned")
        except (FileNotFoundError, GoogleAPICallError) as e:
            print(e)
            results = utils_cloud_sql.get_random_products(size=3)
        else:
            results = utils_cloud_sql.get_products(
                [doc["id"] for doc in documents_dict]
            )

    try:
        utils_workspace.send_email_single_thread("body email",message_dict['email'],"Thank you for ordering from Cymbal!")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Error writing document to Firestore. " + str(e),
        ) from e

    return "ok"