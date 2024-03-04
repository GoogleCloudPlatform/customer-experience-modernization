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
import { Observable, ReplaySubject, Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ObservablesService {

    constructor() { }

    private userDetails = new ReplaySubject<any>(1);
    userDetails$: Observable<any> = this.userDetails.asObservable();

    sendUserDetails(message: string) {
        this.userDetails.next(message);
    }

    getUserDetails(): Observable<any> {
        return this.userDetails$;
    }

    private loading = new ReplaySubject<any>(1);
    loading$: Observable<any> = this.loading.asObservable();
    private updatedDocumentID = new ReplaySubject<any>(1);
    updatedDocumentID$: Observable<any> = this.updatedDocumentID.asObservable();
    private addToCartProducts = new Subject<any>();
    addToCartProducts$: Observable<any> = this.addToCartProducts.asObservable();

    private productDisplay = new ReplaySubject<any>(1);
    productDisplay$: Observable<any> = this.productDisplay.asObservable();

    private cartDisplay = new ReplaySubject<any>(1);
    cartDisplay$: Observable<any> = this.cartDisplay.asObservable();


    private productDescription = new ReplaySubject<any>(1);
    productDescription$: Observable<any> = this.productDescription.asObservable();


    private productDetails = new ReplaySubject<any>(1);
    productDetails$: Observable<any> = this.productDetails.asObservable();

    setLoading(message: any) {
        this.loading.next(message);
    }

    getLoading(): Observable<any> {
        return this.loading$;
    }

    sendUpdatedDocumentID(message: any) {
        this.updatedDocumentID.next(message);
    }

    getupdatedDocumentID(): Observable<any> {
        return this.updatedDocumentID$;
    }
    setAddToCartDetails(message: any) {
        this.addToCartProducts.next(message);
    }

    getAddToCartDetails(): Observable<any> {
        return this.addToCartProducts$;
    }

    setProductDisplay(message: any) {
        this.productDisplay.next(message);
    }

    getProductDisplay(): Observable<any> {
        return this.productDisplay$;
    }

    setCartDisplay(message: any) {
        this.cartDisplay.next(message);
    }

    getCartDisplay(): Observable<any> {
        return this.cartDisplay$;
    }


    setProductDescription(message: any) {
        this.productDescription.next(message);
    }

    getProductDescription(): Observable<any> {
        return this.productDescription;
    }



    setProductDetails(message: any) {
        this.productDetails.next(message);
    }

    getProductDetails(): Observable<any> {
        return this.productDetails$;
    }

}
