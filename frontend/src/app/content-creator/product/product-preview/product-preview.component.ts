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

import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { NgFor } from '@angular/common';
import { Product } from '../../../shared/services/creator.service';
import { MatDividerModule } from '@angular/material/divider';
import { CarouselModule } from 'primeng/carousel';

@Component({
  selector: 'content-creator-product-preview',
  standalone: true,
  imports: [
    NgFor,
    MatDividerModule,
    CarouselModule,
  ],
  templateUrl: './product-preview.component.html',
  styleUrl: './product-preview.component.scss'
})
export class ContentCreatorProductPreviewComponent implements OnChanges {

  @Input()
  product!: Product;
  @Input()
  imageSrc!: string;
  imageDisplay: string = "";
  responsiveOptions = [
    {
      breakpoint: '1024px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '768px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '560px',
      numVisible: 1,
      numScroll: 1
    }
  ];
  ngOnChanges(_changes: SimpleChanges): void {
    this.imageDisplay = this.imageSrc;
    console.log('product', this.product)
  }

  changeDisplay(src: string) {
    this.imageDisplay = src;
  }

}
