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
import { environment } from '../../../environments/environment';
import { catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductService {

  constructor(private http: HttpClient) { }

  getProduct(productId: string) {
    let url = `${environment.apiURL}/p1/get-product/${productId}`;
    return this.http
      .get(url)
      .pipe(
        catchError(this.handleError)
      );
  }

  getProductSummary(productId: string) {
    let url = `${environment.apiURL}/p1/get-product-summary/${productId}`;
    return this.http
      .get(url)
      .pipe(
        catchError(this.handleError)
      );
  }

  compareProducts(products: any) {
    const reqBody =
    {
      "products": products
    }
    return this.http.post(`${environment.apiURL}/p1/compare-products`, reqBody, { responseType: 'text' });
  }


  getReviews(productId: string) {
    let url = `${environment.apiURL}/p1/get-reviews/${productId}`;
    return this.http
      .get(url)
      .pipe(
        catchError(this.handleError)
      );
  }

  getReviewsSummary(productId: string) {
    let url = `${environment.apiURL}/p1/get-reviews-summary/${productId}`;
    return this.http
      .get(url)
      .pipe(
        catchError(this.handleError)
      );
  }



  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error);
    } else {

    }

    return throwError(() => new Error(
      'Something bad happened; please try again later.'));
  }
}
