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

""" Create Vector Search Index """

import argparse

from google.cloud import aiplatform_v1beta1 as aiplatform
from google.protobuf import struct_pb2
from google.protobuf.json_format import ParseDict

# pylint: disable-next = line-too-long
METADATA_SCHEMA_URI = "gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml"
INDEX_UPDATE_METHOD = aiplatform.Index.IndexUpdateMethod(2)


def create_vector_index(
    project_id: str,
    location: str,
    display_name: str,
    description: str,
    metadata: struct_pb2.Value,
):
    """
    Create vector index

    Args:
        project_id:
            Project id
        location:
            Index location
        display_name:
            Display name
        description:
            Index description
        metadata:
            Index Metadata

    Returns:
        Creation response

    """
    index_client = aiplatform.IndexServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )
    index = aiplatform.Index()
    index.display_name = display_name
    index.description = description
    index.metadata_schema_uri = METADATA_SCHEMA_URI
    index.metadata = metadata
    index.index_update_method = INDEX_UPDATE_METHOD

    request = aiplatform.CreateIndexRequest(
        parent=f"projects/{project_id}/locations/{location}", index=index
    )

    operation = index_client.create_index(request=request)
    response = operation.result(timeout=None)

    return response


def create_index_endpoint(
    project_id: str,
    location: str,
    display_name: str,
    description: str,
    public_endpoint_enabled: bool,
):
    """
    Create index endpoint

    Args:
        project_id:
            Project id
        location:
            Index endpoint location
        display_name:
            Index endpoint display name
        description:
            Index endpoint description
        public_endpoint_enabled:
            Whether to enable public endpoint

    Returns:
        Creation response

    """
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
        index_endpoint=index_endpoint,
    )

    operation = index_endpoint_client.create_index_endpoint(request=request)
    response = operation.result(timeout=None)

    return response


def deploy_index_to_endpoint(
    deploy_id: str,
    index: str,
    display_name: str,
    index_endpoint: str,
):
    """
    Deploy index to endpoint

    Args:
        deploy_id:
            Deploy id
        index:
            Index
        display_name:
            Display name
        index_endpoint:
            Index endpoint

    Returns:
        Deployment response

    """
    index_endpoint_client = aiplatform.IndexEndpointServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )

    deploy = aiplatform.DeployedIndex()
    deploy.id = deploy_id
    deploy.index = index
    deploy.display_name = display_name

    request = aiplatform.DeployIndexRequest(
        index_endpoint=index_endpoint, deployed_index=deploy
    )

    operation = index_endpoint_client.deploy_index(request=request)
    response = operation.result(timeout=None)

    return response


def get_index_resource_name(
    project_id: str, location: str, index_display_name: str
) -> str:
    """
    Get index resource name

    Args:
        project_id:
            Project id
        location:
            Index location
        index_display_name:
            Index display name

    Returns:
        Resource name

    """
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
    project_id: str, location: str, endpoint_display_name: str
) -> tuple:
    """
    Get endpoint info

    Args:
        project_id:
            Project id
        location:
            Endpoint location
        endpoint_display_name:
            Endpoint display name

    Returns:
        Tuple with Endpoint name, Deployed index id and Public Endpoint domain name

    """
    client = aiplatform.IndexEndpointServiceClient(
        client_options={
            "api_endpoint": "us-central1-aiplatform.googleapis.com"
        }
    )

    request = aiplatform.ListIndexEndpointsRequest(
        parent=f"projects/{project_id}/locations/{location}",
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


def main(args):
    """
    Main creation function

    Args:
        args:
            Command line args
    """
    metadata = {
        "contentsDeltaUri": args.contents_delta_uri,
        "config": {
            "dimensions": 1408,
            "approximateNeighborsCount": 150,
            "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
            "featureNormType": "UNIT_L2_NORM",
            "algorithmConfig": {
                "treeAhConfig": {
                    "leafNodeEmbeddingCount": 1000,
                    "fractionLeafNodesToSearch": 0.05,
                }
            },
        },
    }

    struct = struct_pb2.Struct()
    ParseDict(metadata, struct)
    schema_value = struct_pb2.Value(struct_value=struct)

    create_vector_index(
        project_id=args.project_id,
        location=args.location,
        display_name=args.index_display_name,
        description=args.index_description,
        metadata=schema_value,
    )

    create_index_endpoint(
        project_id=args.project_id,
        location=args.location,
        display_name=args.endpoint_display_name,
        description=args.endpoint_description,
        public_endpoint_enabled=True,
    )

    index_resource_name = get_index_resource_name(
        project_id=args.project_id,
        location=args.location,
        index_display_name=args.index_display_name,
    )

    (
        endpoint_name,
        deployed_index_id,
        public_endpoint_domain_name,
    ) = get_endpoint_info(
        project_id=args.project_id,
        location=args.location,
        endpoint_display_name=args.endpoint_display_name,
    )

    deploy_index_to_endpoint(
        deploy_id=args.deploy_id,
        index=index_resource_name,
        display_name=args.deploy_display_name,
        index_endpoint=endpoint_name,
    )
    print("Index endpoint id:")
    print(endpoint_name.split(sep="/")[-1])

    print("Deployed index id:")
    print(deployed_index_id)

    print("Vector API endpoint")
    print(public_endpoint_domain_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("location")

    parser.add_argument(
        "index_display_name",
        default="csm-multimodal-vector-search",
        required=False,
    )
    parser.add_argument(
        "index_description",
        default="CSM Multimodal Vector Search",
        required=False,
    )

    parser.add_argument(
        "endpoint_display_name", default="csm-index-endpoint", required=False
    )
    parser.add_argument(
        "endpoint_description", default="CSM Index Endpoint", required=False
    )

    parser.add_argument(
        "deploy_display_name", default="csm_deployed_index", required=False
    )
    parser.add_argument(
        "deploy_id", default="csm_deployed_index", required=False
    )
    parser.add_argument(
        "contents_delta_uri",
        default="gs://csm-solution-dataset/metadata/vertex-vector-search",
        required=False,
    )

    parsed_args = parser.parse_args()

    main(parsed_args)
