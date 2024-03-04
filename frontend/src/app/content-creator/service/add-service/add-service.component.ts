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

import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Component, ViewChild, inject } from '@angular/core';
import { MatStepper, MatStepperModule } from '@angular/material/stepper';
import { MatInputModule } from '@angular/material/input';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { NgFor, NgIf } from '@angular/common';
import { CreatorService, Service } from '../../../shared/services/creator.service';
import { FirebaseService } from '../../../shared/services/firebase.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatChipEditedEvent, MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { RouterLink } from '@angular/router';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription, firstValueFrom } from 'rxjs';
import { ProductService } from '../../../shared/services/product.service';
import { HttpResponse, HttpStatusCode } from '@angular/common/http';
import { ContentCreatorLogoComponent } from '../../logo/logo.component';
import { UserPhotoComponent } from '../../../shared/user-photo/user-photo.component';
import { ContentCreatorHeaderComponent } from '../../header/header.component';
import { CarouselModule } from 'primeng/carousel';
import { MatDividerModule } from '@angular/material/divider';
import { ContentCreatorProductListComponent } from '../../product/product-list/product-list.component';
import { MatTabsModule } from '@angular/material/tabs';

const NUM_IMAGES_TO_GENERATE = 3;

enum ItemTypes { Labels, Features, Categories };
@Component({
  selector: 'content-creator-add-service',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    MatStepperModule,
    MatFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
    MatDividerModule,
    MatInputModule,
    MatToolbarModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatIconModule,
    CarouselModule,
    RouterLink,
    ContentCreatorLogoComponent,
    UserPhotoComponent,
    ContentCreatorHeaderComponent,
    ContentCreatorProductListComponent,
    MatTabsModule
  ],
  templateUrl: './add-service.component.html',
  styleUrl: './add-service.component.scss'
})
export class ContentCreatorAddServiceComponent {
  firstFormGroup: FormGroup = this._formBuilder.group({
    firstCtrl: ['', Validators.required],
    secondCtrl: ['', Validators.required],

  });
  secondFormGroup: FormGroup = this._formBuilder.group({
    thirdCtrl: [''],
    fourthCtrl: [''],
  });

  selectedFiles?: FileList;
  isGenerated: boolean = false;
  isImageGenerated: boolean = false;
  isTitleGenerated: boolean = false;
  isSaved: boolean = false;
  generatedJSON: any;
  imagesNames: string[] = [];
  imagesURLs: string[] = [];
  title: string = "";
  description: string = "";
  labels: string[] = [];
  features: string[] = [];
  categories: string[] = [];
  similar_products: string[] = [];
  selectedFileNames: string[] = [];
  loading: boolean = false;

  progressInfos: any[] = [];
  message: string[] = [];
  public ItemTypesEnum = ItemTypes;

  previews: string[] = [];
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  addOnBlur = true;
  announcer = inject(LiveAnnouncer);
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  userId: string = "";
  imageDisplay: string = "";

  responsiveOptions = [
    {
      breakpoint: '1690px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '576px',
      numVisible: 1,
      numScroll: 1
    }

  ];

  @ViewChild('stepper', { static: false }) private stepper!: MatStepper;
  showAddProductCompoment: boolean = false;
  showAddServiceCompoment: boolean = false;

