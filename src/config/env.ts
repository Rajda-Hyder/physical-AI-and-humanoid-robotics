/**
 * Environment Variables Configuration
 *
 * This module exports environment variables that are loaded at build time.
 * Docusaurus v3 bundles this module normally, making env vars available to client code.
 */

// Firebase Configuration
export const FIREBASE_CONFIG = {
  apiKey: process.env.VITE_FIREBASE_API_KEY || '',
  authDomain: process.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: process.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: process.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: process.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: process.env.VITE_FIREBASE_APP_ID || '',
};

// API Configuration
export const API_CONFIG = {
  baseUrl: process.env.VITE_API_URL || 'http://localhost:8000',
  timeout: parseInt(process.env.VITE_API_TIMEOUT || '30000', 10),
  debug: process.env.VITE_DEBUG === 'true',
};

// Helper to check if Firebase is configured
export const isFirebaseConfigured = (): boolean => {
  return !!(
    FIREBASE_CONFIG.apiKey &&
    FIREBASE_CONFIG.authDomain &&
    FIREBASE_CONFIG.projectId &&
    FIREBASE_CONFIG.appId
  );
};
