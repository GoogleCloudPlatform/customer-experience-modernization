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
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatTabsModule } from '@angular/material/tabs';
import { CustomerServiceAgentService, SearchResponseKB, SearchResponseConversation, SearchResultConversation, SearchResultKB } from '../../shared/services/customer-service-agent.service';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { marked } from 'marked';
import { MatDividerModule } from '@angular/material/divider';
import { NgbRatingModule } from '@ng-bootstrap/ng-bootstrap';
import { ClipboardModule } from '@angular/cdk/clipboard';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'customer-service-agent-agent-knowledge-search',
  standalone: true,
  imports: [
    NgFor,
    MatExpansionModule,
    MatButtonModule,
    MatDividerModule,
    MatIconModule,
    MatInputModule,
    MatTabsModule,
    MatFormFieldModule,
    MatPaginatorModule,
    FormsModule,
    ReactiveFormsModule,
    NgIf,
    NgClass,
    NgbRatingModule,
    ClipboardModule,
    MatSnackBarModule
  ],
  templateUrl: './agent-knowledge-search.component.html',
  styleUrl: './agent-knowledge-search.component.scss'
})
export class AgentKnowledgeSearchComponent implements OnChanges{
  rating: any = '';
  @Input() userId!: string;
  @Input() searchCompanyKnowledgeText!: string;
  @Output() aiResultKbSummary = new EventEmitter<string>();

  showCompanyKnowledge: boolean = true
  showConversation: boolean = false;
  compKnowClicked: boolean = true
  conversationClick: boolean = false
  categoryValue: any = '';
  statusValue: any = '';
  ratingValue: any = '';
  sentimentValue: any = '';
  statusButtonClick: boolean = false
  selectButtonId: any;
  selectButtonCategoryId: any;
  selectButtonSetimentId: any;
  kbMsgCtrl = new FormControl<string>("");
  conversationMsgCtrl = new FormControl<string>("");

  conversationsSummary: string = "";
  conversationsResults: SearchResultConversation[] = [];

  kbSummary: string = "";
  kbResults: SearchResultKB[] = [];
  showSummary: boolean = false;
  showConversationSummary: boolean = false;
  pageIndexKB = 0;
  pageSizeKB = 3;
  showFilterSection: boolean = false;
  pageIndexConversations = 0;
  pageSizeConversations = 3;
  //buttonValuesStatus!: ['Resolved' , 'Not Resolved'];
  buttonValuesRating = [
    { 'name': 1, _id: 1, 'value': "1" },
    { 'name': 2, _id: 2, 'value': "2" },
    { 'name': 3, _id: 3, 'value': "3" },
    { 'name': 4, _id: 4, 'value': "4" },
    { 'name': 5, _id: 5, 'value': "5" },
  ];
  buttonValuesStatus = [
    { 'name': "Resolved", _id: 1, 'value': "resolved" },
    { 'name': "Not Resolved", _id: 2, 'value': "not resolved" }
  ];
  buttonValuesSentiments = [
    { 'name': "Positive", _id: 1, 'value': "positive" },
    { 'name': "Neutral", _id: 2, 'value': "neutral" },
    { 'name': "Negative", _id: 3, 'value': "negative" }
  ];

  buttonValuesCatagorys = [{ 'name': "Bath Robe", _id: 1, 'value': "Bath Robe" },
  { 'name': "Bath Towel Set", _id: 2, 'value': "Bath Towel Set" },
  { 'name': "Bed", _id: 3, 'value': "Bed" },
  { 'name': "Bookcase", _id: 4, 'value': "Bookcase" },
  { 'name': "Chair", _id: 5, 'value': "Chair" },
  { 'name': "Console Table", _id: 6, 'value': "Console Table" },
  { 'name': "Dining Table", _id: 7, 'value': "Dining Table" },
  { 'name': "Game Table", _id: 8, 'value': "Game Table" },
  { 'name': "Grill", _id: 9, 'value': "Grill" },
  { 'name': "Office Chair", _id: 10, 'value': "Office Chair" },
  { 'name': "Ottoman", _id: 11, 'value': "Ottoman" },
  { 'name': "Outdoor Heater", _id: 12, 'value': "Outdoor Heater" }]
  showLoading: boolean = false;

  constructor(
    private customerServiceAgentService: CustomerServiceAgentService, private snackBar: MatSnackBar
  ) { }

