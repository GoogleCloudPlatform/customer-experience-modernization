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
""" Vertex Search datastores creation """

import argparse
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1alpha as discoveryengine


def import_documents(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: Optional[str] = None,
) -> str:
    """
    Import documents to the datastore

    Args:
        project_id:
            Id of the Google Cloud project
        location:
            Datastore location
        data_store_id:
            Datastore id
        gcs_uri:
            Google Cloud Storage URI

    Returns:
        Google Cloud API Operation name

    """
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(
            api_endpoint=f"{location}-discoveryengine.googleapis.com"
        )
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.DocumentServiceClient(
        client_options=client_options
    )

    # The full resource name of the search engine branch.
    # e.g. projects/{project}/locations/{location}/dataStores/{data_store_id}/branches/{branch}
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri], data_schema="document"
        ),
    )

    operation = client.import_documents(request=request)
    return operation.operation.name


def create_datastore(
    project_id: str,
    location: str,
    data_store_id: str,
):
    """
    Create a datastore

    Args:
        project_id:
            Id of the Google Cloud project
        location:
            Datastore location
        data_store_id:
            Datastore id
    """
    client = discoveryengine.DataStoreServiceClient()

    # Initialize request argument(s)
    data_store = discoveryengine.DataStore()
    data_store.display_name = data_store_id
    data_store.industry_vertical = discoveryengine.IndustryVertical.GENERIC
    data_store.content_config = (
        discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
    )
    data_store.solution_types = [
        discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH
    ]

    collection = client.collection_path(
        project=project_id, location=location, collection="default_collection"
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=collection, data_store=data_store, data_store_id=data_store_id
    )

    # Make the request
    operation = client.create_data_store(request=request)
    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)


def create_engine(
    project_id: str,
    location: str,
    engine_id: str,
    data_store_id: str,
    company_name: str,
):
    """
    Create a search engine

    Args:
        project_id:
            Id of the Google Cloud project
        engine_id:
            Id of the search engine
        data_store_id:
            Id of the datastore
        company_name:
            Company name
    """
    client = discoveryengine.EngineServiceClient()
    engine = discoveryengine.Engine()
    engine.search_engine_config = discoveryengine.Engine.SearchEngineConfig(
        search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
        search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
    )
    engine.display_name = engine_id
    engine.data_store_ids = [data_store_id]
    engine.solution_type = discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH
    engine.industry_vertical = discoveryengine.IndustryVertical.GENERIC
    engine.common_config = discoveryengine.Engine.CommonConfig(
        company_name=company_name
    )

    collection = client.collection_path(
        project=project_id, location=location, collection="default_collection"
    )

    request = discoveryengine.CreateEngineRequest(
        parent=collection, engine=engine, engine_id=engine_id
    )

    operation = client.create_engine(request=request)
    response = operation.result()
    print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Vertex AI search datastores creation"
    )
    parser.add_argument("project_id", required=True)
    parser.add_argument("location", required=True)
    parser.add_argument(
        "data_store_id", default="csm-search-datastore", required=False
    )
    parser.add_argument(
        "engine_id", default="csm-search-engine", required=False
    )
    parser.add_argument(
        "gcs_uri",
        default="gs://csm-solution-dataset/metadata/search_products.jsonl",
        required=False,
    )
    parser.add_argument(
        "engine_id", default="csm-search-engine", required=False
    )
    parser.add_argument("company_name", default="CSM", required=False)
    args = parser.parse_args()

    print("Creating Datastore")
    create_datastore(
        project_id=args.project_id,
        location=args.location,
        data_store_id=args.data_store_id,
    )

    print("Creating App")
    import_documents(
        project_id=args.project_id,
        location=args.location,
        data_store_id=args.data_store_id,
        gcs_uri=args.gcs_uri,
    )

    create_engine(
        project_id=args.project_id,
        location=args.location,
        engine_id=args.engine_id,
        data_store_id=args.data_store_id,
        company_name=args.company_name,
    )
