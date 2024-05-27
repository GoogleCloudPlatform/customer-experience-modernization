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
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
export interface DialogData {
  status: string;
}
@Component({
  selector: 'app-resolve-dialog',
  standalone: true,
  imports: [],
  templateUrl: './resolve-dialog.component.html',
  styleUrl: './resolve-dialog.component.css'
})
export class ResolveDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<ResolveDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData) { }

  onReject(): void {
    this.dialogRef.close({ status: 'reject' });
  }
  onAccept(): void {
    this.dialogRef.close({ status: 'accept' })
  }
}
