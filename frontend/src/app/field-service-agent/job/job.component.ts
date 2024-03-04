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

import { AfterViewInit, Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { FirebaseService } from '../../shared/services/firebase.service';
import { Observable, Subscription, firstValueFrom } from 'rxjs';
import { AgentActivity, Conversation, Customer, CustomerInfo, FieldServiceAgentService, GeneratedInsights, SearchResponseKB, SearchResultKB } from '../../shared/services/field-service-agent.service';
import { Auth, User, user } from '@angular/fire/auth';
import { marked } from 'marked';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCardModule } from '@angular/material/card';
import { AsyncPipe, KeyValuePipe, NgClass, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { SelectionModel } from '@angular/cdk/collections';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { GoogleMapsModule, MapDirectionsResponse, MapDirectionsService } from '@angular/google-maps';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';


@Component({
  selector: 'field-service-agent-job',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    GoogleMapsModule,
    MatButtonModule,
    MatCardModule,
    MatDividerModule,
    MatExpansionModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatToolbarModule,
    FormsModule,
    ReactiveFormsModule,
    KeyValuePipe,
    TitleCasePipe,
    UserPhotoComponent,
    MatTableModule,
    MatCheckboxModule,
    NgClass,
    MatTabsModule,
    MatFormFieldModule,
    AsyncPipe,
    ArchitectureComponent,
  ],
  templateUrl: './job.component.html',
  styleUrl: './job.component.scss'
})
export class FieldServiceAgentJobComponent implements AfterViewInit {
  agentActivity: AgentActivity | undefined;
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  createdRecommendations: boolean = false;
  userId: string = "";
  geminiImageName: string = "";
  geminiImageURL: string = "";

  customerInfo: CustomerInfo | undefined;
  customerConversations: any[]  = [];

  geminiResponse: string = "";
  kbSummary: string = "";
  kbResults: SearchResultKB[] = [];

  kbMsgCtrl = new FormControl<string>("");
  geminiMsgCtrl = new FormControl<string>("");

  extractedPendingTasksHTML = "";
  generatedInsightsHTML = "";
  generatedNextBestActionHTML = "";
  generatedSummaryHTML = "";
  selectedConversationHTML: string | null = null;
  insightsLoading = false;
  pageIndexKB = 0;
  pageSizeKB = 3;
  displayedColumns: string[] = [
    "select",
    "conversation",
    "category",
    "sentiment",
    "rating"
  ];
  dataSource = new MatTableDataSource(this.customerConversations);
  selection = new SelectionModel(true, []);
  selectedConversations: any = [];

  center: google.maps.LatLngLiteral = { lat: 24, lng: 12 };
  zoom = 4;

  directionsResults: google.maps.DirectionsResult | undefined;

  originAddress: string = "1600 Amphitheatre Pkwy, Mountain View, CA 94043, United States";
  destinationAddress: string = "100 Bay Vw Dr #100, Mountain View, CA 94043, United States";

  architecture: string = "/assets/architectures/p6_uj_1.svg";
  imageUploading: boolean = false;

