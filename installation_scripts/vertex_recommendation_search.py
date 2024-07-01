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
#import utils_toml


def import_events(
    project_id: str,
    location: str,
    data_store_id: str,
    parent_collection: str,
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
    client = discoveryengine.UserEventServiceClient(client_options=client_options)

    request = discoveryengine.ImportUserEventsRequest(
        parent=f"{parent_collection}/dataStores/{data_store_id}",
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri], data_schema="user_event"
        )
    )

    operation = client.import_user_events(request=request)
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
    data_store.industry_vertical = discoveryengine.IndustryVertical.MEDIA
    data_store.content_config = discoveryengine.DataStore.ContentConfig.CONTENT_CONFIG_UNSPECIFIED
    data_store.solution_types = [discoveryengine.SolutionType.SOLUTION_TYPE_RECOMMENDATION]

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
        recommendatation_type: str,
        company_name: str
):
    client = discoveryengine.EngineServiceClient()
    engine = discoveryengine.Engine()
    engine.media_recommendation_engine_config = discoveryengine.Engine.MediaRecommendationEngineConfig(
        type=recommendatation_type,
        optimization_objective="ctr"
    )
    engine.display_name = engine_id
    engine.data_store_ids = [data_store_id]
    engine.solution_type = discoveryengine.SolutionType.SOLUTION_TYPE_RECOMMENDATION
    engine.industry_vertical = discoveryengine.IndustryVertical.MEDIA
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
    # parser = argparse.ArgumentParser()
    # parser.add_argument("project_id")
    # parser.add_argument("location")
    # args = parser.parse_args()

    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="Id of project to use", type=str)
    parser.add_argument("--location", help="Location to deploy",type=str, default="global")
    parser.add_argument("--recommendatation_type", help="Id of project to use", type=str)
    parser.add_argument("--data_store_id", help="Id of project to use", type=str)
    parser.add_argument("--engine_id", help="Id of project to use", type=str)

    dict_args = parser.parse_args()

    print(f"Using arguments: {dict_args}")

    project_id = dict_args.project_id
    location = dict_args.location
    recommendatation_type = dict_args.recommendatation_type
    data_store_id = dict_args.data_store_id
    engine_id = dict_args.engine_id

    # default_collection
    # data_store_id = "csm-media-rec-datastore"
    # engine_id = "csm-media-more-like-this"

    gcs_uri = "gs://csm_automation/full_media_events.jsonl"

    collection = "default_collection"
    default_schema_id = "default_schema"
    company_name = "CSM"
    datastore_client = discoveryengine.DataStoreServiceClient()
    engine_client = discoveryengine.EngineServiceClient()
    parent_collection = f"projects/{project_id}/locations/{location}/collections/default_collection"
    print("parent_collection: ",parent_collection)
    
    try:
        datastore = datastore_client.get_data_store(request=discoveryengine.GetDataStoreRequest(
            name=f"{parent_collection}/dataStores/{data_store_id}",
        ))
        print(f"Datastore already exist: {datastore}")
    except:
        print("Creating Datastore")
        create_datastore(
            project_id=project_id,
            location=location,
            collection=collection,
            data_store_id=data_store_id)
        
               
        import_events(
            project_id=project_id,
            location=location,
            data_store_id=data_store_id,
            parent_collection=parent_collection,
            gcs_uri=gcs_uri
        )
    try:
        engine = engine_client.get_engine(request=discoveryengine.GetEngineRequest(
            name=f"{parent_collection}/engines/{engine_id}"
        ))
        print(f"Engine already exist: {engine}")
    except:
        print("Creating App")
        create_engine(
                project_id=project_id,
                location=location,
                collection=collection,
                engine_id=engine_id,
                data_store_id=data_store_id,
                recommendatation_type=recommendatation_type,
                company_name=company_name)


    