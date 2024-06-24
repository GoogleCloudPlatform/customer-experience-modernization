# Generative AI for Customer Experience Modernization

This repository provides a deployment guide showcasing the application of Google Cloud's Generative AI for Customer Experience Modernization scenarios. It offers detailed, step-by-step guidance for setting up and utilizing the Generative AI tools

## Repository structure

```
.
├── frontend
└── backend-apis
```

- [`/frontend`](/frontend): Source code for demo app.  
- [`/backend-apis`](/backend-apis): Source code for backend APIs.


## Demonstrations

In this repository, the following demonstrations are provided:  

### Persona 1 - Customer - Website
![Persona 1 Architecture](/frontend/src/assets/architectures/p1_uj_1_2.svg)
* **[Customer Search using Vertex AI Search](https://www.youtube.com/watch?v=47jNYuuhbNA)**
* **[Multimodal Search using Vertex AI Vector Search](https://www.youtube.com/watch?v=8-OZmOZTTr4)**
* **[Website on demand translation using Translation AI](https://www.youtube.com/watch?v=tvyoR4dRCqQ)**
* **[Product Recommendations using Vertex AI Recommendations](https://www.youtube.com/watch?v=e5NRvTygZYg)**
* **[Infobot using Vertex AI Conversation](https://www.youtube.com/watch?v=92ulAdbwUoE)**

***

### Persona 1 - Customer - Email
![Persona 1 Architecture](/frontend/src/assets/architectures/p1_uj_3.svg)
* **[Email answering and hand off using Vertex AI Conversation](https://www.youtube.com/watch?v=lA2s7t3XdV0)**

***

### Persona 2 - Content Creator
![Persona 2 Architecture](/frontend/src/assets/architectures/p2_uj_1_2.svg)
* **[Products and services creation using Vertex AI LLMs for Text and Image Generation, Vertex AI Vector Search and Vision API for labeling](https://www.youtube.com/watch?v=4LeV_Ea9RGQ)**

***

### Persona 3 - Customer Experience Analyst
![Persona 3 Architecture](/frontend/src/assets/architectures/p3_uj_csm.svg)
* **[User Experience analytics using Looker, Firebase Analytics, Firebase Realtime Analytics and Google Analytics](https://www.youtube.com/watch?v=rh5vCWLVdRA)**

***

### Persona 3 - Marketing Integration
![Persona 3 Marketing Architecture](/frontend/src/assets/architectures/p3_uj_marketing.svg)
* **[Gen AI for Marketing](https://github.com/GoogleCloudPlatform/genai-for-marketing)**

***

### Persona 4 - Customer Service Agent
![Persona 4 Architecture](/frontend/src/assets/architectures/p4_uj_1.svg)
* **[Real time translation between user and agent using Translation AI](https://www.youtube.com/watch?v=vaz_KmVxsXc)**
* **[Message rephrasing using Vertex AI LLM](https://www.youtube.com/watch?v=qyPNGotOJA0)**
* **[Company Knowledge and Conversations Lookup and Q&A using Vertex AI Search](https://www.youtube.com/watch?v=fGBEEUxxkXQ)**
* **[Conversation Summary using Vertex AI LLM](https://www.youtube.com/watch?v=6bkEuwrEWOs)**
* **[Meet conversation with end user](https://www.youtube.com/watch?v=JmLJq5f5L0E)**

***

### Persona 5 - Contact Center Analyst
![Persona 5 Architecture](/frontend/src/assets/architectures/p5_uj_1.svg)
* **[Overall KPIs, Sentiment and Agent Performance using Looker](https://www.youtube.com/watch?v=9R1O-TPEUdU)**
* **[Insights from Reviews and Conversations using Vertex AI Search, Vertex AI LLM and Natural Language AI](https://www.youtube.com/watch?v=fh7rzDiEzJw)**
* **[Similarity search using Vertex AI Vector Search](https://www.youtube.com/watch?v=aQO6kb4ja2w)**
* **[Q&A using Vertex AI Search](https://www.youtube.com/watch?v=i_9FDWWcQsI)**

***

### Persona 6 - Field Service Agent
![Persona 6 Architecture](/frontend/src/assets/architectures/p6_uj_1.svg)
* **[Scheduling using Vertex AI Conversation](https://www.youtube.com/watch?v=m10qRO1CAVE)**
* **[Insights from Reviews and Conversations using Vertex AI Search, Vertex AI LLM and Natural Language AI](https://www.youtube.com/watch?v=bu1e0ZIaohQ)**
* **[Q&A using Vertex AI Search and Multimodal Q&A using Gemini](https://www.youtube.com/watch?v=jFBFknOrVac)**

Persona 7 - Return Service Agent
![Persona 7 Architecture](/frontend/src/assets/architectures/p7_uj_1.svg)
* **[Image and video comparison using Gemini]**
* **[Product recommendations]**
* **[Multiple surfaces]**


## Select a Google Cloud project

In the Google Cloud Console, on the project selector page, [select or create a Google Cloud project](https://console.cloud.google.com/projectselector2).  
> **As this is a DEMONSTRATION, you need to be a project owner in order to set up the environment.**


## Enable the required services

From [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell), run the following commands to enable the required Cloud APIs.  
Change `PROJECT_ID` to the id of your project.

```bash
export PROJECT_ID=<CHANGE TO YOUR PROJECT ID>
```


```bash
gcloud config set project $PROJECT_ID
```

```bash
gcloud services enable \
  cloudapis.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudtrace.googleapis.com \
  compute.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  run.googleapis.com
```

```bash
gcloud services enable \
  admin.googleapis.com \
  aiplatform.googleapis.com \
  appengine.googleapis.com \
  appenginereporting.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  bigquerydatatransfer.googleapis.com \
  bigquerymigration.googleapis.com \
  bigquerystorage.googleapis.com \
  containerfilesystem.googleapis.com \
  datacatalog.googleapis.com \
  datastore.googleapis.com \
  dialogflow.googleapis.com \
  discoveryengine.googleapis.com \
  docs.googleapis.com \
  drive.googleapis.com \
  eventarc.googleapis.com \
  fcm.googleapis.com \
  fcmregistrations.googleapis.com
```

```bash
gcloud services enable \
  firebase.googleapis.com \
  firebaseappdistribution.googleapis.com \
  firebasedynamiclinks.googleapis.com \
  firebasehosting.googleapis.com \
  firebaseinstallations.googleapis.com \
  firebaseremoteconfig.googleapis.com \
  firebaseremoteconfigrealtime.googleapis.com \
  firebaserules.googleapis.com \
  firebasestorage.googleapis.com \
  firestore.googleapis.com \
  iap.googleapis.com \
  identitytoolkit.googleapis.com \
  language.googleapis.com \
  logging.googleapis.com \
  looker.googleapis.com \
  mobilecrashreporting.googleapis.com \
  monitoring.googleapis.com \
  notebooks.googleapis.com \
  oslogin.googleapis.com
```

```bash
gcloud services enable \
  pubsub.googleapis.com \
  runtimeconfig.googleapis.com \
  secretmanager.googleapis.com \
  securetoken.googleapis.com \
  servicemanagement.googleapis.com \
  serviceusage.googleapis.com \
  sourcerepo.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  storage-component.googleapis.com \
  storage.googleapis.com \
  translate.googleapis.com \
  vision.googleapis.com
```

## Python environment
Create a new python environment of your choice and install backend-apis/deployment-scripts/requirements.txt

### Example using python venv with bash

Go to the right folder
```bash
cd backend-apis/deployment-scripts
```

Generate a venv environment
```bash
python3 -m venv venv
```

Activate venv environment
```bash
source ./venv/bin/activate
```

Install required libs
```bash
pip install -r requirements.txt
```

## Vertex AI Search and Conversation Setup

You must also activate the Vertex AI Search and Conversation API:

- In the Google Cloud console, go to the Search and Conversation page.

- [Search and Conversation](https://console.cloud.google.com/gen-app-builder//start)

- Select your project from the console drop-down.

- Read and agree to the Terms of Service, then click Continue and activate the API.


This demo uses Vertex AI Search and Conversation for Website Search, Website Recommendations, Infobot, Knowledbase Search and Customer Lookup.

### Persona 1 Search

For Persona 1 Search you can use the script provided to upload the products.

Go to the right folder
```bash
cd backend-apis/deployment-scripts
```

```bash
python vertex_search_operations.py --project_id $PROJECT_ID --location global
```

This will create the `csm-search-engine` using the generated example dataset [search_products.jsonl](backend-apis/deployment_scripts/dataset/search_products.jsonl)

### Persona 1 Recommendations

For Persona 1 Recommendations, upload products and events to Cloud Storage first.

The events should be fresh. Use the provided script to generate events.

Go to the right folder
```bash
cd backend-apis/deployment-scripts
```

Run the python script
```bash
python media_event_generation.py
```

This will generate a file named `full_media_events.jsonl` in a few seconds.

Upload full_media_events.jsonl to Cloud Storage.

[Create a recommendations app](https://cloud.google.com/generative-ai-app-builder/docs/create-app-data-store-media-recommendations) in Vertex AI Search and Conversations using the Console.
Create 1 App for each model, but use the same datastore for all of them.

- csm-media-rec-datastore - Datastore name.
- Dataset: gs://csm-solution-dataset/metadata/media_recommendations_products.jsonl

Apps Name

- csm-media-more-like-this - For the `More Like this` model
- csm-media-most-popular - For `Most Popular` model
- csm-media-others-you-maylike - For `Others you may like` model
- csm-media-rec-for-you - For `Recommended for you` model

### Persona 5 Conversations

For Persona 5 Conversations [Create a Search App](https://cloud.google.com/generative-ai-app-builder/docs/create-engine-es) using the Console
- Name: p5-conversations-search
- Dataset: gs://csm-solution-dataset/persona5/conversations_search_dataset.jsonl

### Persona 5 Reviews

For Persona 5 Reviews [Create a Search App](https://cloud.google.com/generative-ai-app-builder/docs/create-engine-es) using the Console
- Name: p5-reviews-search
- Dataset: gs://csm-solution-dataset/persona5/reviews_search_dataset.jsonl

### Infobot

For the infobot Create a Conversation App using the Console
- Name: p6-manuals-infobot
- Dataset: gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl

### Persona 6 Manuals search

For Persona 6 Manuals [Create a Search App](https://cloud.google.com/generative-ai-app-builder/docs/create-engine-es) using the Console
- Name: p6-search-manuals
- Dataset: gs://csm-solution-dataset/persona6/argolis_vertexai_search_products_manuals.jsonl

## Firestore Setup
Firestore datasets are used by Persona 1 (website reviews) and Persona 5 (conversations, reviews and customer information)

### Create a Firestore in Native mode database
If this is a new project, you need to create a Firestore database instance.

```bash
gcloud firestore databases create --location=nam5
```

### Data upload
Go to the right folder
```bash
cd backend-apis/deployment-scripts
```

Upload the collections data
```bash
python firestore_upload_data.py
```
This may take a few minutes.


## Cloud SQL
This demo uses Cloud SQL to store product information.

[Create a Cloud SQL Instance](https://cloud.google.com/sql/docs/mysql/create-instance#create-2nd-gen)

- Version: MySQL 8.0
- Name: csm-instance

[Add a Service Account](https://cloud.google.com/sql/docs/mysql/add-manage-iam-users#creating-a-database-user) to the database that will be used by the application

[Upload from backup](https://cloud.google.com/sql/docs/mysql/import-export/import-export-sql#import_a_sql_dump_file_to) 
- Database: csm
- 875 products
- gs://csm-solution-dataset/persona1/Cloud_SQL_Export.sql

## Vertex AI Vector Search
This demo uses Vertex AI Vector Search for similarity search

Use the [example](backend-apis/deployment_scripts/vertex_vector_operations.py) to create 3 Vector Search Endpoints

p5-conversations-index - 19250 conversations
- gs://csm-solution-dataset/persona5/conversations-embeddings/vertexai_conversations_embeddings.json

p5-reviews-index - 8750 reviews
- gs://csm-solution-dataset/persona5/reviews-embeddings/vertexai_reviews_embeddings.json

csm-multimodal-vector-search - 875 products
- gs://csm-solution-dataset/persona1/vector_search_website/vector_website_products.jsonl


## Pubsub Setup
Pubsub is used to offload LLM Requests in the website.

[Create 2 Topics](https://cloud.google.com/pubsub/docs/create-topic#create_a_topic_2)

- website-recommendations
- website-search

## Update the backend configuration with information of your project
Open the [configuration file](/backend-apis/app/config.toml) and include your informations.

### global
- project_id - Project used for this demo - e.g. "example-project"
- location - location used for this demo - e.g. "us-central1"
- datastore_location - location used for Vertex AI Search and Conversation datastores - e.g. "global"
- serving_config_id - configuration used for Vertex AI Search and Conversation serving - e.g. "default_config"
- images_bucket_name - bucket for images in Firebase Storage - e.g. "project-id.appspot.com"
- project_number - Project number used for this demo - e.g. "123456789123"


### website_search
- website_datastore_id - Id for the website search datastore - e.g. "dataset_1234567891234"
- website_topic_id - Pubsub topic id for search - e.g. "website-search"


### workspace
- calendar_id - Workspace calendar id - e.g. "example@example.com"
- calendar_secret_id - Id of workspace credentials secret stored in Secret Manager - e.g. "projects/123456789012/secrets/workspace-calendar/versions/1"


### search-persona5
- conversations_datastore_id - Id of the conversations Vertex AI Search datastore for Persona 5 - e.g. "p5-conversations_1234567890123"
- reviews_datastore_id - Id of the reviews Vertex AI Search datastore for Persona 5 - e.g. "p5-reviews_1234567891234"
- product_manuals_datastore_id - Id of the manuals Vertex AI Search datastore for Persona 6 - e.g."p6-manuals-field-agent_1703610731438"

- conversations_index_endpoint_id - Vertex Vector Search endpoint id for conversations for Persona 5 - e.g. "1234567891234567890"
- conversations_deployed_index_id - Vertex Vector Search index id for conversations for Persona 5 - e.g. "csm_p5_conversations_1234567890123"
- conversations_vector_api_endpoint - Vertex Vector Search api endpoint for conversations for Persona 5 - e.g. "123456789.us-central1-123456789012.vdb.vertexai.goog"

- reviews_index_endpoint_id - Vertex Vector Search endpoint id for reviews for Persona 5 - e.g. "1234567891234567890"
- reviews_deployed_index_id - Vertex Vector Search index id for reviews for Persona 5 - e.g. "csm_p5_reviews_1234567890123"
- reviews_vector_api_endpoint - Vertex Vector Search api endpoint for reviews for Persona 5 - e.g. "123456789.us-central1-123456789012.vdb.vertexai.goog"

### search
- p4_support_datastore_id - Id of the conversations Vertex AI Search datastore for Persona 4 - e.g. "p5-conversations_1234567890123"
- p4_salesforce_datastore_id - Id of the conversations Vertex AI Search datastore for Persona 4 - e.g. "p6-manuals-field-agent_1703610731438"

### salesforce
- user_secret_name - User Workspace credentials - e.g. "projects/123456789012/secrets/workspace-csm/versions/1"
- sa_secret_name - Service Account Workspace Credentials secret - e.g. "projects/123456789123/secrets/workspace-docs/versions/1"
- user_id - User email used for the emails - e.g. "example@example.com"

- website_uri - Website uri prefix for products - eg. "https://WEBISTE/customer/home?productId="
- drive_folder_id - Folder id which both the user and Service Account has access "1bo0rw7xC0b2L7NJA4qD7jWtm31d_RN4k"             
- docs_template_id - Template Docs id that the Service Account has access - eg. "15EThm_lOo6m54TWPzKBw2VAHsii4NBQnb4BpkUga5GA"

- apps_script_code - Replace CloudRunURL with the Cloud Run Url. This is the AppScript that will send email from docs. 

> "function sendId() {\n  var id = DocumentApp.getActiveDocument().getId();\n  var data = {\n  'docs_id': id\n  }\n\n  var options = {\n    'method' : 'post',\n    'contentType': 'application/json',\n    // Convert the JavaScript object to a JSON string.\n    'payload' : JSON.stringify(data)\n  };\n  UrlFetchApp.fetch('https://CloudRunURL/p1/send-email-from-docs', options);\n}\n\nfunction onOpen() {\n  var ui = DocumentApp.getUi();\n  // Or DocumentApp or FormApp.\n  ui.createMenu('Send Email')\n      .addItem('Send email to Salesforce case', 'sendId')\n      .addToUi();\n}\n"

### recommendations
- media_rec_datastore_id - Recommedantions datastore id - e.g. "csm-full-recommendations_1234567890123"
- media_rec_app_id.recommended-for-you - Recommended for you id - "csm-full-media-rec-for-you_1234567890123"
- media_rec_app_id.others-you-may-like - Others you may like id - "csm-full-media-others-you-_1234567890123"
- media_rec_app_id.more-like-this - More like this id - e.g. "csm-full-media-more-like-t_1234567890123"
- media_rec_app_id.most-popular-items - Most popular items id - e.g. "csm-full-media-most-popular"

### multimodal
- index_endpoint_id - Vertex Vector Search endpoint id for multimodal for Persona 1 - e.g. "1234567890123456789"
- deployed_index_id - Vertex Vector Search index id for multimodal search for Persona 1 - e.g. "csm_deployed_index"
- vector_api_endpoint - Vertex Vector Search api endpoint for multimodal search for Persona 1 - e.g. "1234567890.us-central1-123456789012.vdb.vertexai.goog"

### sql
- db_user - Service Account user for the Cloud Sql Instance - e.g. "123456789012-compute"
- db_name - Database name - e.g. "csm"
- project - Project id - e.g. "example-project"
- region - Cloud SQL Region - e.g. "us-central1"
- instance_name - Cloud SQL instance name - "csm-instance"

## Cloud Run Setup
Cloud Run is used to serve the backend APIs.

Deploy cloud run
```bash
cd backend-apis
gcloud run deploy csm-demo --source . --region us-central1
```

Create eventarc for Pubsub + Search
```bash
gcloud eventarc triggers create trigger-unstructured-search \
    --destination-run-service=csm-demo \
    --destination-run-path=trigger-unstructured-search \
    --destination-run-region=us-central1 \
    --location=us-central1 \
    --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
    --transport-topic=projects/PROJECT/topics/website-search
```

Create eventarc for Pubsub + Recommendations
```bash
gcloud eventarc triggers create trigger-unstructured-recommendations \
    --destination-run-service=csm-demo \
    --destination-run-path=trigger-unstructured-recommendations \
    --destination-run-region=us-central1 \
    --location=us-central1 \
    --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
    --transport-topic=projects/PROJECT/topics/website-recommendations
```

## Firebase Hosting app setup
After you have a Firebase project, you can register your web app with that project.

In the center of the Firebase console's project overview page, click the Web icon (plat_web) to launch the setup workflow.

If you've already added an app to your Firebase project, click Add app to display the platform options.

Enter your app's nickname.
This nickname is an internal, convenience identifier and is only visible to you in the Firebase console.

Click Register app.

Copy the information to include in the configuration.

## Update the frontend configuration with information of your project

Open the [frontend environment file](/frontend/src/environments/environment.ts) and include the Firebase information.

## Build Angular Frontend
Angular is the framework for the Frontend

```bash
npm install -g @angular/cli

cd frontend

ng build
```

## Firebase Hosting Setup
Firebase Hosting is used to serve the frontend.

### Install firebase tools
```bash
npm install -g firebase-tools

firebase login
```

### Init hosting
```bash
cd frontend/dist/genai-csm-project

firebase init hosting
```

select browser as public folder


### Deploy hosting
```bash
firebase deploy --only hosting
```

## Getting help

If you have any questions or if you found any problems with this repository, please report through GitHub issues.
