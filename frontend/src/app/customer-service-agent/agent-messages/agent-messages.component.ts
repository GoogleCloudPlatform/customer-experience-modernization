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

import { Component, Input, SimpleChanges, inject } from '@angular/core';
import { ChatMessage, CustomerServiceAgentService } from '../../shared/services/customer-service-agent.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { NgClass, NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'customer-service-agent-agent-messages',
  standalone: true,
  imports: [
    NgClass,
    NgFor,
    NgIf,
  ],
  templateUrl: './agent-messages.component.html',
  styleUrl: './agent-messages.component.scss'
})
export class AgentMessagesComponent {
  @Input() messages!: ChatMessage[];
  @Input() summary!: string;
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId: string = "";
  userName: string = "";

  constructor( private customerServiceAgentService: CustomerServiceAgentService
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
        this.userName = aUser.displayName || "";
      }
    });
  }

  ngOnChanges(changes : SimpleChanges){
    for (const propName in changes) {
      if (changes.hasOwnProperty(propName)) {
        switch (propName) {
          case 'messages': {
            this.customerServiceAgentService.getDataMessages$().subscribe((res:any)=>{
              this.messages = res
            })
          }
        }
      }
    }
  }

}
