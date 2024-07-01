# Req
# 100 documents
# 10k view-item
# 10k view-homepage
# 100 pseudo users
# 60 event days in the last 90 days

import json
import random
from datetime import datetime, timedelta, timezone

import pandas as pd


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


today = datetime.now(timezone.utc)
today = today - timedelta(
    hours=today.hour,
    minutes=today.minute,
    seconds=today.second,
    microseconds=today.microsecond,
)
catalog = pd.read_json("dataset/recommendation_products.jsonl", lines=True)
with open("full_media_events.jsonl", "w", encoding="utf-8") as jsonl_file:
    documents_len = len(catalog.index)
    users_len = (documents_len - 1) * 20
    categories = catalog["categories"].unique()
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
            category = catalog.iloc[user // 20 - 1]["categories"]
            filtered_catalog = catalog[catalog["categories"] == category]
            document = filtered_catalog.sample(n=1)
            view_homepage_event = json.dumps(
                generate_view_homepage(
                    user_pseudo_id=f"user-{user}", event_time=home_page_time
                )
            )
            view_item_event = json.dumps(
                generate_view_item(
                    user_pseudo_id=f"user-{user}",
                    event_time=view_item_time,
                    document_id=str(document.iloc[0]["id"]),
                )
            )
            jsonl_file.write(f"{view_homepage_event}\n")
            jsonl_file.write(f"{view_item_event}\n")
