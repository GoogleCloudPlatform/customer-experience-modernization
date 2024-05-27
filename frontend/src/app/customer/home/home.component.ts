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
import { MatDialog } from '@angular/material/dialog';
import { ObservablesService } from '../../shared/services/observables.service';
import { SearchService } from '../../shared/services/search.service';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AsyncPipe, NgIf } from '@angular/common';
import { AssistantChatComponent } from '../assistant-chat/assistant-chat.component';
import { MatDividerModule } from '@angular/material/divider';
import { AddToCartDetailsComponent } from '../add-to-cart-details/add-to-cart-details.component';
import { ProductDescriptionComponent } from '../product-description/product-description.component';
import { ProductDashboardComponent } from '../product-dashboard/product-dashboard.component';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CustomerHomeFooterComponent } from '../customer-home-footer/customer-home-footer.component';
import { Observable, Subscription, map, startWith } from 'rxjs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatMenuModule } from '@angular/material/menu';
import { translationOptions, TranslationLanguage } from '../../shared/constants/languages.constant';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';
import { FirebaseService } from '../../shared/services/firebase.service';
import { RecommendationsService } from '../../shared/services/recommendations.service';
import { Auth, User, user } from '@angular/fire/auth';
import { TranslationService } from '../../shared/services/translation.service';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { ProductService } from '../../shared/services/product.service';
import { MatSelectModule } from '@angular/material/select';
import { NgFor } from '@angular/common';
import { DfMessengerComponent } from '../df-messenger/df-messenger.component';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: true,
  imports: [
    UserPhotoComponent,
    FormsModule,
    MatProgressSpinnerModule,
    NgIf,
    NgFor,
    AssistantChatComponent,
    MatDividerModule,
    AddToCartDetailsComponent,
    ProductDescriptionComponent,
    ProductDashboardComponent,
    MatButtonModule,
    MatIconModule,
    CustomerHomeFooterComponent,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatAutocompleteModule,
    ReactiveFormsModule,
    AsyncPipe,
    MatMenuModule,
    ArchitectureComponent,
    MatSelectModule,
    DfMessengerComponent,
    RouterOutlet
  ]
})
export class CustomerHomeComponent implements OnInit {
  products: any;
  top10SearchProductResults: any = []
  inputSearch!: string;
  documentId: string | undefined;
  productResultsFromSystem: any = [];
  resMsgFromSystem: any = "";
  closeButtonDisplay: boolean = false;
  showTranslationForm: boolean = false;

  conversations: any;

  chatMsgs: any = []
  chatInputMessage!: string;
  sourceLanguage: string = "en";

  systemSuggestedProducts: any = [];
  systemSuggestedImages: any[] = [];
  loading: boolean = false;
  displayProductDetails: boolean = false;
  url: string = ""
  displayCart: boolean = false;
  translationOptions: TranslationLanguage[] = translationOptions;
  languageControl!: FormControl<TranslationLanguage | null | undefined>;
  filteredOptions!: Observable<TranslationLanguage[]>;

  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId = "";
  userEmail = "";
  photoURL!: string | null;
  architecture: string = "/assets/architectures/p1_uj_1_2.svg";
  imageProcessing: boolean = false;
  searchVal: any;
  selectedLang: any = '';
  showChatArea: boolean = false;

  constructor(
    public observablesService: ObservablesService,
    public searchService: SearchService,
    public dialog: MatDialog,
    public firebaseService: FirebaseService,
    public recommendationsService: RecommendationsService,
    public translationService: TranslationService,
    private activatedRoute: ActivatedRoute,
    public productService: ProductService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user
      if (aUser) {
        this.userId = aUser.uid;
        this.userEmail = aUser.email || "";
        this.photoURL = aUser.photoURL
      }
    });

    this.observablesService.getProductDisplay().subscribe(displayProd => {
      this.displayProductDetails = displayProd;
    });
    this.observablesService.getCartDisplay().subscribe(displayCart => {
      this.displayCart = displayCart;
    });
    this.activatedRoute.queryParamMap.subscribe((queryParams) => {
      const productId = queryParams.get("productId");
      if (productId) {
        this.productService.getProduct(productId).subscribe((res: any) => {
          this.observablesService.setProductDisplay(true);
          this.observablesService.setProductDescription(res);
        });
      }
    });

  }

  ngOnInit() {
    this.languageControl = new FormControl<TranslationLanguage | null | undefined>(translationOptions.find(i => i.value === 'en'));
    this.filteredOptions = this.languageControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return name ? this._filter(name as string) : this.translationOptions.slice();
      }),
    );
    this.selectedLang = this.languageControl?.value?.name;
  }

  displayFn(language: TranslationLanguage): string {
    return language && language.name ? language.name : '';
  }
  changeLang(event: any) {
    this.languageControl.patchValue(event)
    this.showTranslationForm = false;
    this.translateHome(event.value)
  }
  private _filter(name: string): TranslationLanguage[] {
    const filterValue = name.toLowerCase();

    return this.translationOptions.filter(option => option.name.toLowerCase().includes(filterValue));
  }

  search(searchVal: any, event?: any) {
    this.searchVal = searchVal
    this.firebaseService.analyticsLogEvent("search", { search_term: searchVal })
    this.recommendationsService.collectRecommendationsEvents("search", this.userId, [], {
      "search_info": { "search_query": searchVal }
    });
    this.displayCart = false;
    this.observablesService.setProductDisplay(false);
    event?.preventDefault();
    this.observablesService.setLoading(true);
    if (searchVal) {
      this.loading = true;
      this.searchService.getDocumentIdForTextSearch(searchVal).subscribe((res: any) => {
        this.documentId = res;
        this.loading = false;
        this.inputSearch = "";
      });
    }
  }

  processFile(imageInput: any, assistantChat: any) {
    this.imageProcessing = true;
    const file: File = imageInput.files[0];
    const reader = new FileReader();
    this.observablesService.setLoading(true)
    this.loading = true
    this.displayCart = false;
    this.observablesService.setProductDisplay(false);
    reader.addEventListener('load', (event: any) => {
      this.searchService.getDocumentIdForImageSearch(assistantChat, file, event).then((obs) => {
        obs.subscribe((res: any) => {
          this.chatInputMessage = "";
          this.documentId = res;
          this.url = event.target.result;
          this.loading = false;
        })
      });

    });
    reader.readAsDataURL(file);
  }

  close() {
    this.inputSearch = "";
  }

  clearHome() {
    this.documentId = undefined;
    this.loading = false;
    this.observablesService.setProductDisplay(false);
    this.displayCart = false;
    this.showChatArea = !this.showChatArea;
    this.close();
  }

  translateHome(lang: any) {
    let targetLanguage = lang;
    if (targetLanguage) {
      this.translationService.translatePage(this.sourceLanguage, targetLanguage);
      this.sourceLanguage = targetLanguage;
    }
  }
  addTocart() {
    this.displayCart = true;
    this.displayProductDetails = false;
    this.observablesService.sendIsAddToCart(true);
  }
}
