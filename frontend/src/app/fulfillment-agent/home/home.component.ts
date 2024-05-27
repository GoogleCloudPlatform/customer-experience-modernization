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

import { LiveAnnouncer } from '@angular/cdk/a11y';
import { Component, ViewChild, inject } from '@angular/core';
import { Auth, User, user } from '@angular/fire/auth';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSort, MatSortModule, Sort } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { Subscription, Observable, firstValueFrom } from 'rxjs';
import { AgentActivity, FieldServiceAgentService } from '../../shared/services/field-service-agent.service';
import { FirebaseService } from '../../shared/services/firebase.service';
import { NgIf, NgFor, CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterLink } from '@angular/router';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'fulfillment-agent-home',
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
    MatSelectModule,
    FormsModule
  ],

  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class FulfillmentAgentHomeComponent {
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
  userEmail!: string | null;
  orders: any[] = [];
  selectedOrderDetails: any;
  itemStatus = ['Open', 'In Progress', 'Completed']
  selectedOrderItemStatus = 'Open'
  inProgressOrder: any = [];
  completedOrder: any = [];
  selectedInprogressOrderView: any = null;
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
        this.userEmail = aUser.email

        this.firebaseService.getUserOrders(aUser.uid).subscribe((res: any) => {
          this.orders = res;
          //append status to each order item
          this.orders.map((obj) => {
            obj.order_items.map((obj: { status: string; }) => {
              obj.status = 'Open';
            })
            return obj;
          })
          console.log(this.orders)

          this.selectedOrderDetails = this.orders[0];
        })
        const activities$ = this.firebaseService.getAgentActivities(aUser.uid) as Observable<AgentActivity[]>
        activities$.subscribe((res: AgentActivity[]) => {
          this.activities = res;
          this.dataSource = new MatTableDataSource(this.activities)
        });
      }
    });
  }
  ngOnInit() {

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

  showOrderDetailedView(orderId: any) {
    this.selectedOrderDetails = this.orders.filter((ele: any) => {
      if (ele.id === orderId) {
        return ele
      }
    })[0];
  }

  setOrderItemStatus(val: any, selectedOrderDetails: any, item: any) {
    this.orders.map((ele: any) => {
      if (ele.id == selectedOrderDetails.id) {
        ele.order_items.map(() => {
          if (ele.order_items.id == item.id) {
            ele.order_items.status = val;
          }
        })
      }
    })
  }
  onItemStatusChange(val: any, selectedOrderDetails: any, item: any) {
    if (val == 'In Progress' && this.inProgressOrder.length > 0) {
      for (let i = 0; i < this.inProgressOrder.length; i++) {
        if (selectedOrderDetails.id !== this.inProgressOrder[i].id) {
          this.inProgressOrder.push(selectedOrderDetails);
          this.setOrderItemStatus(val, selectedOrderDetails, item)
        }
      }
    }
    else if (val == 'In Progress' && this.inProgressOrder.length == 0) {
      this.inProgressOrder.push(selectedOrderDetails);
      this.setOrderItemStatus(val, selectedOrderDetails, item)
    }
    else if (val == 'Completed' && this.completedOrder.length > 0) {
      this.completedOrder.push(selectedOrderDetails);
      this.setOrderItemStatus(val, selectedOrderDetails, item)
    }
    this.selectedInprogressOrderView = this.inProgressOrder[0];
  }
  showInprogressOrderDetailedView(orderId: any) {
    this.selectedInprogressOrderView = this.inProgressOrder.filter((ele: any) => {
      if (ele.id === orderId) {
        return ele
      }
    })[0];
  }
}
