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

import { CUSTOM_ELEMENTS_SCHEMA, Component, HostListener, Input, ViewChild } from '@angular/core';
import { FieldServiceAgentService } from '../../shared/services/field-service-agent.service';
import { Observable, firstValueFrom } from 'rxjs';
import { Timestamp } from '@angular/fire/firestore';
import { environment } from '../../../environments/environment';
import { NgIf } from '@angular/common';
import { ChatMessage, CustomerServiceAgentService } from '../../shared/services/customer-service-agent.service';

@Component({
  selector: 'customer-df-messenger',
  standalone: true,
  imports: [NgIf],
  templateUrl: './df-messenger.component.html',
  styleUrl: './df-messenger.component.scss',
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class DfMessengerComponent {
  @Input()
  userId: string = "";

  @Input()
  userEmail: string = "";

  dfProject: string = environment.dfProject;
  dfAgent: string = environment.dfAgent;

  conversation: string = "";
  conversationList: ChatMessage[] = [];

  constructor(
    private fieldServiceAgentService: FieldServiceAgentService,
    private customerServiceAgentService: CustomerServiceAgentService
  ) { }

  @ViewChild('df-messenger') dfMessenger!: any;

  @HostListener('window:df-response-received', ['$event'])
  onMessageReceived(event: any) {
    event.detail.messages.forEach(async (message: any) => {
      console.log(message.type);
      if (message.type === 'customCard') {
        if ('parameters' in event.detail.raw.queryResult) {
          if ('date-time' in event.detail.raw.queryResult.parameters) {


            const dateTime = event.detail.raw.queryResult.parameters['date-time'];
            const today: Date = new Date();
            const startTime: Date = new Date(
              dateTime.year || today.getFullYear(),
              dateTime.month - 1 || today.getMonth(),
              dateTime.day || today.getDay(),
              dateTime.hours || 12,
              dateTime.minutes || 0,
              dateTime.seconds || 0);

            const firestoreDateTime: Timestamp = Timestamp.fromDate(startTime);
            firstValueFrom(this.fieldServiceAgentService.generateAgentActivity(this.userId, "2", this.conversation, firestoreDateTime));
            const scheduleResponse: any = await firstValueFrom(
              this.fieldServiceAgentService.scheduleEvent(
                [this.userEmail], startTime.toISOString().split(".")[0] + 'Z'
              ) as Observable<any>);
            const payload = [
              {
                "icon": {
                  "color": "#FF9800",
                  "type": "chevron_right"
                },
                "event": {
                  "event": ""
                },
                "type": "button",
                "mode": "blocking",
                "anchor": {
                  "href": scheduleResponse.calendar_link
                },
                "text": "Go to Calendar link"
              }
            ]
            const dfMessenger: any = document.querySelector('df-messenger');
            dfMessenger.renderCustomCard(payload);

          }
        }
        if ('intent' in event.detail.raw.queryResult) {
          if ('displayName' in event.detail.raw.queryResult.intent) {
            if (event.detail.raw.queryResult.intent.displayName = "Talk to human agent") {
              const chatMessage: ChatMessage = {
                author: "Agent",
                language: "en-US",
                text: "Hi, I will check the chat history and answer you in a few moments",
              }
              this.conversationList.push(chatMessage);


              console.log(event.detail.raw.queryResult.intent.displayName);
              let res: any = await firstValueFrom(this.customerServiceAgentService.addMessage(this.userId, "new", this.conversationList[0]));
              if (this.conversationList.length > 1) {
                for (let index = 1; index < this.conversationList.length; index++) {
                  res = await firstValueFrom(this.customerServiceAgentService.addMessage(this.userId, res.conversation_id, this.conversationList[index]));
                }
              }
            }

          }
        }
      } else if (message.type === 'text') {
        this.conversation += "Virtual Support Agent: ";
        this.conversation += message.text;
        this.conversation += "\n";
        const chatMessage: ChatMessage = {
          author: "Agent",
          language: "en-US",
          text: message.text,
        }
        this.conversationList.push(chatMessage);

      }
    });
    console.log(event);
  }

  @HostListener('window:df-user-input-entered', ['$event'])
  onUserMessage(event: any) {
    this.conversation += "Customer: ";
    this.conversation += event.detail.input;
    this.conversation += "\n";
    const chatMessage: ChatMessage = {
      author: "User",
      language: "en-US",
      text: event.detail.input,
    }
    this.conversationList.push(chatMessage);
  }

}
