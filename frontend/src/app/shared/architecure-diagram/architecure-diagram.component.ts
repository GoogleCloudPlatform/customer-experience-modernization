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

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-architecure-diagram',
  templateUrl: './architecure-diagram.component.html',
  styleUrl: './architecure-diagram.component.scss',
  standalone: true
})
export class ArchitecureDiagramComponent {
  architecture: SafeUrl | undefined;

  constructor(
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: { architecture: string },
    private sanitizer: DomSanitizer,
  ) {
    this.architecture = this.sanitizer.bypassSecurityTrustResourceUrl(data.architecture);

  }

  close(): void {
    this.dialog.closeAll()
  }
}
