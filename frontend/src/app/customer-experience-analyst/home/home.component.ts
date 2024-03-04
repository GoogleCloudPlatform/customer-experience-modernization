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

import { Component, OnInit } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { environment } from '../../../environments/environment';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { Router, RouterLink } from '@angular/router';
import { ThemePalette } from '@angular/material/core';
import { Auth, User, user } from '@angular/fire/auth';
import { inject } from '@angular/core';
import { Subscription } from 'rxjs';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';
@Component({
  selector: 'customer-experience-analyst-home',
  standalone: true,
  imports: [
    MatToolbarModule,
    UserPhotoComponent,
    MatButtonModule,
    MatIconModule,
    MatTabsModule,
    MatDividerModule,
    RouterLink,
    ArchitectureComponent,
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class CustomerExperienceAnalystHomeComponent implements OnInit{
  lookerTab: boolean = true
  fadTab: boolean = false
  fraTab: boolean = false
  gadTab: boolean = false

  constructor(private _router: Router) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      if (aUser) {
        this.userId = aUser.uid;
        this.userId = 'xuBZNiigPqSt0ZpprUPyfbQpdFR2'
        this.photoURL = aUser.photoURL
      }
    });
  }
  ngOnInit() {
    window.scroll(0, 0);
  }
  overview: boolean = false
  environment = environment;
  links = ['First', 'Second', 'Third'];
  activeLink = this.links[0];
  background: ThemePalette = undefined;
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription | undefined;
  userId = "";
  photoURL!: string | null;
  genAIforMktURL: string = environment.genAIForMktURL;
  firebaseAnalyticsURL: string = environment.firebaseAnalyticsURL;
  firebaseRealtimeURL: string = environment.firebaseRealtimeURL;
  architecture: string = "/assets/architectures/p3_uj_csm.svg";


  toggleBackground() {
    this.background = this.background ? undefined : 'primary';
  }

  addLink() {
    this.links.push(`Link ${this.links.length + 1}`);
  }
  onClick(selectedValue: any) {
    if (selectedValue === 'Overview') {
      this.overview = true;
    }
  }

  tabFirebaseAnalyticsClick() {

    this._router.navigateByUrl('https://firebase.corp.google.com/project/rl-llm-dev/analytics/app/web:YTY0NGJkNDctOGE0Ni00MjM4LWJkNTUtM2VkMTRjYTVmY2Yx/streamview/realtime~2Foverview')
  }

  tab(val: any) {
    if (val == 'Looker') {
      this.lookerTab = true;
    } else if (val == 'FAD') {
      this.fadTab = true;
      this.lookerTab = false;
    } else if (val == 'FRA') {
      this.fraTab = true;
      this.lookerTab = false;
    } else if (val == 'GAD') {
      this.gadTab = true;
      this.lookerTab = false;
    }

  }

  goToLink(url: string){
    window.open(url, "_blank");
}
}
