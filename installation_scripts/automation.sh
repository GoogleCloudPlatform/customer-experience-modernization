#!/bin/bash

#PROJECT_ID="vpc-host-dev-th021-md234"
LOCATION="global"
#USER_EMAIL="example@example.com"
SERVICE_ACCOUNT="csm-sa" 
GDRIVE_FOLDER_NAME="csm-assets" 

read -p "Enter Project ID: " PROJECT_ID
read -p "Enter your email id: " USER_EMAIL

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"   # Do not modify this
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID  --format="value(projectNumber)")
echo "* Project Number=${PROJECT_NUMBER}"

gcloud config set project $PROJECT_ID 

if [ -e api_credentials.json ]; then
    echo "creating user credentials..."
    python3 create_user_credentails.py --file_name="api_credentials.json"
else
    echo "required api_credentials.json file is not found, so Please add the file with credentials"
    exit
fi

bucket_check=`gcloud storage ls | grep -w "gs://csm_automation_${PROJECT_ID}/"`

if [[ $bucket_check > 0 ]]; then
    echo "required gcs bucket exist"
else
    gcloud storage buckets create gs://csm_automation_${PROJECT_ID} --location=us-central1
fi

### Persona 1

rm -rf customer-services-modernization
mkdir -p customer-services-modernization
cp -r ../backend-apis ./customer-services-modernization
cp -r ../frontend ./customer-services-modernization

# if [ ! -d "csm_automation_venv" ]; then   # Checking the Virtualenv folder exists or not
#    python3 -m venv csm_automation_venv    # Creating virtualenv  
# fi

# source csm_automation_venv/bin/activate   # activate Virtualenv

# pip install -U google-cloud-datacatalog google-cloud-storage google-cloud-bigquery numpy google-api-python-client google.cloud google.auth google-cloud-discoveryengine google-cloud-dialogflow-cx pandas google-cloud-firestore google-cloud-pubsub google-cloud-aiplatform google_auth_oauthlib

PROJECT_NUMBER=`gcloud projects describe $PROJECT_ID --format="value(projectNumber)"` 

sed -i "s|project_id = \"\"|project_id = '${PROJECT_ID}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|images_bucket_name = \"\"|images_bucket_name = '${PROJECT_ID}.appspot.com'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|project_number = \"\"|project_number = '${PROJECT_NUMBER}'|" customer-services-modernization/backend-apis/app/config.toml


python3 vertex_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --data_store_id="csm-search-datastore" --engine_id="csm-search-engine" --gcs_uri="gs://csm-solution-dataset/metadata/search_products.jsonl"

python3 media_event_generation.py

python3 vertex_recommendation_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --recommendatation_type="more-like-this" --data_store_id="csm-media-rec-datastore" --engine_id="csm-media-more-like-this"

python3 vertex_recommendation_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --recommendatation_type="most-popular-items" --data_store_id="csm-media-rec-datastore" --engine_id="csm-media-most-popular"

python3 vertex_recommendation_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --recommendatation_type="others-you-may-like" --data_store_id="csm-media-rec-datastore" --engine_id="csm-media-others-you-maylike"

python3 vertex_recommendation_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --recommendatation_type="recommended-for-you" --data_store_id="csm-media-rec-datastore" --engine_id="csm-media-rec-for-you"


### persona 5

#### Vertex AI search
python3 vertex_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --data_store_id="p5-conversations-search-datastore" --engine_id="p5-conversations-search" --gcs_uri="gs://csm-solution-dataset/persona5/conversations_search_dataset.jsonl"

python3 vertex_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --data_store_id="p5-reviews-search-datastore" --engine_id="p5-reviews-search" --gcs_uri="gs://csm-solution-dataset/persona5/reviews_search_dataset.jsonl"

#### Vertex AI Conversation
# python3 vertex_conversation.py --project="${PROJECT_ID}" --location="${LOCATION}" --app-name="p6-manuals-infobot" --company-name="CSM" --uris="" --datastore-storage-folder="gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl"
python3 vertex_df_agent.py --project_number="${PROJECT_NUMBER}" --project="${PROJECT_ID}" --location="${LOCATION}" --app-name="p6-manuals-infobot" --company-name="CSM" --uris="" --datastore-storage-folder="gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl"
# python3 vertex_df_agent.py --project_number=658069682209 --project=kalschi-csm-5 --location=global --app-name="p6-manuals-infobot" --company-name="CSM" --uris="" --datastore-storage-folder="gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl"

### persona 6

