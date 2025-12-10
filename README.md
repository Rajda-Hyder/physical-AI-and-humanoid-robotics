# Physical AI & Humanoid Robotics Textbook

<div align="center">

**Learn to build and control the future of embodied intelligence**

[![Docusaurus v3](https://img.shields.io/badge/Docusaurus-v3.0-blue)](https://docusaurus.io/)
[![React 18](https://img.shields.io/badge/React-18.2-blue)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Firebase Auth](https://img.shields.io/badge/Firebase-Authentication-orange)](https://firebase.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](./LICENSE)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success)](./docs/intro.mdx)

[View Live](#) • [Documentation](#features) • [Get Started](#quick-start) • [Contributing](#contributing)

</div>

---

## 📚 Overview

**Physical AI & Humanoid Robotics** is a comprehensive, interactive textbook designed to teach students and professionals how to build, understand, and deploy embodied AI systems and humanoid robots. Built with modern web technologies, it combines educational content with hands-on learning and professional authentication features.

This project leverages **Docusaurus v3** for content management, **React 18** for interactive components, and **Firebase** for secure user authentication—creating a production-ready educational platform.

---

## ✨ Features

### 📖 Educational Content
- **4 Comprehensive Modules**: Structured learning path from fundamentals to advanced applications
  - **Module 1**: Foundations of Physical AI
  - **Module 2**: Embodied Intelligence & Robotics Core
  - **Module 3**: Humanoid Robotics & AI Agents
  - **Module 4**: Applied Systems & AI-Native Learning
- **12+ Detailed Lessons**: Each module contains 3 in-depth lessons with clear learning objectives
- **Interactive Navigation**: Smooth transitions between modules and lessons with intuitive sidebar

### 🎨 Professional Homepage
- **Hero Section**: Striking cover design with call-to-action buttons
- **Features Showcase**: Highlights key learning benefits (Hands-on, AI-Powered, Real-World)
- **Module Cards**: Visual overview of all 4 learning modules with descriptions and learning goals
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Smooth Animations**: Professional micro-interactions and transitions

### 🔐 Authentication System
- **Email/Password Authentication**: Secure account creation and login
- **Google OAuth Integration**: One-click sign-in with Google accounts
- **Protected Dashboard**: User profile and progress tracking (client-side only)
- **Firebase Security**: Industry-standard authentication and security

### 💻 Modern Tech Stack
- **Docusaurus v3**: Static site generation with React-based theme
- **TypeScript**: Full type safety across all components
- **React 18**: Modern component architecture with hooks
- **CSS Modules**: Scoped styling with advanced animations
- **Firebase**: Real-time authentication and user management
- **MDX**: Interactive markdown documentation

### ⚡ Performance & Reliability
- **Production Build**: Verified and optimized for deployment
- **Zero Build Errors**: Clean compilation with no warnings
- **SSR-Compatible**: Server-side rendering safe components
- **Fast Load Times**: Optimized bundles and code splitting
- **Accessibility**: Semantic HTML, alt text, proper heading hierarchy

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** ≥ 18.0.0
- **pnpm** ≥ 8.0.0 (or npm/yarn)
- **Git** for version control

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Rajda-Hyder/physical-AI-and-humanoid-robotics.git
cd physical-AI-and-humanoid-robotics
```

2. **Install dependencies**
```bash
pnpm install
```

3. **Set up environment variables**
```bash
# Copy the example environment file
cp .env.example .env.local

# Fill in your Firebase credentials
# Get these from your Firebase Console: https://console.firebase.google.com/
```

4. **Start the development server**
```bash
pnpm start
```

The site will open at `http://localhost:3000` with hot-reload enabled.

---

## 📋 Available Scripts

```bash
# Start development server with hot reload
pnpm start

# Build for production
pnpm build

# Serve production build locally (test before deployment)
pnpm serve

# Clear Docusaurus cache and build artifacts
pnpm clear

# Docusaurus CLI
pnpm docusaurus <command>

# Other useful commands
pnpm swizzle              # Customize theme components
pnpm write-translations   # Generate translation files
pnpm write-heading-ids    # Auto-generate heading IDs
```

---

## 🏗️ Project Structure

```
physical-AI-and-humanoid-robotics/
├── docs/                          # MDX documentation files
│   ├── intro.mdx                 # Welcome page
│   ├── module-1-foundations/     # Module 1 lessons
│   ├── module-2-embodied-robotics/
│   ├── module-3-humanoid-ai-agents/
│   └── module-4-applied-ai-native/
│
├── src/                           # React source code
│   ├── components/                # Reusable React components
│   │   ├── HomepageHero/         # Hero section component
│   │   ├── ModuleCard/           # Module display cards
│   │   └── FeaturesSection/      # Features showcase
│   ├── config/
│   │   └── firebase.ts           # Firebase initialization
│   ├── contexts/
│   │   └── AuthContext.tsx       # Authentication context
│   ├── pages/                     # Page components
│   │   ├── index.tsx             # Homepage
│   │   ├── login.tsx             # Login page
│   │   ├── register.tsx          # Registration page
│   │   └── dashboard.tsx         # User dashboard
│   ├── css/                       # Global styles
│   │   ├── custom.css            # Docusaurus overrides
│   │   └── variables.module.css  # CSS variables
│   └── theme/
│       └── Root.tsx              # Root wrapper component
│
├── static/                        # Static assets
│   └── img/                       # Images and SVGs
│       ├── cover/                # Book cover image
│       ├── module-*/             # Module icons
│       └── features/             # Feature icons
│
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── docusaurus.config.js           # Docusaurus configuration
├── package.json                   # Project dependencies
├── pnpm-lock.yaml                # Dependency lock file
├── sidebars.js                    # Documentation sidebar
├── tsconfig.json                  # TypeScript configuration
└── README.md                      # This file
```

---

## 🔧 Configuration

### Firebase Setup

1. **Create a Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Create a new project"
   - Follow the setup wizard

2. **Enable Authentication**
   - In Firebase Console, navigate to "Authentication"
   - Click "Get started"
   - Enable "Email/Password" provider
   - Enable "Google" provider

3. **Get Credentials**
   - Go to Project Settings → Service Accounts
   - Click "Generate new private key"
   - Copy your API key and other credentials

4. **Configure Environment Variables**
```bash
# .env.local
REACT_APP_FIREBASE_API_KEY=your_api_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
REACT_APP_FIREBASE_APP_ID=your_app_id
```

### Docusaurus Configuration

Edit `docusaurus.config.js` to customize:
- **Site Title & Tagline**: Update `title` and `tagline`
- **Domain & Base URL**: Set `url` and `baseUrl`
- **GitHub Organization**: Update `organizationName` and `projectName`
- **Custom CSS**: Modify `src/css/custom.css`

---

## 💡 Usage Examples

### Running Locally for Development

```bash
# 1. Install dependencies
pnpm install

# 2. Set up environment variables
cp .env.example .env.local
# Edit .env.local with your Firebase credentials

# 3. Start development server
pnpm start

# 4. Access the site
# Open http://localhost:3000 in your browser
# Changes to docs/ and src/ will hot-reload automatically
```

### Building for Production

```bash
# Clean previous builds
pnpm clear

# Build the site
pnpm build

# Test the production build locally
pnpm serve

# The build/ directory is ready for deployment
```

### Deploying to GitHub Pages

```bash
# Ensure docusaurus.config.js has correct URL and baseUrl
pnpm build
pnpm deploy
```

### Deploying to Other Platforms

The `build/` directory contains static files ready for:
- **Vercel**: Connect GitHub repo → Auto-deploy from `main` branch
- **Netlify**: Drag-and-drop `build/` folder or connect GitHub
- **GitHub Pages**: Use GitHub Actions workflow
- **Docker**: Serve `build/` with nginx or express

---

## 🎓 Learning Path

### For Students
1. **Start at Homepage** → Overview of what you'll learn
2. **Begin Module 1** → Foundations of Physical AI
3. **Progress Sequentially** → Each module builds on previous knowledge
4. **Sign Up** → Create account to track progress
5. **Explore Dashboard** → View learning journey (when logged in)

### For Educators
1. **Review Module Structure** → See `docs/` folder organization
2. **Customize Content** → Edit `.mdx` files to match your curriculum
3. **Add New Lessons** → Create new `.mdx` files in module folders
4. **Deploy** → Use included deployment scripts

---

## 🔐 Authentication Features

### Supported Login Methods
- **Email & Password**: Create new account with email
- **Google Account**: Sign in with existing Google account

### User Flow
```
Unauthenticated User
    ↓
Homepage (public) → Sign In / Register
    ↓
Authentication (Firebase)
    ↓
Dashboard (protected) → View Profile & Progress
    ↓
All Lessons (public) → Interactive Learning
    ↓
Sign Out → Back to Homepage
```

### Protected Routes
- `/dashboard` - User dashboard (client-side only)
- `/login` - Login page
- `/register` - Registration page

---

## 📦 Dependencies

### Core Framework
- `@docusaurus/core@^3.0.0` - Static site generator
- `@docusaurus/preset-classic@^3.0.0` - Classic theme preset
- `react@^18.2.0` - UI framework
- `react-dom@^18.2.0` - DOM rendering

### Authentication
- `firebase@^12.6.0` - Firebase SDK
- `react-firebase-hooks@^5.1.1` - Firebase React hooks

### Routing & Components
- `react-router-dom@^7.10.1` - Client-side routing
- `@mdx-js/react@^3.0.0` - MDX React components

### Development
- `typescript@^5.0.0` - Type safety
- `prism-react-renderer@^2.3.0` - Code syntax highlighting

See `package.json` for complete dependency list.

---

## 🚀 Deployment

### GitHub Pages
```bash
# Configure in docusaurus.config.js:
organizationName: 'your-github-username'
projectName: 'your-repo-name'
url: 'https://your-github-username.github.io'
baseUrl: '/your-repo-name/'

# Deploy
pnpm deploy
```

### Vercel
1. Push code to GitHub
2. Import repository in [Vercel Dashboard](https://vercel.com)
3. Framework: `Docusaurus`
4. Build Command: `pnpm build`
5. Deployment complete!

### Netlify
1. Connect GitHub repository
2. Build Command: `pnpm build`
3. Publish Directory: `build`
4. Set environment variables in Netlify dashboard
5. Deploy!

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN pnpm install
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "serve"]
```

---

## 🤝 Contributing

We welcome contributions! To contribute:

### Getting Started
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/physical-AI-and-humanoid-robotics.git`
3. **Create branch**: `git checkout -b feature/your-feature`
4. **Install dependencies**: `pnpm install`

### Making Changes
- **Add lessons**: Create new `.mdx` files in appropriate module folder
- **Modify components**: Edit files in `src/components/`
- **Update styles**: Modify CSS modules in component folders
- **Fix bugs**: Work on `fix/*` branches

### Before Submitting
```bash
# Build to check for errors
pnpm build

# Test locally
pnpm start

# Commit with clear message
git add .
git commit -m "feat: Add new lesson on robotics control"
git push origin feature/your-feature
```

### Submitting Pull Requests
1. **Create PR** with clear description
2. **Reference issues**: Use `Closes #123` in PR description
3. **Provide context**: Explain what and why
4. **Test verification**: Confirm build passes
5. **Wait for review**: Maintainers will review ASAP

### Contribution Guidelines
- ✅ Keep messages in existing documentation style
- ✅ Follow TypeScript conventions
- ✅ Test before submitting
- ✅ Update README if adding features
- ❌ Don't commit `.env.local` or secrets
- ❌ Don't include `node_modules/` or `build/`

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](./LICENSE) file for details.

You are free to:
- Use for commercial or educational purposes
- Modify and distribute
- Include in your own projects

Just acknowledge the original author!

---

## 👤 Author

**Syeda Rajda Bano**
- 📧 Email: [rajdahyder@gmail.com](mailto:rajdahyder@gmail.com)
- 🐙 GitHub: [@Rajda-Hyder](https://github.com/Rajda-Hyder)
- 🎓 Organization: [Panaversity](https://github.com/panaversity)

---

## 🙏 Acknowledgments

- [Docusaurus](https://docusaurus.io/) - Amazing static site generator
- [Firebase](https://firebase.google.com/) - Secure authentication platform
- [React](https://react.dev/) - UI framework
- All contributors and educators using this textbook

---

## 📞 Support & Feedback

### Getting Help
- 📖 **Documentation**: See [docs/](./docs/) folder
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/Rajda-Hyder/physical-AI-and-humanoid-robotics/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Rajda-Hyder/physical-AI-and-humanoid-robotics/discussions)
- 📧 **Email**: Open an issue or contact directly

### Roadmap
- [ ] Add video tutorials for each lesson
- [ ] Implement progress tracking system
- [ ] Add quiz and assessment features
- [ ] Create mobile app
- [ ] Multi-language support
- [ ] Community forum integration

---

## 📊 Project Statistics

```
Build Status:     ✅ Production Ready
Build Time:       ~4.5 minutes
Server Compile:   2.00m
Client Compile:   2.52m
Files:            99
Lines of Code:    ~30,000+
Modules:          4
Lessons:          12+
Components:       20+
```

---

<div align="center">

**Made with ❤️ for the robotics and AI learning community**

[⬆ back to top](#physical-ai--humanoid-robotics-textbook)

</div>
