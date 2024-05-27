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

import { Component, Input } from '@angular/core';
import { CarouselModule } from 'primeng/carousel';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { Output, EventEmitter } from '@angular/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { Router } from '@angular/router';
import { UploadImageComponent } from '../upload-image/upload-image.component';

@Component({
  selector: 'app-order-details',
  standalone: true,
  imports: [CarouselModule, FormsModule, NgClass, MatCheckboxModule, UploadImageComponent],
  templateUrl: './order-details.component.html',
  styleUrl: './order-details.component.css'
})
export class OrderDetailsComponent {
  @Input()
  userOrder: any
  @Input()
  documentId: any;
  selectedItemforReturn: any;
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
  showNavigation: boolean = false;
  activateConfirm: boolean = false;
  disableSelect: boolean = false;
  updatedOrderReturnDetails: any;
  @Output() newItemEvent = new EventEmitter<string>();
  returnItem: any;
  constructor(public router: Router) { }
  ngOnInit() {
    this.showNavigation = this.userOrder.order_items.length > 3
  }

  selectProduct(checked: boolean, product: any) {
    if (checked) {
      console.log(checked);
      console.log(product)

      this.disableSelect = checked;
      this.selectedItemforReturn = product.id;
      this.activateConfirm = true;
      this.updatedOrderReturnDetails = [this.userOrder].map((obj: any) => {
        obj.order_items.map((obj: any) => {
          if (obj.id == product.id) {
            obj.isProductReturn = checked;
          }
          else {
            obj.isProductReturn = false;
          }
        })
        return obj;
      });
    }
  }

  confirmReturn() {
    this.displayReturnItem(this.userOrder)
  }

  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }

  displayReturnItem(userOrder: any) {
    console.log(userOrder)
    this.returnItem = userOrder.order_items.filter((obj: any) => {
      if (obj.isProductReturn) {
        return true;
      }
      return false;
    })
  }
}
