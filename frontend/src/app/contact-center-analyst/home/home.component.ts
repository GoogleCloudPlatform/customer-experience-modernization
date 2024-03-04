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
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule, MatListOption } from '@angular/material/list';
import { ContactCenterAnalystService, Conversation, Review, GeneratedInsights, Customer, CustomerInfo, Entity, UserJourney } from '../../shared/services/contact-center-analyst.service';
import { Observable, firstValueFrom } from 'rxjs';
import { marked } from 'marked';
import { KeyValuePipe, NgClass, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatRadioModule } from '@angular/material/radio';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';
import { environment } from '../../../environments/environment';
export interface Product {
  title: string;
  description: string;
  image_urls: string[];
  labels: string[];
  categories: string[];
  features: string[];
}
@Component({
  selector: 'contact-center-analyst-home',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    NgClass,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatListModule,
    MatProgressSpinnerModule,
    MatRadioModule,
    MatTabsModule,
    MatToolbarModule,
    FormsModule,
    ReactiveFormsModule,
    KeyValuePipe,
    TitleCasePipe,
    UserPhotoComponent,
    MatTableModule,
    MatCheckboxModule,
    ArchitectureComponent,
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class ContactCenterAnalystHomeComponent {
  genAIforMktURL = environment.genAIForMktURL;
  contactChannelCtrl = new FormControl<UserJourney>("conversations");
  customerIdCtrl = new FormControl<string>("");
  similarQuestionCtrl = new FormControl<string>("");
  followUpQuestionCtrl = new FormControl<string>("");
  customerInfo: CustomerInfo | undefined;
  customerConversations: Conversation[] = [];
  customerReviews: Review[] = [];
  dataSource = new MatTableDataSource(this.customerConversations);
  dataSourceReview = new MatTableDataSource(this.customerReviews);

  extractedEntities: Entity[] = [];
  extractedPendingTasksHTML = "";
  generatedInsightsHTML = "";
  generatedNextBestActionHTML = "";
  generatedSummaryHTML = "";
  selectedConversationHTML: string | null = null;
  insightsLoading = false;

  searchedSummary: string = "";
  searchLoading = false;
  searchInsightsLoading = false;

  similarConversations: Conversation[] = [];
  searchedConversations: Conversation[] = [];
  dataSourceSearchConvesation = new MatTableDataSource(this.searchedConversations);
  dataSourceSimilarConvesation = new MatTableDataSource(this.similarConversations);

  searchConversationsId: string = "";
  selectedConversations: any = [];
  selectedConversationsReview: any = [];
  selectedReviewData: any = [];
  selectedConversationsSearch: any = [];
  selectedConversationsSimilarSearch: any = [];
  similarReviews: Review[] = [];
  searchedReviews: Review[] = [];
  selectedsimilarSearchReviewData: any = [];
  dataSourceSearchSimilarReviews = new MatTableDataSource(this.similarReviews);
  dataSourcesearchedReviews = new MatTableDataSource(this.searchedReviews);
  searchReviewsId: string = "";
  userId = "";
  disableButton: boolean = true
  extractedEntitiesSearch: Entity[] = [];
  extractedPendingTasksSearchHTML = "";
  generatedInsightsSearchHTML = "";
  generatedNextBestActionSearchHTML = "";
  generatedSummarySearchHTML = "";
  selectedConversationSearchHTML: string | null = null;
  displayedColumns: string[] = [
    "select",
    "conversation",
    "category",
    "sentiment",
    "rating"
  ];

  architecture: string = "/assets/architectures/p5_uj_1.svg";


  constructor(
    private contactCenterAnalystService: ContactCenterAnalystService
  ) { }

  async getCustomerInfo() {
    const customer: Customer = await firstValueFrom(this.contactCenterAnalystService.getCustomerInfo(this.customerIdCtrl.value || "") as Observable<Customer>)

    this.customerInfo = customer.customer_info;
    this.customerConversations = customer.conversations;
    this.dataSource = new MatTableDataSource(this.customerConversations);
    console.log('dataSource', this.dataSource)
    console.log('customerConversations', this.customerConversations)
    this.customerReviews = customer.reviews;
    this.dataSourceReview = new MatTableDataSource(this.customerReviews);



  }

  updateInsights(generatedInsights: GeneratedInsights, isCustomer: boolean) {
    const key = 'name';
    const uniqueEntities = [...new Map(generatedInsights.entities.map(item => [item[key].replaceAll('*', ''), item])).values()];
    const extractedEntities = uniqueEntities.filter((entity) => entity.name.length > 1).sort((a: Entity, b: Entity) => {
      if (a.entity_type == "OTHER") {
        return 1;
      } else if (b.entity_type == "OTHER") {
        return -1;

      } else {
        if (a.entity_type < b.entity_type) {
          return -1;
        }
        if (a.entity_type > b.entity_type) {
          return 1;
        }

        // names must be equal
        return 0;
      }
    });
    if (isCustomer) {
      this.extractedEntities = extractedEntities;
      this.extractedPendingTasksHTML = String(marked.parse(generatedInsights.pending_tasks));
      this.generatedInsightsHTML = String(marked.parse(generatedInsights.insights));
      this.generatedNextBestActionHTML = String(marked.parse(generatedInsights.next_best_action));
      this.generatedSummaryHTML = String(marked.parse(generatedInsights.summary));
      this.insightsLoading = false;
    }
    else {
      this.extractedEntitiesSearch = extractedEntities;
      this.extractedPendingTasksSearchHTML = String(marked.parse(generatedInsights.pending_tasks));
      this.generatedInsightsSearchHTML = String(marked.parse(generatedInsights.insights));
      this.generatedNextBestActionSearchHTML = String(marked.parse(generatedInsights.next_best_action));
      this.generatedSummarySearchHTML = String(marked.parse(generatedInsights.summary));
      this.searchInsightsLoading = false;
    }

  }

  async generateConversationsInsights(conversations: MatListOption[], isCustomer: boolean = true) {
    this.clearInsights(isCustomer);
    if (isCustomer) {
      this.insightsLoading = true;
    } else {
      this.searchInsightsLoading = true;
    }
    if (conversations.length == 1) {
      if (isCustomer) {
        this.selectedConversationHTML = String(marked.parse(conversations[0].value.conversation));
      } else {
        this.selectedConversationSearchHTML = String(marked.parse(conversations[0].value.conversation));
      }
    }
    else {
      if (isCustomer) {
        this.selectedConversationHTML = null;
      } else {
        this.selectedConversationSearchHTML = null;
      }
    }
    const generatedInsights: GeneratedInsights = await firstValueFrom(
      this.contactCenterAnalystService.generateConversationsInsights(
        conversations.map((conversation: MatListOption) => conversation.value)
      ) as Observable<GeneratedInsights>
    );
    this.updateInsights(generatedInsights, isCustomer);
  }

  clearInsights(isCustomer: boolean) {
    if (isCustomer) {
      this.generatedInsightsHTML = "";
      this.extractedEntities = [];
      this.extractedPendingTasksHTML = "";
      this.generatedNextBestActionHTML = "";
      this.generatedSummaryHTML = "";
      this.selectedConversationHTML = null;
    } else {
      this.generatedInsightsSearchHTML = "";
      this.extractedEntitiesSearch = [];
      this.extractedPendingTasksSearchHTML = "";
      this.generatedNextBestActionSearchHTML = "";
      this.generatedSummarySearchHTML = "";
      this.selectedConversationSearchHTML = null;

    }
  }

  async generateReviewsInsights(reviews: MatListOption[], isCustomer: boolean = true) {
    this.clearInsights(isCustomer);
    if (isCustomer) {
      this.insightsLoading = true;
    } else {
      this.searchInsightsLoading = true;
    }
    const generatedInsights: GeneratedInsights = await firstValueFrom(
      this.contactCenterAnalystService.generateReviewsInsights(
        //reviews.map((review: MatListOption) => review.value)
        reviews.map((review: any) => review)
      ) as Observable<GeneratedInsights>
    )
    this.updateInsights(generatedInsights, isCustomer);
  }

  async search(followup: boolean) {
    this.clearInsights(false);
    this.searchedSummary = "";
    this.searchLoading = true;
    const contactChannel = this.contactChannelCtrl.value;
    let query = this.followUpQuestionCtrl.value;
    this.similarConversations = [];
    this.similarReviews = [];
    this.searchedConversations = [];
    this.searchedReviews = [];


    if (!followup) {
      query = this.similarQuestionCtrl.value;
      this.searchReviewsId = "";
      this.searchConversationsId = "";
    }
    this.similarQuestionCtrl.setValue(query);
    this.followUpQuestionCtrl.setValue("");
    if (contactChannel == "conversations") {
      this.searchReviewsId = "";
      firstValueFrom(
        this.contactCenterAnalystService.searchConversations(
          query || "", this.userId, this.searchConversationsId) as Observable<any>
      ).then((res) => {
        this.searchedConversations = res.responses.search_results;

        this.dataSourceSearchConvesation = new MatTableDataSource(this.searchedConversations);
        this.searchedSummary = res.responses.summary;
        this.searchConversationsId = res.conversation_id;
        this.searchLoading = false;

      })
    } else {
      this.searchConversationsId = "";

      firstValueFrom(this.contactCenterAnalystService.searchReviews(
        query || "", this.userId, this.searchReviewsId) as Observable<any>
      ).then((res) => {
        this.searchedReviews = res.responses.search_results;
        this.dataSourcesearchedReviews = new MatTableDataSource(this.searchedReviews);
        this.searchedSummary = res.responses.summary;
        this.searchReviewsId = res.conversation_id;
        this.searchLoading = false;
      });


    }
  }

  async searchSimilarConversations(conversations: any) {
    const conversation: Conversation = conversations[0];
    this.similarConversations = await firstValueFrom(this.contactCenterAnalystService.vectorFindSimilar(
      conversation.conversation || "", "conversations") as Observable<any>).then((res) => res.similar_vectors);
    this.dataSourceSimilarConvesation = new MatTableDataSource(this.similarConversations);
  }

  async searchSimilarReviews(reviews: any) {
    const review: Review = reviews[0];
    this.similarReviews = await firstValueFrom(this.contactCenterAnalystService.vectorFindSimilar(
      review.review || "", "reviews") as Observable<any>).then((res) => res.similar_vectors);
    this.dataSourceSearchSimilarReviews = new MatTableDataSource(this.similarReviews);

  }

  onSelection(i: any, product: any, checked: any) {
    console.log(i);
    console.log(product);
    console.log(checked)
    if (checked) {
      this.selectedConversations.push(product);
    } else {
      this.selectedConversations = this.selectedConversations.filter((res: any) => res.id != product.id)
    }
  }
  onSelectionSearchReview(i: any, product: any, checked: any) {
    console.log(i);
    console.log(product);
    console.log(checked)
    if (checked) {
      this.selectedReviewData.push(product);
    } else {
      this.selectedReviewData = this.selectedReviewData.filter((res: any) => res.id != product.id)
    }
  }
  onSelectionSimilarSearchReview(i: any, product: any, checked: any) {
    console.log(i);
    console.log(product);
    console.log(checked)
    if (checked) {
      this.selectedsimilarSearchReviewData.push(product);
    } else {
      this.selectedsimilarSearchReviewData = this.selectedsimilarSearchReviewData.filter((res: any) => res.id != product.id)
    }
  }
  onSelectionReview(i: any, product: any, checked: any) {
    console.log(i);
    console.log(product);
    console.log(checked)
    if (checked) {
      this.selectedConversationsReview.push(product);
    } else {
      this.selectedConversationsReview = this.selectedConversationsReview.filter((res: any) => res.id != product.id)
    }
  }

  onSelectionSearchConversation(i: any, product: any, checked: any) {
    console.log(i);
    console.log(product);
    console.log(checked)
    if (product.length > 0) {
      this.disableButton = false
    }
    if (checked) {
      this.selectedConversationsSearch.push(product);
    } else {
      this.selectedConversationsSearch = this.selectedConversationsSearch.filter((res: any) => res.id != product.id)
    }
  }

  // onSelectionSimilarSearchConversation(i: any, product: any, checked: any){
  //   console.log(i);
  //   console.log(product);
  //   console.log(checked)
  //   if (checked) {
  //     this.selectedConversationsSimilarSearch.push(product);
  //     } else {
  //    this.selectedConversationsSimilarSearch = this.selectedConversationsSimilarSearch.filter((res: any) => res.title != product.title)
  //   }
  // }

  async clickGenrateInsightConversation(conversations: any, isCustomer: boolean = true) {
    this.clearInsights(isCustomer);
    if (isCustomer) {
      this.insightsLoading = true;
    } else {
      this.searchInsightsLoading = true;
    }
    if (conversations.length == 1) {
      if (isCustomer) {
        this.selectedConversationHTML = String(marked.parse(conversations[0].conversation));
      } else {
        this.selectedConversationSearchHTML = String(marked.parse(conversations[0].conversation));
      }
    }
    else {
      if (isCustomer) {
        this.selectedConversationHTML = null;
      } else {
        this.selectedConversationSearchHTML = null;
      }
    }
    const generatedInsights: GeneratedInsights = await firstValueFrom(
      this.contactCenterAnalystService.generateConversationsInsights(
        conversations.map((conversation: any) => conversation)
      ) as Observable<GeneratedInsights>
    );
    this.updateInsights(generatedInsights, isCustomer);
  }

  async clickGenrateInsightReview(reviews: MatListOption[], isCustomer: boolean = true) {
    this.clearInsights(isCustomer);
    if (isCustomer) {
      this.insightsLoading = true;
    } else {
      this.searchInsightsLoading = true;
    }
    const generatedInsights: GeneratedInsights = await firstValueFrom(
      this.contactCenterAnalystService.generateReviewsInsights(
        reviews.map((review: any) => review)
      ) as Observable<GeneratedInsights>
    )
    this.updateInsights(generatedInsights, isCustomer);
  }
}


