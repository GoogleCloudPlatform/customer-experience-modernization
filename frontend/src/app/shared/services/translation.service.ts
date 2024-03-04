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

import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TranslationService {

  constructor() { }

  async translate(textList: string[], sourceLanguage: string, targetLanguage: string) {
    let data = { text: textList, target_language: targetLanguage, source_language: sourceLanguage }
    var response = await fetch(`${environment.apiURL}/p1/translate-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    var responseJson = await response.json()
    return responseJson.translation
  }

  async translateTextNodes(textNodes: any[], sourceLanguage: string, targetLanguage: string) {
    var textList = [];
    for (let i = 0; i < textNodes.length; i++) {
      textList.push(textNodes[i].nodeValue)
    }
    this.translate(textList, sourceLanguage, targetLanguage).then(translation => {
      for (let i = 0; i < textNodes.length; i++) {
        let translatedText = translation[i].translatedText
        if (translation[i].input[0] == ' ') {
          translatedText = ' ' + translatedText;
        }
        if (translation[i].input[translation[i].input.length - 1] == ' ') {
          translatedText += ' ';
        }

        textNodes[i].nodeValue = translatedText
      }
    })
  }

  translatePage(sourceLanguage: string, targetLanguage: string) {
    var walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
    );

    var node;
    var textNodes = [];
    while (node = walker.nextNode()) {

      if (node.parentElement?.tagName != "MAT-ICON" && !node.parentElement?.className.includes("google-symbols") && node.nodeValue?.trim().length) {
        // if(node.parentElement?.tagName != "SPAN" && !node.parentElement?.classList.contains("mat-mdc-select-min-line") )
        textNodes.push(node);
      }
    }
    this.translateTextNodes(textNodes, sourceLanguage, targetLanguage)
  }

}
