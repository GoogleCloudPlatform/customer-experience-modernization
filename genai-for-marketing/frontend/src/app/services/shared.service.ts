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

import { Injectable, inject } from '@angular/core';
import { LoginService } from './login.service';
import { Firestore, collection, collectionData } from '@angular/fire/firestore';
import { GoogleAuthProvider, getAuth, signInWithPopup, User } from '@firebase/auth';
import { getStorage, ref, uploadBytesResumable } from "firebase/storage";
import { initializeApp } from '@angular/fire/app';
import { Auth } from '@angular/fire/auth';
@Injectable({
  providedIn: 'root'
})
export class SharedService {
  userData: any;
  private auth: Auth = inject(Auth);
  
  constructor(private fs: Firestore, public loginservice: LoginService) { }
  fireBaseConfig = {
    apiKey: "=",
    authDomain: "",
    projectId: "",
    storageBucket: "",
    messagingSenderId: "",
    appId: "",
    measurementId: ""
  };


  // async googleSignin() {
  //   const provider = new GoogleAuthProvider();

  //   // const credential = await this.afAuth.signInWithPopup(provider);
  //   // return this.updateUserData(credential.user);
  //   const app = initializeApp(this.fireBaseConfig);
  //   const auth = getAuth(app);
  //   const storage = getStorage(app);
  //   return await signInWithPopup(auth, provider)
  //     .then((result) => {
  //       return result.user
  //     }).
  //     catch(

  //       function (error) {
  //         // Handle Errors here.
  //         var errorCode = error.code;
  //         var errorMessage = error.message;
  //         var photoUrl = error.photoUrl;
  //         // The email of the user's account used.
  //         var email = error.email;
  //         // The firebase.auth.AuthCredential type that was used.
  //         var credential = error.credential;
  //         if (errorCode === 'auth/account-exists-with-different-credential') {
  //           alert('You have already signed up with a different auth provider for that email.');
  //           // If you are using multiple auth providers on your app you should handle linking
  //           // the user's accounts here.
  //         } else {
  //           console.error(error);
  //         }
  //       });
  // }
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
}