  ngOnChanges(changes: SimpleChanges) {
    for (const propName in changes) {
      if (changes.hasOwnProperty(propName)) {
        switch (propName) {
          case 'searchCompanyKnowledgeText': {
            this.kbMsgCtrl.patchValue(this.searchCompanyKnowledgeText)
          }
        }
      }
    }
  }
  searchKB() {
    this.customerServiceAgentService.searchManuals(this.kbMsgCtrl.value || "", this.userId, []).subscribe(
      (res: any) => {
        const searchResponse: SearchResponseKB = res.responses;
        this.showSummary = true;
        this.kbSummary = searchResponse.summary;
        this.kbResults = searchResponse.search_results.map((searchResult: SearchResultKB) => {
          searchResult.snippet = String(marked.parse(searchResult.snippet));
          searchResult.manual = String(marked.parse(searchResult.manual));
          return searchResult;
        });

      }
    );
  }

  searchConversations() {

    this.customerServiceAgentService.searchConversations(
      this.conversationMsgCtrl.value || "", this.userId, [], [], [], [], "", "", "").subscribe(
        (res: any) => {
          const searchResponse: SearchResponseConversation = res.responses;
          this.showConversationSummary = true;
          this.conversationsSummary = searchResponse.summary;
          this.conversationsResults = searchResponse.search_results.map((searchResult: SearchResultConversation) => {
            searchResult.snippet = String(marked.parse(searchResult.snippet));
            searchResult.conversation = String(marked.parse(searchResult.conversation));
            return searchResult;
          });

        }
      );
  }

  handlePageEventKB(e: PageEvent) {
    this.pageIndexKB = e.pageIndex;
    this.pageSizeKB = e.pageSize;
  }

  handlePageEventConversations(e: PageEvent) {
    this.pageIndexConversations = e.pageIndex;
    this.pageSizeConversations = e.pageSize;
  }


  slicedResultsKB() {
    return this.kbResults.slice(Math.min(this.pageIndexKB * this.pageSizeKB, this.kbResults.length), Math.min((this.pageIndexKB + 1) * this.pageSizeKB, this.kbResults.length))
  }

  slicedResultsConversations() {
    return this.conversationsResults.slice(Math.min(this.pageIndexConversations * this.pageSizeConversations, this.conversationsResults.length), Math.min((this.pageIndexConversations + 1) * this.pageSizeConversations, this.conversationsResults.length))
  }


  companyKnowledgeClick() {
    this.showCompanyKnowledge = true
    this.showConversation = false
    this.compKnowClicked = true
    this.conversationClick = false

  }
  conversation() {
    this.showCompanyKnowledge = false
    this.showConversation = true
    this.conversationClick = true
    this.compKnowClicked = false
  }

  OnClickStatus(val: any, id: any) {
    this.statusValue = val
    this.statusButtonClick = true
    this.selectButtonId = id;
  }
  OnClickCategory(val: any, id: any) {
    this.categoryValue = val
    this.selectButtonCategoryId = id;
  }
  OnClickSentiment(val: any, id: any) {
    this.sentimentValue = val
    this.selectButtonSetimentId = id;
  }

  OnClickApply() {
    this.showLoading = true
    let selectedRating: any[] = [];
    if (this.rating) {
      selectedRating = [this.rating.toString()]
    }
    let statusVal: any[] = [];
    if (this.statusValue) {
      statusVal = [this.statusValue]
    }
    let sentimentVal: any[] = [];
    if (this.sentimentValue) {
      sentimentVal = [this.sentimentValue]
    }

    let categoryVal: any[] = [];
    if (this.categoryValue) {
      categoryVal = [this.categoryValue]
    }
    this.customerServiceAgentService.searchConversations(
      this.conversationMsgCtrl.value || "", this.userId, selectedRating, statusVal, sentimentVal, categoryVal, "", "", "").subscribe(
        (res: any) => {
          const searchResponse: SearchResponseConversation = res.responses;
          this.showConversationSummary = true;
          this.showFilterSection = false;
          this.conversationsSummary = searchResponse.summary;
          this.showLoading = false;
          this.conversationsResults = searchResponse.search_results.map((searchResult: SearchResultConversation) => {
            searchResult.snippet = String(marked.parse(searchResult.snippet));
            searchResult.conversation = String(marked.parse(searchResult.conversation));
            return searchResult;
          });

        }
      );
  }
  OnClickClear() {
    this.rating = '';
    this.statusValue = ''
    this.statusButtonClick = false
    this.selectButtonId = '';
    this.sentimentValue = ''
    this.selectButtonSetimentId = ''
    this.categoryValue = ''
    this.selectButtonCategoryId = ''
  }

  showContentCopiedMsg() {
    this.showSnackbar("Content Copied", 'Close', '4000');
    this.aiResultKbSummary.emit(this.kbSummary)
  }

  showSnackbar(content: any, action: any, duration: any) {
    let sb = this.snackBar.open(content, action, {
      duration: duration,
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }
  showFilters() {
    this.showFilterSection = true
  }
}
