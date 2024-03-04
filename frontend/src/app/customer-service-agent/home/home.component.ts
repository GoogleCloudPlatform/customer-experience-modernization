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
import { CustomerServiceAgentAgentComponent } from '../agent/agent.component';
import { CustomerServiceAgentCustomerComponent } from '../customer/customer.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';
import { MatDividerModule } from '@angular/material/divider';

@Component({
  selector: 'customer-service-agent-home',
  standalone: true,
  imports: [
    MatToolbarModule,
    UserPhotoComponent,
    CustomerServiceAgentAgentComponent,
    CustomerServiceAgentCustomerComponent,
    ArchitectureComponent,
    MatDividerModule
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class CustomerServiceAgentHomeComponent implements OnInit{
  architecture: string = "/assets/architectures/p4_uj_1.svg";
  ngOnInit() {
    window.scroll(0, 0);
  }
}
