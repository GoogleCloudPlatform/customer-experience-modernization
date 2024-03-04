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

import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { AgentMessagesComponent } from '../agent-messages/agent-messages.component';
import { ChatMessage, Conversation, CustomerServiceAgentService } from '../../shared/services/customer-service-agent.service';
import { AsyncPipe, NgClass, NgFor, NgIf } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { FirebaseService } from '../../shared/services/firebase.service';
import { Observable, firstValueFrom, map, startWith } from 'rxjs';
import { marked } from 'marked';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { TranslationLanguage, translationOptions } from '../../shared/constants/languages.constant';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { TruncatePipe } from '../../shared/pipes/truncate.pipe';

@Component({
  selector: 'customer-service-agent-case-history',
  standalone: true,
  imports: [
    NgClass,
    NgIf,
    NgFor,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDividerModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatPaginatorModule,
    FormsModule,
    ReactiveFormsModule,
    AgentMessagesComponent,
    AsyncPipe,
    TruncatePipe
  ],
  templateUrl: './case-history.component.html',
  styleUrl: './case-history.component.scss'
})
export class CaseHistoryComponent implements OnChanges {
  @Input() caseHistory!: Conversation[];
  @Input() userName!: string;
  @Input() userEmail!: string;
  @Input() userId!: string;
  @Input() userPhotoURL!: string;

  @Output() conversationId = new EventEmitter<string>();
  @Output() updatedMessages = new EventEmitter<any>();


  agentLanguage: string = navigator.language || "en-us";
  cases: Conversation[] = [];
  messages: ChatMessage[] = [];
  summary: string = "";

  pageIndex = 0;
  pageSize = 5;

  showTranslationForm: boolean = false;

  languageControl = new FormControl<TranslationLanguage>({ name: "English", value: "en" });
  filteredOptions!: Observable<TranslationLanguage[]>;

  translationOptions: TranslationLanguage[] = translationOptions;


  constructor(
    private firebaseService: FirebaseService,
    private customerServiceAgentService: CustomerServiceAgentService,
  ) {
  }

  async ngOnChanges() {
    this.filteredOptions = this.languageControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return name ? this._filter(name as string) : this.translationOptions.slice();
      }),
    );
    this.cases = await Promise.all(this.caseHistory.map(async (conversation: Conversation) => {
      if (conversation.summary) {
        const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(conversation.summary, this.agentLanguage))
        conversation.summary = translateRes.output_text;
      }
      if (conversation.title) {
        const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(conversation.title, this.agentLanguage))
        conversation.title = translateRes.output_text;
      }

      return conversation;
    }));


  }
  private _filter(name: string): TranslationLanguage[] {
    const filterValue = name.toLowerCase();

    return this.translationOptions.filter(option => option.name.toLowerCase().includes(filterValue));
  }

  displayFn(language: TranslationLanguage): string {
    return language && language.name ? language.name : '';
  }

  async changeLanguage() {
    this.agentLanguage = this.languageControl.value?.value || "en";
    this.showTranslationForm = false;
    this.messages = await Promise.all(this.messages.map(async (message: ChatMessage) => {
      if (message.language != this.agentLanguage) {
        const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.agentLanguage))
        message.text = translateRes.output_text;
      }
      return message;
    }));
    this.cases = await Promise.all(this.caseHistory.map(async (conversation: Conversation) => {
      if (conversation.summary) {
        const translateResSummary: any = await firstValueFrom(this.customerServiceAgentService.translateText(conversation.summary, this.agentLanguage))
        conversation.summary = translateResSummary.output_text;
      }
      if (conversation.title) {
        const translateResTitle: any = await firstValueFrom(this.customerServiceAgentService.translateText(conversation.title, this.agentLanguage))
        conversation.title = translateResTitle.output_text;
      }

      return conversation;
    }));


  }


  selectCase(conversation: Conversation) {
    if (!conversation.title) {
      this.conversationId.emit(conversation.id);
    }
    if (conversation.summary) {
      this.summary = String(marked.parse(conversation.summary));
    }
    else {
      this.summary = "";
    }
    let chatMessages$ = this.firebaseService.getChatMessages(this.userId, conversation.id!) as Observable<ChatMessage[]>;
    chatMessages$.subscribe(async (res: ChatMessage[]) => {
      this.messages = await Promise.all(res.map(async (message: ChatMessage) => {
        if (message.language != this.agentLanguage) {
          const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.agentLanguage))
          message.text = translateRes.output_text;
        }
        return message;
      }));

    });

  }

  handlePageEvent(e: PageEvent) {
    this.pageIndex = e.pageIndex;
    this.pageSize = e.pageSize;
  }

  slicedCaseHistory() {
    return this.cases.slice(Math.min(this.pageIndex * this.pageSize, this.caseHistory.length), Math.min((this.pageIndex + 1) * this.pageSize, this.caseHistory.length));
  }
  archiveAll(){
    this.customerServiceAgentService.deleteAllConversations(this.userId).subscribe();
    this.messages =[];
    this.customerServiceAgentService.setConversationId("");
    this.customerServiceAgentService.setDataMessages(this.messages)
    this.updatedMessages.emit(this.messages);

  }
}
