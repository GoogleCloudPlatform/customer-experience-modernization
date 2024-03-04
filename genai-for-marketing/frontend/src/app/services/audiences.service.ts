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
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environments';
@Injectable({
  providedIn: 'root'
})
export class AudiencesService {

  constructor( public http: HttpClient) { }


  getPreviewTableData(){
    return this.http
      .get(`${environment.apiUrl}/get-dataset-sample/customers`)
      .pipe(
        catchError(this.handleError)
      );
  }

  // getPreviewTableData(){
  //   return this.http
  //     .get(`assets/audience.json`)
  //     .pipe(
  //       catchError(this.handleError)
  //     );
  // }

   getPreviewTableDataEvents(){
    return this.http
      .get(`${environment.apiUrl}/get-dataset-sample/events`)
      .pipe(
         catchError(this.handleError)
       );
   }

  //  getPreviewTableDataEvents(){
  //   return this.http
  //     .get(`assets/events.json`)
  //     .pipe(
  //        catchError(this.handleError)
  //      );
  //  }

  //  getPreviewTableDataTransactions(){
  //   return this.http
  //     .get(`assets/transactions.json`)
  //     .pipe(
  //        catchError(this.handleError)
  //      );
  //  }

  getPreviewTableDataTransactions(){
    return this.http
      .get(`${environment.apiUrl}/get-dataset-sample/transactions`)
      .pipe(
         catchError(this.handleError)
       );
   }
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error);
    } else {
    }
    return throwError(
      'Something bad happened; please try again later.');
  }

  generateQuery(question: any) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
    // let questionData = {
    //   "question": query
    // }
    return this.http.post(`${environment.apiUrl}/post-audiences`, {question}, options)
      .pipe(catchError(this.handleError));

  }

  getaudienceTableData(){
    return this.http
      .get(`assets/audienceEmailDetails.json`)
      .pipe(
         catchError(this.handleError)
       );
   }



  updateCampaign(query: any, userId: string , campaignId: string) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
    return this.http.put(`${environment.apiUrl}/users/${userId}/campaigns/${campaignId}`, query, options)
      .pipe(catchError(this.handleError));

  }
}
