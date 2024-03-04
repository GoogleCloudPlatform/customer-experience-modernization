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

import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { Observable, catchError, throwError } from 'rxjs';

export interface Product {
  title: string;
  description: string;
  image_urls: string[];
  labels: string[];
  categories: string[];
  features: string[];
}

export interface Service {
  title: string;
  description: string;
  image_urls: string[];
  labels: string[];
  categories: string[];
  features: string[];
}


@Injectable({
  providedIn: 'root'
})
export class CreatorService {
  product: any;
  service: any;

  constructor(public http: HttpClient) { }

  generateImage(prompt: string, numberOfImages: number, negativePrompt: string = "") {
    const reqBody = {
      "prompt": prompt,
      "number_of_images": numberOfImages,
      "negative_prompt": negativePrompt
    }
    return this.http.post<any>(`${environment.apiURL}/p2/generate-image`, reqBody)
      .pipe(catchError(this.handleError));

  }

  editImage(prompt: string, baseImageName: string, maskImageName: "", numberOfImages: number, negativePrompt: string = "") {
    const reqBody = {
      "prompt": prompt,
      "base_image_name": baseImageName,
      "mask_iamge_name": maskImageName,
      "number_of_images": numberOfImages,
      "negative_prompt": negativePrompt
    }
    return this.http.post<any>(`${environment.apiURL}/p2/edit-image`, reqBody)
      .pipe(catchError(this.handleError));

  }

  generateTitleDescription(productCategories: string[], context: string) {
    const reqBody = {
      "product_categories": productCategories,
      "context": context
    }
    return this.http.post<any>(`${environment.apiURL}/p2/generate-title-description`, reqBody)
      .pipe(catchError(this.handleError));

  }

  detectProductCategories(imagesNames: string[]) {
    const reqBody = {
      "images_names": imagesNames,
    }
    return this.http.post<any>(`${environment.apiURL}/p2/detect-product-categories`, reqBody)
      .pipe(catchError(this.handleError));

  }

  saveProduct(userId: string, product: Product): Observable<HttpResponse<string>> {
    return this.http.post<string>(`${environment.apiURL}/p2/user-product/${userId}`, product, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  updateProduct(userId: string, productId: string, product: Product): Observable<HttpResponse<string>> {
    return this.http.put<string>(`${environment.apiURL}/p2/user-product/${userId}/${productId}`, product, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  deleteProduct(userId: string, productId: string): Observable<HttpResponse<string>> {
    return this.http.delete<string>(`${environment.apiURL}/p2/user-product/${userId}/${productId}`, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  saveService(userId: string, service: Service): Observable<HttpResponse<string>> {
    return this.http.post<string>(`${environment.apiURL}/p2/user-service/${userId}`, service, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  updateService(userId: string, serviceId: string, service: Service): Observable<HttpResponse<string>> {
    return this.http.put<string>(`${environment.apiURL}/p2/user-service/${userId}/${serviceId}`, service, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  deleteService(userId: string, serviceId: string): Observable<HttpResponse<string>> {
    return this.http.delete<string>(`${environment.apiURL}/p2/user-service/${userId}/${serviceId}`, { observe: "response" })
      .pipe(catchError(this.handleError));
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

}
