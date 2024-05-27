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

import { NgClass } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { CarouselModule } from 'primeng/carousel';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SafePipe } from '../../shared/pipes/safe.pipe';
import { Router } from '@angular/router';
import { FirebaseService } from '../../shared/services/firebase.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ReturnService } from '../../shared/services/return-service.service';

@Component({
  selector: 'app-alternative-items',
  standalone: true,
  imports: [NgClass, CarouselModule, FormsModule, ReactiveFormsModule, SafePipe, MatProgressSpinnerModule],
  templateUrl: './alternative-items.component.html',
  styleUrl: './alternative-items.component.css'
})
export class AlternativeItemsComponent {
  @Input() returnItem: any;
  @Input()
  documentId!: string;
  @Input() userOrder: any
  recommendations: any[] = [];
  responsiveOptions = [
    {
      breakpoint: '1024px',
      numVisible: 3,
      numScroll: 3
    },
    {
      breakpoint: '768px',
      numVisible: 2,
      numScroll: 2
    },
    {
      breakpoint: '560px',
      numVisible: 1,
      numScroll: 1
    }
  ];
  return_reason = ['Found Better Price', 'Defective', 'No Longer Needed'];
  isAlternateProductSelected: boolean = false;
  alternateProductSelectedDetails: any;
  showComparison: boolean = false;
  validationInprogress: boolean = false;
  showRefundSection: boolean = false;
  isAlternateProductSelectedId: any;
  differenceAmount!: string;
  storeReturnItemImageInOrders: string = '';
  isRecommendationsLoading: boolean = false;
  showNavigation: boolean = false;
  updatedOrderReturnDetails: any[] = [];
  constructor(public recommendationsService: RecommendationsService, public router: Router, public returnService: ReturnService, public firebaseService: FirebaseService) { }
  ngOnInit() {
    console.log("returnItem", this.returnItem)
    this.isRecommendationsLoading = true;
    let imageUrl: string = this.returnItem.image
    imageUrl = imageUrl.replace("https://storage.googleapis.com/", '')
    this.returnService.searchSimilar(imageUrl, this.returnItem.categories[0]).subscribe({
      next: (res: any) => {
        this.recommendations = res.results;
        this.isRecommendationsLoading = false;
        this.showNavigation = this.recommendations.length > 3
      },
      error: (error: any) => {
        this.isRecommendationsLoading = false
        throw error;
      },
    })
  }

  next() {
    if (this.isAlternateProductSelectedId) {
      this.showComparison = true;
    } else {
      this.refundBtn();
    }
  }

  selectAlternateProduct(product: any) {
    this.isAlternateProductSelectedId = product.id
    this.recommendations = this.recommendations.map((obj: any) => {
      if (obj.id == product.id) {
        obj.isAlternateProductSelected = true;
      }
      else {
        obj.isAlternateProductSelected = false;
      }
      return obj;
    });
    this.alternateProductSelectedDetails = product
  }

  nextBtn() {
    this.showRefundSection = true;
    this.differenceAmount = (this.returnItem.price - this.alternateProductSelectedDetails.snapshot.price).toPrecision(4)
  }

  refundBtn() {
    console.log(this.returnItem)
    this.returnItem.is_returned = true;
    this.returnItem.return_metadata.return_status = 'completed'
    delete this.returnItem['isProductReturn'];

    this.userOrder.order_items.forEach((element: any, index: any) => {
      if (element.id === this.returnItem.id) {
        this.userOrder.order_items.splice(index, 1, this.returnItem);
      }
    });
    this.returnService.updateOrders(this.userOrder, this.documentId).subscribe((res) => {
      console.log(res)
      if (res) {
        this.router.navigateByUrl(`/return-service/refund-item/valid`)
      }
    })
  }

  async onReasonChange(reason: any, product: any) {
    if (reason) {
      this.updatedOrderReturnDetails = [this.userOrder].map((obj: any) => {
        obj.order_items.map((obj: any) => {
          if (obj.id == product.id) {
            obj.return_metadata = {
              "return_type": reason
            }
          }
        })
        return obj;
      });
    }
  }

  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }

}