python3 vertex_search.py --project_id="${PROJECT_ID}" --location="${LOCATION}" --data_store_id="p6-search-manuals-datastore" --engine_id="p6-search-manuals" --gcs_uri="gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl"

###### Firestore ####
gcloud alpha firestore databases update --type=firestore-native --project=${PROJECT_ID}

python3 firestore_upload_data.py

#### Cloud SQL 
cd terraform/cloudSql && terraform init && terraform apply --var "project_id=${PROJECT_ID}" --var "region=us-central1" --var "service_account_email=${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" --var "sql_instance_name=csm-instance" --var "gcs_bucket=csm_automation" --auto-approve
cd ../../
gcloud sql import sql csm-instance gs://csm-solution-dataset/persona1/Cloud_SQL_Export.sql --project=${PROJECT_ID} --quiet

### Vector store setup
python3 vertex_vector_store.py  --project_id="${PROJECT_ID}" --location="us-central1" --index_display_name="p5-conversations-index" --endpoint_display_name="p5-conversations-index-endpoint" --deploy_display_name="p5_conversations_index" --gcs_url="gs://csm-solution-dataset/persona5/conversations-embeddings/vertexai_conversations_embeddings.json"

python3 vertex_vector_store.py  --project_id="${PROJECT_ID}" --location="us-central1" --index_display_name="p5-reviews-index" --endpoint_display_name="p5-reviews-index-endpoint" --deploy_display_name="p5_reviews_index" --gcs_url="gs://csm-solution-dataset/persona5/reviews-embeddings/vertexai_reviews_embeddings.json"

python3 vertex_vector_store.py  --project_id="${PROJECT_ID}" --location="us-central1" --index_display_name="csm-multimodal-vector-search-index" --endpoint_display_name="csm-multimodal-vector-search-index-endpoint" --deploy_display_name="csm_multimodal_vector_search" --gcs_url="gs://csm-solution-dataset/persona1/vector_search_website/vector_website_products.jsonl"

### creating pubsub topics

python3 create_pubsub_topics.py --project_id="${PROJECT_ID}" --topic_id="website-recommendations"

python3 create_pubsub_topics.py --project_id="${PROJECT_ID}" --topic_id="website-search"


sed -i "s|website_datastore_id = \"\"|website_datastore_id = 'csm-search-datastore'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|website_topic_id = \"website-search\"|website_topic_id = 'website-search'|" customer-services-modernization/backend-apis/app/config.toml

## [workspace]
sed -i "s|calendar_id = \"\"|calendar_id = '${SERVICE_ACCOUNT_EMAIL}'|" customer-services-modernization/backend-apis/app/config.toml


## [search-persona5]

sed -i "s|conversations_datastore_id = \"\"|conversations_datastore_id = \"p5-conversations-search-datastore\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|reviews_datastore_id = \"\"|reviews_datastore_id = \"p5-reviews-search-datastore\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|product_manuals_datastore_id = \"\"|product_manuals_datastore_id = \"p6-search-manuals-datastore\"|" customer-services-modernization/backend-apis/app/config.toml

csm_multimodal_vector_search_index_endpoint=`jq -r '.csm_multimodal_vector_search_index_endpoint' < marketingEnvValue.json`
csm_multimodal_vector_search_index_id=`jq -r '.csm_multimodal_vector_search_index_id' < marketingEnvValue.json`

p5_conversations_index_endpoint=`jq -r '.p5_conversations_index_endpoint' < marketingEnvValue.json`
p5_conversations_index_id=`jq -r '.p5_conversations_index_id' < marketingEnvValue.json`

p5_reviews_index_endpoint=`jq -r '.p5_reviews_index_endpoint' < marketingEnvValue.json`
p5_reviews_index_id=`jq -r '.p5_reviews_index_id' < marketingEnvValue.json`

sed -i "s|conversations_vector_api_endpoint = \"\"|conversations_vector_api_endpoint = '${p5_conversations_index_endpoint}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|conversations_index_endpoint_id = \"\"|conversations_index_endpoint_id = '${p5_conversations_index_id}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|conversations_deployed_index_id = \"\"|conversations_deployed_index_id = 'p5_conversations_index'|" customer-services-modernization/backend-apis/app/config.toml

sed -i "s|reviews_vector_api_endpoint = \"\"|reviews_vector_api_endpoint = '${p5_reviews_index_endpoint}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|reviews_index_endpoint_id = \"\"|reviews_index_endpoint_id = '${p5_reviews_index_id}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|reviews_deployed_index_id = \"\"|reviews_deployed_index_id = 'p5_reviews_index'|" customer-services-modernization/backend-apis/app/config.toml

