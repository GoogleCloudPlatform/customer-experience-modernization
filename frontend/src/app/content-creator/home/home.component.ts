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
import { ContentCreatorServiceListComponent } from '../service/service-list/service-list.component';
import { ContentCreatorProductListComponent } from '../product/product-list/product-list.component';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { ContentCreatorHeaderComponent } from '../header/header.component';
import { ContentCreatorMenuComponent } from '../menu/menu.component';
import { ContentCreatorLogoComponent } from '../logo/logo.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { Observable, Subscription, map, startWith } from 'rxjs';
import { UserPhotoComponent } from '../../shared/user-photo/user-photo.component';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { ContentCreatorAddProductComponent } from '../product/add-product/add-product.component';
import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { ContentCreatorAddServiceComponent } from '../service/add-service/add-service.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { translationOptions, TranslationLanguage } from '../../shared/constants/languages.constant';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslationService } from '../../shared/services/translation.service';
import { MatSelectModule } from '@angular/material/select';
import { ArchitectureComponent } from '../../shared/architecture/architecture.component';


@Component({
  selector: 'content-creator-home',
  standalone: true,
  imports: [
    ContentCreatorServiceListComponent,
    ContentCreatorProductListComponent,
    ContentCreatorHeaderComponent,
    ContentCreatorAddProductComponent,
    ContentCreatorAddServiceComponent,
    ContentCreatorMenuComponent,
    ContentCreatorLogoComponent,
    ArchitectureComponent,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    UserPhotoComponent,
    RouterLink,
    MatTabsModule,
    MatDividerModule,
    NgIf,
    NgFor,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    MatFormFieldModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    AsyncPipe
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class ContentCreatorHomeComponent {
  title = 'material-responsive-sidenav';
  isCollapsed = true;
  subscription: Subscription | undefined;
  currentLoggedInUser: any;
  showAddProductCompoment: boolean = false
  showAddServiceCompoment: boolean = false;
  translationOptions: TranslationLanguage[] = translationOptions;
  languageControl!: FormControl<TranslationLanguage | null | undefined>;
  filteredOptions!: Observable<TranslationLanguage[]>;
  sourceLanguage: string = "en";
  architecture: string = "/assets/architectures/p2_uj_1_2.svg";

  constructor(public translationService: TranslationService) { }
  ngOnInit() {
    this.languageControl = new FormControl<TranslationLanguage | null | undefined>(translationOptions.find(i => i.value === 'en'));
    this.filteredOptions = this.languageControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const name = typeof value === 'string' ? value : value?.name;
        return name ? this._filter(name as string) : this.translationOptions.slice();
      }),
    );
  }

  displayFn(language: TranslationLanguage): string {
    return language && language.name ? language.name : '';
  }
  changeLang(event: any) {
    this.translateHome(event.option.value)
  }
  private _filter(name: string): TranslationLanguage[] {
    const filterValue = name.toLowerCase();

    return this.translationOptions.filter(option => option.name.toLowerCase().includes(filterValue));
  }
  translateHome(lang: any) {
    let targetLanguage = lang?.value;
    if (targetLanguage) {
      this.translationService.translatePage(this.sourceLanguage, targetLanguage);
      this.sourceLanguage = targetLanguage;
    }
  }

  addProduct() {
    this.showAddProductCompoment = true;
    this.showAddServiceCompoment = false;
  }
  addService() {
    this.showAddServiceCompoment = true;
    this.showAddProductCompoment = false;
  }
}
