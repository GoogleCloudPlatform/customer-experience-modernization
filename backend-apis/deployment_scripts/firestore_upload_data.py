# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Upload dataset to Firestore"""

import asyncio
import json
from typing import Literal, TypedDict

from google.cloud import firestore, storage

firestore_client = firestore.AsyncClient()
gcs_client = storage.Client()

GCS_BUCKET = "csm-solution-dataset"
COLLECTIONS_DICT = {
    "website_reviews": "persona5/product_reviews.jsonl",
    "p5-customers": "persona5/customer_list.json",
    "p5-conversations": "persona5/conversations_search_dataset.jsonl",
    "p5-reviews": "persona5/reviews_search_dataset.jsonl",
}


class ReviewDoc(TypedDict):
    """A dict representing a review document for Firestore"""

    review: str
    sentiment: Literal["positive", "negative", "neutral"]
    stars: int


async def review_upload(product_id: str, review: ReviewDoc):
    """Uploads a single review

    Args:
        product_id:
            Product ID
        review:
            Review data
    """
    await firestore_client.collection("website_reviews").document(
        product_id
    ).collection("reviews").document().set(review)


async def upload_reviews(review_docs: dict[str, list[ReviewDoc]]):
    """Upload reviews"""
    await asyncio.gather(
        *(
            review_upload(product_id, review)
            for product_id, reviews in review_docs.items()
            for review in reviews
        )
    )


async def p5_upload(collection_name, document_id: str, data: dict):
    """Uploads a single p5 Firestore document

    Args:
        document_id:
            Document ID
        data:
            Document data
    """

    await firestore_client.collection(collection_name).document(
        document_id
    ).set(data)


async def upload_p5_documents(collection_name, documents: dict[str, dict]):
    """Upload p5 documents"""
    await asyncio.gather(
        *(
            p5_upload(collection_name, document_id, data)
            for document_id, data in documents.items()
        )
    )


async def main():
    """
    Upload documents to firestore
    """
    bucket = gcs_client.get_bucket(GCS_BUCKET)
    collection_lines = {}

    print("Downloading documents")
    # Transform JSONL to Documents
    for collection_name, collection_uri in COLLECTIONS_DICT.items():
        print(f"Downloading {collection_uri}")
        blob = bucket.blob(collection_uri)
        lines = blob.download_as_text().splitlines()
        json_lines = [json.loads(line) for line in lines]

        # Website reviews uses collections of collections
        if collection_name == "website_reviews":
            review_docs: dict[str, list[ReviewDoc]] = {}
            for review_dict in json_lines:
                review_doc: ReviewDoc = {
                    "review": review_dict["review"],
                    "sentiment": review_dict["sentiment"],
                    "stars": review_dict["stars"],
                }
                if review_dict["id"] not in review_docs:
                    review_docs[review_dict["id"]] = []
                review_docs[review_dict["id"]].append(review_doc)
            collection_lines["website_reviews"] = review_docs
            continue

        # Other collections are flat
        docs = {}
        for line in json_lines:
            if collection_name != "p5-customers":
                data = json.loads(line["jsonData"])
            else:
                data = line

            if collection_name == "p5-customers":
                docs[line["customer_id"]] = data
            else:
                docs[line["id"]] = data
        collection_lines[collection_name] = docs

    # Upload collections
    for name, lines in collection_lines.items():
        print(f"Uploading collection: {name}")
        if name == "website_reviews":
            await upload_reviews(lines)
        else:
            await upload_p5_documents(name, lines)


if __name__ == "__main__":
    asyncio.run(main())
