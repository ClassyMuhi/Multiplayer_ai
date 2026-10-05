import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type Auth,
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

export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey && firebaseConfig.apiKey.trim().length > 5
);

// Safely initialize Firebase App (Singleton pattern)
let app: FirebaseApp | null = null;
let authInstance: Auth | null = null;
let googleProviderInstance: GoogleAuthProvider | null = null;

if (isFirebaseConfigured) {
  try {
    app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
    authInstance = getAuth(app);
    googleProviderInstance = new GoogleAuthProvider();
    googleProviderInstance.setCustomParameters({
      prompt: 'select_account'
    });
  } catch (err) {
    console.warn('Firebase failed to initialize with provided config:', err);
    app = null;
    authInstance = null;
    googleProviderInstance = null;
  }
}

export const auth = authInstance;
export const googleProvider = googleProviderInstance;

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
  if (!authInstance || !googleProviderInstance) {
    throw new Error('Firebase Google Authentication is not configured. Please supply VITE_FIREBASE_API_KEY in .env or sign in using Preset Accounts / Custom Developer profile.');
  }

  try {
    const result = await signInWithPopup(authInstance, googleProviderInstance);
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
  if (!authInstance) return;
  try {
    await firebaseSignOut(authInstance);
  } catch (error) {
    console.error('Error signing out of Firebase:', error);
  }
};

/**
 * Listen to Firebase Auth state changes
 */
export const subscribeToAuthState = (
  callback: (user: FirebaseUser | null) => void
) => {
  if (!authInstance) {
    return () => {};
  }
  return onAuthStateChanged(authInstance, callback);
};

