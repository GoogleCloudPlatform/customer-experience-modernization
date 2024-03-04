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

export interface Audience {
    customer_id?: any;
    email?: any;
    city?: any;
    state?: any;
    channel?: any;
    total_purchases?: any;
    total_value?: any;
    total_emails?: any;
    loyalty_score?: any;
    is_media_follower: any;
    last_sign_up_date:any;
    last_purchase_date:any;
    last_activity_date:any;
    cart_total:any;
}