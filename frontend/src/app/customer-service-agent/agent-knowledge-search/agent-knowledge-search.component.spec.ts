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

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgentKnowledgeSearchComponent } from './agent-knowledge-search.component';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';

describe('AgentKnowledgeSearchComponent', () => {
  let component: AgentKnowledgeSearchComponent;
  let fixture: ComponentFixture<AgentKnowledgeSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentKnowledgeSearchComponent],
      providers: [
        provideHttpClient(),
        provideAnimations()
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(AgentKnowledgeSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
