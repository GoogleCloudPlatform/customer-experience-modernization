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
import { MatDialog } from '@angular/material/dialog';
import { ArchitecureDiagramComponent } from '../../shared/architecure-diagram/architecure-diagram.component';
import { NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';

@Component({
  selector: 'app-guide',
  standalone: true,
  imports: [UserPhotoComponent, NgFor, RouterLink],
  templateUrl: './guide.component.html',
  styleUrl: './guide.component.css'
})
export class GuideComponent {
  demoList: any = [{
    demoId: "7.1",
    demoImg: "/assets/persona-headshots/Customer.thumbnail",
    demoTitle: "Customer Kiosk",
    description: "An interface where we welcome the user and ask for order ID The user selects the items they would like to return. Show a list with descriptive names and images to allow easy identification.",
    featuresHTML: `
      <ul>
        <li>An interface where we welcome the user and ask for order ID.</li>
        <li>The user selects the items they would like to return. Show a list with descriptive names and images to allow easy identification.<ul>`,
    instructionsHTML: `
      <u>`,
    demoHome: "/return-service/home",
    userArchitecture: "/assets/architectures/p7_uj_1.svg",
  },
  {
    demoId: "7.2",
    demoImg: "/assets/persona-headshots/Customer.thumbnail",
    demoTitle: "Agent View",
    description: "",
    featuresHTML: `
      <ul>
        <li> If the return is not processed due to the product image match failing then in the agent view, summarize all the actions that have been taken so far and the reason for why the return was rejected and possible next steps for the agent </li>
      </ul>`
    ,
    instructionsHTML: `
    `,
    demoHome: "/return-service/agent-view/home",
    userArchitecture: "/assets/architectures/p7_uj_1.svg",
  },

  ];

  constructor(public dialog: MatDialog) { }

  openArchitecture(architectureUrl: string) {
    this.dialog.open(ArchitecureDiagramComponent, {
      disableClose: true, height: "90%",
      data: { architecture: architectureUrl }
    });
  }
}
