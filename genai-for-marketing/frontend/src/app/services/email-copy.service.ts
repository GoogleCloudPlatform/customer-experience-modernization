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

import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environments';

@Injectable({
  providedIn: 'root'
})
export class EmailCopyService {

  constructor( public http: HttpClient, public snackBar: MatSnackBar) { }


  generateEmailCopy(obj: any) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
    return this.http.post(`${environment.apiUrl}/generate-image`, obj, options)
      .pipe(catchError(this.handleError));
  }

  generateEmailText(obj: any) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
   
    return this.http.post(`${environment.apiUrl}/generate-content`, obj, options)
      .pipe(catchError(this.handleError));

  }

  bulkEmail(obj: any) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
   
    return this.http.post(`${environment.apiUrl}/bulk-email-generate`, obj, options)
      .pipe(catchError(this.handleError));

  }
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error);

   //   this.showSnackbarCssStyles(error.error, 'Close', '4000')
    } else {

   //   this.showSnackbarCssStyles(error?.message, 'Close', '4000')
    }
    return throwError(
      'Something bad happened; please try again later.');
  }
  //
  editImage(query: any) {
    const head = new HttpHeaders().set('content-type', 'application/json')
    let options = {
      headers: head
    }
    return this.http.post(`${environment.apiUrl}/edit-image`, query, options)
      .pipe(catchError(this.handleError));

  }

  showSnackbarCssStyles(content: any, action: any, duration: any) {
    let sb = this.snackBar.open(content, action, {
      duration: duration,
      panelClass: ["custom-style"]
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }
}
