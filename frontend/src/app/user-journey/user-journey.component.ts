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
import { RouterLink } from '@angular/router';
import { UserPhotoComponent } from '../shared/user-photo/user-photo.component';
import { NgFor } from '@angular/common';
import { ArchitecureDiagramComponent } from '../shared/architecure-diagram/architecure-diagram.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'app-user-journey',
  standalone: true,
  templateUrl: './user-journey.component.html',
  styleUrls: ['./user-journey.component.scss'],
  imports: [UserPhotoComponent, NgFor, RouterLink]
})
export class UserJourneyComponent {

  userJourneyList: any = [{
    userId: "User journey 1",
    userImg: "/assets/persona-headshots/Customer.thumbnail",
    userTitle: "Customer",
    userContent: [
      "Optimized website search, with review summarization, comparisons, and multimodal search.",
      "Optimized website navigation with translation, recommendations for you.",
      "Website email support, extracting metadata and intent from emails, responding with relevant links, integrated with Salesforce."
    ],
    userHome: "/demo/customer",
    userArchitecture: "/assets/architectures/p1_uj_1_2.svg",
  },
  {
    userId: "User journey 2",
    userImg: "/assets/persona-headshots/Content_Creator.thumbnail",
    userTitle: "Content Creator",
    userContent: [
      "Generate a description from an image",
      "Generate long description",
      "Generate images based on features",
      "Generate Audio",
      "Similar tagging"
    ],
    userHome: "/content-creator/home",
    userArchitecture: "/assets/architectures/p2_uj_1_2.svg",
  },
  {
    userId: "User journey 3",
    userImg: "/assets/persona-headshots/Customer_Experience_Analyst.thumbnail",
    userTitle: "Customer Experience Analyst",
    userContent: [
      "Website performance analytics",
      "Data integration and visualization with Looker",
      "Connection with external data sources (CDP, GA4, Google Ads)",
      "Marketing assets generation (text and image)",
      "Campaign Activation"
    ],

    userHome: "/customer-experience-analyst/home",
    userArchitecture: "/assets/architectures/p3_uj_csm.svg",
  },
  {
    userId: "User journey 4",
    userImg: "/assets/persona-headshots/Customer_Service_Agent.thumbnail",
    userTitle: "Customer Service Agent",
    userContent: [
      "Search capability for internal knowledge bases and external references",
      "Response for customers inquiries with citations (grounding)",
      "Summarize historical conversations to enhance customer experience"
    ],

    userHome: "/customer-service-agent/home",
    userArchitecture: "/assets/architectures/p4_uj_1.svg",

  },
  {
    userId: "User journey 5",
    userImg: "/assets/persona-headshots/Contact_Center_Analyst.thumbnail",
    userTitle: "Contact Center Analyst",
    userContent: [
      "Contact center agent performance analytics",
      "Data integration and visualization with Looker",
      "Connection with external data sources (CDP, GA4, Google Ads)",
      "Campaign Activation"
    ],

    userHome: "/contact-center-analyst/home",
    userArchitecture: "/assets/architectures/p5_uj_1.svg",


  },

  {
    userId: "User journey 6",
    userImg: "/assets/persona-headshots/Field_Service_Agent.thumbnail",
    userTitle: "Field Service Agent",
    userContent: [
      "Search capability for internal knowledge bases and external references",
    ],

    userHome: "/field-service-agent/home",
    userArchitecture: "/assets/architectures/p6_uj_1.svg",
  }


  ];

  /*   greyOutUserJourneyList = [
  
    ] */

  constructor(public dialog: MatDialog) { }

  openArchitecture(architectureUrl: string) {
    this.dialog.open(ArchitecureDiagramComponent, {
      disableClose: true, height: "90%",
      data: { architecture: architectureUrl }
    });
  }
}
