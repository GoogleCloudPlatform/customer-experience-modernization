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

import { AfterViewChecked, AfterViewInit, Component, ElementRef, Input, OnChanges, OnDestroy, OnInit, SimpleChanges, ViewChild, inject } from '@angular/core';
import { ObservablesService } from '../../shared/services/observables.service';
import { FirebaseService } from '../../shared/services/firebase.service';
import { SearchService } from '../../shared/services/search.service';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { ProductCarouselComponent } from '../product-carousel/product-carousel.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { FormsModule } from '@angular/forms';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription } from 'rxjs';
import { RecommendationsService } from '../../shared/services/recommendations.service';

@Component({
  selector: 'app-assistant-chat',
  templateUrl: './assistant-chat.component.html',
  styleUrls: ['./assistant-chat.component.scss'],
  standalone: true,
  imports: [
    NgIf,
    NgFor,
    ProductCarouselComponent,
    MatProgressSpinnerModule,
    MatDividerModule,
    FormsModule,
    NgClass
  ]
})
export class AssistantChatComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {
  chatLoading: boolean = false
  documentId!: any;
  chatMsgs: any[] = [];
  showAssistantTyping: boolean = false;
  photoURL: any;
  chatInputMessage!: string;
  products = new Map<number, any>();
  systemSuggestedProducts: any = [];
  systemSuggestedImages: any[] = [];
  initialSearchResult: any[] = [];
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  docSubscription: Subscription;
  searchSubscription!: Subscription;
  userId = "";
  uploadingImage: boolean = false;
  @Input() imageProcessing!: boolean;

  constructor(
    public observablesService: ObservablesService,
    public firebaseService: FirebaseService,
    public searchService: SearchService,
    public recommendationsService: RecommendationsService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user
      if (aUser) {
        this.userId = aUser.uid;
        if (aUser.photoURL) {
          this.photoURL = aUser.photoURL;
        }
      }
      else {
        this.photoURL = null;
      }
    })

    this.docSubscription = this.observablesService.getupdatedDocumentID().subscribe(docId => {
      this.documentId = docId;
      this.searchSubscription = this.searchService.fetchResults(docId).subscribe((res: any) => {
        this.chatMsgs = res;
        if (this.chatMsgs[this.chatMsgs.length - 1].author === 'user') {
          this.showAssistantTyping = true;
        } else {
          this.showAssistantTyping = false;
        }
        this.chatLoading = true;
        this.initialSearchResult = this.chatMsgs.slice(0, 2);
      });

    });
  }
  @ViewChild('chatMessage')
  private myScrollContainer!: ElementRef;

  ngOnInit() {
    this.scrollToBottom();
  }

  ngOnChanges(_changes: SimpleChanges): void {
    this.imageProcessing = this.imageProcessing;
  }

  ngAfterViewInit() {
    this.scrollToBottom();
  }

  ngOnDestroy() {
    // when manually subscribing to an observable remember to unsubscribe in ngOnDestroy
    this.userSubscription.unsubscribe();
    if (this.searchSubscription) {
      this.searchSubscription.unsubscribe();
    }
    this.docSubscription.unsubscribe();
  }


  scrollToBottom(): void {
    //const el: HTMLDivElement = this._el.nativeElement;
    //el.scrollTop = Math.max(0, el.scrollHeight - el.offsetHeight);
    try {

      //this.myScrollContainer.nativeElement.scrollTop = this.myScrollContainer.nativeElement.scrollHeight;
      let el = this.myScrollContainer.nativeElement;
      el.scrollIntoView({
        behavior: "smooth",
        block: "start",
        inline: "nearest"
      });
    //  el.scrollTop = Math.max(0, el.scrollHeight - el.offsetHeight);
    } catch (err) { }
  }
  followUp(assistantChat: any, event?: any) {
    this.chatInputMessage = "";
    event?.preventDefault();
    this.firebaseService.analyticsLogEvent("search", { search_term: assistantChat })
    this.recommendationsService.collectRecommendationsEvents("search", this.userId, [], {
      "search_info": { "search_query": assistantChat }
    });
    this.searchService.continueFollowupForText(assistantChat)
  }

  getProductsList(index: any): any {
    return this.products.get(index);
  }

  processFile(imageInput: any, assistantChat: any) {
    this.uploadingImage = true;
    const file: File = imageInput.files[0];
    const reader = new FileReader();
    //this.chatLoading = false
    reader.addEventListener('load', (event: any) => {
      this.chatInputMessage = "";
      this.searchService.continueFollowupForImage(file, assistantChat, event).subscribe((data: any) => {
        this.uploadingImage = false
      });
    });

    reader.readAsDataURL(file);
  }
}
