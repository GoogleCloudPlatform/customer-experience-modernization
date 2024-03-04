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
import { Service } from '../../../shared/services/creator.service';
import { MatDividerModule } from '@angular/material/divider';
import { CarouselModule } from 'primeng/carousel';

@Component({
  selector: 'content-creator-service-preview',
  standalone: true,
  imports: [
    NgFor,
    MatDividerModule,
    CarouselModule,
  ],
  templateUrl: './service-preview.component.html',
  styleUrl: './service-preview.component.scss'
})
export class ContentCreatorServicePreviewComponent implements OnChanges {
  @Input()
  service!: Service;
  @Input()
  imageSrc!: string;
  imageDisplay: string = "";
  responsiveOptions = [
    {
      breakpoint: '2300px',
      numVisible: 2,
      numScroll: 1
    },

    {
      breakpoint: '1540px',
      numVisible: 1,
      numScroll: 1
    },

    {
      breakpoint: '1399px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '991px',
      numVisible: 3,
      numScroll: 1
    },
    {
      breakpoint: '767px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '576px',
      numVisible: 1,
      numScroll: 1
    }

  ];

  ngOnChanges(_changes: SimpleChanges): void {
    this.imageDisplay = this.imageSrc;
  }

  changeDisplay(src: string) {
    this.imageDisplay = src;
  }



}
