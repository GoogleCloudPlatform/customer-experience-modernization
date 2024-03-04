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

import { AfterViewInit, Component, ViewChild, inject } from '@angular/core';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { MatSort, Sort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { User } from '@firebase/auth';
import { Auth, user } from '@angular/fire/auth';
import { Observable, Subscription } from 'rxjs';
import { FirebaseService } from '../../../shared/services/firebase.service';
import { CreatorService, Service } from '../../../shared/services/creator.service';
import { ContentCreatorServicePreviewComponent } from '../service-preview/service-preview.component';
import { NgClass, NgIf } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatDividerModule } from '@angular/material/divider';


@Component({
  selector: 'content-creator-service-list',
  standalone: true,
  imports: [
    NgIf,
    NgClass,
    MatButtonModule,
    MatIconModule,
    MatSortModule,
    MatTableModule,
    MatPaginatorModule,
    ContentCreatorServicePreviewComponent,
    MatDividerModule
  ],
  templateUrl: './service-list.component.html',
  styleUrl: './service-list.component.css'
})
export class ContentCreatorServiceListComponent implements AfterViewInit {
  services: Service[] = [];
  service: any | undefined;
  imageSrc: string = "";
  servicePosition: number = 0;
  displayedColumns: string[] = ['title', 'categories', 'delete'];
  dataSource = new MatTableDataSource(this.services);
  private auth: Auth = inject(Auth);
  user$ = user(this.auth);
  userSubscription: Subscription;
  createdRecommendations: boolean = false;
  userId: string = "";
  paginator!: MatPaginator;

  constructor(
    private _liveAnnouncer: LiveAnnouncer,
    public firebaseService: FirebaseService,
    public creatorService: CreatorService,
  ) {
    this.userSubscription = this.user$.subscribe((aUser: User | null) => {
      //handle user state changes here. Note, that user will be null if there is no currently logged in user

      if (aUser) {
        this.userId = aUser.uid;
        let services$ = this.firebaseService.getUserServices(aUser.uid) as Observable<Service[]>
        services$.subscribe((res: Service[]) => {
          this.services = res;
          if (this.services.length > 0) {
            this.dataSource = new MatTableDataSource(this.services)
            this.service = this.services[0]
            this.imageSrc = this.service.image_urls[0];
            this.servicePosition = 0;
          }
        });
      }
    });
  }

  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) set matPaginator(mp: MatPaginator) {
    this.paginator = mp;
    this.setDataSourceAttributes();
  }

  setDataSourceAttributes() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }
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

  previewRow(row: any) {
    this.service = row;
    this.imageSrc = this.service.image_urls[0];
  }
  deleteRow(row: any) {
    this.creatorService.deleteService(this.userId, row.id).subscribe();
  }

}
