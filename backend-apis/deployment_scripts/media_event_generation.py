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
"""Media event generation"""

import json
import random
from datetime import datetime, timedelta, timezone


def generate_view_homepage(user_pseudo_id: str, event_time: str):
    # {
    #  "eventType": "view-home-page",
    #  "userPseudoId": "user-pseudo-id",
    #  "eventTime": "2020-01-01T03:33:33.000001Z",
    # };
    return {
        "eventType": "view-home-page",
        "userPseudoId": user_pseudo_id,
        "eventTime": event_time,
    }


def generate_view_item(user_pseudo_id: str, event_time: str, document_id: str):
    # {
    #  "eventType": "view-item",
    #  "userPseudoId": "user-pseudo-id",
    #  "eventTime": "2020-01-01T03:33:33.000001Z",
    #  "documents": [{
    #    "id": "document-id"
    #  }]
    # }
    return {
        "eventType": "view-item",
        "userPseudoId": user_pseudo_id,
        "eventTime": event_time,
        "documents": [{"id": document_id}],
    }


def generate_event_lines(today: datetime, catalog: list[dict]) -> list[str]:
    documents_len = len(catalog)
    categories_catalog = {}
    for product in catalog:
        if product["categories"] not in categories_catalog:
            categories_catalog[product["categories"]] = []
        categories_catalog[product["categories"]].append(product)
    users_len = (documents_len - 1) * 20
    json_lines = []
    for i in range(60):  # 60 days
        day = today - timedelta(days=i + 1)
        rate = 1440 / (10 * documents_len)
        for j in range(10 * documents_len):
            home_page_time = (
                (day + timedelta(minutes=int(j * rate)))
                .isoformat()
                .replace("+00:00", "Z")
            )
            view_item_time = (
                (day + timedelta(minutes=int(j * rate), seconds=30))
                .isoformat()
                .replace("+00:00", "Z")
            )

            user = random.randint(0, users_len)
            category = catalog[user // 20 - 1]["categories"]
            document = random.choice(categories_catalog[category])
            view_homepage_event = json.dumps(
                generate_view_homepage(
                    user_pseudo_id=f"user-{user}", event_time=home_page_time
                )
            )
            view_item_event = json.dumps(
                generate_view_item(
                    user_pseudo_id=f"user-{user}",
                    event_time=view_item_time,
                    document_id=str(document["id"]),
                )
            )
            json_lines.append(view_homepage_event)
            json_lines.append(view_item_event)
    return json_lines


def main():
    today_datetime = datetime.now(timezone.utc)
    today_datetime = today_datetime - timedelta(
        hours=today_datetime.hour,
        minutes=today_datetime.minute,
        seconds=today_datetime.second,
        microseconds=today_datetime.microsecond,
    )
    with open("./dataset/recommendation_products.jsonl") as f:
        lines = f.readlines()
    products_json_lines = [json.loads(line) for line in lines]

    events_json_lines = generate_event_lines(
        today_datetime, products_json_lines
    )

    with open("full_media_events.jsonl", "w", encoding="utf-8") as jsonl_file:
        jsonl_file.write("\n".join(events_json_lines))


if __name__ == "__main__":
    main()
