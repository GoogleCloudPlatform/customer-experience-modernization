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
import { Observable, catchError, throwError } from 'rxjs';
import { FirebaseService } from './firebase.service';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class RecommendationsService {

  constructor(public firebaseService: FirebaseService, private http: HttpClient) { }

  recommendationsApi(recommendation_type: string, event_type: string, user_pseudo_id: string) {
    const reqBody = {
      "recommendation_type": recommendation_type,
      "event_type": event_type,
      "user_pseudo_id": user_pseudo_id,
      "documents": [],
      "optional_user_event_fields": {}
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-recommendations`, reqBody)
      .pipe(catchError(this.handleError));
  }

  getRecommendationsDocumentId(recommendation_type: string, event_type: string, user_pseudo_id: string): Observable<any> {
    const reqBody = {
      "recommendation_type": recommendation_type,
      "event_type": event_type,
      "user_pseudo_id": user_pseudo_id,
      "documents": [],
      "optional_user_event_fields": {}
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-recommendations`, reqBody)
      .pipe(catchError(this.handleError));
  }

  getViewItemRecommendationsDocumentId(recommendation_type: string, user_pseudo_id: string, docs: string[]): Observable<any> {
    const event_type = docs.length > 1 ? "view-item-list" : "view-item";
    const reqBody = {
      "recommendation_type": recommendation_type,
      "event_type": event_type,
      "user_pseudo_id": user_pseudo_id,
      "documents": docs,
      "optional_user_event_fields": {}
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-recommendations`, reqBody)
      .pipe(catchError(this.handleError));
  }

  getPurchaseRecommendationsDocumentId(recommendation_type: string, user_pseudo_id: string, docs: string[]): Observable<any> {
    const reqBody = {
      "recommendation_type": recommendation_type,
      "event_type": "purchase",
      "user_pseudo_id": user_pseudo_id,
      "documents": docs,
      "optional_user_event_fields": {}
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-recommendations`, reqBody)
      .pipe(catchError(this.handleError));
  }
  getAddToCartRecommendationsDocumentId(recommendation_type: string, user_pseudo_id: string, docId: string): Observable<any> {
    const reqBody = {
      "recommendation_type": recommendation_type,
      "event_type": "add-to-cart",
      "user_pseudo_id": user_pseudo_id,
      "documents": [docId],
      "optional_user_event_fields": {}
    }
    return this.http.post<any>(`${environment.apiURL}/p1/initiate-vertexai-recommendations`, reqBody)
      .pipe(catchError(this.handleError));
  }

  collectRecommendationsEvents(event_type: string, user_pseudo_id: string, docs: string[], optional_user_event_fields: object) {
    const reqBody = {
      "event_type": event_type,
      "user_pseudo_id": user_pseudo_id,
      "documents": docs,
      "optional_user_event_fields": optional_user_event_fields
    };
    this.http.post<any>(`${environment.apiURL}/p1/collect-recommendations-events`, reqBody).pipe(catchError(this.handleError)).subscribe();
  }

  fetchRecommendationResults(recommendationsDocumentId: any): Observable<any> {
    return new Observable(observer => {
      this.firebaseService.getRecommendationsResults(recommendationsDocumentId).subscribe((res) => {
        var serverMsgs = res?.['recommendations'];
        observer.next(serverMsgs);
      })
    });
  }
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error.message);
    } else {

      // console.error(
      //   `Backend returned code ${error.status}, ` +
      //   `body was: ${error.error}`);
    }

    return throwError(() => new Error(
      'Something bad happened; please try again later.'));
  }

  addOrder(obj : any) :Observable<any>{
    const reqBody = obj
    return this.http.post<any>(`https://csm-dev-42fk6qqj5a-uc.a.run.app/p1/add-order`, reqBody).pipe(catchError(this.handleError));
  }
}