sed -i "s|p4_support_datastore_id = \"\"|p4_support_datastore_id = \"p5-conversations-search-datastore\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|p4_salesforce_datastore_id = \"\"|p4_salesforce_datastore_id = \"p6-search-manuals-datastore\"|" customer-services-modernization/backend-apis/app/config.toml



sed -i "s|media_rec_datastore_id = \"\"|media_rec_datastore_id = \"csm-media-rec-datastore\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|media_rec_app_id.recommended-for-you = \"\"|media_rec_app_id.recommended-for-you = \"csm-media-rec-for-you\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|media_rec_app_id.others-you-may-like = \"\"|media_rec_app_id.others-you-may-like = \"csm-media-others-you-maylike\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|media_rec_app_id.more-like-this = \"\"|media_rec_app_id.more-like-this = \"csm-media-more-like-this\"|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|media_rec_app_id.most-popular-items = \"\"|media_rec_app_id.most-popular-items = \"csm-media-most-popular\"|" customer-services-modernization/backend-apis/app/config.toml


sed -i "s|vector_api_endpoint = \"\"|vector_api_endpoint = '${csm_multimodal_vector_search_index_endpoint}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|index_endpoint_id = \"\"|index_endpoint_id = '${csm_multimodal_vector_search_index_id}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|deployed_index_id = \"\"|deployed_index_id = 'csm_multimodal_vector_search'|" customer-services-modernization/backend-apis/app/config.toml


sed -i "s|db_user = \"\"|db_user = '${PROJECT_NUMBER}-compute'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|project = \"\"|project = '${PROJECT_ID}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|instance_name = \"csm-database\"|instance_name = 'csm-instance'|" customer-services-modernization/backend-apis/app/config.toml

######## Docs file in Gdrive
python3 Create_GDrive_folder.py --folder_name="${GDRIVE_FOLDER_NAME}" --service_account_email="${SERVICE_ACCOUNT_EMAIL}"

GDRIVE_FOLDER_ID=`jq -r '.GDRIVE_FOLDER_ID' < marketingEnvValue.json`
CSMDocID=`jq -r '.CSMDocID' < marketingEnvValue.json`

sed -i "s|drive_folder_id = \"\"|drive_folder_id = '${GDRIVE_FOLDER_ID}' |" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|docs_template_id = \"\"|docs_template_id = '${CSMDocID}' |" customer-services-modernization/backend-apis/app/config.toml

workspace_calendar_secret=`cat token.json`

SERVICE_ACCOUNT_CHECK=`gcloud iam service-accounts list --format=json | jq .[].email | grep "${SERVICE_ACCOUNT_EMAIL}" | wc -l`

if [[ SERVICE_ACCOUNT_CHECK -eq 0 ]]; then
    gcloud iam service-accounts create ${SERVICE_ACCOUNT} --display-name="${SERVICE_ACCOUNT} --project=${PROJECT_ID}"
fi

if [ ! -f sa_credentials.json ]; then
  echo "${SERVICE_ACCOUNT_EMAIL}:${PROJECT_ID}"
  gcloud iam service-accounts keys create sa_credentials.json --iam-account=${SERVICE_ACCOUNT_EMAIL} --project=${PROJECT_ID}
else
    echo "* sa_credentials.json ALREADY exists"
fi

workspace_calendar_sa_secret=`cat sa_credentials.json`

# sed -i 's|terraform/state/secretmanager/|terraform/state/secretmanager/workspace-calendar-user|' terraform/secretManager/backend.tf

## Instead of having a single terraform for 2 secret versions, use 2 different terraform resources.
## Because if you re-run the script again, the creation fails, and terraform out always gives you previous value.
cd terraform/GWSsecretManager
echo "*** terraform apply=>PROJECT_ID=${PROJECT_ID}"
terraform init && terraform apply --var "project_id=${PROJECT_ID}" --var "gws_user_secret_name=workspace-calendar-user" --var "gws_user_secret_data=${workspace_calendar_secret}" --var "gws_sa_secret_name=workspace-calendar-sa" --var "gws_sa_secret_data=${workspace_calendar_sa_secret}" --auto-approve
workspace_calendar_user_version="$(terraform output -raw gws_user_secret_version_id)"
workspace_calendar_sa_version="$(terraform output -raw gws_sa_secret_version_id)"
echo "workspace_calendar_user_version=$workspace_calendar_user_version"
echo "workspace_calendar_sa_version=$workspace_calendar_sa_version"

