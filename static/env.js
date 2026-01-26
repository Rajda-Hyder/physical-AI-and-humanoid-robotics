/**
 * Runtime Environment Loader for Docusaurus
 * This file is loaded in the HTML head and provides window.__ENV__ globally
 * Works seamlessly in dev (localhost:3000) and production (Railway)
 *
 * Usage: Access via window.__ENV__.VITE_API_URL (always available)
 */

(function() {
  // Detect if we're in development
  const isDev = window.location.hostname === 'localhost' ||
                window.location.hostname === '127.0.0.1';

  // Default URLs based on environment
  const defaultDevUrl = 'http://localhost:8000';
  const defaultProdUrl = 'https://physical-ai-and-humanoid-robotics-production-e85e.up.railway.app';

  // Initialize window.__ENV__ object
  window.__ENV__ = {
    // API Configuration
    VITE_API_URL: isDev ? defaultDevUrl : defaultProdUrl,
    VITE_API_TIMEOUT: '30000',
    VITE_DEBUG: isDev ? 'true' : 'false',

    // Firebase Configuration
    VITE_FIREBASE_API_KEY: 'AIzaSyBi4E3LKz2gvVpHRUSnLHbvdueysrwKZLY',
    VITE_FIREBASE_AUTH_DOMAIN: 'rag-chatbot-bf4d8.firebaseapp.com',
    VITE_FIREBASE_PROJECT_ID: 'rag-chatbot-bf4d8',
    VITE_FIREBASE_STORAGE_BUCKET: 'rag-chatbot-bf4d8.firebasestorage.app',
    VITE_FIREBASE_MESSAGING_SENDER_ID: '740750686590',
    VITE_FIREBASE_APP_ID: '1:740750686590:web:b37960fef6365a28135b2f',
  };

  // Debug logging in development
  if (isDev) {
    console.log('[ENV] Runtime environment initialized:', {
      hostname: window.location.hostname,
      env: {
        VITE_API_URL: window.__ENV__.VITE_API_URL,
        VITE_DEBUG: window.__ENV__.VITE_DEBUG,
      }
    });
  }
})();
