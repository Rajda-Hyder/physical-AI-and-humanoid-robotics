// src/types/global.d.ts

/**
 * Global environment variables for Docusaurus v3
 * Accessible in browser code via `window.__ENV__`
 */
interface Window {
  __ENV__?: {
    VITE_FIREBASE_API_KEY: string;
    VITE_FIREBASE_AUTH_DOMAIN: string;
    VITE_FIREBASE_PROJECT_ID: string;
    VITE_FIREBASE_STORAGE_BUCKET: string;
    VITE_FIREBASE_MESSAGING_SENDER_ID: string;
    VITE_FIREBASE_APP_ID: string;
    VITE_API_URL: string;
    VITE_API_TIMEOUT: string;
    VITE_DEBUG: string;
  };
}
