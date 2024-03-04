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

import { Component, ElementRef } from '@angular/core';
import { LoginButtonComponent } from '../login-button/login-button.component';
import { Subscription } from 'rxjs';
import { LoginService } from '../services/login.service';
import { Router } from '@angular/router';
import { Dialog } from '@angular/cdk/dialog';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  photoURL: string | undefined;
  subscription: Subscription | undefined;
  acceptAndAgreeButton: boolean = true
  constructor(private _router: Router, public loginService: LoginService, private elementRef:ElementRef
    ,public dialog: Dialog) {
    this.subscription = this.loginService.getUserDetails().subscribe(res => {
      this.userLoggedIn = true;
      this.photoURL = res?.photoURL
    });
  }

  ngOnInit() {
    this.showLogIn()
  }

  userLoggedIn: boolean = false;
  navigateToUserJourney() {
    this.userLoggedIn = true;
    this._router.navigate(['user-journey'])
  }


  showLogIn(): void {
    const dialogRef = this.dialog.open(LoginButtonComponent, {
      disableClose: true,
      width: '350px',
      panelClass: 'login-container' 
    });
  }

  checkboxChecked(event: any) {
    if (event.target.checked) {
      this.acceptAndAgreeButton = false
    } else {
      this.acceptAndAgreeButton = true
    }
  }
}
