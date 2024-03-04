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

import { Component, Inject, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { CurrencyPipe, NgIf } from '@angular/common';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';
import { CarouselModule } from 'primeng/carousel';
import { User } from '@firebase/auth';
import { Auth, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { ObservablesService } from '../../shared/services/observables.service';
import { HomeProductCarouselComponent } from '../home-product-carousel/home-product-carousel.component';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'app-product-cart',
  templateUrl: './product-cart.component.html',
  styleUrls: ['./product-cart.component.scss'],
  standalone: true,
  imports: [
    NgIf,
    TruncatePipe,
    CurrencyPipe,
    CarouselModule,
    HomeProductCarouselComponent,
    MatDividerModule
  ]
})
export class ProductCartComponent {
  product!: any;
  productId!: any;
  categories: any = [
    {
      categoryTitle: "More like this",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: true,
      placeholder: true
    },
  ];
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;

  createdRecommendations: boolean = false;

  constructor(public _router: Router,
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) private data: any,
    public recommendationsService: RecommendationsService,
    public observablesService: ObservablesService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        if (!this.createdRecommendations) {
          this.createdRecommendations = true;
          this.recommendationsService.getViewItemRecommendationsDocumentId(
            "more-like-this",
            aUser!.uid,
            [this.productId]
          ).subscribe((res: any) => {
            this.recommendationsService.fetchRecommendationResults(res?.recommendations_doc_id).subscribe((recommendations: any) => {
              this.categories[0].products = recommendations;
              this.categories[0].placeholder = false;
            });
          });
        }

      }
    });
    if (this.data) {
      this.product = this.data;
    }
    else {
      this.navigateToHome()
    }

  }

  navigateToHome() {
    this.dialog.closeAll();
  }

  navigateToCart() {
    this.observablesService.setCartDisplay(true);
    this.observablesService.setProductDisplay(false);
    this.dialog.closeAll();
  }
  close(): void {
    this.dialog.closeAll()
  }

  onClickProduct(product: any) {
    this.observablesService.setProductDisplay(true);
    this.observablesService.setProductDescription(product);
    this.dialog.closeAll()
  }
}
