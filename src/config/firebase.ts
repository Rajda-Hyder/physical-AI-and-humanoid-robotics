import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { FIREBASE_CONFIG } from './env';

// Firebase configuration from environment variables
const firebaseConfig = FIREBASE_CONFIG;

let app: ReturnType<typeof initializeApp> | null = null;
let auth: ReturnType<typeof getAuth> | null = null;

// Initialize Firebase only on client side
if (typeof window !== 'undefined') {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } catch (error) {
    console.warn('Firebase not initialized (likely build time or missing config)', error);
  }
}

export { app, auth };
export default app;