  constructor(
    private _formBuilder: FormBuilder,
    public creatorService: CreatorService,
    public firebaseService: FirebaseService,
    public productService: ProductService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;

      }
    });
  }

  async generateImages() {
    if (this.firstFormGroup.value.firstCtrl && this.firstFormGroup.value.secondCtrl) {
      this.loading = true;
      this.isImageGenerated = true;
      const imagePrompt = `Generate an image for this service: \n Title: ${this.firstFormGroup.value.firstCtrl} Description: ${this.firstFormGroup.value.secondCtrl}`
      this.creatorService.generateImage(imagePrompt, NUM_IMAGES_TO_GENERATE).subscribe((res) => {
        this.imagesNames = res.generated_images.map((generatedImage: any) => generatedImage.image_name);
        Promise.all(this.imagesNames.map(
          (imageName) => this.firebaseService.imageNameToDownloadURL(imageName).then(
            (imageURL) => this.previews.push(imageURL)))).then(() => this.imageDisplay = this.previews[0]);
        this.loading = false;
        this.stepper.next();

      });
    }
  }

  async generate() {
    if (this.imagesNames) {
      this.loading = true;
      this.isGenerated = true;
      this.creatorService.detectProductCategories(this.imagesNames).subscribe(async (res: any) => {
        this.generatedJSON = res;
        this.labels = res.vision_labels;
        this.features = res.images_features;
        this.categories = res.images_categories;
        const similarCategories: string[][] = await Promise.all(res.similar_products.map(
          async (similarProductId: string) =>
            firstValueFrom(this.productService.getProduct(similarProductId)).then((res: any) =>
              res.categories
            )));
        this.categories = [...new Set(this.categories.concat(...similarCategories))];
        this.imagesURLs = [];
        this.imagesNames.map(
          (imageName) => this.firebaseService.imageNameToDownloadURL(imageName).then(
            (imageURL) => this.imagesURLs.push(imageURL)));


        this.similar_products = res.similar_products;
        this.loading = false;
        this.stepper.next();
      });
    }
  }

  async generateTitleDescription() {
    if (this.labels || this.categories || this.features) {
      this.loading = true;
      this.isTitleGenerated = true;
      this.creatorService.generateTitleDescription(
        this.labels.concat(this.categories, this.features), `User title for the service: ${this.firstFormGroup.value.firstCtrl} \n User description for the service: ${this.firstFormGroup.value.firstCtrl}`
      ).subscribe((res: any) => {
        this.title = res.title;
        this.description = res.description;
        this.loading = false;
        this.stepper.next();
        this.secondFormGroup.setValue({
          thirdCtrl: this.title,
          fourthCtrl: this.description,
        })
        console.log(this.secondFormGroup.value.thirdCtrl);


      });
    }
  }

  saveService() {
    if (this.imagesURLs && this.title && this.description) {
      this.loading = true;
      this.isSaved = true;
      const service: Service = {
        title: this.secondFormGroup.value.thirdCtrl,
        description: this.secondFormGroup.value.fourthCtrl,
        image_urls: this.imagesURLs,
        labels: this.labels,
        categories: this.categories,
        features: this.features
      }
      this.creatorService.saveService(this.userId, service).subscribe((res: HttpResponse<string>) => {
        if (res.status == HttpStatusCode.Ok) {
          this.loading = false;
          this.stepper.next();
        }
      });
    }
  }

  getItemArray(itemType: ItemTypes): string[] {
    switch (itemType) {
      case ItemTypes.Labels:
        return this.labels;
      case ItemTypes.Features:
        return this.features;
      case ItemTypes.Categories:
        return this.categories;
      default:
        return this.labels;
    }
  }

  add(event: MatChipInputEvent, itemType: ItemTypes): void {
    const value = (event.value || '').trim();

    // Add our fruit
    if (value) {
      this.getItemArray(itemType).push(value);
    }

    // Clear the input value
    event.chipInput!.clear();
  }

  remove(item: string, itemType: ItemTypes): void {
    const itemArray = this.getItemArray(itemType)
    const index = itemArray.indexOf(item);

    if (index >= 0) {
      itemArray.splice(index, 1);

      this.announcer.announce(`Removed ${item}`);
    }
  }

  edit(item: string, event: MatChipEditedEvent, itemType: ItemTypes) {
    const value = event.value.trim();

    // Remove fruit if it no longer has a name
    if (!value) {
      this.remove(item, itemType);
      return;
    }

    // Edit existing fruit
    const itemArray = this.getItemArray(itemType)
    const index = itemArray.indexOf(item);
    if (index >= 0) {
      itemArray[index] = value;
    }
  }

  reset() {
    this.isTitleGenerated = false;
    this.isGenerated = false;
    this.isSaved = false;
    this.firstFormGroup.reset();
    this.secondFormGroup.reset();
    this.labels =[];
    this.categories =[];
    this.features =[];
    this.previews =[];
    this.selectedFileNames =[];
    this.selectedFileNames =[]
    this.stepper.reset();
  }
  changeDisplay(src: string) {
    this.imageDisplay = src;
  }
  addProduct() {
    this.showAddProductCompoment = true;
    this.showAddServiceCompoment = false;
  }
  addService() {
    this.showAddServiceCompoment = true;
    this.showAddProductCompoment = false;
  }
}
