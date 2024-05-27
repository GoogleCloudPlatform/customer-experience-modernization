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
import { FirebaseService } from '../../../shared/services/firebase.service';
import { NgFor, NgIf } from '@angular/common';
import { Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ReturnService } from '../../../shared/services/return-service.service';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ResolveDialogComponent } from '../../resolve-dialog/resolve-dialog.component';
import { ArchitectureComponent } from '../../../shared/architecture/architecture.component';

@Component({
  selector: 'app-agent-view-home',
  standalone: true,
  imports: [NgIf, NgFor, MatSnackBarModule, MatDialogModule, ArchitectureComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  architecture: string = "/assets/architectures/p7_uj_1.svg";
  orders: any[] = [];
  selectedKiosk: boolean = false;
  selectedOrder: any;
  returningItemsLength: any;
  returnStatus: any;
  today = new Date()
  ngOnInit() {
    this.returnService.getYYYYMMDD(this.today)
    this.firebase.getOrdersDocuments().subscribe(async (res: any) => {
      this.orders = res?.filter((ele: any) => {
        return ele?.order_items?.find((res: any) => { return (res.is_returned && !res.return_metadata.is_valid) });
      }).sort((a: { order_items: any[]; }, b: { order_items: any[]; }) => {
        let sortedItems1 = this.sortOrderItems(a.order_items);
        let sortedItems2 = this.sortOrderItems(b.order_items);
        let item1 = new Date(sortedItems1[0].return_metadata?.returned_date);
        let item2 = new Date(sortedItems2[0].return_metadata?.returned_date);

        if (item1?.getTime() < item2?.getTime()) return 1
        else if (item1?.getTime() > item2?.getTime()) return -1;
        else return 0;
      })
    });
  }
  sortOrderItems(order_items: any[]) {
    return order_items.sort((a, b) => {
      var d1 = new Date(a.return_metadata?.returned_date);
      var d2 = new Date(b.return_metadata?.returned_date);
      if (d1.getTime() < d2.getTime()) return 1
      else if (d1.getTime() > d2.getTime()) return -1;
      else return 0;
    })
  }

  constructor(public firebase: FirebaseService, public snackbar: MatSnackBar, public router: Router, public returnService: ReturnService, public dialog: MatDialog) { }

  navigateToHome() {
    this.router.navigateByUrl('/return-service/home');
  }

  seeWhyBtn(order: any) {
    this.selectedKiosk = true;
    this.selectedOrder = order;
    this.returningItemsLength = order.order_items.filter((ele: any) => {
      return ele.is_returned
    }).length;
  }

  resolveItem(order: any, returnId: string) {
    this.openDialog(order, returnId);
  }

  openDialog(order: any, returnId: string): void {
    const dialogRef = this.dialog.open(ResolveDialogComponent, {
      width: '300px',
      height: '200px',
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed', result);
      this.updateOrder(order, returnId, result.status);
    });
  }
  updateOrder(order: any, returnId: string, status: string) {
    order.order_items.forEach((element: any) => {
      if (element.id === returnId) {
        element.return_metadata.is_valid = true;
        if (status == 'accept') {
          element.return_metadata.return_status = 'accept';
        } else {
          element.return_metadata.return_status = 'reject';
        }
        element.return_metadata.ai_validation_reason = element.return_metadata.ai_validation_reason + " Verified by Human "
      }
    });
    this.returnService.updateOrders(order, order.id).subscribe((res) => {
      this.showSnackbar(`Return Item issue marked as ${status}`, 'Close', '6000');
      if (res && status == 'accept') {
        this.router.navigateByUrl('/return-service/refund-item/valid');
      } else {
        this.router.navigateByUrl('/return-service/refund-item/reject');
      }
    });
  }

  showSnackbar(content: any, action: any, duration: any) {
    let sb = this.snackbar.open(content, action, {
      duration: duration,
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }
}
