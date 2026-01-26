/**
 * Safe environment loader for Docusaurus (NO import.meta, NO process.env)
 * Works in browser and build.
 */

declare global {
  interface Window {
    __ENV__?: Record<string, string>;
  }
}

const env = typeof window !== 'undefined' ? window.__ENV__ || {} : {};

export const FIREBASE_CONFIG = {
  apiKey: env.VITE_FIREBASE_API_KEY || '',
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: env.VITE_FIREBASE_APP_ID || '',
};

export const API_CONFIG = {
  baseUrl: env.VITE_API_URL || 'http://localhost:8000',
  timeout: Number.isFinite(Number(env.VITE_API_TIMEOUT))
    ? Number(env.VITE_API_TIMEOUT)
    : 30000,

  debug: env.VITE_DEBUG === 'true',
};

export const isFirebaseConfigured = () =>
  Boolean(
    FIREBASE_CONFIG.apiKey &&
    FIREBASE_CONFIG.authDomain &&
    FIREBASE_CONFIG.projectId &&
    FIREBASE_CONFIG.appId
  );
