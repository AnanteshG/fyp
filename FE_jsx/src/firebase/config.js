// Firebase Configuration
// Get your config from Firebase Console > Project Settings > Your apps > SDK setup and configuration
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyC...", // Get from Firebase Console
  authDomain: "fy-project-518d9.firebaseapp.com",
  projectId: "fy-project-518d9",
  storageBucket: "fy-project-518d9.appspot.com",
  messagingSenderId: "...", // Get from Firebase Console
  appId: "...", // Get from Firebase Console
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

export default app;
