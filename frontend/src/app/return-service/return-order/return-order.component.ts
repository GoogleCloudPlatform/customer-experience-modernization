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

import { Component } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs';
import { FirebaseService } from '../../shared/services/firebase.service';
import { Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';
import { CarouselModule } from 'primeng/carousel';
import { OrderDetailsComponent } from '../order-details/order-details.component';
import { AlternativeItemsComponent } from '../alternative-items/alternative-items.component';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';

@Component({
  selector: 'app-return-order',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, NgIf, NgFor, CarouselModule, OrderDetailsComponent, AlternativeItemsComponent, ArchitectureComponent],
  templateUrl: './return-order.component.html',
  styleUrl: './return-order.component.css'
})
export class ReturnOrderComponent {
  architecture: string = "/assets/architectures/p7_uj_1.svg";
  public searchControl!: FormControl;
  public debounce: number = 400;
  showOrderDetails = false;
  userOrder: any;
  errorMessage!: string;
  documentId: any;
  returnItem: any;
  constructor(public firebase: FirebaseService, public router: Router) { }
  ngOnInit() {
    this.searchControl = new FormControl('');
    this.searchControl.valueChanges
      .pipe(debounceTime(this.debounce), distinctUntilChanged())
      .subscribe({
        next: (query: any) => {
          this.firebase.getUserOrdersById(query).subscribe({
            next: (res) => {
              if (res) {
                this.errorMessage = ''
                this.documentId = query;
                this.userOrder = res;
                let allItemsReturned = (this.userOrder.order_items.every((_item: any) => {
                  return _item.is_returned
                }));
                if (allItemsReturned) {
                  this.errorMessage = "All items under this order are already returned. Please enter order with valid return status."
                } else {
                  this.showOrderDetails = true
                }
              } else if (!res) {
                this.errorMessage = "Please enter valid order id";
              }
            },
            error: (error: any) => {                              //Error callback
              this.errorMessage = "Query cannot be completed. An error has occurred";
              this.showOrderDetails = false
              throw error;
            }
          })
        }, error: (error: any) => {                              //Error callback
          this.errorMessage = "Query cannot be completed. An error has occurred";
          this.showOrderDetails = false
          throw error;
        }
      });
  }

  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }

  displayReturnItem(userOrder: any) {
    this.returnItem = userOrder[0].order_items.filter((obj: any) => {
      // if (obj.returnReason !== "") {
      if (obj.isProductReturn) {
        return true;
      }
      return false;
    })
  }
}
