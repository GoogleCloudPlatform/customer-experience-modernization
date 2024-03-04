# Copyright 2023 Google LLC
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

import argparse
import json
import time

from google.cloud import aiplatform_v1beta1 as aiplatform
from google.protobuf import struct_pb2
from google.protobuf.json_format import ParseDict
import utils_toml


def create_vector_index(
        project_id: str,
        location: str,
        display_name: str,
        description: str,
        metadata_schema_uri: str,
        metadata: struct_pb2.Value,
        index_update_method: aiplatform.Index.IndexUpdateMethod
):
    index_client = aiplatform.IndexServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )
    index = aiplatform.Index()
    index.display_name = display_name
    index.description = description
    index.metadata_schema_uri = metadata_schema_uri
    index.metadata = metadata
    index.index_update_method = index_update_method
    
    request = aiplatform.CreateIndexRequest(
        parent=f"projects/{project_id}/locations/{location}",
        index=index
    )

    operation = index_client.create_index(request=request)
    response = operation.result(timeout=None)

    return response


def create_index_endpoint(
        project_id: str,
        location: str,
        display_name: str,
        description: str,
        public_endpoint_enabled: bool
):
    index_endpoint_client = aiplatform.IndexEndpointServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )

    index_endpoint = aiplatform.IndexEndpoint()
    index_endpoint.display_name = display_name
    index_endpoint.description = description
    index_endpoint.public_endpoint_enabled = public_endpoint_enabled

    request = aiplatform.CreateIndexEndpointRequest(
        parent=f"projects/{project_id}/locations/{location}",
        index_endpoint=index_endpoint
    )

    operation = index_endpoint_client.create_index_endpoint(
        request=request
    )
    response = operation.result(timeout=None)
    
    return response


def deploy_index_to_endpoint(
        project_id: str,
        location: str,
        id: str,
        index: str,
        display_name: str,
        index_endpoint: str
):
    index_endpoint_client = aiplatform.IndexEndpointServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )

    deploy = aiplatform.DeployedIndex()
    deploy.id = id
    deploy.index = index
    deploy.display_name = display_name

    request = aiplatform.DeployIndexRequest(
        index_endpoint = index_endpoint,
        deployed_index = deploy
    )

    operation = index_endpoint_client.deploy_index(request=request)
    response = operation.result(timeout=None)

    return response


def get_index_resource_name(
        project_id: str,
        location: str,
        index_display_name: str
) -> str:
    client = aiplatform.IndexServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )
    request = aiplatform.ListIndexesRequest(
        parent=f"projects/{project_id}/locations/{location}"
    )

    results = client.list_indexes(request=request)
    resource_name = ""
    for i in list(results):
        if i.display_name == index_display_name:
            resource_name = i.name
        break

    return resource_name


def get_endpoint_info(
        project_id: str,
        location: str,
        endpoint_display_name: str
) -> tuple:
    client = aiplatform.IndexEndpointServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )

    request = aiplatform.ListIndexEndpointsRequest(
        parent = f"projects/{project_id}/locations/{location}",
    )

    results = client.list_index_endpoints(request=request)
    endpoint_name = ""
    deployed_index_id = ""
    public_endpoint_domain_name = ""
    for i in list(results):
        if i.display_name == endpoint_display_name:
            endpoint_name = i.name
            deployed_index_id = i.deployed_indexes[0].id
            public_endpoint_domain_name = i.public_endpoint_domain_name
    
    return endpoint_name, deployed_index_id, public_endpoint_domain_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("location")
    args = parser.parse_args()

    index_display_name = "csm-multimodal-vector-search"
    index_description = "CSM Multimodal Vector Search"
    index_update_method = aiplatform.Index.IndexUpdateMethod(2)

    endpoint_display_name = "csm-index-endpoint"
    endpoint_description = "CSM Index Endpoint"

    deploy_display_name = "csm_deployed_index"
    deploy_id = "csm_deployed_index"

    
    metadata = {
        "contentsDeltaUri": "gs://csm-solution-dataset/metadata/vertex-vector-search",
        "config":{
            "dimensions": 1408,
            "approximateNeighborsCount": 150,
            "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
            "featureNormType": "UNIT_L2_NORM",
            "algorithmConfig": {
                "treeAhConfig": {
                    "leafNodeEmbeddingCount": 1000, 
                    "fractionLeafNodesToSearch": 0.05
                }
            }
        }
    }

    struct = struct_pb2.Struct()
    ParseDict(metadata, struct)
    schema_value = struct_pb2.Value(struct_value=struct)
    metadata_schema_uri = "gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml"

    create_vector_index(
        project_id=args.project_id,
        location=args.location,
        display_name=index_display_name,
        description=index_description,
        metadata_schema_uri=metadata_schema_uri,
        metadata=schema_value,
        index_update_method=index_update_method
    )

    create_index_endpoint(
        project_id=args.project_id,
        location=args.location,
        display_name=endpoint_display_name,
        description=endpoint_description,
        public_endpoint_enabled=True
    )

    index_resource_name = get_index_resource_name(
        project_id=args.project_id,
        location=args.location,
        index_display_name=index_display_name
    )

    (endpoint_name, 
     deployed_index_id, 
     public_endpoint_domain_name) = get_endpoint_info(
        project_id=args.project_id,
        location=args.location,
        endpoint_display_name=endpoint_display_name
    )

    deploy_index_to_endpoint(
        project_id=args.project_id,
        location=args.location,
        id=deploy_id,
        index=index_resource_name,
        display_name=deploy_display_name,
        index_endpoint=endpoint_name
    )

    utils_toml.update_toml(
        toml_path="config.toml",
        new_values={
            "$$index_endpoint_id$$": f'"{endpoint_name.split(sep="/")[-1]}"',
            "$$deployed_index_id$$": f'"{deployed_index_id}"',
            "$$vector_api_endpoint$$": f'"{public_endpoint_domain_name}"'
        })

