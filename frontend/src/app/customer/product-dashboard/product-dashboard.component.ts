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

import { Component, inject } from '@angular/core';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { ObservablesService } from '../../shared/services/observables.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { Dialog } from '@angular/cdk/dialog';
import { NgIf } from '@angular/common';
import { HomeProductCarouselComponent } from '../home-product-carousel/home-product-carousel.component';

@Component({
  selector: 'app-product-dashboard',
  templateUrl: './product-dashboard.component.html',
  styleUrls: ['./product-dashboard.component.scss'],
  standalone: true,
  imports: [
    NgIf,
    HomeProductCarouselComponent
  ]
})
export class ProductDashboardComponent {
  recommendationDocId: any;
  currentLoggedInUser: User | null = null;
  categories: any = [
    {
      categoryTitle: "New & Featured",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: false,
      placeholder: true
    },
    {
      categoryTitle: "Trending",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: false,
      placeholder: true

    },
    {
      categoryTitle: "Recommended for you",
      products: Array(8).fill({ title: "", categories: "", price: "" }),
      assistant: true,
      placeholder: true
    },
  ];
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  createdRecommendations: boolean = false;

  constructor(public recommendationService: RecommendationsService, public observablesService: ObservablesService, public dialog: Dialog) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      this.currentLoggedInUser = aUser;
      if (aUser) {

        if (!this.createdRecommendations) {
          this.createdRecommendations = true;
          this.getRecommendations();
        }
      }
    })
  }

  getRecommendations() {
    this.recommendationService.getRecommendationsDocumentId("new-and-featured", "view-home-page", this.currentLoggedInUser!.uid).subscribe((res: any) => {
      this.recommendationDocId = res?.recommendations_doc_id;
      this.recommendationService.fetchRecommendationResults(this.recommendationDocId).subscribe((res: any) => {
        this.categories[0].products = res;
        this.categories[0].placeholder = false;
      });
    });

    // Trending
    this.recommendationService.getRecommendationsDocumentId("most-popular-items", "view-home-page", this.currentLoggedInUser!.uid).subscribe((res: any) => {
      this.recommendationDocId = res?.recommendations_doc_id;
      this.recommendationService.fetchRecommendationResults(this.recommendationDocId).subscribe((res: any) => {
        this.categories[1].products = res;
        this.categories[1].placeholder = false;

      });
    });

    // Recommended-for-you
    this.recommendationService.getRecommendationsDocumentId("recommended-for-you", "view-home-page", this.currentLoggedInUser!.uid).subscribe((res: any) => {
      this.recommendationDocId = res?.recommendations_doc_id;
      this.recommendationService.fetchRecommendationResults(this.recommendationDocId).subscribe((res: any) => {
        this.categories[2].products = res;
        this.categories[2].placeholder = false;

      });
    });

  }

}
