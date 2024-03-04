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
import { ObservablesService } from '../../shared/services/observables.service';
import { MatDialog } from '@angular/material/dialog';
import { CarouselModule } from 'primeng/carousel';
import { MatDividerModule } from '@angular/material/divider';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';

@Component({
  selector: 'app-home-product-carousel',
  templateUrl: './home-product-carousel.component.html',
  styleUrls: ['./home-product-carousel.component.scss'],
  standalone: true,
  imports: [
    CarouselModule,
    MatDividerModule,
    TruncatePipe
  ]
})
export class HomeProductCarouselComponent {

  @Input()
  categories!: any;
  responsiveOptions: any[] | undefined;
  expandMore = true;
  expandedProductDetails: any;
  addToCartDatils: any = [];
  showClose: boolean = false;
  expandedProductId: any;
  showExpandedProduct: boolean = false;
  constructor(public observablesService: ObservablesService,
    public dialog: MatDialog) {
  }
  ngOnInit() {
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

  displayExpandedProduct(product: any) {
    //this.expandMore = !this.expandMore;
    this.showExpandedProduct = true;
    this.expandedProductDetails = product;
    this.showClose = true;
    this.expandedProductId = product?.id;
  }

  closeExpandedProduct(product: any) {
    this.showExpandedProduct = false
    this.expandedProductDetails = product;
    this.expandedProductId = product?.id;
    this.expandMore = true;
    this.showClose = false;
  }
  onClickProduct(product: any) {
    this.observablesService.setProductDisplay(true);
    this.observablesService.setProductDescription(product);
    this.dialog.closeAll()
  }
}
