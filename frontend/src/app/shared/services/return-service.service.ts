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

import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/internal/operators/catchError';

@Injectable({
  providedIn: 'root'
})
export class ReturnService {

  constructor(private http: HttpClient) { }

  getYYYYMMDD(date: Date) {
    var today = new Date(date);
    var dd = today.getDate();
    var mm = today.getMonth() + 1;
    var yyyy = today.getFullYear();
    var time = today.toLocaleTimeString()
    let res
    if (dd < 10 && mm < 10)
      res = yyyy + '/' + '0' + mm + '/' + '0' + dd + ' ' + time;
    else if (mm < 10)
      res = yyyy + '/' + '0' + mm + '/' + dd + ' ' + time;
    else if (dd < 10)
      res = yyyy + '/' + mm + '/' + '0' + dd + ' ' + time;
    console.log(res)
    return res;
  }
  returnValidation(product_url: string, return_image: any, return_video_url: any) {
    const reqBody = {
      "product_url": product_url,
      "return_image": return_image,
      "return_video_url": return_video_url
    }
    return this.http.post<any>(`https://csm-dev-42fk6qqj5a-uc.a.run.app/p7/return-validation`, reqBody)
      .pipe(catchError(this.handleError));

  }

  searchSimilar(return_image: any, category: string) {
    const reqBody = {
      "image": return_image,
      "query": category
    }
    return this.http.post<any>(`https://csm-dev-42fk6qqj5a-uc.a.run.app/p7/search-similar`, reqBody)

  }

  updateOrders(data: any, order_Id: string,) {
    return this.http.post(`https://csm-dev-42fk6qqj5a-uc.a.run.app/p7/order-update/${order_Id}`, data).pipe(catchError(this.handleError));
  }
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      console.error('An error occurred:', error.error);
    } else {
      console.error('An error occurred:', error.error);
    }
    return throwError(() => new Error(
      'Something bad happened; please try again later.'));
  }
}
