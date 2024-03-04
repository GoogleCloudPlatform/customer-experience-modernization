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

import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { catchError, throwError } from 'rxjs';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

export type Rating = "1" | "2" | "3" | "4" | "5";
export type Status = "resolved" | "not resolved";
export type Sentiment = "positive" | "negative" | "neutral";
export type Category = "Bath Robe" | "Bath Towel Set" | "Bed" | "Bookcase" | "Chair" | "Console Table" | "Dining Table" | "Game Table" | "Grill" | "Office Chair" | "Ottoman" | "Outdoor Heater" | "Pool" | "Sofa" | "Tool Cabinet";
export type UserJourney = "conversations" | "reviews";

export interface Conversation {
  id?: string,
  snippet?: string,
  link?: string,
  title: string,
  category: Category,
  status: Status,
  rating: Rating,
  sentiment: Sentiment,
  product_id: string,
  customer_id: string,
  customer_email: string,
  conversation: string,
  agent_id: string,
  agent_email: string,
}

export interface Review {
  id?: string,
  snippet?: string,
  link?: string,
  title: string,
  category: Category,
  rating: Rating,
  sentiment: Sentiment,
  product_id: string,
  customer_id: string,
  customer_email: string,
  review: string,
}

export interface CustomerInfo {
  customer_id: string,
  is_media_follower: boolean,
  cart_total: number,
  channel: string,
  city: string,
  last_activity_date: string,
  total_value: string,
  total_purchases: string,
  last_purchase_date: string,
  last_sign_up_date: string,
  state: string,
  total_emails: string,
  loyalty_score: string,
  email: string,
}

export interface Customer {
  conversations: Conversation[],
  reviews: Review[],
  customer_info: CustomerInfo,
}

export interface EntityMention {
  text: string,
  type: 'TYPE_UNKNOWN' | 'PROPER' | 'COMMON',
  probability: number
}

export interface Entity {
  name: string,
  entity_type: 'UNKNOWN' | 'PERSON' | 'LOCATION' | 'ORGANIZATION' | 'EVENT' | 'WORK_OF_ART' | 'CONSUMER_GOOD' | 'OTHER' | 'PHONE_NUMBER' | 'ADDRESS' | 'DATE' | 'NUMBER' | 'PRICE',
  metadata: object[],
  mentions: EntityMention[],
}

export interface GeneratedInsights {
  entities: Entity[],
  pending_tasks: string,
  insights: string,
  next_best_action: string,
  summary: string,
}


@Injectable({
  providedIn: 'root'
})
export class ContactCenterAnalystService {

  constructor(public http: HttpClient) { }

  getCustomerInfo(customerId: string) {
    return this.http.get(`${environment.apiURL}/p5/customer/${customerId}`).pipe(catchError(this.handleError));
  }

  generateConversationsInsights(conversations: Conversation[]) {
    const data = { "conversations": conversations }
    return this.http.post(`${environment.apiURL}/p5/generate-conversations-insights`, data).pipe(catchError(this.handleError));
  }

  generateReviewsInsights(reviews: Review[]) {
    const data = { "reviews": reviews }
    return this.http.post(`${environment.apiURL}/p5/generate-reviews-insights`, data).pipe(catchError(this.handleError));
  }

  searchConversations(
    query: string,
    userPseudoId: string,
    conversationId: string,
    rating: Rating[] = [],
    status: Status[] = [],
    sentiment: Sentiment[] = [],
    category: Category[] = [],
    agentId: string = "",
    customerId: string = "",
    productId: string = "",
  ) {
    const data = {
      "query": query,
      "user_pseudo_id": userPseudoId,
      "conversation_id": conversationId,
      "rating": rating,
      "status": status,
      "sentiment": sentiment,
      "category": category,
      "agent_id": agentId,
      "customer_id": customerId,
      "product_id": productId,
    };
    return this.http.post(`${environment.apiURL}/p5/search-conversations`, data).pipe(catchError(this.handleError));
  }

  searchReviews(
    query: string,
    userPseudoId: string,
    conversationId: string,
    rating: Rating[] = [],
    sentiment: Sentiment[] = [],
    category: Category[] = [],
    agentId: string = "",
    customerId: string = "",
    productId: string = "",
  ) {
    const data = {
      "query": query,
      "user_pseudo_id": userPseudoId,
      "conversation_id": conversationId,
      "rating": rating,
      "sentiment": sentiment,
      "category": category,
      "agent_id": agentId,
      "customer_id": customerId,
      "product_id": productId,
    };
    return this.http.post(`${environment.apiURL}/p5/search-reviews`, data).pipe(catchError(this.handleError));
  }

  vectorFindSimilar(text: string, userJourney: UserJourney) {
    const data = { "input_text": text, "user_journey": userJourney }
    return this.http.post(`${environment.apiURL}/p5/vector-find-similar`, data).pipe(catchError(this.handleError));
  }


  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {

      console.error('An error occurred:', error.error.message);
    } else {

      // console.error(
      //   `Backend returned code ${error.status}, ` +
      //   `body was: ${error.error}`);
    }

    return throwError(() => new Error(
      'Something bad happened; please try again later.'));
  }

}
