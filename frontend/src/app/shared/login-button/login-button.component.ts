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
import { FirebaseService } from '../services/firebase.service';
import { Dialog } from '@angular/cdk/dialog';

@Component({
  selector: 'app-login-button',
  templateUrl: './login-button.component.html',
  styleUrl: './login-button.component.scss',
  standalone: true
})
export class LoginButtonComponent {
  photoURL: any;
  userLoggedIn: boolean = false;
  constructor(public firebaseService: FirebaseService,
    public dialog: Dialog) {
  }
  getLogin() {
    this.firebaseService.googleSignin()
  }

}
