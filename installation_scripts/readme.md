# Steps

## Environment
* NodeJS 18.19+
* Python 3.11+

## Google Cloud Project
* Create a new GCP project
```shell
# export WEB_HOST=localhost # Uncomment If not running automation.sh in CloudShell
export GOOGLE_CLOUD_PROJECT=<YOUR PROJECT ID>

# export PATH=$PATH:$(dirname $(which npm))

gcloud config set project $GOOGLE_CLOUD_PROJECT

gcloud services enable \
  calendar-json.googleapis.com \
  cloudapis.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudtrace.googleapis.com \
  compute.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  gmail.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  run.googleapis.com

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

* For Googlers only
  - Disable `Disable Service Key Creation` Org policy.
  - Set `Domain Restricted Sharing` Org policy to `Allow All`.
* Configure Consent Screen
    - Add the user email to `Test Users`
* Create an OAuth 2.0 Client Credential and download the key as `api_credentials.json`
    - Application Type: Desktop app

* Service Account Role Assignment - Default Compute Engine Service Account (`$PROJECT_NUMBER-compute@developer.gserviceaccount.com`)
  - Cloud Build
    - Artifacts Registry Writer
    - Artifacts Registry Admin
    - Storage Object Viewer
    - Storage Object Admin
    - Storage Admin
  - Cloud Run
    - Discovery Engine Admin
    - Secret Manager Secret Accessor

* User IAM Role Assignmnet
  - Users who will use the solution
    - Firebase Viewer

## Firebase
* Register the Google Cloud Project to Firebase.
  - Enable Firebase analytics.

* Register Web App
  - Goto [Firebase console](https://firebase.corp.google.com).
  - On the left panel, `Project Overview`, `Project Settings`.
  - On the middle panel, scroll down to `Your Apps`. Create a new Web App.
    - App nickname: Your project Id.
    - Check `Also set up Firebase Hosting for this app`. 

* Add Authentication Method
  - Go to [Firebase console](https://firebase.corp.google.com).
  - Select your project.
  - On the left panel, go to `Build`, `Authentication`, `Get Started`.
  - In `Sign-in providers`, Enable `Google` Authentication method and Save.

* Add Authorized Domain.
   - Go to Firebase console -> Authentication -> Settings -> Authorized domains tab.
   - Scroll down to `Authorized Domains`, add `<PROJECT_ID>.web.app`.

## Deployment
* If you use `nvm` to manage your NodeJS environment, ensure you have install and activate NodeJS 18.19+
```shell
nvm install 20.15.0
nvm use 20.15.0
```
* Create Python environment
```shell
cd installation_scripts

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
* Generate Media Events
This will take several minutes.
```shell
python3 media_event_generation.py 
```

* Create a Firestore database
```shell
gcloud firestore databases create --location=nam5 --type=firestore-native --project=$GOOGLE_CLOUD_PROJECT
```
* Update [Dockerfile](../backend-apis/Dockerfile)
```dockerfile
ARG PROJECT_ID=<YOUR GCP PROJECT ID>
```

* Run `automation.sh`

- When running `automation.sh` and prompted to login, please login with an Google account that has access to Google Workspace (Gmail and Calendar).

```shell
. automation.sh 2>&1 | tee run.log
```

* Update Firebase database rule

```
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow write: if false;
      allow read: if true;
    }
  }
}
```

* Update Cloud SQL Permissions

```sql
grant select on csm.products to "<<PROJECT_NUMBER>>-compute";
```

* Create Firebase Storage

1. Go To Firebase console, Storage.
2. Create a Storage in `Production` mode with the following rule.
```
rules_version = '2';

// Craft rules based on data in your Firestore database
// allow write: if firestore.get(
//    /databases/(default)/documents/users/$(request.auth.uid)).data.isAdmin;
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if true;
    }
  }
}
```
3. Add folder
  - images
  - p7

* Enable Dialogflow Messenger Unauthorized Integration

* Google Workspace Setup
  - The `automation.sh` uses the email you input during the setup to create a calendar event. If your organization restricts uses of Google Workspace, you may need to manually update the calendar_id setting in the generated `config.toml`, and update the setting.

  ```ini
  calendar_id = 'YOUR@GMAIL.COM'
  ```

  - The `automation.sh` uses the email you input during the setup to send emails. The email is configured in `config.toml`. If your organization restricts uses of Google Workspace, you may need to manually update the calendar_id setting in the generated `config.toml`, and update the setting.

  ```ini
  [salesforce]
  # Vertex AI Search for email support
  user_id = 'YOUR EMAIL'
  ```