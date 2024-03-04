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
import time
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1alpha as discoveryengine
import utils_toml


def import_documents(
    project_id: str,
    location: str,
    data_store_id: str,
    gcs_uri: Optional[str] = None
) -> str:
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )

    # Create a client
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

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
        )
    )

    operation = client.import_documents(request=request)
    return operation.operation.name


def create_datastore(
        project_id: str,
        location: str,
        collection: str,
        data_store_id: str
):
    client = discoveryengine.DataStoreServiceClient()

    # Initialize request argument(s)
    data_store = discoveryengine.DataStore()
    data_store.display_name = data_store_id
    data_store.industry_vertical = discoveryengine.IndustryVertical.GENERIC
    data_store.content_config = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
    data_store.solution_types = [discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH]

    collection = client.collection_path(
        project=project_id,
        location=location,
        collection=collection
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=collection,
        data_store=data_store,
        data_store_id=data_store_id
    )

    # Make the request
    operation = client.create_data_store(request=request)
    # TODO: Change to `operation.result()` when available
    while not operation.done():
        time.sleep(secs=1)


def create_engine(
        project_id: str,
        location: str,
        collection: str,
        engine_id: str,
        data_store_id: str,
        company_name: str
):
    client = discoveryengine.EngineServiceClient()
    engine = discoveryengine.Engine()
    engine.search_engine_config = discoveryengine.Engine.SearchEngineConfig(
        search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
        search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM]
    )
    engine.display_name = engine_id
    engine.data_store_ids = [data_store_id]
    engine.solution_type = discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH
    engine.industry_vertical = discoveryengine.IndustryVertical.GENERIC
    engine.common_config = discoveryengine.Engine.CommonConfig(
        company_name=company_name
    )

    collection = client.collection_path(
        project=project_id,
        location=location,
        collection=collection
    )

    request = discoveryengine.CreateEngineRequest(
        parent=collection,
        engine=engine,
        engine_id=engine_id
    )

    operation = client.create_engine(request=request)
    response = operation.result()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("location")
    args = parser.parse_args()

    # default_collection
    data_store_id = "csm-search-datastore"
    engine_id = "csm-search-engine"

    gcs_uri = "gs://csm-solution-dataset/metadata/search_products.jsonl"

    collection = "default_collection"
    default_schema_id = "default_schema"
    company_name = "CSM"

    print("Creating Datastore")
    create_datastore(
        project_id=args.project_id,
        location=args.location,
        collection=collection,
        data_store_id=data_store_id)

    print("Creating App")
    import_documents(
        project_id=args.project_id,
        location=args.location,
        data_store_id=data_store_id,
        gcs_uri=gcs_uri
    )

    create_engine(
            project_id=args.project_id,
            location=args.location,
            collection=collection,
            engine_id=engine_id,
            data_store_id=data_store_id,
            company_name=company_name)


    