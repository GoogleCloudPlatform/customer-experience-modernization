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

import { Injectable, Injector, inject } from '@angular/core';
import { Firestore, collection, collectionData, doc, docData, orderBy, query } from '@angular/fire/firestore';
import { GoogleAuthProvider, signInWithPopup } from '@firebase/auth';
import { getDownloadURL, ref, uploadBytesResumable, UploadTaskSnapshot, UploadTask } from "firebase/storage";
import { Auth } from '@angular/fire/auth';
import { Analytics, isSupported, logEvent } from '@angular/fire/analytics';
import { Storage } from '@angular/fire/storage';

@Injectable({
  providedIn: 'root'
})

export class FirebaseService {
  userData: any;
  private auth: Auth = inject(Auth);
  private analytics: Analytics | undefined;
  private firestore: Firestore = inject(Firestore);
  private storage: Storage = inject(Storage);

  constructor(private injector: Injector) {
    isSupported().then(() => {
      this.analytics = this.injector.get(Analytics);
    })
  }

  getDocument(collection: string, documentId: string) {
    let document = doc(this.firestore, `${collection}/${documentId}`);
    return docData(document);
  }
  getSearchResults(documentId: string) {
    return this.getDocument("website_search", documentId);
  }

  getRecommendationsResults(documentId: string) {
    return this.getDocument("website_recommendations", documentId);
  }

  getUserProductsAndServicesDoc(userId: string) {
    return doc(this.firestore, `content-creator/${userId}`)
  }

  getUserProducts(userId: string) {
    const userDoc = this.getUserProductsAndServicesDoc(userId);
    const productCollection = collection(this.firestore, `${userDoc.path}/products`);
    return collectionData(productCollection, { idField: 'id' })
  }

  getUserServices(userId: string) {
    const userDoc = this.getUserProductsAndServicesDoc(userId);
    const productCollection = collection(this.firestore, `${userDoc.path}/services`);
    return collectionData(productCollection, { idField: 'id' })
  }

  getChatMessages(userId: string, conversationId: string) {
    const userDoc = doc(this.firestore, "p4-conversations", userId);
    const userConversations = collection(this.firestore, `${userDoc.path}/conversations`);
    const conversationDoc = doc(this.firestore, userConversations.path, conversationId);
    const messagesCollection = collection(this.firestore, `${conversationDoc.path}/messages`);
    const orderedCollection = query(messagesCollection, orderBy("timestamp"));
    return collectionData(orderedCollection);
  }

  getCaseHistory(userId: string) {
    const userDoc = doc(this.firestore, "p4-conversations", userId);
    const userConversationsCollection = collection(this.firestore, `${userDoc.path}/conversations`);
    const orderedCollection = query(userConversationsCollection, orderBy("timestamp", "desc"));
    return collectionData(orderedCollection, { idField: 'id' });
  }

  getAgentActivity(userId: string, agentActivityId: string) {
    const userDoc = doc(this.firestore, "field-agent", userId);
    const activitiesCollection = collection(this.firestore, `${userDoc.path}/activities`);
    const activityDoc = doc(this.firestore, activitiesCollection.path, agentActivityId);
    return docData(activityDoc, { idField: 'id' });
  }

  getAgentActivities(userId: string) {
    const userDoc = doc(this.firestore, "field-agent", userId);
    const activitiesCollection = collection(this.firestore, `${userDoc.path}/activities`);
    const orderedCollection = query(activitiesCollection, orderBy("timestamp"));
    return collectionData(orderedCollection, { idField: 'id' });
  }


  async googleSignin() {
    const provider = new GoogleAuthProvider();

    return await signInWithPopup(this.auth, provider)

      .then((result) => {
        return result.user
      }).
      catch(

        function(error) {
          // Handle Errors here.
          var errorCode = error.code;
          if (errorCode === 'auth/account-exists-with-different-credential') {
            alert('You have already signed up with a different auth provider for that email.');
            // If you are using multiple auth providers on your app you should handle linking
            // the user's accounts here.
          } else {
            console.error(error);
          }
        });
  }

  uploadImageToStorage(file: any): UploadTask {
    const fileUUID = window.crypto.randomUUID();
    const storageRef = ref(this.storage, "images/" + fileUUID);
    return uploadBytesResumable(storageRef, file)
  }

  async getDownloadURLFromSnapshot(snapshot: UploadTaskSnapshot): Promise<string> {
    return await getDownloadURL(snapshot.ref);
  }

  analyticsLogEvent(eventName: string, eventParams?: object) {
    if (this.analytics) {
      logEvent(this.analytics, eventName, eventParams);
    }
  }

  imageNameToDownloadURL(imageName: string) {
    const storageRef = ref(this.storage, "images/" + imageName);
    return getDownloadURL(storageRef);
  }
}
