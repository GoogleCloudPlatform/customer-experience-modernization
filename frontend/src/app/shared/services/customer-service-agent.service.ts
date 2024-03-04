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
import { Observable, ReplaySubject, catchError, throwError } from 'rxjs';
import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Timestamp } from '@angular/fire/firestore'

type Author = "User" | "Agent" | "System";
type Rating = "1" | "2" | "3" | "4" | "5";
type Status = "resolved" | "not resolved";
type Sentiment = "positive" | "negative" | "neutral";
type Category = "Bath Robe" | "Bath Towel Set" | "Bed" | "Bookcase" | "Chair" | "Console Table" | "Dining Table" | "Game Table" | "Grill" | "Office Chair" | "Ottoman" | "Outdoor Heater" | "Pool" | "Sofa" | "Tool Cabinet";

export interface ChatMessage {
  author: Author,
  language: string,
  text: string,
  timestamp?: Timestamp,
  link?: string,
  iconURL?: string,
  sentiment_score?: number;
  sentiment_magnitude?: number
}

export interface Conversation {
  timestamp: Timestamp,
  summary?: string,
  title?: string,
  id?: string,
}

export interface SearchResultKB {
  id: string,
  snippet: string,
  link: string,
  title: string,
  category: Category,
  manual: string,
}

export interface SearchResultConversation {
  id: string,
  snippet: string,
  link: string,
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

export interface SearchResponseKB {
  summary: string,
  user_input: string,
  search_results: SearchResultKB[],
}

export interface SearchResponseConversation {
  summary: string,
  user_input: string,
  search_results: SearchResultConversation[],
}

@Injectable({
  providedIn: 'root'
})

export class CustomerServiceAgentService {

  constructor(public http: HttpClient) { }

  private conversationId: ReplaySubject<string> = new ReplaySubject<string>(1);

  setConversationId(data: string): void {
    this.conversationId.next(data);
  }

  getConversationId$(): Observable<string> {
    return this.conversationId.asObservable();
  }

  private messages: ReplaySubject<string> = new ReplaySubject<string>(1);

  setDataMessages(data: any): void {
    this.messages.next(data);
  }

  getDataMessages$(): Observable<any> {
    return this.messages.asObservable();
  }

  addMessage(userId: string, conversationId: string, message: ChatMessage) {
    return this.http.post(`${environment.apiURL}/p4/message/${userId}/${conversationId}`, message).pipe(catchError(this.handleError));
  }

  getConversationSummary(userId: string, conversationId: string) {
    return this.http.get(`${environment.apiURL}/p4/conversation_summary_and_title/${userId}/${conversationId}`).pipe(catchError(this.handleError));
  }

  rephraseText(text: string) {
    const data = { "rephrase_text_input": text };
    return this.http.post(`${environment.apiURL}/p4/rephrase-text`, data).pipe(catchError(this.handleError));
  }

  scheduleEvent(eventSummary: string, attendees: string[], startTime: string, endTime: string) {
    const data = { "event_summary": eventSummary, "attendees": attendees, "start_time": startTime, "end_time": endTime };
    return this.http.post(`${environment.apiURL}/p4/schedule-event`, data).pipe(catchError(this.handleError));
  }

  searchConversations(
    query: string,
    userPseudoId: string,
    rating: Rating[],
    status: Status[],
    sentiment: Sentiment[],
    category: Category[],
    agentId: string,
    customerId: string,
    productId: string,
  ) {
    const data = {
      "query": query,
      "user_pseudo_id": userPseudoId,
      "rating": rating,
      "status": status,
      "sentiment": sentiment,
      "category": category,
      "agent_id": agentId,
      "customer_id": customerId,
      "product_id": productId,
    };
    return this.http.post(`${environment.apiURL}/p4/search-conversations`, data).pipe(catchError(this.handleError));
  }

  searchManuals(query: string, userPseudoId: string, category: Category[]) {
    const data = { "query": query, "user_pseudo_id": userPseudoId, "category": category };
    return this.http.post(`${environment.apiURL}/p4/search-manuals`, data).pipe(catchError(this.handleError));
  }

  translateText(text: string, targetLanguage: string) {
    const data = { "input_text": text, "target_language": targetLanguage };
    return this.http.post(`${environment.apiURL}/p4/translate`, data).pipe(catchError(this.handleError));
  }

  deleteAllConversations(userId: string): Observable<HttpResponse<string>> {
    return this.http.delete<string>(`${environment.apiURL}/p4/clear_conversations/${userId}`, { observe: "response" })
      .pipe(catchError(this.handleError));
  }

  autoSuggestQuery(text: string) {
    const data = { "input_text": text };
    return this.http.post(`${environment.apiURL}/p4/auto-suggest-query`, data).pipe(catchError(this.handleError));
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
