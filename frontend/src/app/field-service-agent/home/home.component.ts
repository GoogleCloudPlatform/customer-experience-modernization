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

import { Component, ViewChild, inject } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSort, MatSortModule, Sort } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { AgentActivity, FieldServiceAgentService } from '../../shared/services/field-service-agent.service';
import { Auth, User, user } from '@angular/fire/auth';
import { Observable, Subscription, firstValueFrom } from 'rxjs';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { FirebaseService } from '../../shared/services/firebase.service';
import { RouterLink } from '@angular/router';
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatFormFieldModule } from '@angular/material/form-field';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';

@Component({
  selector: 'field-service-agent-home',
  standalone: true,
  imports: [
    NgIf,
    MatButtonModule,
    MatIconModule,
    MatSortModule,
    MatTableModule,
    MatToolbarModule,
    MatPaginatorModule,
    UserPhotoComponent,
    RouterLink,
    MatFormFieldModule,
    NgFor,
    CommonModule,
    ArchitectureComponent,
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class FieldServiceAgentHomeComponent {
  activities: AgentActivity[] = [];
  imageSrc: string = "";
  productPosition: number = 0;
  displayedColumns: string[] = ['jobId', 'title', 'customer', 'address', 'complete'];
  dataSource = new MatTableDataSource(this.activities);
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  createdRecommendations: boolean = false;
  userId: string = "";
  userName: string = "";
  today = new Date();
  architecture: string = "/assets/architectures/p6_uj_1.svg";

  constructor(
    private _liveAnnouncer: LiveAnnouncer,
    public firebaseService: FirebaseService,
    private _snackBar: MatSnackBar,
    public fieldServiceAgentService: FieldServiceAgentService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
        this.userName = aUser.displayName || "";
        const activities$ = this.firebaseService.getAgentActivities(aUser.uid) as Observable<AgentActivity[]>
        activities$.subscribe((res: AgentActivity[]) => {
          this.activities = res;
          this.dataSource = new MatTableDataSource(this.activities)
        });
      }
    });
  }

  @ViewChild(MatSort) sort!: MatSort;

  ngAfterViewInit() {
    this.dataSource.sort = this.sort;
  }

  /** Announce the change in sort state for assistive technology. */
  announceSortChange(sortState: Sort) {
    // This example uses English messages. If your application supports
    // multiple language, you would internationalize these strings.
    // Furthermore, you can customize the message to add additional
    // details about the values being sorted.
    if (sortState.direction) {
      this._liveAnnouncer.announce(`Sorted ${sortState.direction}ending`);
    } else {
      this._liveAnnouncer.announce('Sorting cleared');
    }
  }

  completeRow(event: any, row: any) {
    event.preventDefault();
    this._snackBar.open(`Wow, completed ${row.id}`, 'Great');
  }

  changeActivityStatus(agentActivity: AgentActivity, newStatus: AgentActivity['status']) {
    agentActivity.status = newStatus;
    firstValueFrom(this.fieldServiceAgentService.putAgentActivity(this.userId, agentActivity.id || "", agentActivity));
  }


}
