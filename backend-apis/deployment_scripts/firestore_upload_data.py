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

"""Import firestore"""

import json

from google.cloud import firestore, storage

GCS_BUCKET = "csm-solution-dataset"
COLLECTIONS_DICT = {
    "p5-customers": "persona5/customer_list.json",
    "p5-conversations": "persona5/full_conversations.jsonl",
    "p5-reviews": "persona5/product_reviews.jsonl",
}
db = firestore.Client()
gcs_client = storage.Client()


def get_collection(collection_name: str):
    """
    Gets collection count

    Args:
        collection_name:
            Collection name

    Returns:
        Collection count
    """
    ref = db.collection(collection_name)
    result = ref.count().get()
    count = int(result[0][0].value)
    return count


def firestore_upload():
    """
    Upload documents to firestore
    """
    bucket = gcs_client.get_bucket(GCS_BUCKET)
    for collection_name, collection_uri in COLLECTIONS_DICT.items():
        blob = bucket.blob(collection_uri)
        lines = blob.download_as_text().splitlines()
        json_lines = [json.loads(line) for line in lines]

        for line in json_lines:
            # print(line)
            if collection_name == "p5-conversations":
                data = json.loads(line["jsonData"])
            else:
                data = line

            if collection_name == "p5-customers":
                db.collection(collection_name).document(
                    line["customer_id"]
                ).set(data)
            else:
                db.collection(collection_name).document(line["id"]).set(data)


if __name__ == "__main__":
    firestore_upload()
