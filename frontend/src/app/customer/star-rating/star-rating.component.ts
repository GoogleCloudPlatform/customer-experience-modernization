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

import { Component, Input, OnInit } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'customer-star-rating',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    MatIconModule],
  templateUrl: './star-rating.component.html',
  styleUrl: './star-rating.component.scss'
})
export class StarRatingComponent implements OnInit {
  @Input()
  stars!: number;
  filledStars: number[] = [];
  halfStar: boolean = false;
  emptyStars: number[] = [];

  constructor() {
  }

  ngOnInit(): void {
    this.filledStars = Array(Math.floor(this.stars));
    this.halfStar = Math.round(this.stars % 1) > 0;
    this.emptyStars = Array(5 - this.filledStars.length - (this.halfStar ? 1 : 0));
  }

}
