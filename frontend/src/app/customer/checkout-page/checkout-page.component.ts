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

import { CurrencyPipe, DatePipe, NgClass, NgFor, NgIf, UpperCasePipe } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output, inject } from '@angular/core';
import { FormGroup, FormControl, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { MatDividerModule } from '@angular/material/divider';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { Auth, user, User } from '@angular/fire/auth';
import { Subscription, async, of } from 'rxjs';
import { HomeProductCarouselComponent } from '../home-product-carousel/home-product-carousel.component';
import { CarouselModule } from 'primeng/carousel';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerInputEvent, MatDatepickerModule } from '@angular/material/datepicker';
import { MatRadioModule } from '@angular/material/radio';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';


@Component({
  selector: 'app-checkout-page',
  standalone: true,
  imports: [UpperCasePipe,
    CurrencyPipe,
    NgFor,
    MatDividerModule,
    NgIf,
    DatePipe,
    NgClass,
    ReactiveFormsModule,
    HomeProductCarouselComponent,
    CarouselModule,
    TruncatePipe,
    MatNativeDateModule,
    MatDatepickerModule,
    MatInputModule,
    MatFormFieldModule,
    MatRadioModule,
    FormsModule, MatSnackBarModule],
  templateUrl: './checkout-page.component.html',
  styleUrl: './checkout-page.component.css',
  providers: [DatePipe]
})
export class CheckoutPageComponent implements OnInit {
  @Input() products: any;
  totalPrice = 0;
  isHomeDelivery: boolean = false;
  pickUpInStore: boolean = false;
  today = new Date();
  purchaseStartDate: any;
  defaultPickUpTime: string = '6:00 PM - 7:00 PM';
  pickupTimeSlots: string[] = ['6:00 PM - 7:00 PM', '7:00 PM - 8:00 PM', '8:00 PM - 9:00 PM'];

  purchaseDeliveryForm = new FormGroup({
    firstName: new FormControl('John', [Validators.required]),
    lastName: new FormControl('Doe', [Validators.required]),
    streetAddress: new FormControl('124 W 8th St, Apt 2', [Validators.required]),
    streetAddress2: new FormControl(''),
    city: new FormControl('New York', [Validators.required]),
    zip: new FormControl('90000', [Validators.required]),
    emailQuote: new FormControl('')
  });
  purchaseEndDate!: Date;
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription!: Subscription;
  //docSubscription: Subscription;
  searchSubscription!: Subscription;
  userId = "";
  userEmail!: any;
  photoURL: any;
  categories: any = [
    {
      categoryTitle: "thinks you’d also love",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: true,
      placeholder: true
    },
  ];
  minDate!: Date;
  responsiveOptions!: { breakpoint: string; numVisible: number; numScroll: number; }[];
  isPickUpDateChange: boolean = false;
  isPickUpAddressChange: boolean = false;
  @Output() emptyProducts = new EventEmitter<string>();

  constructor(public recommendationsService: RecommendationsService, public datepipe: DatePipe, private snackBar: MatSnackBar) { }
  ngOnInit() {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user
      if (aUser) {
        console.log(aUser);
        this.userId = aUser.uid;
        this.userEmail = aUser.email;
        if (this.products.length > 0 && this.userId) {
          this.recommend();
        }
        if (aUser.photoURL) {
          this.photoURL = aUser.photoURL;
        }
      }
      else {
        this.photoURL = null;
      }
    });
    this.totalPrice = 0;
    let futureDate: Date = new Date();
    futureDate = new Date(this.today.setDate(this.today.getDate() + 2));
    this.purchaseEndDate = new Date(this.today.setDate(this.today.getDate() + 4));
    this.purchaseStartDate = futureDate;
    this.minDate = futureDate

    this.products!.map((product: any) => {
      this.totalPrice += product.price;
    });

    this.responsiveOptions = [
      {
        breakpoint: '1400px',
        numVisible: 4,
        numScroll: 1
      },

      {
        breakpoint: '1199px',
        numVisible: 2,
        numScroll: 1
      },
      {
        breakpoint: '991px',
        numVisible: 1,
        numScroll: 1
      },
      {
        breakpoint: '767px',
        numVisible: 1,
        numScroll: 1
      }
    ];
  }
  homeDelivery() {
    this.isHomeDelivery = !this.isHomeDelivery;
    this.pickUpInStore = false;
  }

  pickInStore() {
    this.pickUpInStore = !this.pickUpInStore;
    this.isHomeDelivery = false
  }
  continuePurchase() {
    let today = new Date();
    let latest_date = this.datepipe.transform(this.purchaseStartDate, 'YYYY-MM-dd');
    latest_date = latest_date + " " + this.defaultPickUpTime
    let obj = {}
    if (this.isHomeDelivery) {
      obj = {
        "order_date": this.datepipe.transform(today, 'YYYY-MM-dd'),
        "order_status": "Inititated",
        "order_items": this.products,
        "user_id": this.userId,
        "email": this.userEmail,
        "total_amount": this.totalPrice,
        "is_delivery": this.isHomeDelivery,
        "is_pickup": false,
        "pickup_datetime": ""

      }
    } else {
      obj = {
        "order_date": this.datepipe.transform(today, 'YYYY-MM-dd'),
        "order_status": "Inititated",
        "order_items": this.products,
        "user_id": this.userId,
        "email": this.userEmail,
        "total_amount": this.totalPrice,
        "is_delivery": false,
        "is_pickup": this.pickUpInStore,
        "pickup_datetime": latest_date
      }
    }
    this.recommendationsService.addOrder(obj).subscribe((res: any) => {
      this.products = [];
      this.totalPrice = 0
      this.emptyProducts.emit(this.products);
      this.showSnackbar("Order placed", 'Close', '4000')
    })
  }

  showSnackbar(content: any, action: any, duration: any) {
    let sb = this.snackBar.open(content, action, {
      duration: duration,
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }

  async recommend() {
    let productIds: string[] = [];
    for (var item of this.products) {
      productIds.push(String(item.id));
    }
    console.log(this.userId)
    await this.recommendationsService.getPurchaseRecommendationsDocumentId(
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
  changePickUpDate() {
    this.isPickUpDateChange = true;
  }
  changePickUpAddress() {
    this.isPickUpAddressChange = true;
  }
  addEvent(type: string, event: MatDatepickerInputEvent<Date>) {
    this.purchaseStartDate = event.value
  }
}
