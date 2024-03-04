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
import { ChatMessage, Conversation } from '../../shared/services/customer-service-agent.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Observable, Subscription } from 'rxjs';
import { FirebaseService } from '../../shared/services/firebase.service';
import { AgentChatComponent } from '../agent-chat/agent-chat.component';
import { AgentKnowledgeSearchComponent } from '../agent-knowledge-search/agent-knowledge-search.component';
import { CaseHistoryComponent } from '../case-history/case-history.component';
import { NgClass, NgIf } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';

@Component({
  selector: 'customer-service-agent-agent',
  standalone: true,
  imports: [
    NgIf,
    MatCardModule,
    MatDividerModule,
    MatTabsModule,
    AgentChatComponent,
    AgentKnowledgeSearchComponent,
    CaseHistoryComponent,
    NgClass,
    MatToolbarModule,
    UserPhotoComponent
  ],
  templateUrl: './agent.component.html',
  styleUrl: './agent.component.scss'
})
export class CustomerServiceAgentAgentComponent {
  showCaseHistory: boolean = true
  showCurrentCase: boolean = false
  caseHist: boolean = true;
  curtCase: boolean = false;
  agentName = "Agent";
  conversationId: undefined | string;
  agentLanguage: string = navigator.language || "en-us";
  messages: ChatMessage[] = []

  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId: string = "";
  userName: string = "";
  userEmail: string = "";
  userPhotoURL: string = "";

  caseHistory: Conversation[] = [];
  tabIndex: number = 1;
  searchCompanyKnowledgeText: string = '';
  copiedAiResultKbSummary: string ='';




  constructor(
    private firebaseService: FirebaseService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
        this.userName = aUser.displayName || "";
        this.userEmail = aUser.email || "";
        this.userPhotoURL = aUser.photoURL || "";
        const caseHistory$ = this.firebaseService.getCaseHistory(this.userId) as Observable<Conversation[]>;
        caseHistory$.subscribe((res: Conversation[]) => {
          this.caseHistory = res;
        })
      }
    });
  }

  setConversationId(conversationId: string) {
    this.conversationId = conversationId;
    const foundConversation = this.caseHistory.find((conversation) => conversation.id == conversationId);
    if (!foundConversation?.title) {
      this.tabIndex = 2;
    }
  }

  getMessages(messages : any){
    this.messages = messages
  }

  drawLoading(elementId: string) {
    let element = document.getElementById(elementId);
    let loading = `<div class="d-flex justify-content-center">
                  <div class="spinner-border text-primary m-5" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>`
    if (element)
      element.innerHTML = loading;
  }


  showError(errorMessage: string) {
    alert(`[Error]${errorMessage}`);
  }


  caseHistoryClick() {
    this.showCaseHistory = true;
    this.showCurrentCase = false
    this.caseHist = true
    this.curtCase = false
  }


  currentCaseClick() {
    this.showCurrentCase = true;
    this.showCaseHistory = false;
    this.caseHist = false
    this.curtCase = true
  }

  getCompanyKnowledge(companyKnowledge: string) {
    this.searchCompanyKnowledgeText = companyKnowledge
  }

  getAiResultKbSummary(aiResultKbSummary: string) {
    this.copiedAiResultKbSummary = aiResultKbSummary
  }
}