cd ../../

sed -i "s|user_secret_name = \"\"|user_secret_name = '${workspace_calendar_user_version}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|sa_secret_name = \"\"|sa_secret_name = '${workspace_calendar_sa_version}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|user_id = \"\"|user_id = '${USER_EMAIL}'|" customer-services-modernization/backend-apis/app/config.toml
sed -i "s|calendar_secret_id = \"\"|calendar_secret_id = '${workspace_calendar_user_version}'|" customer-services-modernization/backend-apis/app/config.toml

CHAT_AGENT_ID=`jq -r '.AGENT_ENGINE_NAME' < marketingEnvValue.json | cut -d'/' -f6`

sed -i "s|PROJECT_ID=<YOUR-PROJECT-ID>|PROJECT_ID=${PROJECT_ID}|" customer-services-modernization/backend-apis/Dockerfile
sed -i "s|website_uri = \"https://HOSTING.web.app/customer/home?productId=\"|website_uri = \"https://${PROJECT_ID}.web.app/customer/home?productId=\"|" customer-services-modernization/backend-apis/app/config.toml

cloud_run_check=`gcloud run services list --project=${PROJECT_ID} --format=json | jq .[].metadata.name | grep -w "csm-demo" | wc -l`
if [[ $cloud_run_check > 0 ]]; then
    echo "cloud run already exists"
    nr=`gcloud run services list --project=${PROJECT_ID} --format=json | jq .[].metadata.name | grep -wn "csm-demo" | cut -d':' -f1`
    nr=$(( nr-1 ))
    cloud_run_url=`gcloud run services list --project=${PROJECT_ID} --format=json | jq .[${nr}].status.url | sed 's|"||g'`
else
    echo "Creating cloud run ...."
    cloud_run_url=`gcloud run deploy csm-demo --image=us-docker.pkg.dev/cloudrun/container/hello --region=us-central1 --project=${PROJECT_ID} --format=json | jq .status.url | sed 's|"||g'`
fi
sed -i "s|https://APIURL/p1/send-email-from-docs|${cloud_run_url}/p1/send-email-from-docs|" customer-services-modernization/backend-apis/app/config.toml

cd customer-services-modernization/backend-apis/ && gcloud run deploy csm-demo --source . --region us-central1 --project=${PROJECT_ID} --quiet
cd ../../

triggers=`gcloud eventarc triggers list --location=us-central1 --project=${PROJECT_ID} --format=json | jq .[].name`
search_trigger_check=`echo "${triggers}" | sed 's|"||g' | cut -d'/' -f6 | grep -w "trigger-unstructured-search" | wc -l`
if [[ $search_trigger_check > 0 ]]; then
    echo "trigger-unstructured-search trigger already exists"
else
    echo "creating trigger-unstructured-search trigger"
    gcloud eventarc triggers create trigger-unstructured-search --destination-run-service=csm-demo --destination-run-path=p1/trigger-unstructured-search --destination-run-region=us-central1 --location=us-central1 --project=${PROJECT_ID} --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" --transport-topic=projects/${PROJECT_ID}/topics/website-search
fi

recommendations_trigger_check=`echo "${triggers}" | sed 's|"||g' | cut -d'/' -f6 | grep -w "trigger-unstructured-recommendations" | wc -l`
if [[ $recommendations_trigger_check > 0 ]]; then
    echo "trigger-unstructured-recommendations trigger already exists"
else
    gcloud eventarc triggers create trigger-unstructured-recommendations --destination-run-service=csm-demo --destination-run-path=p1/trigger-unstructured-recommendations --destination-run-region=us-central1 --location=us-central1 --project=${PROJECT_ID} --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" --transport-topic=projects/${PROJECT_ID}/topics/website-recommendations
fi

# Fix permission denied when running `firebase login`

if [ ! -f "$(npm root -g)/firebase-tools" ]; then
    echo "Deleting exising firebase-tools"
    npm uninstall -g firebase-tools --force

    # NPM_PAGKAGE_ROOT_FOLDER=$(npm root -g)
    # FIREBASE_TOOL_PACKAGE_FOLDER="${NPM_PAGKAGE_ROOT_FOLDER}/firebase-tools"
    # rm -rf $FIREBASE_TOOL_PACKAGE_FOLDER
else
    echo "No firebase-tools found"
fi

