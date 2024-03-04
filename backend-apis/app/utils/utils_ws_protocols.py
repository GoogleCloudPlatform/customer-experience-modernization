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


from typing import Any, NotRequired, Protocol, Self, TypedDict

from googleapiclient.discovery import BatchHttpRequest, HttpRequest

class DocumentsBatchUpdateBody(TypedDict):
    requests: list
    writeControl: NotRequired[dict]

class DocumentResource (TypedDict):
    documentId: str
    title: str
    body: dict
    headers: dict
    footers: dict
    footnotes: dict
    documentStyle: dict
    suggestedDocumentStyleChanges: dict
    namedStyles: dict
    suggestedNamedStylesChanges: dict
    lists: dict
    namedRanges: dict
    revisionId: str
    suggestionsViewMode: str
    inlineObjects: dict
    positionedObjects: dict
    

class ResourceProtocol(Protocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback


class DocumentsProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback

    def batchUpdate(self, documentId: str,
                    body: DocumentsBatchUpdateBody,
                    x__xgafv=None) -> HttpRequest:
        del documentId, body, x__xgafv
        return HttpRequest(None, None, None)

    def get(self, documentId: str, x__xgafv=None,
            suggestionsViewMode=None) -> HttpRequest:
        del documentId, x__xgafv, suggestionsViewMode
        return HttpRequest(None, None, None)

    def create(self, body=None, x__xgafv=None) -> HttpRequest:
        del body, x__xgafv
        return HttpRequest(None, None, None)


class DocsProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback

    def documents(self) -> DocumentsProtocol: ...

    def new_batch_http_request(self) -> BatchHttpRequest: ...

class ThreadsProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback

    def delete(self, userId: str, id: str) -> HttpRequest:
        del userId, id
        return HttpRequest(None, None, None)

    def modify(self, userId: str, id: str, body=None) -> HttpRequest:
        del userId, id, body
        return HttpRequest(None, None, None)

    def trash(self, userId: str, id: str) -> HttpRequest:
        del userId, id
        return HttpRequest(None, None, None)

    def untrash(self, userId: str, id: str) -> HttpRequest:
        del userId, id
        return HttpRequest(None, None, None)

    def get(self, userId: str, id: str,
            format=None, metadataHeaders=None) -> HttpRequest:
        del userId, id, format, metadataHeaders
        return HttpRequest(None, None, None)

    def list(self, userId: str, labelIds=None, q=None,
             pageToken=None, maxResults=None,
             includeSpamTrash=None) -> HttpRequest:
        del userId, labelIds, q, pageToken, maxResults, includeSpamTrash
        return HttpRequest(None, None, None)

    def list_next(self, previous_request: str,
                  previous_response: str) -> HttpRequest:
        del previous_request, previous_response
        return HttpRequest(None, None, None)


class UsersProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback

    def drafts(self) -> Any: ...

    def history(self) -> Any: ...

    def labels(self) -> Any: ...

    def messages(self) -> Any: ...

    def settings(self) -> Any: ...

    def threads(self) -> ThreadsProtocol: ...

    def getProfile(self, userId: str) -> HttpRequest:
        del userId
        return HttpRequest(None, None, None)

    def create(self, body=None, x__xgafv=None) -> HttpRequest:
        del body, x__xgafv
        return HttpRequest(None, None, None)


class GmailProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback

    def users(self) -> UsersProtocol: ...

    def new_batch_http_request(self) -> BatchHttpRequest: ...


class FilesProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback


    def list_next(self, previous_request: str,
                  previous_response: str) -> HttpRequest:
        del previous_request, previous_response
        return HttpRequest(None, None, None)

    def copy(self, fileId: str, body=None, enforceSingleParent=None, 
             keepRevisionForever=None, ignoreDefaultVisibility=None, 
             ocrLanguage=None, supportsTeamDrives=None, 
             supportsAllDrives=None) -> HttpRequest:
        del (fileId, body, enforceSingleParent, keepRevisionForever,
             ignoreDefaultVisibility, ocrLanguage, supportsTeamDrives,
             supportsAllDrives)
        return HttpRequest(None, None, None)



    def create(self, body=None, enforceSingleParent=None, 
               keepRevisionForever=None, media_body=None, 
               useContentAsIndexableText=None, supportsTeamDrives=None, 
               ocrLanguage=None, ignoreDefaultVisibility=None, 
               supportsAllDrives=None, media_mime_type=None) -> HttpRequest:
        del (body, enforceSingleParent, keepRevisionForever, media_body, 
             useContentAsIndexableText, supportsTeamDrives, ocrLanguage, 
             ignoreDefaultVisibility, supportsAllDrives, media_mime_type)     
        return HttpRequest(None, None, None)



    def delete(self, fileId: str, supportsTeamDrives=None,
               supportsAllDrives=None) -> HttpRequest:
        del fileId, supportsTeamDrives, supportsAllDrives       
        return HttpRequest(None, None, None)


    def emptyTrash(self) -> HttpRequest: ...


    def export(self, fileId: str, mimeType: str) -> HttpRequest:
        del fileId, mimeType
        return HttpRequest(None, None, None)



    def export_media(self, fileId: str, mimeType: str) -> HttpRequest:
        del fileId, mimeType
        return HttpRequest(None, None, None)



    def generateIds(self, count=None, space=None) -> HttpRequest:
        del count, space
        return HttpRequest(None, None, None)



    def get(self, fileId: str, supportsTeamDrives=None, supportsAllDrives=None, 
            acknowledgeAbuse=None) -> HttpRequest:
        del fileId, supportsTeamDrives, supportsAllDrives, acknowledgeAbuse
        return HttpRequest(None, None, None)



    def get_media(self, fileId: str, supportsTeamDrives=None, 
                  supportsAllDrives=None, acknowledgeAbuse=None) -> HttpRequest:
        del fileId, supportsTeamDrives, supportsAllDrives, acknowledgeAbuse
        return HttpRequest(None, None, None)



    def list(self, orderBy=None, pageSize=None, supportsTeamDrives=None, 
             spaces=None, q=None, pageToken=None, corpus=None, 
             teamDriveId=None, includeItemsFromAllDrives=None, 
             includeTeamDriveItems=None, corpora=None, 
             supportsAllDrives=None, driveId=None) -> HttpRequest:
        del (orderBy, pageSize, supportsTeamDrives, spaces, q, pageToken,
             corpus, teamDriveId, includeItemsFromAllDrives,
             includeTeamDriveItems, corpora, supportsAllDrives, driveId)
        return HttpRequest(None, None, None)



    def update(self, fileId: str, body=None, keepRevisionForever=None, 
               removeParents=None, supportsTeamDrives=None, 
               media_body=None, ocrLanguage=None, addParents=None, 
               enforceSingleParent=None, useContentAsIndexableText=None, 
               supportsAllDrives=None, media_mime_type=None) -> HttpRequest:
        del (fileId, body, keepRevisionForever, removeParents, 
             supportsTeamDrives, media_body, ocrLanguage, addParents, 
             enforceSingleParent, useContentAsIndexableText, 
             supportsAllDrives, media_mime_type)
        return HttpRequest(None, None, None)



    def watch(self, fileId: str, body=None, supportsTeamDrives=None,
              supportsAllDrives=None, acknowledgeAbuse=None) -> HttpRequest:
        del (fileId, body, supportsTeamDrives, supportsAllDrives,
             acknowledgeAbuse)
        return HttpRequest(None, None, None)



    def watch_media(self, fileId: str, body=None, supportsTeamDrives=None, 
                    supportsAllDrives=None,
                    acknowledgeAbuse=None) -> HttpRequest:
        del (fileId, body, supportsTeamDrives, supportsAllDrives,
             acknowledgeAbuse)
        return HttpRequest(None, None, None)


class PermissionsProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        del exc_type, exc_value, traceback


    def list_next(self, previous_request: str,
                  previous_response: str) -> HttpRequest:
        del previous_request, previous_response
        return HttpRequest(None, None, None)

    def create(self, fileId: str, body=None, moveToNewOwnersRoot=None, 
               enforceSingleParent=None, sendNotificationEmail=None, 
               supportsTeamDrives=None, supportsAllDrives=None, 
               transferOwnership=None, emailMessage=None, 
               useDomainAdminAccess=None)-> HttpRequest:
        del (fileId, body, moveToNewOwnersRoot, enforceSingleParent,
             sendNotificationEmail, supportsTeamDrives, supportsAllDrives, 
             transferOwnership, emailMessage, useDomainAdminAccess)
        return HttpRequest(None, None, None)


    def delete(self, fileId: str, permissionId: str, supportsTeamDrives=None, 
               supportsAllDrives=None, useDomainAdminAccess=None)-> HttpRequest:
        del (fileId, permissionId, supportsTeamDrives, supportsAllDrives, 
             useDomainAdminAccess)
        return HttpRequest(None, None, None)



    def get(self, fileId: str, permissionId: str, supportsTeamDrives=None, 
            supportsAllDrives=None, useDomainAdminAccess=None)-> HttpRequest:
        del (fileId, permissionId, supportsTeamDrives, supportsAllDrives, 
             useDomainAdminAccess)
        return HttpRequest(None, None, None)



    def list(self, fileId: str, pageSize=None, pageToken=None, 
             supportsTeamDrives=None, supportsAllDrives=None, 
             useDomainAdminAccess=None)-> HttpRequest:
        del (fileId, pageSize, pageToken, supportsTeamDrives, 
             supportsAllDrives, useDomainAdminAccess)
        return HttpRequest(None, None, None)



    def update(self, fileId: str, permissionId: str, body=None, 
               removeExpiration=None, supportsTeamDrives=None, 
               supportsAllDrives=None, useDomainAdminAccess=None, 
               transferOwnership=None)-> HttpRequest:
        del (fileId, permissionId, body, removeExpiration, 
             supportsTeamDrives, supportsAllDrives, useDomainAdminAccess, 
             transferOwnership)
        return HttpRequest(None, None, None)



class DriveProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback

    def about(self) -> Any: ...

    def changes(self) -> Any: ...

    def channels(self) -> Any: ...

    def comments(self) -> Any: ...

    def drives(self) -> Any: ...

    def files(self) -> FilesProtocol: ...

    def permissions(self) -> PermissionsProtocol: ...

    def replies(self) -> Any: ...

    def revisions(self) -> Any: ...

    def teamdrives(self) -> Any: ...

    def new_batch_http_request(self) -> BatchHttpRequest: ...


class ScriptProjectsProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback

    def deployments(self) -> Any: ...

    def versions(self) -> Any: ...

    def create(self, body=None, x__xgafv=None) -> HttpRequest:
        del body, x__xgafv
        return HttpRequest(None, None, None)

    def get(self, scriptId: str, x__xgafv=None) -> HttpRequest:
        del scriptId, x__xgafv
        return HttpRequest(None, None, None)

    def getContent(self, scriptId: str, versionNumber=None,
                   x__xgafv=None) -> HttpRequest:
        del scriptId, versionNumber, x__xgafv
        return HttpRequest(None, None, None)

    def getMetrics(self, scriptId: str, metricsFilter_deploymentId=None,
                   x__xgafv=None, metricsGranularity=None) -> HttpRequest:
        del scriptId, metricsFilter_deploymentId, x__xgafv, metricsGranularity
        return HttpRequest(None, None, None)

    def updateContent(self, scriptId: str, body=None,
                      x__xgafv=None) -> HttpRequest:
        del scriptId, body, x__xgafv
        return HttpRequest(None, None, None)

class ScriptProtocol(ResourceProtocol):
    def close(self) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback

    def processes(self) -> Any: ...

    def projects(self) -> ScriptProjectsProtocol: ...

    def scripts(self) -> Any: ...

    def new_batch_http_request(self) -> BatchHttpRequest: ...
