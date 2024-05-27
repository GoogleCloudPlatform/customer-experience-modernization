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

import { NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';

@Component({
  selector: 'app-refund-item',
  standalone: true,
  imports: [NgIf, ArchitectureComponent],
  templateUrl: './refund-item.component.html',
  styleUrl: './refund-item.component.css'
})
export class RefundItemComponent {
  architecture: string = "/assets/architectures/p7_uj_1.svg";

  constructor(public router: Router, private route: ActivatedRoute) { }
  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }

  isValid: string | null = "valid";

  ngOnInit() {
    this.isValid = this.route.snapshot.paramMap.get('is_valid');
  }
}