# if [ ! -f "$(which firebase)"]; then
#     echo "Deleting exising firebase"
#     rm -rf $(which firebase)
# else
#     echo "No firebase found"
# fi
# Create a directory for global installations in your home folder
# mkdir -p ~/.npm-global

# Configure npm to use the new directory
# npm config set prefix '~/.npm-global'

# Add the following line to your profile or rc file (e.g., ~/.bashrc, ~/.zshrc)
# export PATH=~/.npm-global/bin:$PATH
# source ~/.bashrc

# End

echo "Installing Firebase-tools"
npm install -g firebase-tools --no-cache

firebase login --no-localhost
firebase init hosting --project ${PROJECT_ID}

app_count=`firebase apps:list --project ${PROJECT_ID} --json | jq .result[].displayName | grep -w "csm-frontend-app" | wc -l`

if [[ $app_count > 0 ]]; then
    echo "Firebase app already exist.."
    n=`firebase apps:list --project ${PROJECT_ID} --json | jq .result[].displayName | grep -nw "csm-frontend-app" | cut -d':' -f1`
    n=$(( n-1 ))
    firebase_app_id=`firebase apps:list --project ${PROJECT_ID} --json | jq .result[${n}].appId | sed 's|"||g'`
else
    echo "creating app.."
    firebase_app_id=`firebase apps:create web csm-frontend-app --json | jq .result.appId | sed 's|"||g'`
fi
echo $firebase_app_id
firebase_config=`firebase apps:sdkconfig WEB ${firebase_app_id} --json`
echo $firebase_config
firebase_storageBucket=`echo "${firebase_config}" | jq .result.sdkConfig.storageBucket | sed 's|"||g'`
firebase_apiKey=`echo "${firebase_config}" | jq .result.sdkConfig.apiKey | sed 's|"||g'`
firebase_authDomain=`echo "${firebase_config}" | jq .result.sdkConfig.authDomain | sed 's|"||g'`
firebase_projectId=`echo "${firebase_config}" | jq .result.sdkConfig.projectId | sed 's|"||g'`
firebase_messagingSenderId=`echo "${firebase_config}" | jq .result.sdkConfig.messagingSenderId | sed 's|"||g'`
firebase_appId=`echo "${firebase_config}" | jq .result.sdkConfig.appId | sed 's|"||g'`
echo $firebase_storageBucket

sed -i "s|apiKey: \"\"|apiKey: '${firebase_apiKey}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|authDomain: \"\"|authDomain: '${firebase_authDomain}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|projectId: \"\"|projectId: '${firebase_projectId}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|storageBucket: \"\"|storageBucket: '${firebase_storageBucket}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|messagingSenderId: \"\"|messagingSenderId: '${firebase_messagingSenderId}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|appId: \"\"|appId: '${firebase_appId}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|apiURL: \"\"|apiURL: '${cloud_run_url}'|" customer-services-modernization/frontend/src/environments/environment.ts

sed -i "s|dfProject: \"\"|dfProject: '${PROJECT_ID}'|" customer-services-modernization/frontend/src/environments/environment.ts
sed -i "s|dfAgent: \"\"|dfAgent: '${CHAT_AGENT_ID}'|" customer-services-modernization/frontend/src/environments/environment.ts

echo "Installing Firebase Cli"
cd customer-services-modernization/frontend
rm -rf node_modules
npm install -g @angular/cli@17.3.8 --no-cache
npm install --save-dev @angular-devkit/build-angular@17.3.8 --no-cache

# rm -rf ~/.npm/_cacache/
# npm uninstall @angular-devkit/build-angular --force --no-cache
# rm -rf ~/.npm/_cacache/
# npm install @angular-devkit/build-angular --force --no-cache
# rm -rf ~/.npm/_cacache/

# Package                         Version
# ---------------------------------------------------------
# @angular-devkit/architect       0.1703.8
# @angular-devkit/build-angular   17.3.8
# @angular-devkit/core            17.3.8
# @angular-devkit/schematics      17.3.8
# @angular/cdk                    17.3.10
# @angular/cli                    17.3.8
# @angular/fire                   17.1.0
# @angular/google-maps            17.3.10
# @angular/material               17.3.10
# @schematics/angular             17.3.8
# rxjs                            7.8.1
# typescript                      5.4.5
# zone.js                         0.14.7

ng build
cd dist/genai-csm-proj
echo "Deploying Firebase web app"
firebase deploy --only hosting -p customer-services-modernization/frontend/dist/genai-csm-proj/browser --project ${PROJECT_ID} --force