  constructor(
    private activatedRoute: ActivatedRoute,
    public firebaseService: FirebaseService,
    public fieldServiceAgentService: FieldServiceAgentService,
    public mapDirectionsService: MapDirectionsService,
  ) {

    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;

        this.activatedRoute.queryParamMap.subscribe(async (queryParams) => {
          const activityId = queryParams.get("activityId");
          if (activityId) {
            this.agentActivity = await firstValueFrom(this.firebaseService.getAgentActivity(this.userId, activityId) as Observable<AgentActivity>);
            const customer: Customer = await firstValueFrom(this.fieldServiceAgentService.getCustomerInfo(this.agentActivity.customer_id) as Observable<Customer>);
            customer.customer_info.address = this.destinationAddress;
            this.customerInfo = customer.customer_info;
            this.customerConversations = customer.conversations;
            this.dataSource = new MatTableDataSource(this.customerConversations);
          }
        });
      }
    });

  }
  async ngAfterViewInit() {
    const { TravelMode } = await google.maps.importLibrary("routes") as google.maps.RoutesLibrary;
    const request: google.maps.DirectionsRequest = {
      destination: this.destinationAddress,
      origin: this.originAddress,
      travelMode: TravelMode.DRIVING
    };
    firstValueFrom(this.mapDirectionsService.route(request)).then((res: MapDirectionsResponse) => {
      this.directionsResults = res.result;
    });

  }

  async askGemini() {
    const geminiContext = `Question from user: ${this.geminiMsgCtrl.value} Knowledge Base: ${this.kbSummary}`
    const answer = await firstValueFrom(this.fieldServiceAgentService.askImageGemini(this.geminiImageName, geminiContext) as Observable<any>);
    this.geminiResponse = answer.response;
  }

  search() {
    this.fieldServiceAgentService.searchManuals(this.kbMsgCtrl.value || "", this.userId, []).subscribe(
      (res: any) => {
        const searchResponse: SearchResponseKB = res.responses;
        this.kbSummary = searchResponse.summary;
        this.kbResults = searchResponse.search_results.map((searchResult: SearchResultKB) => {
          searchResult.snippet = String(marked.parse(searchResult.snippet));
          searchResult.manual = String(marked.parse(searchResult.manual));
          return searchResult;
        });
        if (this.geminiImageName) {
          this.askGemini();
        }

      }
    );

  }
  updateInsights(generatedInsights: GeneratedInsights) {
    this.extractedPendingTasksHTML = String(marked.parse(generatedInsights.pending_tasks));
    this.generatedInsightsHTML = String(marked.parse(generatedInsights.insights));
    this.generatedNextBestActionHTML = String(marked.parse(generatedInsights.next_best_action));
    this.generatedSummaryHTML = String(marked.parse(generatedInsights.summary));
    this.insightsLoading = false;
  }

  async generateConversationsInsights(conversations: any) {
    this.clearInsights();
    this.insightsLoading = true;
    if (conversations.length == 1) {
      this.selectedConversationHTML = String(marked.parse(conversations[0].conversation));
    }
    else {
      this.selectedConversationHTML = null;
    }
    const generatedInsights: GeneratedInsights = await firstValueFrom(
      this.fieldServiceAgentService.generateConversationsInsights(
        conversations.map((conversation: any) => conversation)
      ) as Observable<GeneratedInsights>
    );
    this.updateInsights(generatedInsights);
  }

  clearInsights() {
    this.generatedInsightsHTML = "";
    this.extractedPendingTasksHTML = "";
    this.generatedNextBestActionHTML = "";
    this.generatedSummaryHTML = "";
    this.selectedConversationHTML = null;
  }

  handlePageEventKB(e: PageEvent) {
    this.pageIndexKB = e.pageIndex;
    this.pageSizeKB = e.pageSize;
  }
  slicedResultsKB() {
    return this.kbResults.slice(Math.min(this.pageIndexKB * this.pageSizeKB, this.kbResults.length), Math.min((this.pageIndexKB + 1) * this.pageSizeKB, this.kbResults.length))
  }
  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;
    return numSelected === numRows;
  }

  isSomeSelected() {
    console.log(this.selection.selected);
    return this.selection.selected.length > 0;
  }

  onSelection(_i: any, product: any, checked: any) {
    if (checked) {
      this.selectedConversations.push(product);
    } else {
      this.selectedConversations = this.selectedConversations.filter((res: any) => res.product_id != product.product_id)
    }
  }

  processFile(imageInput: any) {
    this.imageUploading = true
    const file: File = imageInput.files[0];
    const reader = new FileReader();
    //this.chatLoading = false
    reader.addEventListener('load', () => {

      this.firebaseService.uploadImageToStorage(file).then((snapshot) => {
        this.geminiImageName = snapshot.metadata.name;
        this.firebaseService.imageNameToDownloadURL(snapshot.metadata.name).then(
          (url) => {
            this.geminiImageURL = url;
            this.imageUploading = false;
          }
        )
      });
    });

    reader.readAsDataURL(file);
  }



}
