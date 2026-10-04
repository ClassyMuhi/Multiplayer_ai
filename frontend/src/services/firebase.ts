import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User as FirebaseUser
} from 'firebase/auth';

// Vite environment variables for Firebase Configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || ''
};

// Initialize Firebase App ONLY (Singleton pattern)
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);

// Initialize Firebase Auth ONLY
export const auth = getAuth(app);

// Configure Google Auth Provider
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

export interface AuthUserProfile {
  uid: string;
  displayName: string | null;
  email: string | null;
  photoURL: string | null;
}

/**
 * Sign in using Firebase Google Authentication Popup
 */
export const signInWithGoogle = async (): Promise<AuthUserProfile> => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    return {
      uid: user.uid,
      displayName: user.displayName,
      email: user.email,
      photoURL: user.photoURL
    };
  } catch (error: any) {
    let friendlyMessage = 'Failed to sign in with Google.';
    
    if (error.code === 'auth/popup-closed-by-user') {
      friendlyMessage = 'Sign-in popup was closed before completing authentication.';
    } else if (error.code === 'auth/popup-blocked') {
      friendlyMessage = 'Sign-in popup was blocked by your browser. Please allow popups for this site.';
    } else if (error.code === 'auth/cancelled-popup-request') {
      friendlyMessage = 'Only one sign-in popup can be opened at a time.';
    } else if (error.code === 'auth/network-request-failed') {
      friendlyMessage = 'Network error during sign in. Please check your internet connection.';
    } else if (error.code === 'auth/unauthorized-domain') {
      friendlyMessage = 'This domain (localhost) is not authorized in your Firebase Authentication Console.';
    } else if (error.message) {
      friendlyMessage = error.message;
    }

    const customError = new Error(friendlyMessage);
    (customError as any).code = error.code;
    throw customError;
  }
};

/**
 * Sign out of Firebase Authentication
 */
export const signOutUser = async (): Promise<void> => {
  try {
    await firebaseSignOut(auth);
  } catch (error) {
    console.error('Error signing out of Firebase:', error);
    throw error;
  }
};

/**
 * Listen to Firebase Auth state changes
 */
export const subscribeToAuthState = (
  callback: (user: FirebaseUser | null) => void
) => {
  return onAuthStateChanged(auth, callback);
};
