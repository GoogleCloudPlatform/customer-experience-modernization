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
import { Observable, catchError, throwError } from 'rxjs';
import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Timestamp } from '@angular/fire/firestore';

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
  address: string,
}

export interface Customer {
  conversations: Conversation[],
  reviews: Review[],
  customer_info: CustomerInfo,
}

export interface AgentActivity {
  title: string;
  description: string;
  customer_id: string;
  status: 'Open' | 'In progress' | 'Completed';
  timestamp: Timestamp;
  id?: string;
}

export interface SearchResultKB {
  id: string,
  snippet: string,
  link: string,
  title: string,
  category: Category,
  manual: string,
}

export interface SearchResponseKB {
  summary: string,
  user_input: string,
  search_results: SearchResultKB[],
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
export class FieldServiceAgentService {

  constructor(public http: HttpClient) { }

  addAgentActivity(userId: string, agentActivity: AgentActivity): Observable<HttpResponse<string>> {
    return this.http.post<string>(`${environment.apiURL}/p6/agent-activity/${userId}`, agentActivity, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  deleteAgentActivity(userId: string, activityId: string): Observable<HttpResponse<string>> {
    return this.http.delete<string>(`${environment.apiURL}/p6/agent-activity/${userId}/${activityId}`, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  putAgentActivity(userId: string, activityId: string, agentActivity: AgentActivity): Observable<HttpResponse<string>> {
    return this.http.put<string>(`${environment.apiURL}/p6/agent-activity/${userId}/${activityId}`, agentActivity, { observe: "response" })
      .pipe(catchError(this.handleError))
  }

  askImageGemini(imageName: string, userQuery: string) {
    const data = {
      "image_name": imageName,
      "user_query": userQuery,
    }
    return this.http.post(`${environment.apiURL}/p6/ask-image-gemini`, data).pipe(catchError(this.handleError));
  }

  generateAgentActivity(userId: string, customerId: string, conversation: string, timestamp: Timestamp): Observable<HttpResponse<string>> {
    const data = {
      "user_id": userId,
      "customer_id": customerId,
      "conversation": conversation,
      "timestamp": timestamp
    }
    return this.http.post<string>(`${environment.apiURL}/p6/generate-agent-activity`, data, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  getCustomerInfo(customerId: string) {
    return this.http.get(`${environment.apiURL}/p6/customer/${customerId}`).pipe(catchError(this.handleError));
  }

  generateConversationsInsights(conversations: any[]) {
    const data = { "conversations": conversations }
    return this.http.post(`${environment.apiURL}/p6/generate-conversations-insights`, data).pipe(catchError(this.handleError));
  }


  scheduleEvent(attendees: string[], startTime: string) {
    const data = { "attendees": attendees, "start_time": startTime };
    return this.http.post(`${environment.apiURL}/p6/schedule-event`, data).pipe(catchError(this.handleError));
  }

  searchManuals(query: string, userPseudoId: string, category: Category[]) {
    const data = { "query": query, "user_pseudo_id": userPseudoId, "category": category };
    return this.http.post(`${environment.apiURL}/p6/search-manuals`, data).pipe(catchError(this.handleError));
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
