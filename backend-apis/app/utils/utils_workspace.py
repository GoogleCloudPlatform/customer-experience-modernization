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
Utils for Workspace

"""

import base64
import json
import tomllib
from email.mime.text import MIMEText

from fastapi import HTTPException
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.models.p1_model import SalesforceEmailSupportRequest
from app.utils.utils_ws_protocols import (
    DocsProtocol,
    DocumentResource,
    DriveProtocol,
    GmailProtocol,
    ScriptProtocol,
)

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

calendar_id = config["workspace"]["calendar_id"]
project_id = config["global"]["project_id"]
calendar_secret_id = config["workspace"]["calendar_secret_id"]

secret_client = secretmanager.SecretManagerServiceClient()
secret_user_info = secret_client.access_secret_version(
    request={"name": calendar_secret_id}
)
workspace_user_info = json.loads(secret_user_info.payload.data.decode("UTF-8"))
calendar_credentials = Credentials.from_authorized_user_info(
    info=workspace_user_info, scopes=config["workspace"]["calendar_scopes"]
)

calendar_service = build(
    serviceName="calendar", version="v3", credentials=calendar_credentials
)


class WorkspaceServices:

    """Workspace Services"""

    _user_credentials: Credentials | None = None
    _sa_credentials: service_account.Credentials | None = None

    _secret_client: secretmanager.SecretManagerServiceClient | None = None

    _gmail_service: GmailProtocol | None = None
    _drive_service: DriveProtocol | None = None
    _script_service: ScriptProtocol | None = None
    _docs_service: DocsProtocol | None = None

    def _get_secret_client(self) -> secretmanager.SecretManagerServiceClient:
        if not self._secret_client:
            self._secret_client = secretmanager.SecretManagerServiceClient()
        return self._secret_client

    def _get_user_credentials(self) -> Credentials:
        if not self._user_credentials:
            secret_user_info = self._get_secret_client().access_secret_version(
                request={"name": config["salesforce"]["user_secret_name"]}
            )
            workspace_user_info = json.loads(
                secret_user_info.payload.data.decode("UTF-8")
            )
            self._user_credentials = Credentials.from_authorized_user_info(
                info=workspace_user_info,
                scopes=config["salesforce"]["email_scopes"],
            )
        return self._user_credentials

    def _get_sa_credentials(self) -> service_account.Credentials:
        if not self._sa_credentials:
            sa_secret_info = self._get_secret_client().access_secret_version(
                request={"name": config["salesforce"]["sa_secret_name"]}
            )
            self._sa_credentials = (
                service_account.Credentials.from_service_account_info(
                    info=json.loads(
                        sa_secret_info.payload.data.decode("UTF-8")
                    ),
                    scopes=config["salesforce"]["workspace_scopes"],
                )
            )
        return self._sa_credentials

    def gmail(self) -> GmailProtocol:
        """Gmail Service

        Returns:
            Resource
                Gmail Service
        """
        if not self._gmail_service:
            self._gmail_service = build(
                "gmail", "v1", credentials=self._get_user_credentials()
            )

        return self._gmail_service

    def script(self) -> ScriptProtocol:
        """Script Service

        Returns:
            Resource
                Script Service
        """
        if not self._script_service:
            self._script_service = build(
                "script", "v1", credentials=self._get_user_credentials()
            )

        return self._script_service

    def docs(self) -> DocsProtocol:
        """Docs Service

        Returns:
            Resource
                Docs Service
        """
        if not self._docs_service:
            self._docs_service = build(
                "docs", "v1", credentials=self._get_sa_credentials()
            )

        return self._docs_service

    def drive(self) -> DriveProtocol:
        """Drive Service

        Returns:
            Resource
                Drive Service
        """
        if not self._drive_service:
            self._drive_service = build(
                "drive", "v3", credentials=self._get_sa_credentials()
            )

        return self._drive_service


ws = WorkspaceServices()


def get_last_message_id(email_thread: dict) -> str:
    """

    Args:
        email_thread:

    Raises:
        HTTPException:

    Returns:

    """
    message_id = ""
    try:
        # Get message ID from the last message
        for header in email_thread["messages"][-1]["payload"]["headers"]:
            if header["name"].lower() == "message-id":
                message_id = header["value"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return message_id


def get_gmail_thread(user_id: str, internal_thread_id: str) -> dict:
    """

    Args:
        user_id:
        internal_thread_id:

    Raises:
        HTTPException:

    Returns:

    """
    try:
        thread = (
            ws.gmail()
            .users()
            .threads()
            .get(userId=user_id, id=internal_thread_id)
            .execute(num_retries=20)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return thread


def list_gmail_threads(
    user_id: str, email_address: str, subject: str, max_results: int = 1
) -> dict:
    """

    Args:
        user_id:
        email_address:
        subject:
        max_results:

    Raises:
        HTTPException:

    Returns:

    """
    try:
        query = f'from:{email_address} label:inbox subject:"{subject}"'

        list_threads = (
            ws.gmail()
            .users()
            .threads()
            .list(userId=user_id, maxResults=max_results, q=query)
            .execute(num_retries=20)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return list_threads


def get_email_thread_id(email_thread: dict) -> tuple:
    """

    Args:
        email_thread:

    Raises:
        HTTPException:

    Returns:

    """
    email_thread_id = ""
    email_message_id = ""
    try:
        # Get thread ID from the first message
        for header in email_thread["messages"][0]["payload"]["headers"]:
            if header["name"].lower() == "message-id":
                email_thread_id = header["value"]

        # Get message ID from the last message
        for header in email_thread["messages"][-1]["payload"]["headers"]:
            if header["name"].lower() == "message-id":
                email_message_id = header["value"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return email_thread_id, email_message_id


def get_attachment_ids(email_thread: dict) -> list:
    """

    Args:
        email_thread:

    Raises:
        HTTPException:

    Returns:

    """
    attachments = set()
    try:
        email_parts = email_thread["messages"][-1]["payload"].get("parts", [])
        for part_level_0 in email_parts:
            if (
                part_level_0["mimeType"] == "image/png"
                or part_level_0["mimeType"] == "image/jpg"
            ):
                attachments.add(part_level_0["body"]["attachmentId"])
            elif "multipart" in part_level_0["mimeType"]:
                for part_level_1 in part_level_0["parts"]:
                    if (
                        part_level_1["mimeType"] == "image/png"
                        or part_level_1["mimeType"] == "image/jpg"
                    ):
                        attachments.add(part_level_1["body"]["attachmentId"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return list(attachments)


def get_attachment(
    attachment_id: str, internal_message_id: str, user_id: str
) -> dict:
    """

    Args:
        attachment_id:
        internal_message_id:
        user_id:

    Raises:
        HTTPException:

    Returns:

    """
    try:
        attachment = (
            ws.gmail()
            .users()
            .messages()
            .attachments()
            .get(
                userId=user_id, messageId=internal_message_id, id=attachment_id
            )
            .execute(num_retries=20)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return attachment


def create_salesforce_email_body(
    results: list,
    results_multimodal: list,
    user_name: str,
    is_human_talking: bool,
) -> str:
    """

    Args:
        results:
        user_name:
        is_human_talking:

    Returns:

    """
    email_response = (
        f"<html><body><p>Dear Customer {user_name},</p>"
        "<p>Thank you for contacting the support team.</p>"
    )

    if not results and not results_multimodal:
        if not is_human_talking:
            email_response += "<p>How can we help you today?</p>"
        else:
            email_response += "<p>Soon one of our specialists will get in touch with you.</p>"
    elif results_multimodal:
        email_response += (
            "<p>We found some questions about the attached image (multimodal search). "
            "We hope the following answers can be of help to you:</p>"
        )
        for i in results_multimodal:
            joined_links = [
                (f'<li><a href="{link}">Reference</a></li>')
                for link in i["links"]
            ]
            joined_links = "\n".join(joined_links)
            summary = (
                i["summary_text"]
                or "Here are some links you might find useful."
            )
            email_response += (
                f"<p><b>Question: </b>{i['question']}</p>"
                f"<p><b>Answer: </b>{summary}</p>"
                f"<ol>{joined_links}</ol>"
            )
    elif results:
        email_response += (
            "<p>We identified some questions in your email. "
            "We hope the following answers can be of help to you:</p>"
        )

        for i in results:
            joined_links = [
                (f'<li><a href="{link}">Reference</a></li>')
                for link in i["links"]
            ]
            joined_links = "\n".join(joined_links)
            summary = (
                i["summary_text"]
                or "Here are some links you might find useful."
            )
            email_response += (
                f"<p><b>Question: </b>{i['question']}</p>"
                f"<p><b>Answer: </b>{summary}</p>"
                f"<ol>{joined_links}</ol>"
            )

    if (results or results_multimodal) and is_human_talking:
        email_response += (
            "<p>We also know that you would like to talk to a human agent. "
            "Soon one of our specialists will get in touch with you.</p>"
        )

    email_response += "<p>This response was generated by an AI assistant. " \
        'Please respond with "I want to speak with a human agent" to get connected to a human</p>' \
        "<p>Best Regards,<br>You support team</p>"

    return email_response


def send_human_email(
    email_response: str,
    user_email_address: str,
    subject: str,
    email_thread_id: str,
    email_message_id: str,
    salesforce_thread_id: str,
    internal_thread_id: str,
) -> None:
    """

    Args:
        email_response:
        user_email_address:
        subject:
        email_thread_id:
        email_message_id:
        salesforce_thread_id:
        internal_thread_id:

    Raises:
        HTTPException:
    """
    try:
        message = MIMEText(email_response, "html")
        message["To"] = user_email_address
        message["From"] = config["salesforce"]["user_id"]
        message["Subject"] = subject
        message["In-Reply-To"] = email_message_id
        message["References"] = email_thread_id + " " + salesforce_thread_id

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            "raw": encoded_message,
            "threadId": internal_thread_id,
        }

        ws.gmail().users().messages().send(
            userId=config["salesforce"]["user_id"], body=create_message
        ).execute(num_retries=20)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def send_email_single_thread(
    email_response_html: str,
    destination_email_address: str,
    email_subject: str,
) -> str:
    """

    Args:
        email_response:
        request:
        case_dict:
        is_human_talking:

    Raises:
        HTTPException:

    Returns:
        str
            Google Docs Id if created or empty if not
    """

    message = MIMEText(email_response_html, "html")
    message["To"] = destination_email_address
    message["From"] = config["salesforce"]["user_id"]
    message["Subject"] = email_subject
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    ws.gmail().users().messages().send(
        userId=config["salesforce"]["user_id"], body={"raw": encoded_message}
    ).execute(num_retries=20)

    return "ok"


def send_salesforce_email_with_reply(
    email_response: str,
    request: SalesforceEmailSupportRequest,
    case_dict: dict,
    is_human_talking: bool,
) -> str:
    """

    Args:
        email_response:
        request:
        case_dict:
        is_human_talking:

    Raises:
        HTTPException:

    Returns:
        str
            Google Docs Id if created or empty if not

    """
    docs_id = ""
    try:
        message = MIMEText(email_response, "html")
        message["To"] = request.email_address
        message["From"] = config["salesforce"]["user_id"]
        message["Subject"] = request.subject
        message["In-Reply-To"] = case_dict["email_message_id"]
        message["References"] = (
            case_dict["email_thread_id"] + " " + request.salesforce_thread_id
        )

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            "raw": encoded_message,
            "threadId": case_dict["internal_thread_id"],
        }

        ws.gmail().users().messages().send(
            userId=config["salesforce"]["user_id"], body=create_message
        ).execute(num_retries=20)

        if is_human_talking:
            # Create email draft
            ws.gmail().users().drafts().create(
                userId=config["salesforce"]["user_id"],
                body={
                    "message": {
                        "raw": encoded_message,
                        "threadId": case_dict["internal_thread_id"],
                    }
                },
            ).execute(num_retries=20)

            if case_dict["docs_id"]:
                reset_docs_content(
                    case_docs_id=case_dict["docs_id"],
                    template_docs_id=config["salesforce"]["docs_template_id"],
                )
                docs_id = case_dict["docs_id"]
            else:
                # Create document to help edit the email
                docs_id = copy_drive_file(
                    drive_file_id=config["salesforce"]["docs_template_id"],
                    parent_folder_id=config["salesforce"]["drive_folder_id"],
                    copy_title=request.case_number,
                )
                add_apps_script_to_case_docs(
                    script_name=f"SendEmail{request.case_number}",
                    file_id=docs_id,
                )

            update_doc(
                document_id=docs_id,
                email_content=request.email_content,
                subject=request.subject,
                user_name=request.user_name,
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return docs_id


def set_docs_permission(file_id: str):
    """

    Args:
        file_id:

    Returns:

    """
    permission = {"type": "domain", "domain": "google.com", "role": "writer"}
    return (
        ws.drive()
        .permissions()
        .create(
            fileId=file_id,
            sendNotificationEmail=False,
            body=permission,
            supportsAllDrives=True,
        )
        .execute(num_retries=20)
    )


def add_apps_script_to_case_docs(script_name: str, file_id: str):
    """

    Args:
        script_name:
        file_id:
    """
    script: dict = (
        ws.script()
        .projects()
        .create(body={"title": script_name, "parentId": file_id})
        .execute(num_retries=20)
    )
    request = {
        "files": [
            {
                "name": "Code",
                "type": "SERVER_JS",
                "source": config["salesforce"]["apps_script_code"],
                "functionSet": {
                    "values": [{"name": "sendId"}, {"name": "onOpen"}]
                },
            },
            {
                "name": "appsscript",
                "type": "JSON",
                "source": '{"timeZone": "America/New_York", "exceptionLogging": "CLOUD"}',
            },
        ]
    }
    ws.script().projects().updateContent(
        scriptId=script["scriptId"], body=request
    ).execute(num_retries=20)


def copy_drive_file(
    drive_file_id: str, parent_folder_id: str, copy_title: str
):
    """

    Args:
        drive_file_id:
        parentFolderId:
        copy_title:

    Returns:

    """
    body = {"name": copy_title, "parents": [parent_folder_id]}
    drive_response = (
        ws.drive()
        .files()
        .copy(fileId=drive_file_id, body=body, supportsAllDrives=True)
        .execute(num_retries=20)
    )
    docs_copy_id = drive_response.get("id")

    return docs_copy_id


def reset_docs_content(template_docs_id: str, case_docs_id: str):
    """

    Args:
        template_docs_id:
        case_docs_id:

    Raises:
        HTTPException:
    """
    document = (
        ws.docs()
        .documents()
        .get(documentId=template_docs_id)
        .execute(num_retries=20)
    )
    docs_template_content = document["body"]["content"]

    # get content of the current doc and delete its content
    current_document = (
        ws.docs()
        .documents()
        .get(documentId=case_docs_id)
        .execute(num_retries=20)
    )
    current_document_content = current_document["body"]["content"]

    try:
        # Delete everything
        requests = []
        requests = [
            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": current_document_content[-1]["endIndex"]
                        - 1,
                    }
                }
            }
        ]
        ws.docs().documents().batchUpdate(
            documentId=case_docs_id, body={"requests": requests}
        ).execute(num_retries=20)

        # Update document with template
        requests = []
        for i in docs_template_content[1:]:
            for j in i["paragraph"]["elements"]:
                requests.append(
                    {
                        "insertText": {
                            "text": j["textRun"]["content"],
                            "location": {"index": j["startIndex"]},
                        }
                    }
                )
                if j["textRun"]["textStyle"]:
                    requests.append(
                        {
                            "updateTextStyle": {
                                "range": {
                                    "startIndex": j["startIndex"],
                                    "endIndex": j["endIndex"],
                                },
                                "textStyle": {**j["textRun"]["textStyle"]},
                                "fields": ", ".join(
                                    j["textRun"]["textStyle"].keys()
                                ),
                            }
                        }
                    )
            if i["paragraph"].get("paragraphStyle", ""):
                requests.append(
                    {
                        "updateParagraphStyle": {
                            "range": {
                                "startIndex": i["startIndex"],
                                "endIndex": i["endIndex"],
                            },
                            "paragraphStyle": {
                                **i["paragraph"]["paragraphStyle"]
                            },
                            "fields": ", ".join(
                                [
                                    k
                                    for k in i["paragraph"][
                                        "paragraphStyle"
                                    ].keys()
                                    if k != "headingId"
                                ]
                            ),
                        }
                    }
                )

        ws.docs().documents().batchUpdate(
            documentId=case_docs_id, body={"requests": requests}
        ).execute(num_retries=20)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def update_doc(
    document_id: str, email_content: str, subject: str, user_name: str
):
    """

    Args:
        document_id:
        email_content:
        subject:
        user_name:
    """
    requests = [
        {
            "replaceAllText": {
                "containsText": {
                    "text": "{{email-content}}",
                    "matchCase": "true",
                },
                "replaceText": email_content,
            }
        },
        {
            "replaceAllText": {
                "containsText": {"text": "{{subject}}", "matchCase": "true"},
                "replaceText": subject,
            }
        },
        {
            "replaceAllText": {
                "containsText": {"text": "{{user-name}}", "matchCase": "true"},
                "replaceText": user_name,
            }
        },
    ]
    ws.docs().documents().batchUpdate(
        documentId=document_id, body={"requests": requests}
    ).execute(num_retries=20)


def get_email_from_docs(docs_id: str) -> tuple:
    """

    Args:
        docs_id:

    Returns:

    """
    document: DocumentResource = (
        ws.docs().documents().get(documentId=docs_id).execute(num_retries=20)
    )
    document_content = document["body"]["content"]
    case_number = document["title"]
    found = False
    jump = False
    complete = False
    email = "<body>"
    for structural_element in document_content:
        if complete:
            break
        if jump:
            jump = False
            continue
        if found and "paragraph" in structural_element:
            email += "<p>"

        for element in structural_element.get("paragraph", {"elements": []})[
            "elements"
        ]:
            if "message_body" in element["textRun"]["content"]:
                if not found:
                    found = True
                    jump = True
                    continue
                complete = True
                break
            if found:
                email += element["textRun"]["content"]

        if found and "paragraph" in structural_element:
            email += "</p>"

    email = email.replace("\n", "<br>")

    email += "</body>"

    return case_number, email


def create_calendar_event(
    event_summary: str, attendees: list[str], start_date: str, end_date: str
) -> dict:
    event_data = {
        "summary": event_summary,
        "start": {
            "dateTime": start_date,
        },
        "end": {
            "dateTime": end_date,
        },
        "attendees": [{"email": attendee} for attendee in attendees],
        "conferenceData": {
            "createRequest": {
                "requestId": "support",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    event = (
        calendar_service.events()
        .insert(
            calendarId=calendar_id, body=event_data, conferenceDataVersion=1
        )
        .execute(num_retries=20)
    )

    return event
