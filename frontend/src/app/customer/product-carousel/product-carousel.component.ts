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

import { Component, Input, inject } from '@angular/core';
import { ProductCartComponent } from '../product-cart/product-cart.component';
import { MatDialog } from '@angular/material/dialog';
import { ObservablesService } from '../../shared/services/observables.service';
import { CarouselModule } from 'primeng/carousel';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';
import { ProductService } from '../../shared/services/product.service';
import { User } from '@firebase/auth';
import { Auth, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { FirebaseService } from '../../shared/services/firebase.service';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-product-carousel',
  templateUrl: './product-carousel.component.html',
  styleUrls: ['./product-carousel.component.scss'],
  standalone: true,
  imports: [
    CarouselModule,
    MatCheckboxModule,
    TruncatePipe,
    MatProgressSpinnerModule,
  ]
})
export class ProductCarouselComponent {
  @Input()
  products!: any;
  responsiveOptions: any[] | undefined;
  expandMore = true;
  product: any;
  addToCartDetails: any = [];
  showClose: boolean = false;
  productId: any;
  showExpandedProduct: boolean = false;
  isChecked: boolean = false;
  showCompare: boolean = false;
  disableButtons: boolean = false;
  showClearCompare: boolean = false;
  compareResults: any[] = []
  htmlContent: any;

  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId = "";
  showSpinner: boolean = false;


  constructor(
    public observablesService: ObservablesService,
    public productService: ProductService,
    public dialog: MatDialog,
    public firebaseService: FirebaseService,
    public recommendationsService: RecommendationsService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
      }
    });
  }
  ngOnInit() {
    this.products.forEach((item: any) => (item.isChecked = false));
    this.responsiveOptions = [
      {
        breakpoint: '1199px',
        numVisible: 1,
        numScroll: 1
      },
      {
        breakpoint: '991px',
        numVisible: 2,
        numScroll: 1
      },
      {
        breakpoint: '767px',
        numVisible: 1,
        numScroll: 1
      }
    ];
  }

  displayExpandedProduct(product: any) {
    this.showExpandedProduct = true;
    this.product = product.snapshot;
    this.product.id = product?.id;
    this.showClose = true;
    this.productId = product?.id;
  }

  closeExpandedProduct() {
    this.showExpandedProduct = false
    this.expandMore = true;
    this.showClose = false;
  }

  addToCart(): void {
    this.observablesService.setAddToCartDetails(this.product);

    this.recommendationsService.collectRecommendationsEvents("media-play", this.userId, [this.productId], {
      "media_info": {
        "media_progress_duration": "0s",
        "media_progress_percentage": 0
      }
    });

    let item = {
      id: this.product.id,
      name: this.product.title,
      brand: "Cymbal Furniture",
      category: this.product.category,
      price: this.product.price,
      quantity: 1,
    };


    this.firebaseService.analyticsLogEvent("add_to_cart", {
      value: this.product.price,
      currency: "USD",
      items: [item]
    });


    this.dialog.open(ProductCartComponent, {
      data: this.product,
      width: '100%', disableClose: true, height: '80%', maxWidth:'98%'
    });

  }

  selectProduct(product: any) {
    let selectedProduct = this.products.find((p: any) => p.id == product.id)
    selectedProduct.isChecked = !selectedProduct.isChecked;
    this.checkForCompare();
  }

  checkForCompare() {
    var selectedCount = this.products.filter((item: any) => item?.isChecked === true).length;
    this.compareResults = this.products.filter((item: any) => item?.isChecked === true);
    this.showCompare = (selectedCount == 2) ? true : false;
    this.disableButtons = (selectedCount == 2) ? true : false;
  }

  compareProducts() {
    this.showSpinner = true;
    const products = this.compareResults.map((item: any) => JSON.stringify(item?.snapshot))
    this.productService.compareProducts(products)
      .subscribe(res => {
        this.showSpinner = false;
        this.htmlContent = res.replace('<table', '<table class="table table-hover"')
      })
    this.showClearCompare = this.showCompare;
    this.showCompare = false;

  }

  clearCompare() {
    this.showClearCompare = false;
    this.products.forEach((item: any) => (item.isChecked = false));
    this.checkForCompare();
    this.htmlContent = ""
  }

  seeMore() {
    this.observablesService.setProductDisplay(true);
    this.observablesService.setProductDescription(this.product);
  }

} 
