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

import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserPhotoComponent } from '../shared/user-photo/user-photo.component';

@Component({
  selector: 'app-terms-page',
  standalone: true,
  templateUrl: './terms-page.component.html',
  styleUrls: ['./terms-page.component.scss'],
  imports: [UserPhotoComponent]
})
export class TermsPageComponent {
  acceptAndAgreeButton: boolean = true

  constructor(private _router: Router) { }

  navigateToUserJourney() {
    this._router.navigate(['demo/user-journey'])
  }

  checkboxChecked(event: any) {
    if (event.target.checked) {
      this.acceptAndAgreeButton = false
    } else {
      this.acceptAndAgreeButton = true
    }
  }
}
