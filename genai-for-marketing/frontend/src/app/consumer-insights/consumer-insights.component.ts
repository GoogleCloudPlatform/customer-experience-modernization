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
import { LoginService } from '../services/login.service';
import { FormGroup, FormControl } from '@angular/forms';
import { TrendspottingService } from '../services/trendspotting.service';

@Component({
  selector: 'app-consumer-insights',
  templateUrl: './consumer-insights.component.html',
  styleUrl: './consumer-insights.component.scss'
})
export class ConsumerInsightsComponent {
  userLoggedIn: boolean = false;
  showchatboot: boolean = false;
  photoURL: any;
  generateSuccessMsg: boolean = false;
  insightResults: any[] = [];
  constructor(public loginService: LoginService, public trendsService: TrendspottingService) {
    this.loginService.getUserDetails().subscribe(res => {
      this.userLoggedIn = true;
      this.photoURL = res?.photoURL
    });
  }
  insightsForm = new FormGroup({
    name: new FormControl(),
  });

  onClickMarketingAssi() {
    this.showchatboot = true
  }
  
  onSubmit() {
    let obj = {
      query: this.insightsForm.controls.name?.value
    }
    this.trendsService.consumerInsightsSearch(obj).subscribe((res:any) => {
      this.generateSuccessMsg = true;
      this.insightResults = res?.results
    })
  }
}
