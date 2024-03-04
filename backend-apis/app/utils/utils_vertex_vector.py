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
Utility module for Vertex AI Vector Search
"""

import tomllib

from google.cloud import aiplatform_v1

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

project_id = config["global"]["project_id"]
project_number = config["global"]["project_number"]

p1_index_endpoint_id = config["multimodal"]["index_endpoint_id"]
p1_deployed_index_id = config["multimodal"]["deployed_index_id"]

p5_conversations_index_endpoint_id = config["search-persona5"][
    "conversations_index_endpoint_id"
]
p5_conversations_deployed_index_id = config["search-persona5"][
    "conversations_deployed_index_id"
]

p5_reviews_index_endpoint_id = config["search-persona5"][
    "reviews_index_endpoint_id"
]
p5_reviews_deployed_index_id = config["search-persona5"][
    "reviews_deployed_index_id"
]

p1_match_client = aiplatform_v1.MatchServiceClient(
    client_options={
        "api_endpoint": config["multimodal"]["vector_api_endpoint"]
    }
)
p5_conversations_match_client = aiplatform_v1.MatchServiceClient(
    client_options={
        "api_endpoint": config["search-persona5"][
            "conversations_vector_api_endpoint"
        ]
    }
)
p5_reviews_match_client = aiplatform_v1.MatchServiceClient(
    client_options={
        "api_endpoint": config["search-persona5"][
            "reviews_vector_api_endpoint"
        ]
    }
)


def find_neighbor(
    feature_vector: list,
    datapoint_id: str = "0",
    neighbor_count: int = 10,
    persona: int = 1,
    user_journey: str = "conversations",
) -> aiplatform_v1.FindNeighborsResponse:
    """

    Args:
        feature_vector:
        datapoint_id:
        neighbor_count:
        return_full_datapoint:
        persona:
        user_journey:

    Returns:

    """
    if persona == 1:
        index_endpoint_id = p1_index_endpoint_id
        deployed_index_id = p1_deployed_index_id
        match_client = p1_match_client
    else:
        if user_journey == "conversations":
            index_endpoint_id = p5_conversations_index_endpoint_id
            deployed_index_id = p5_conversations_deployed_index_id
            match_client = p5_conversations_match_client
        else:
            index_endpoint_id = p5_reviews_index_endpoint_id
            deployed_index_id = p5_reviews_deployed_index_id
            match_client = p5_reviews_match_client

    query = aiplatform_v1.FindNeighborsRequest.Query(
        datapoint=aiplatform_v1.IndexDatapoint(
            datapoint_id=datapoint_id, feature_vector=feature_vector
        ),
        neighbor_count=neighbor_count,
    )

    request = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=f"projects/{project_number}/locations/us-central1/"
        f"indexEndpoints/{index_endpoint_id}",
        deployed_index_id=deployed_index_id,
        return_full_datapoint=False,
        queries=[query],
    )

    return match_client.find_neighbors(request)
