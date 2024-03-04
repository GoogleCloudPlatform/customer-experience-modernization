/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Injectable } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ObservablesService } from './observables.service';
import { FirebaseService } from './firebase.service';
import { Observable, catchError, throwError } from 'rxjs';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { UploadTaskSnapshot } from '@firebase/storage'

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  documentId: string = '';
  chatMsgs: any = [];
  lastReadIndex: number = -1;

  constructor(private http: HttpClient, public observablesService: ObservablesService,
    private firebaseService: FirebaseService, public dialog: MatDialog) { }

  getDocumentIdForTextSearch(searchVal: any): Observable<any> {
    this.chatMsgs = []
    this.lastReadIndex = -1;
    this.documentId = '';
    return new Observable(observer => {
      this.getDocumentId(searchVal).subscribe((res: any) => {
        this.documentId = res.document_id;
        this.chatMsgs.push({
          'author': 'user',
          'message': searchVal
        })
        this.observablesService.setLoading(false);
        this.observablesService.sendUpdatedDocumentID(this.documentId);
        observer.next(this.documentId);
      })
    });
  }

  async getDocumentIdForImageSearch(assistantChat: any, file: any, event: any) {
    return this.firebaseService.uploadImageToStorage(file).then(
      (snapshot: UploadTaskSnapshot): UploadTaskSnapshot => {
        this.uploadImageOnInitialSearch(assistantChat, snapshot.metadata.name);
        return snapshot;
      }).then((snapshot: any): Observable<string> => {
        this.chatMsgs = []
        this.lastReadIndex = -1;
        this.documentId = '';
        return new Observable(observer => {
          this.uploadImageOnInitialSearch(assistantChat, snapshot.metadata.name).subscribe((res: any) => {
            this.documentId = res.document_id;
            this.chatMsgs.push({
              'author': 'user',
              'message': assistantChat,
              'imageSrc': event.target.result
            })
            observer.next(this.documentId);
            this.observablesService.sendUpdatedDocumentID(res.document_id);
          })
        });
      })

  }

  continueFollowupForText(assistantChat: any) {
    this.continueConversation(assistantChat, this.documentId).subscribe(() => {
      this.chatMsgs.push({
        'author': 'user',
        'message': assistantChat
      })
      //this.firebaseService.getSearchResults().subscribe()
    });
  }

  continueFollowupForImage(imageFile: any, assistantChat: any, event: any): Observable<any> {
    return new Observable(observer => {
      this.firebaseService.uploadImageToStorage(imageFile).then((snapshot) => {
        this.uploadImage(this.documentId, "", snapshot.metadata.name);
        return snapshot
      }).then((snapshot: any) => {
        this.chatMsgs.push({
          'author': 'user',
          'message': assistantChat,
          'imageSrc': event.target.result
        })
        this.uploadImage(assistantChat, this.documentId, snapshot.metadata.name).subscribe(() => {
          this.firebaseService.getSearchResults(this.documentId).subscribe((res)=>{
            observer.next(res)
          })
        });
      });
    });
  }

  fetchResults(docId: string): Observable<any> {
    return new Observable(observer => {
      this.firebaseService.getSearchResults(docId).subscribe((res) => {
        var serverMsgs = res?.['conversation'];
        var lastServerMsgsIndex = serverMsgs?.length - 1
        if (this.lastReadIndex < lastServerMsgsIndex) {
          if (serverMsgs[lastServerMsgsIndex].author === 'system') {
            this.chatMsgs.push(serverMsgs[lastServerMsgsIndex])
            this.lastReadIndex = lastServerMsgsIndex;
          }
        }
        this.observablesService.setLoading(false);
        observer.next(this.chatMsgs);
      })
    });
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error);
    } else {

    }

    return throwError(() => new Error(
      'Something bad happened; please try again later.'));
  }


  getDocumentId(query: string) {
    const reqBody = {
      "query": query,
      "visitor_id": "",
      "search_doc_id": "",
      "image": ""
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-search`, reqBody)
      .pipe(catchError(this.handleError));

  }

  continueConversation(query: string, docId: string) {
    const reqBody = {
      "query": query,
      "visitor_id": "",
      "search_doc_id": docId,
      "image": ""
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-search`, reqBody)
      .pipe(catchError(this.handleError));

  }
  uploadImage(query: string, docId: string, image: string) {
    const reqBody = {
      "query": query,
      "visitor_id": "",
      "search_doc_id": docId,
      "image": image
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-search`, reqBody)
      .pipe(catchError(this.handleError));

  }

  uploadImageOnInitialSearch(query: string, image: string) {
    const reqBody = {
      "query": query,
      "visitor_id": "",
      "search_doc_id": "",
      "image": image
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-search`, reqBody)
      .pipe(catchError(this.handleError));

  }


}
