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

export const formatCardNumber = (cardNumber: any) => {
  const format = "#### - #### - #### - ####";
  if (!cardNumber) {
    return format;
  } else {
    return cardNumber.toString()
      .replace(/\s+/g, "")
      .replace(/[^0-9]/gi, "")
      .padEnd(16, "#")
      .match(/.{1,4}/g)
      .join(" - ");
  }
};

export const formatExpiryDate = (str: number) => {
  const format = "##";
  if (!str) {
    return format;
  } else {
    return str.toString().replace(/\s+/g, "").padEnd(2, "#");
  }
};

