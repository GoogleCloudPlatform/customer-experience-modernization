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

import { Component, Input } from '@angular/core';
import { ReturnService } from '../../shared/services/return-service.service';
import { Router } from '@angular/router';
import { FirebaseService } from '../../shared/services/firebase.service';
import { DomSanitizer } from '@angular/platform-browser';
import { NgFor, NgIf } from '@angular/common';
import { SafePipe } from '../../shared/pipes/safe.pipe';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AlternativeItemsComponent } from '../alternative-items/alternative-items.component';

@Component({
  selector: 'app-upload-image',
  standalone: true,
  imports: [NgIf, NgFor, SafePipe, MatProgressSpinnerModule, AlternativeItemsComponent],
  templateUrl: './upload-image.component.html',
  styleUrl: './upload-image.component.css'
})
export class UploadImageComponent {
  @Input() returnItem: any;
  @Input()
  documentId!: string;
  @Input() userOrder: any
  showImageUploadSection: boolean = false;
  uploadingImage: boolean = false;
  uploadingVideo: boolean = false;
  validationInprogress: boolean = false;
  imageSource: any;
  videoSource: any
  showRefundSection: boolean = false;
  imageUploaded: boolean = false;
  videoUploaded: boolean = false;
  isAlternateProductSelectedId: any;
  differenceAmount!: string;
  imagePreview: any;
  videoPreview: any
  showAlternateProducts: boolean = false;
  today = new Date();
  constructor(public returnService: ReturnService, public router: Router, public firebaseService: FirebaseService, public sanitizer: DomSanitizer) { }
  ngOnInit() {
    this.returnItem = this.returnItem[0];
  }
  async processFile(imageInput: any) {
    this.uploadingImage = true;
    const file: File = imageInput.files[0];
    const reader = new FileReader();

    await this.firebaseService.uploadReturnItemImageToStorage(file).then((snapshot) => {
      this.firebaseService.returnItemImageToDownloadURL(snapshot.metadata.name).then(
        (url) => {
          reader.addEventListener('load', () => {
            let base64string = reader.result as string;
            this.imageSource = this.sanitizer.bypassSecurityTrustResourceUrl(base64string);
            this.imagePreview = this.imageSource.changingThisBreaksApplicationSecurity
            this.imageSource = this.imageSource.changingThisBreaksApplicationSecurity.split(',')[1]
            this.imageUploaded = true;
            this.validationInprogress = true;
            this.returnService.returnValidation(this.returnItem.image, this.imageSource, "").subscribe({
              next: (data: any) => {
                this.uploadingImage = false;
                this.validationInprogress = false;
                this.returnItem.return_metadata = {
                  image_uploaded: url,
                  video_uploaded: "",
                  is_valid: data.valid,
                  ai_validation_reason: data.reasoning,
                  return_status: 'under review',
                  return_type: data.return_type,
                  returned_date: this.returnService.getYYYYMMDD(this.today)
                }
                if (data.valid) {
                  this.showAlternateProducts = true;
                } else {
                  this.updateOrder(data, url, '');
                }
              },
              error: (error) => {
                this.uploadingImage = false;
                this.validationInprogress = false;
                throw error;
              }
            });
          });
          reader.readAsDataURL(file);
        }
      )
    });
  }

  async videoUploadtoGCS(videoInput: any): Promise<any> {
    this.uploadingVideo = true;
    const file: File = videoInput.files[0];
    return await this.firebaseService.uploadReturnItemVideoToStorage(file).then((snapshot) => {
      this.firebaseService.returnItemVideoURL(snapshot.metadata.name).then(
        (url) => {
          let gcsurl = 'gs://rl-llm-dev.appspot.com/' + snapshot.metadata.fullPath
          console.log("gcs video url", gcsurl);
          const reader = new FileReader();
          reader.addEventListener('load', () => {
            let base64string = reader.result as string;
            this.videoSource = this.sanitizer.bypassSecurityTrustResourceUrl(base64string);
            this.videoPreview = this.videoSource.changingThisBreaksApplicationSecurity
            this.videoSource = this.videoSource.changingThisBreaksApplicationSecurity.split(',')[1]
            this.videoUploaded = true;
            this.validationInprogress = true;
            this.returnService.returnValidation(this.returnItem.image, "", gcsurl).subscribe({
              next: (data: any) => {
                this.uploadingVideo = false;
                this.validationInprogress = false;
                this.returnItem.return_metadata = {
                  image_uploaded: "",
                  video_uploaded: gcsurl,
                  is_valid: data.valid,
                  ai_validation_reason: data.reasoning,
                  return_status: 'under review',
                  return_type: data.return_type,
                  returned_date: this.returnService.getYYYYMMDD(this.today),
                }
                if (data.valid) {
                  this.showAlternateProducts = true;
                } else {
                  this.updateOrder(data, "", url);
                }
              },
              error: (error) => {
                this.uploadingVideo = false;
                this.validationInprogress = false;
                throw error;
              }
            });
          });
          reader.readAsDataURL(file);
        }
      )
    });
  }

  updateOrder(data: any, storeUploadedImageInOrders: any, storeUploadedVideoUrlInOrders: any) {
    this.returnItem.is_returned = this.returnItem.isProductReturn;
    this.returnItem.return_metadata = {
      returned_date: this.returnService.getYYYYMMDD(this.today),
      // reason_selected: this.returnItem.returnReason,
      image_uploaded: storeUploadedImageInOrders,
      video_uploaded: storeUploadedVideoUrlInOrders,
      is_valid: data.valid,
      ai_validation_reason: data.reasoning,
      return_status: 'under review',
      return_type: data.return_type || 'No Longer Needed'
    }
    delete this.returnItem['isProductReturn'];

    this.userOrder.order_items.forEach((element: any, index: any) => {
      if (element.id === this.returnItem.id) {
        this.userOrder.order_items.splice(index, 1, this.returnItem);
      }
    });
    this.returnService.updateOrders(this.userOrder, this.documentId).subscribe({
      next: () => {
        if (data.valid) {
          this.router.navigateByUrl(`/return-service/refund-item/valid`)
        } else {
          this.router.navigateByUrl(`/return-service/refund-item/invalid`)
        }
      }, error: (error) => {
        throw error;
      }
    });
  }
  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }
  ngOnDestroy() {

  }
}
