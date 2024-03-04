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

import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { AgentMessagesComponent } from '../agent-messages/agent-messages.component';
import { Observable, firstValueFrom, map, startWith } from 'rxjs';
import { ChatMessage, CustomerServiceAgentService } from '../../shared/services/customer-service-agent.service';
import { FirebaseService } from '../../shared/services/firebase.service';
import { AsyncPipe, NgIf } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { TranslationLanguage, translationOptions } from '../../shared/constants/languages.constant';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'customer-service-agent-agent-chat',
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatDividerModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    AsyncPipe,
    AgentMessagesComponent,
  ],
  templateUrl: './agent-chat.component.html',
  styleUrl: './agent-chat.component.scss'
})
export class AgentChatComponent implements OnChanges {
  @Input() conversationId!: string;
  @Input() userName!: string;
  @Input() userEmail!: string;
  @Input() userId!: string;
  @Input() userPhotoURL!: string;
  @Input() copiedAiResultKbSummary!: string
  agentLanguage: string = navigator.language || "en-us";

  @Output() searchCompanyKnowledge = new EventEmitter<string>();

  @Output() emptyConversationId = new EventEmitter<string>();
  @Input() updatedMessages!: ChatMessage[];
  messages: ChatMessage[] = []
  showTranslationForm: boolean = false;

  languageControl = new FormControl<TranslationLanguage>({ name: "English", value: "en" });
  filteredOptions!: Observable<TranslationLanguage[]>;

  translationOptions: TranslationLanguage[] = translationOptions;

  msgFormGroup: FormGroup = this._formBuilder.group({
    msgCtrl: ['', Validators.required],
  });



  constructor(
    private firebaseService: FirebaseService,
    private _formBuilder: FormBuilder,
    private customerServiceAgentService: CustomerServiceAgentService
  ) {

  }

  ngOnChanges(changes: SimpleChanges): void {
    let chatMessages$ = this.firebaseService.getChatMessages(this.userId, this.conversationId) as Observable<ChatMessage[]>;
    chatMessages$.subscribe(async (res: ChatMessage[]) => {
      this.messages = await Promise.all(res.map(async (message: ChatMessage) => {
        const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.agentLanguage))
        message.text = translateRes.output_text;
        return message;
      }));
    });
    this.filteredOptions = this.languageControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return name ? this._filter(name as string) : this.translationOptions.slice();
      }),
    );
    for (const propName in changes) {
      if (changes.hasOwnProperty(propName)) {
        if (propName == 'updatedMessages') {
          this.messages = this.updatedMessages;
        }
        if (propName == 'copiedAiResultKbSummary') {
          this.msgFormGroup.setValue({ msgCtrl: this.copiedAiResultKbSummary });
        }
      }
    }

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
      const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.agentLanguage))
      message.text = translateRes.output_text;
      return message;
    }));

  }

  async sendMessage(event?: any) {
    event.preventDefault();
    if (!this.conversationId) return;
    const message: ChatMessage = {
      author: "Agent",
      language: this.agentLanguage,
      text: this.msgFormGroup.value.msgCtrl,
    }
    this.msgFormGroup.setValue({ msgCtrl: "" });

    this.customerServiceAgentService.addMessage(this.userId, this.conversationId, message).subscribe();
  }

  async googleMeet() {
    const now = new Date();
    const start = now.toISOString().split(".")[0] + 'Z';
    const end = new Date(now.getTime() + 1800000).toISOString().split(".")[0] + 'Z'; // 30 minutes
    this.customerServiceAgentService.scheduleEvent(
      "Talk with the service agent", [this.userEmail], start, end
    ).subscribe((res: any) => {
      const conferenceLink = res.conference_call_link;
      const iconURL = res.icon_url;
      const message: ChatMessage = {
        author: "Agent",
        language: this.agentLanguage,
        text: "Talk with the service agent",
        link: conferenceLink,
        iconURL: iconURL,
      }
      this.customerServiceAgentService.addMessage(this.userId, this.conversationId, message).subscribe();
    });
  }

  async rephrase() {
    this.customerServiceAgentService.rephraseText(this.msgFormGroup.value.msgCtrl).subscribe((res: any) => {
      const textOutput: string = res.rephrase_text_output;
      this.msgFormGroup.setValue({ msgCtrl: textOutput.replaceAll('"', '') }); // Remove double-quote
    })
  }

  async endSession() {
    this.customerServiceAgentService.getConversationSummary(this.userId, this.conversationId).subscribe((res: any) => {
      if (res.title) {
        this.emptyConversationId.emit("");
      }
    }
    );
  }
  autoSuggestQuery() {
    let msgs = this.messages.filter((a: any) => {
      if (a.author === 'User') {
        return a.text
      }
    })
    let concatenatedMsgsList = [];
    let concatenatedMsgs = '';
    for (let i = msgs.length - 1; i >= 0; i--) {
      concatenatedMsgsList.push(msgs[i].text)
    }
    concatenatedMsgs = concatenatedMsgsList.slice(0, 3).join(" ");

    this.customerServiceAgentService.autoSuggestQuery(concatenatedMsgs).subscribe((res: any) => {
      this.searchCompanyKnowledge.emit(res?.output_text)
    })
  }

}
