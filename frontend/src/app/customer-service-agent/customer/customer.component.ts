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

import { Component, OnInit, inject } from '@angular/core';
import { ChatMessage, Conversation, CustomerServiceAgentService } from '../../shared/services/customer-service-agent.service';
import { AsyncPipe, NgClass, NgFor, NgIf } from '@angular/common';
import { Auth, User, user } from '@angular/fire/auth';
import { Observable, Subscription, firstValueFrom, map, startWith } from 'rxjs';
import { FirebaseService } from '../../shared/services/firebase.service';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatDividerModule } from '@angular/material/divider';
import { TranslationLanguage, translationOptions } from '../../shared/constants/languages.constant';

@Component({
  selector: 'customer-service-agent-customer',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    NgClass,
    MatAutocompleteModule,
    MatButtonModule,
    MatCardModule,
    MatDividerModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    AsyncPipe,
  ],
  templateUrl: './customer.component.html',
  styleUrl: './customer.component.scss'
})
export class CustomerServiceAgentCustomerComponent implements OnInit {

  agentName: string = "Agent";
  conversationId: undefined | string;
  userLanguage: string = navigator.language || "en-us";
  messages: ChatMessage[] = []

  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId: string = "";
  userName: string = "";
  chatMessageSubscription: Subscription | undefined;

  showTranslationForm: boolean = false;

  languageControl = new FormControl<TranslationLanguage>({ name: "English", value: "en" });
  filteredOptions!: Observable<TranslationLanguage[]>;

  translationOptions: TranslationLanguage[] = translationOptions;


  msgFormGroup: FormGroup = this._formBuilder.group({
    msgCtrl: ['', Validators.required],
  });


  constructor(
    private customerServiceAgentService: CustomerServiceAgentService,
    private _formBuilder: FormBuilder,
    private firebaseService: FirebaseService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {

        this.userId = aUser.uid;
        this.userName = aUser.displayName || "";
        const caseHistory$ = this.firebaseService.getCaseHistory(this.userId) as Observable<Conversation[]>;
        caseHistory$.subscribe((res: Conversation[]) => {
          if (this.conversationId) {
            const foundConversation = res.find((conversation) => conversation.id == this.conversationId);
            if (foundConversation?.title) {
              this.conversationId = "";
              this.chatMessageSubscription?.unsubscribe();
              this.messages.push(
                {
                  text: "Session ended",
                  author: "System",
                  language: "en-US"
                }
              )
            }
          }
          else {
            if (!res[0]?.title) {
              this.conversationId = res[0]?.id;
              let chatMessages$ = this.firebaseService.getChatMessages(this.userId, this.conversationId!) as Observable<ChatMessage[]>;
              this.chatMessageSubscription = chatMessages$.subscribe(async (res: ChatMessage[]) => {
                this.messages = await Promise.all(res.map(async (message: ChatMessage) => {
                  const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.userLanguage))
                  message.text = translateRes.output_text;
                  return message;
                }));

              });

            }
          }
          this.customerServiceAgentService.getConversationId$().subscribe((res: any) => {
            this.conversationId = res
          })
          this.customerServiceAgentService.getDataMessages$().subscribe((res: any) => {
            this.messages = res;
          })
        })


      }
    });
  }

  ngOnInit(): void {
    this.filteredOptions = this.languageControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return name ? this._filter(name as string) : this.translationOptions.slice();
      }),
    );

  }
  private _filter(name: string): TranslationLanguage[] {
    const filterValue = name.toLowerCase();

    return this.translationOptions.filter(option => option.name.toLowerCase().includes(filterValue));
  }

  displayFn(language: TranslationLanguage): string {
    return language && language.name ? language.name : '';
  }

  async changeLanguage() {
    this.userLanguage = this.languageControl.value?.value || "en";
    this.showTranslationForm = false;
    this.messages = await Promise.all(this.messages.map(async (message: ChatMessage) => {
      const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.userLanguage))
      message.text = translateRes.output_text;
      return message;
    }));

  }


  async sendMessage(event?: any) {
    event.preventDefault();
    let conversationId = "new";
    if (this.conversationId) {
      conversationId = this.conversationId;
    }
    const message: ChatMessage = {
      author: "User",
      language: this.userLanguage,
      text: this.msgFormGroup.value.msgCtrl,
    }
    this.msgFormGroup.setValue({ msgCtrl: "" });

    this.customerServiceAgentService.addMessage(this.userId, conversationId, message).subscribe((res: any) => {
      if (!this.conversationId && res.conversation_id) {
        this.conversationId = res.conversation_id;
        let chatMessages$ = this.firebaseService.getChatMessages(this.userId, this.conversationId!) as Observable<ChatMessage[]>;
        this.chatMessageSubscription = chatMessages$.subscribe(async (res: ChatMessage[]) => {
          this.messages = await Promise.all(res.map(async (message: ChatMessage) => {
            const translateRes: any = await firstValueFrom(this.customerServiceAgentService.translateText(message.text, this.userLanguage))
            message.text = translateRes.output_text;
            return message;
          }));
        });
      }
    })
  }
}
