# Authentication Setup Guide

This document outlines the Firebase authentication system that has been integrated into the Physical AI & Humanoid Robotics Textbook project.

## Overview

The project now includes a complete authentication system with:

- **Email/Password Authentication**: Users can sign up and log in with email credentials
- **Google OAuth**: Quick sign-in with Google accounts
- **Protected Routes**: Dashboard page accessible only to authenticated users
- **User Sessions**: Secure session management with Firebase
- **Authentication UI**: Dedicated login/register pages with professional styling

## Project Structure

### New Files Created

```
src/
├── config/
│   └── firebase.ts              # Firebase configuration and initialization
├── contexts/
│   └── AuthContext.tsx          # React Context for global auth state
├── pages/
│   ├── login.tsx                # Login page component
│   ├── register.tsx             # Registration page component
│   ├── dashboard.tsx            # Protected dashboard page
│   ├── auth.module.css          # Auth pages styling
│   └── dashboard.module.css     # Dashboard styling
└── theme/
    └── Root.tsx                 # Root wrapper with auth provider
```

### Modified Files

- `docusaurus.config.js` - Added Sign In and Dashboard links to navbar
- `src/pages/index.module.css` - Enhanced with animations and hover effects
- `package.json` - Added firebase and react-firebase-hooks dependencies

## Setup Instructions

### 1. Firebase Project Setup

1. Create a Firebase project at [firebase.google.com](https://firebase.google.com)
2. Enable Authentication with:
   - Email/Password provider
   - Google OAuth provider
3. Copy your Firebase config credentials

### 2. Environment Variables

Create a `.env.local` file in the project root (copy from `.env.example`):

```env
REACT_APP_FIREBASE_API_KEY=your_api_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=your_auth_domain_here
REACT_APP_FIREBASE_PROJECT_ID=your_project_id_here
REACT_APP_FIREBASE_STORAGE_BUCKET=your_storage_bucket_here
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
REACT_APP_FIREBASE_APP_ID=your_app_id_here
```

### 3. Google OAuth Configuration

For Google sign-in to work:

1. In Firebase Console → Authentication → Google Provider
2. Add your domain to authorized redirect URIs
3. Download the Google OAuth client credentials if running locally

### 4. Build and Deploy

```bash
pnpm install          # Install dependencies (already done)
pnpm run build        # Build the project
pnpm run serve        # Serve locally to test
```

## Authentication Flow

### User Registration

1. User visits `/register` page
2. Enters email and password
3. System validates password (minimum 6 characters)
4. Firebase creates user account
5. User is automatically logged in and redirected to `/dashboard`

### User Login

1. User visits `/login` page
2. Enters credentials (email + password OR clicks "Continue with Google")
3. Firebase validates credentials
4. User session is created and stored securely
5. User is redirected to `/dashboard`

### Protected Routes

The dashboard (`/dashboard`) is protected:
- If user is not authenticated, they're redirected to `/login`
- Authentication state is checked via the `useAuth()` hook
- Navigation links in navbar show Sign In or Dashboard based on auth state

### Sign Out

1. User clicks Sign Out button on dashboard
2. Firebase session is terminated
3. User is redirected to homepage

## Code Examples

### Using the Auth Hook

```tsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, loading, signOut } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return <div>Please sign in</div>;
  }

  return (
    <div>
      Welcome, {user.email}
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

### Creating Protected Pages

```tsx
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

function ProtectedPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate('/login');
    }
  }, [user, loading, navigate]);

  if (loading) return <div>Loading...</div>;
  if (!user) return null;

  return <div>Protected content</div>;
}
```

## Features Implemented

### Authentication System
- ✅ Email/Password sign up and login
- ✅ Google OAuth integration
- ✅ Session persistence
- ✅ Automatic redirect on auth state change
- ✅ Protected routes with role-based access

### User Interface
- ✅ Professional login/register pages
- ✅ Dashboard with user profile info
- ✅ Navigation bar with auth links
- ✅ Responsive design (mobile-friendly)
- ✅ Error handling and validation

### Homepage Enhancements
- ✅ Fade-in animations on page load
- ✅ Hover effects on buttons and cards
- ✅ Smooth transitions and transforms
- ✅ Staggered animation timing
- ✅ Interactive footer with underline animations

### Build & Deployment
- ✅ TypeScript type safety
- ✅ Server-side rendering compatible
- ✅ No build errors
- ✅ Optimized production build

## Security Considerations

1. **Environment Variables**: Keep `.env.local` out of version control (use `.env.example`)
2. **Firebase Rules**: Configure Firestore/Realtime Database security rules
3. **CORS**: Ensure Firebase domain is properly configured
4. **Session Storage**: Uses browser's secure session storage via Firebase
5. **Password Requirements**: Enforces minimum 6-character passwords

## Troubleshooting

### "Firebase not initialized" warning

This is expected during static builds. The Firebase client is only initialized in the browser (`typeof window !== 'undefined'`).

### Login/Register pages not accessible

1. Check that `.env.local` has valid Firebase credentials
2. Verify Firebase project has Email/Password provider enabled
3. Check browser console for CORS errors

### Google Sign-In not working

1. Verify Google OAuth is enabled in Firebase
2. Check authorized redirect URIs include your domain
3. Ensure JavaScript origin is configured in OAuth credentials

### Session not persisting

1. Check browser allows localStorage
2. Verify Firebase auth persistence is enabled
3. Check browser privacy settings aren't blocking cookies

## Next Steps

1. **User Profile Management**: Add profile page to edit user info
2. **Email Verification**: Require email verification before account activation
3. **Password Reset**: Implement "Forgot Password" functionality
4. **Two-Factor Authentication**: Add 2FA for enhanced security
5. **Analytics**: Track user engagement and authentication metrics
6. **Social Providers**: Add GitHub, Twitter, or other OAuth providers
7. **Role-Based Access**: Implement admin panel with different permission levels

## Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [React Firebase Hooks](https://github.com/CSFrequency/react-firebase-hooks)
- [Docusaurus Client Modules](https://docusaurus.io/docs/docusaurus-core#browseronly)
- [React Router v7](https://reactrouter.com/docs)
