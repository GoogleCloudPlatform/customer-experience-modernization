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

import { Component, Input } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ArchitecureDiagramComponent } from '../architecure-diagram/architecure-diagram.component';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-architecture',
  templateUrl: './architecture.component.html',
  styleUrl: './architecture.component.scss',
  standalone: true,
  imports: [RouterLink]
})
export class ArchitectureComponent {
  @Input() architecture!: string;
  constructor(public dialog: MatDialog , public _router: Router) { }
  showArchitetureDig(): void {
    this.dialog.open(ArchitecureDiagramComponent, {
      disableClose: true, height: "90%",
      data: { architecture: this.architecture }
    });
  }

  navigateToUserJourney() {
    this._router.navigate(['/demo/user-journey'])
  }
}
