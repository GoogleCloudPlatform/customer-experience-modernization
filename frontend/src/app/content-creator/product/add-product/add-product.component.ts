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
import { CreatorService } from '../../../shared/services/creator.service';
import { FirebaseService } from '../../../shared/services/firebase.service';
import { UploadTaskSnapshot } from '@firebase/storage'
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatChipEditedEvent, MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { RouterLink } from '@angular/router';
import { Product } from '../../../shared/services/creator.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Subscription, firstValueFrom } from 'rxjs';
import { ProductService } from '../../../shared/services/product.service';
import { HttpResponse, HttpStatusCode } from '@angular/common/http';
import { ContentCreatorLogoComponent } from '../../logo/logo.component';
import { UserPhotoComponent } from '../../../shared/user-photo/user-photo.component';
import { ContentCreatorHeaderComponent } from '../../header/header.component';
import { MatDividerModule } from '@angular/material/divider';
import { CarouselModule } from 'primeng/carousel';
import { MatTabsModule } from '@angular/material/tabs';
import { ContentCreatorServiceListComponent } from '../../service/service-list/service-list.component';

enum ItemTypes { Labels, Features, Categories };
@Component({
  selector: 'content-creator-add-product',
  standalone: true,
  imports: [
    NgFor,
    NgIf,
    MatStepperModule,
    MatFormFieldModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatToolbarModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatIconModule,
    RouterLink,
    ContentCreatorLogoComponent,
    UserPhotoComponent,
    ContentCreatorHeaderComponent,
    MatDividerModule,
    CarouselModule,
    MatTabsModule,
    ContentCreatorServiceListComponent
  ],
  templateUrl: './add-product.component.html',
  styleUrls: ['./add-product.component.scss']
})
export class ContentCreatorAddProductComponent {

  firstFormGroup: FormGroup = this._formBuilder.group({
    firstCtrl: ['', Validators.required],
  });
  secondFormGroup: FormGroup = this._formBuilder.group({
    secondCtrl: [''],
  });
  thirdFormGroup: FormGroup = this._formBuilder.group({
    thirdCtrl: [''],
    fourthCtrl: [''],
  });
  showAddProductCompoment: boolean = false
  showAddServiceCompoment: boolean = false;
 
  selectedFiles: any[] = []
  isGenerated: boolean = false;
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

  @ViewChild('stepper', { static: false }) private stepper!: MatStepper;

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

  responsiveOptions = [
    {
      breakpoint: '2300px',
      numVisible: 2,
      numScroll: 1
    },

    {
      breakpoint: '1540px',
      numVisible: 1,
      numScroll: 1
    },

    {
      breakpoint: '1399px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '991px',
      numVisible: 3,
      numScroll: 1
    },
    {
      breakpoint: '767px',
      numVisible: 2,
      numScroll: 1
    },
    {
      breakpoint: '576px',
      numVisible: 1,
      numScroll: 1
    }

  ];
  selectFiles(event: any): void {
    this.message = [];
    this.progressInfos = [];
    this.selectedFileNames = [];

    this.selectedFiles = (event.target.files);
    this.selectedFiles = Object.keys(this.selectedFiles).map((key: any) => this.selectedFiles[key]);
    this.previews = [];
    if (this.selectedFiles && this.selectedFiles[0]) {
      const numberOfFiles = this.selectedFiles.length;
      for (let i = 0; i < numberOfFiles; i++) {
        const reader = new FileReader();

        reader.onload = (e: any) => {
          this.previews.push(e.target.result);
        };
        reader.readAsDataURL(this.selectedFiles[i]);
        this.selectedFileNames.push(this.selectedFiles[i].name);
      }
    }
  }

  async generate() {
    if (this.selectedFiles) {
      this.loading = true;
      this.imagesNames = await Promise.all(
        Array.from(this.selectedFiles).map(
          async (file) => this.firebaseService.uploadImageToStorage(file).then(
            (snapshot: UploadTaskSnapshot): string => {
              return snapshot.metadata.name as string;
            }))) as string[];
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
        this.labels.concat(this.categories, this.features), this.firstFormGroup.value.firstCtrl
      ).subscribe((res: any) => {
        this.title = res.title;
        this.description = res.description;
        this.loading = false;
        this.stepper.next();
        this.thirdFormGroup.setValue({
          thirdCtrl: this.title,
          fourthCtrl: this.description,
        })
      });
    }
  }

  saveProduct() {
    if (this.imagesURLs && this.title && this.description) {
      this.loading = true;
      this.isSaved = true;
      const product: Product = {
        title: this.thirdFormGroup.value.thirdCtrl,
        description: this.thirdFormGroup.value.fourthCtrl,
        image_urls: this.imagesURLs,
        labels: this.labels,
        categories: this.categories,
        features: this.features
      }
      this.creatorService.saveProduct(this.userId, product).subscribe((res: HttpResponse<string>) => {
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
    this.firstFormGroup.reset()
    this.secondFormGroup.reset()
    this.thirdFormGroup.reset()
    this.labels =[];
    this.categories =[];
    this.features =[];
    this.previews =[];
    this.selectedFileNames=[];
    this.selectedFiles=[];
    this.stepper.reset();
  }

  getReadableFileSizeString(fileSizeInBytes: any) {
    var i = -1;
    var byteUnits = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB'];
    do {
      fileSizeInBytes /= 1024;
      i++;
    } while (fileSizeInBytes > 1024);

    return Math.max(fileSizeInBytes, 0.1).toFixed(1) + byteUnits[i];
  }

  deleteFromArray(ind: any) {
    this.previews=[];
    this.selectedFiles.splice(ind, 1);
    if (this.selectedFiles && this.selectedFiles[0]) {
      const numberOfFiles = this.selectedFiles.length;
      for (let i = 0; i < numberOfFiles; i++) {
        const reader = new FileReader();
        reader.onload = (e: any) => {
          this.previews.push(e.target.result);
          };
        reader.readAsDataURL(this.selectedFiles[i]);
        this.selectedFileNames.push(this.selectedFiles[i].name);
      }
    }
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
