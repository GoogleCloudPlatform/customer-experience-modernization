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

import { Component, OnInit, inject } from '@angular/core';
import { ObservablesService } from '../../shared/services/observables.service';
import { NgFor } from '@angular/common';
import { CarouselModule } from 'primeng/carousel';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { MatButtonModule } from '@angular/material/button';
import { HomeProductCarouselComponent } from '../home-product-carousel/home-product-carousel.component';
import { PurchaseCompleteComponent } from '../purchase-complete/purchase-complete.component';
import { MatDialog } from '@angular/material/dialog';
import { FirebaseService } from '../../shared/services/firebase.service';
import { CheckoutPageComponent } from '../checkout-page/checkout-page.component';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-add-to-cart-details',
  templateUrl: './add-to-cart-details.component.html',
  styleUrl: './add-to-cart-details.component.scss',
  standalone: true,
  imports: [
    NgFor,
    CarouselModule,
    MatButtonModule,
    HomeProductCarouselComponent,
    PurchaseCompleteComponent,
    CheckoutPageComponent,
    RouterOutlet
  ]
})
export class AddToCartDetailsComponent implements OnInit {
  productDetails: any;
  products: any[] = [];
  showCartDetails: boolean = false
  key: string = 'item';
  cartDetails: any;
  totalPrice = 0;
  getData: any;
  showProductCount = 2;
  userId = "";
  categories: any = [
    {
      categoryTitle: "We also recommend",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: true,
      placeholder: true
    },
  ];
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  showCheckoutPage: boolean = false;

  constructor(
    public observablesService: ObservablesService,
    public recommendationsService: RecommendationsService,
    public dialog: MatDialog,
    public firebaseService: FirebaseService
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
      }
    });

    this.observablesService.addToCartProducts$.subscribe(async (addedProduct) => {
      this.products.push(addedProduct);
      localStorage.setItem('cart', JSON.stringify(this.products));
      await this.reloadCartInfo();
      let items: object[] = [];
      for (var product of this.products) {
        let item = {
          id: product.id,
          name: product.title,
          brand: "Cymbal Furniture",
          category: product.category,
          price: product.price,
          quantity: 1,
        };
        items.push(item)

      }

      this.firebaseService.analyticsLogEvent("view_cart", {
        value: this.totalPrice,
        currency: "USD",
        items: items
      });

    });


  }

  ngOnInit(): void {
    this.getData = localStorage.getItem('cart');
    if (this.getData) {
      this.products = JSON.parse(this.getData);
    } else {
      this.products = [];
    }

    this.reloadCartInfo();
  }

  async recommend() {
    let productIds: string[] = [];
    for (var item of this.products) {
      productIds.push(String(item.id));
    }
    this.recommendationsService.getViewItemRecommendationsDocumentId(
      "others-you-may-like",
      this.userId,
      // Get the id value of each product and make and array
      [productIds[productIds.length - 1]]
    ).subscribe((res: any) => {
      this.recommendationsService.fetchRecommendationResults(res?.recommendations_doc_id).subscribe((recommendations: any) => {
        this.categories[0].products = recommendations;
        this.categories[0].placeholder = false;
      });
    });
  }

  async reloadCartInfo() {
    this.totalPrice = 0;
    this.products.map((product) => {
      this.totalPrice += product.price;
    });

    if (this.products.length > 0) {
      this.showCartDetails = true;
      await this.recommend();
    }
    else {
      this.showCartDetails = false;
    }

  }
  emptyProductsOnCheckout(products:any){
    this.products = products;
    localStorage.setItem('cart', JSON.stringify(this.products));
  }
  removeProduct(product: any) {
    this.products.splice(this.products.findIndex(item => item.id === product.id), 1);
    localStorage.setItem('cart', JSON.stringify(this.products));
    this.reloadCartInfo()
  }

  purchase() {
    this.showCheckoutPage = true;
    // let productIds: string[] = [];
    // let items: object[] = [];
    // for (var product of this.products) {
    //   productIds.push(String(product.id));
    //   let item = {
    //     id: product.id,
    //     name: product.title,
    //     brand: "Cymbal Furniture",
    //     category: product.category,
    //     price: product.price,
    //     quantity: 1,
    //   };
    //   items.push(item)

    // }
    // this.recommendationsService.collectRecommendationsEvents("media-complete", this.userId, productIds, {
    //   "media_info": {
    //     "media_progress_duration": "90s",
    //     "media_progress_percentage": 1
    //   }
    // });

    // this.firebaseService.analyticsLogEvent("purchase", {
    //   transaction_id: self.crypto.randomUUID(),
    //   value: this.totalPrice,
    //   currency: "USD",
    //   items: items
    // });

    // this.products = []
    // localStorage.setItem('cart', JSON.stringify(this.products));
    // this.reloadCartInfo();

    // this.dialog.open(PurchaseCompleteComponent, {
    //   width: '300px', height: '300px'
    // });
  }
}

