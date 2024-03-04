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
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { NgFor } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ArchitecureDiagramComponent } from '../../shared/architecure-diagram/architecure-diagram.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'customer-guide',
  standalone: true,
  imports: [UserPhotoComponent, NgFor, RouterLink],
  templateUrl: './guide.component.html',
  styleUrl: './guide.component.scss'
})
export class CustomerGuideComponent {
  demoList: any = [{
    demoId: "1.1",
    demoImg: "/assets/persona-headshots/Customer.thumbnail",
    demoTitle: "Optimized Website Search",
    description: "Enhance your search experience with our advanced website search powered by Vertex AI Search and Vertex Vector Search. Harness the power of multimodal search to seamlessly navigate through text and images. Our conversational search interface makes it easy to discover the products and services you need. Get concise, fact-based summaries of your search results, complete with links to the original sources for further exploration.",
    featuresHTML: `
      <ul>
        <li>Integration of Vertex AI Search and Vertex Vector Search for multimodal website search across multiple sources.</li>
        <li>Implementation of a conversational search interface for enhanced product and service discovery.</li>
        <li>Provision of concise responses to users, accompanied by source links and factually grounded information</li>
      <ul>`,
    instructionsHTML: `
      <u>`,
    demoHome: "/customer/home",
    userArchitecture: "/assets/architectures/p1_uj_1_2.svg",
  },
  {
    demoId: "1.2",
    demoImg: "/assets/persona-headshots/Customer.thumbnail",
    demoTitle: "Optimized Website Navigation Experience",
    description: "",
    featuresHTML: `
      <ul>
        <li>Real-time translation of website content.</li>
        <li>Personalized recommendations based on user preferences.
          <ul>
            <li>More like this
            <li>Most popular
            <li>Others you may like</li>
            <li>Recommended for you</li>
          </ul>
        </li>
      </ul>`
    ,
    instructionsHTML: `
    `,
    demoHome: "/customer/home",
    userArchitecture: "/assets/architectures/p1_uj_1_2.svg",
  },

  ];

  externalDemoList: any = [{
    demoId: "1.3",
    demoImg: "/assets/persona-headshots/Customer.thumbnail",
    demoTitle: "Website Email Support",
    description: "",
    featuresHTML: `
      <ul>
        <li>Optimized website search, with review summarization, comparisons, and multimodal search.</li>
        <li>Optimized website navigation with translation, recommendations for you.</li>
        <li>Website email support, extracting metadata and intent from emails, responding with relevant links, integrated with Salesforce.</li>
      </ul>`,
    instructionsHTML: `
      <a href="https://valentine.corp.google.com/#/show/1701091709267963">Salesforce user and password</a>
    `,
    salesforceLink: `
      <a href="http://g/csm-salesforce-validation" target="_blank">Group to get your Salesforce token</a>
    `,
    userArchitecture: "/assets/architectures/p1_uj_3.svg",

    links: [{ name: "Email", link: "mailto:renatoleite@1987984870407.altostrat.com" }, { name: "Salesforce", link: "https://google-17b-dev-ed.develop.lightning.force.com/lightning/o/Case/home" }]
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
