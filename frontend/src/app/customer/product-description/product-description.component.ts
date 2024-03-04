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

import { AfterViewInit, Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { ObservablesService } from '../../shared/services/observables.service';
import { CurrencyPipe, NgFor } from '@angular/common';
import { MatDividerModule } from '@angular/material/divider';
import { CarouselModule } from 'primeng/carousel';
import { MatTabsModule } from '@angular/material/tabs';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { ProductCartComponent } from '../product-cart/product-cart.component';
import { MAT_DIALOG_DEFAULT_OPTIONS, MatDialog } from '@angular/material/dialog';
import { CustomerHomeFooterComponent } from '../customer-home-footer/customer-home-footer.component';
import { MatButtonModule } from '@angular/material/button';
import { HomeProductCarouselComponent } from '../home-product-carousel/home-product-carousel.component';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { StarRatingComponent } from '../star-rating/star-rating.component';
import { ProductService } from '../../shared/services/product.service';
import { marked } from 'marked';
import { FirebaseService } from '../../shared/services/firebase.service';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-product-description',
  templateUrl: './product-description.component.html',
  styleUrl: './product-description.component.scss',
  standalone: true,
  imports: [
    CurrencyPipe,
    MatDividerModule,
    NgFor,
    CarouselModule,
    MatTabsModule,
    CustomerHomeFooterComponent,
    MatButtonModule,
    HomeProductCarouselComponent,
    MatListModule,
    MatIconModule,
    StarRatingComponent,
    MatPaginatorModule
  ]
})
export class ProductDescriptionComponent implements OnInit, AfterViewInit {
  @ViewChild("mainContent")
  private mainContentDiv!: ElementRef<null | HTMLElement>;
  product!: any;
  productId!: any;
  productReviews!: any;
  userId = "";
  reviewsSummary: string = "Loading...";
  productSummary: string = "Loading...";
  starsAverage!: number;
  responsiveOptions: any[] | undefined;
  /** Based on the screen size, switch from standard to one column per row */
  cardLayout = {
    columns: 4,
    miniCard: { cols: 1, rows: 1 },
    table: { cols: 4, rows: 4 },
  }
  categories: any = [
    {
      categoryTitle: "More like this",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      placeholder: true,
      assistant: true
    },
  ];

  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;

  createdRecommendations: boolean = false;
  pageIndexKB = 0;
  pageSizeKB = 3;
  constructor(
    public observablesService: ObservablesService,
    public recommendationsService: RecommendationsService,
    public dialog: MatDialog,
    public productService: ProductService,
    public firebaseService: FirebaseService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
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
  }

  ngOnInit() {
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

    this.observablesService.getProductDescription().subscribe(product => {
      this.product = product;
      this.productId = String(product.id);
      this.ngAfterViewInit();
      this.productService.getReviews(this.productId).subscribe((res: any) => {
        this.productReviews = res.reviews;
        this.starsAverage = res.reviews.reduce((sum: number, current: any) => sum + current.stars, 0) / this.productReviews.length;
      })
      this.productService.getReviewsSummary(this.productId).subscribe((res: any) => {
        this.reviewsSummary = String(marked.parse(res.reviews_summary));
      });
      this.productService.getProductSummary(this.productId).subscribe((res: any) => {
        this.productSummary = String(marked.parse(res.product_summary));
      });
      this.firebaseService.analyticsLogEvent("select_content", { content_type: "product", content_id: this.productId });
    });
  }
  ngAfterViewInit() {
    this.mainContentDiv!?.nativeElement?.scrollIntoView({
      behavior: "smooth",
      block: "start",
      inline: "nearest"
    });
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
      width: '100%', disableClose: true, height: '80%' , maxWidth:'98%'
    });
  }

  handlePageEventKB(e: PageEvent) {
    this.pageIndexKB = e.pageIndex;
    this.pageSizeKB = e.pageSize;
  }

  slicedProductReviews() {
    return this.productReviews?.slice(Math.min(this.pageIndexKB * this.pageSizeKB, this.productReviews.length), Math.min((this.pageIndexKB + 1) * this.pageSizeKB, this.productReviews.length))
  }
}
