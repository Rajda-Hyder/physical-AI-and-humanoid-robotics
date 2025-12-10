# Implementation Plan: Physical AI & Humanoid Robotics Textbook

**Branch**: `feature/physical-ai-robotics-textbook` | **Date**: 2025-12-10 | **Spec**: [Feature Specification](./spec.md)

**Input**: User-provided plan focused on homepage, branding, media handling, and module organization for Docusaurus v3 deployment

## Summary

This plan details the implementation of the **Physical AI & Humanoid Robotics** textbook as a Docusaurus v3 site, with a focus on user-facing structure (homepage & branding), media asset handling, and module organization. Implementation aligns with the Constitutional mandate for a clear, hands-on, AI-native learning platform with integrated RAG chatbot support, personalization, and multilingual accessibility. The plan is organized into 5 phases: Visual Identity, Homepage, Branding & Design System, Media Implementation, and Traceability.

---

## Technical Context

**Language/Version**: Node.js 18+ (Docusaurus v3), JavaScript/TypeScript (React)
**Primary Dependencies**: Docusaurus 3.x, React 18+, CSS Modules, Heroicons/Feather icons, MDX
**Storage**: Static file assets in `/static/` (images, fonts); Markdown content in `/docs/`
**Testing**: N/A (static site; validation via visual inspection & link verification)
**Target Platform**: GitHub Pages (static hosting)
**Project Type**: Web (single Docusaurus site with static deployment)
**Performance Goals**: Fast Time-to-Interactive (< 3s), optimized images (WebP fallback), semantic HTML for SEO and RAG ingestibility
**Constraints**: GitHub Pages limitations (static only, 1GB storage), HTTPS enforced, no backend required for this phase
**Scale/Scope**: 4 modules, 12 lessons (~50-70 pages total), 30-40 hero/module images, responsive design (mobile/tablet/desktop)

---

## Constitution Check

**GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.**

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| **I. Spec-Driven Development** | Use Spec-Kit Plus + Claude Code workflows | ✅ PASS | Plan follows SDD structure; phased execution via `/sp.plan` command |
| **II. Docusaurus First** | Built with Docusaurus v3, GitHub Pages deployment | ✅ PASS | Plan mandates Docusaurus v3, homepage design, static generation |
| **III. Integrated RAG Chatbot** | Content structure supports RAG embeddings (chapter/section-level) | ✅ PASS | Plan specifies MDX format, clear section headings, metadata-rich frontmatter for RAG ingestibility |
| **IV. Claude Code Augmentation** | Subagents & Reusable Skills implemented | ⚠️ DEFER | Out of Phase 1 scope; addressed in Phase 3+ (chatbot backend integration) |
| **V. Secure User Authentication** | Better-Auth signup/signin | ⚠️ DEFER | Out of Phase 1 scope; backend/auth implementation separate |
| **VI. Personalized Learning Experience** | "Personalize Content" button per chapter | ⚠️ DEFER | UI component design included; backend integration separate |
| **VII. Multilingual Accessibility** | "Translate to Urdu" button per chapter | ⚠️ DEFER | UI component design included; translation service integration separate |
| **VIII. Clear & Concise Content** | Startup-oriented, friendly brand voice | ✅ PASS | Plan includes branding system (colors, typography, spacing) aligned with friendly, modern aesthetic |

**Gate Assessment**: ✅ **PASS** (Deferred principles are out of Phase 1 scope; will be re-checked when frontend integration tasks begin)

---

## Project Structure

### Documentation (this feature)

```text
specs/physical-ai-robotics/
├── spec.md              # Feature specification (existing)
├── plan.md              # This file (Phase 0 output, `/sp.plan` command)
├── research.md          # Phase 0 research output (to be created)
├── data-model.md        # Phase 1 design output (to be created)
├── quickstart.md        # Phase 1 quickstart guide (to be created)
├── contracts/           # Phase 1 API/component contracts (optional for static site)
└── tasks.md             # Phase 2 task breakdown (created by `/sp.tasks`)
```

### Source Code (repository root)

```text
# Docusaurus Project Structure
docusaurus.config.js        # Docusaurus configuration
package.json               # Project dependencies & scripts
sidebars.ts               # Sidebar configuration (modules & lessons)

docs/                     # Textbook content
├── _category_.json       # Root category for sidebar
├── intro.mdx             # Homepage/intro page
│
├── module-1-foundations/
│   ├── _category_.json
│   ├── lesson-1-1-intro-to-physical-ai.mdx
│   ├── lesson-1-2-software-vs-embodied-ai.mdx
│   └── lesson-1-3-essential-foundational-concepts.mdx
│
├── module-2-embodied-robotics/
│   ├── _category_.json
│   ├── lesson-2-1-sensing-taking-action.mdx
│   ├── lesson-2-2-control-systems.mdx
│   └── lesson-2-3-physical-world-engagement.mdx
│
├── module-3-humanoid-ai-agents/
│   ├── _category_.json
│   ├── lesson-3-1-building-human-like-robots.mdx
│   ├── lesson-3-2-intelligent-minds-physical-bodies.mdx
│   └── lesson-3-3-robots-think-move.mdx
│
└── module-4-applied-ai-native/
    ├── _category_.json
    ├── lesson-4-1-simulation-to-reality.mdx
    ├── lesson-4-2-rag-chatbot-usage.mdx
    └── lesson-4-3-tailored-global-learning.mdx

static/                  # Static assets (images, fonts, etc.)
├── img/
│   ├── cover/
│   │   └── book-cover.png         # AI-generated cover image
│   ├── hero/
│   │   ├── hero-bg.png            # Hero section background
│   │   └── hero-illustration.svg  # Subtle hero illustration
│   └── module-[1-4]/
│       ├── lesson-[1-3]/
│       │   └── *.png              # Lesson images/diagrams
│       └── [module-level icons]
│
├── fonts/
│   ├── Exo2.woff2
│   ├── TitilliumWeb.woff2
│   ├── Inter.woff2
│   ├── Roboto.woff2
│   └── FiraCode.woff2
│
└── css/
    └── custom.css              # Custom Docusaurus overrides (deprecated; use CSS Modules)

src/                     # React components & utilities
├── components/
│   ├── HomepageHero/
│   │   ├── HomepageHero.tsx
│   │   └── HomepageHero.module.css
│   │
│   ├── ModuleCard/
│   │   ├── ModuleCard.tsx
│   │   └── ModuleCard.module.css
│   │
│   ├── FeaturesSection/
│   │   ├── FeaturesSection.tsx
│   │   └── FeaturesSection.module.css
│   │
│   ├── Figure/
│   │   ├── Figure.tsx            # Reusable image + caption component
│   │   └── Figure.module.css
│   │
│   └── PersonalizeButton/        # Deferred to Phase 2
│       └── [placeholder]
│
├── pages/
│   └── index.tsx                # Custom homepage (overrides intro.mdx)
│
├── css/
│   ├── variables.module.css      # Design system (colors, spacing, typography)
│   └── global.css               # Global styles
│
└── utils/
    └── [placeholder]

tests/                   # Visual & integration tests (Phase 2+)
└── [placeholder]
```

**Structure Decision**:
- **Single Docusaurus project** (no separate backend in Phase 1; RAG backend is separate)
- **React components** for homepage sections and reusable UI patterns (Figure, ModuleCard, etc.)
- **CSS Modules** for scoped styling, Docusaurus design tokens for theming
- **MDX for all lesson content** to support future interactive components (personalize button, translate button)
- **Static image assets** in `/static/img/` with alt text and captions
- **Design tokens** in CSS Modules for branding colors, typography, spacing

---

## Phase 0: Research & Clarifications

### Unknowns & Research Tasks

1. **Book Cover Generation** (AI-generated image)
   - Decision: Use DALL-E 3 or Midjourney API to generate cover based on brief
   - Rationale: Ensures visual consistency with brand, no copyright concerns
   - Alternatives considered: Stock photography (too generic), manual design (time-intensive)

2. **Docusaurus v3 Configuration**
   - Decision: Use `@docusaurus/core@latest` with TypeScript support
   - Rationale: Native TypeScript support in v3, better DX for custom components
   - Alternatives: v2 (EOL soon), static site generator (less content management)

3. **Design System & CSS Strategy**
   - Decision: CSS Modules + Docusaurus design tokens, NO hardcoded colors/spacing
   - Rationale: Maintainability, theming support, alignment with Constitution
   - Alternatives: Tailwind CSS (overkill for static site), styled-components (runtime overhead)

4. **Image Optimization & Format**
   - Decision: WebP with PNG fallback, responsive images using `<picture>` or next-gen image component
   - Rationale: Reduces bandwidth, improves LCP (Largest Contentful Paint)
   - Alternatives: JPEG (weaker compression), single format (less optimization)

5. **Homepage Architecture**
   - Decision: Custom React page (`src/pages/index.tsx`) overlaying Docusaurus theme
   - Rationale: Full control over layout, hero section, module cards without MDX constraints
   - Alternatives: MDX-based homepage (less flexible), Docusaurus swizzle (harder to maintain)

6. **RAG Content Chunking Strategy**
   - Decision: Section-level embeddings (H2/H3 headings per lesson)
   - Rationale: Supports selected-text-only answering; granular retrieval
   - Alternatives: Page-level chunks (less precise), sentence-level (too granular)

**Output**: All clarifications resolved; proceeding to Phase 1 design.

---

## Phase 1: Design & Contracts

### 1.1 Visual Identity & Branding System

**Design System (CSS Modules-based)**

```scss
// src/css/variables.module.css (Design tokens)

:root {
  // Colors
  --color-primary: #00D1B2;        // Teal/aqua
  --color-secondary: #FF6B6B;      // Coral/red
  --color-background: #1A1A2E;     // Deep navy
  --color-text: #E0E0E0;          // Light gray
  --color-text-dark: #FFFFFF;      // White
  --color-border: #2A2A3E;        // Slightly lighter navy
  --color-hover: rgba(0, 209, 178, 0.1); // Primary with transparency

  // Typography scale (modular scale)
  --font-size-xs: 0.75rem;        // 12px
  --font-size-sm: 0.875rem;       // 14px
  --font-size-base: 1rem;         // 16px
  --font-size-lg: 1.25rem;        // 20px
  --font-size-xl: 1.5rem;         // 24px
  --font-size-2xl: 2rem;          // 32px
  --font-size-3xl: 2.5rem;        // 40px
  --font-size-4xl: 3rem;          // 48px

  // Font families
  --font-heading: "Exo 2", "Titillium Web", sans-serif;
  --font-body: "Inter", "Open Sans", sans-serif;
  --font-code: "Fira Code", "Roboto Mono", monospace;

  // Spacing scale (0.5rem increments)
  --spacing-xs: 0.5rem;           // 8px
  --spacing-sm: 1rem;             // 16px
  --spacing-md: 2rem;             // 32px
  --spacing-lg: 4rem;             // 64px

  // Shadows & Effects
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.2);

  // Transitions
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
}
```

**Design Deliverables**:
- [ ] Book cover image (1200×1600px, PNG + WebP)
- [ ] Hero background / illustration (2000×1200px)
- [ ] Module card icons (8 total, SVG + PNG)
- [ ] Color swatches documentation
- [ ] Typography samples (headings, body, code)

### 1.2 Homepage Architecture

**Homepage Structure** (`src/pages/index.tsx`):

```
├─ Hero Section
│  ├─ Book cover image (left)
│  ├─ Title & subtitle (right)
│  └─ "Start Learning" CTA button
│
├─ Module Highlights Section
│  ├─ 4 × ModuleCard components
│  ├─ Grid layout (2×2 on desktop, 1 on mobile)
│  └─ Hover effects (scale, shadow, color change)
│
├─ Key Features Section
│  ├─ Feature 1: Hands-on Learning
│  ├─ Feature 2: AI-Powered Insights
│  ├─ Feature 3: Real-World Robotics
│  └─ Icon + description per feature
│
└─ Footer
   ├─ Copyright & links
   └─ GitHub link (Docusaurus default extended)
```

### 1.3 Component Contracts

#### HomepageHero Component

```typescript
interface HomepageHeroProps {
  title: string;
  subtitle: string;
  coverImage: string;
  ctaText: string;
  ctaUrl: string;
}

// Example usage:
<HomepageHero
  title="Physical AI & Humanoid Robotics"
  subtitle="Learn to build and control the future of embodied intelligence"
  coverImage="/static/img/cover/book-cover.png"
  ctaText="Start Learning"
  ctaUrl="/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai"
/>
```

#### ModuleCard Component

```typescript
interface ModuleCardProps {
  moduleNumber: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  lessonCount: number;
  learningGoals: string[];
  onClick: () => void;
}

// Rendered in loop from MODULES constant:
const MODULES = [
  {
    moduleNumber: 1,
    title: "Foundations of Physical AI",
    description: "Essential concepts...",
    icon: <FoundationsIcon />,
    ...
  },
  // ... Module 2-4
];
```

#### Figure Component (Image + Caption)

```typescript
interface FigureProps {
  src: string;
  alt: string;
  caption: string;
  width?: number;
  height?: number;
}

// Usage in lessons:
<Figure
  src="/static/img/module-1/lesson-1-1/robot-perception.png"
  alt="Robot with perception sensors labeled"
  caption="Figure 1.1: Sensors enable robots to perceive their environment"
/>
```

### 1.4 Data Model (Content Metadata)

**Module Metadata** (for sidebar & module cards):

```json
{
  "moduleId": "module-1",
  "moduleNumber": 1,
  "title": "Foundations of Physical AI",
  "description": "Essential concepts and terminology",
  "icon": "FoundationsIcon",
  "learningGoals": [
    "Understand Physical AI definition",
    "Distinguish software vs. embodied AI",
    "Identify core concepts"
  ],
  "lessons": [
    {
      "lessonId": "lesson-1-1",
      "number": "1.1",
      "title": "Introduction to Physical AI",
      "description": "Define Physical AI and its scope",
      "file": "lesson-1-1-intro-to-physical-ai.mdx",
      "duration": "15-20 min"
    },
    // ... lessons 1.2, 1.3
  ]
}
```

### 1.5 Docusaurus Configuration Decisions

**docusaurus.config.js Key Settings**:
- `baseUrl`: `/` (for root GitHub Pages deployment)
- `projectName`: `physical-ai-robotics` (GitHub repo name)
- `organizationName`: `[panaversity or user org]`
- Theme: `@docusaurus/preset-classic` (with custom color overrides)
- Markdown engine: MDX (for component support)
- Build target: Static HTML (GitHub Pages compatible)

---

## Phase 2: Contracts & Quickstart (Deliverables)

### 2.1 API/Component Contracts

**File**: `specs/physical-ai-robotics/contracts/components.md`

Lists all custom React components with:
- Props interface
- Expected behavior
- Accessibility requirements
- Usage examples
- Error states

**File**: `specs/physical-ai-robotics/contracts/content-schema.md`

Defines:
- Frontmatter YAML schema (required fields per lesson)
- Section naming conventions (for RAG chunking)
- Image alt text guidelines
- Metadata field requirements

### 2.2 Quickstart Guide

**File**: `specs/physical-ai-robotics/quickstart.md`

```markdown
## Quick Setup

1. Clone & install:
   git clone [repo]
   cd physical-ai-robotics
   npm install

2. Generate book cover:
   npm run generate:cover

3. Start dev server:
   npm run start
   # Visit http://localhost:3000

## Adding a New Lesson

1. Create file: docs/module-X/lesson-X-Y-[slug].mdx
2. Add frontmatter (title, description, sidebar_position, tags)
3. Follow lesson format (Overview → Objectives → ... → Questions)
4. Add images to static/img/module-X/lesson-X-Y/
5. Test: npm run build

## Deploying to GitHub Pages

1. npm run build
2. git add build/
3. git commit & push to gh-pages branch
```

---

## Complexity Tracking

**No violations**. Plan adheres strictly to Constitution and requires no justification for complexity.

---

## Key Implementation Decisions & Rationales

| Decision | Rationale | Trade-offs |
|----------|-----------|-----------|
| **MDX for all lesson content** | Enables future interactive components (personalize, translate buttons); supports RAG ingestibility via clear structure | Slightly more complex authoring; requires MDX knowledge |
| **Custom React homepage (not Docusaurus default)** | Full control over hero, module cards, feature layout; better UX | Maintenance of separate component; must sync with Docusaurus theme |
| **CSS Modules + design tokens (no Tailwind)** | Fine-grained control, no runtime overhead, maintainable design system | More verbose CSS; requires discipline on token usage |
| **Static image assets with WebP + PNG fallback** | Optimal performance; GitHub Pages friendly | Requires image optimization pipeline |
| **Section-level RAG chunking (H2/H3 headings)** | Supports selected-text answering; granular retrieval | Requires content authors to structure sections carefully |
| **Single Docusaurus project (no separate backend)** | Simplicity for Phase 1; RAG backend integrated later | Requires coordination for data pipeline (lesson exports) |

---

## Acceptance Criteria

- [ ] **Visual Identity**: Book cover, hero assets, and design system tokens finalized
- [ ] **Homepage**: Hero section, module cards, and features section deployed and responsive
- [ ] **Branding System**: All CSS variables in place; no hardcoded colors/spacing in components
- [ ] **Media Assets**: All images optimized, alt text present, captions applied
- [ ] **Module Organization**: 4 modules with 3 lessons each, properly structured in `/docs/`
- [ ] **Docusaurus Config**: Deployed to GitHub Pages with correct `baseUrl` and metadata
- [ ] **RAG Readiness**: Lesson structure supports section-level embeddings and selected-text querying
- [ ] **Documentation**: `research.md`, `data-model.md`, `quickstart.md` completed
- [ ] **Constitutional Alignment**: All principles verified; deferred items noted for Phase 2+

---

## Follow-up & Risks

- **Risk 1: Image optimization pipeline not established** → May impact performance; mitigation: establish ImageOptim workflow early in Phase 1
- **Risk 2: RAG content chunking not validated** → May affect chatbot retrieval accuracy; mitigation: test embeddings with sample lessons before full build
- **Risk 3: Homepage component maintenance burden** → Custom React may drift from Docusaurus theme; mitigation: document component contracts clearly; use Docusaurus hooks for theming

---

## Next Steps (Phase 2: `/sp.tasks`)

1. Generate `tasks.md` with actionable, dependency-ordered breakdown
2. Execute visual identity tasks (cover generation, asset creation)
3. Implement homepage components (Hero, ModuleCard, FeaturesSection)
4. Configure Docusaurus for GitHub Pages deployment
5. Create sample lesson content and validate RAG structure
6. Deploy to GitHub Pages and iterate on design

**Output Path**: This plan is stored at `/home/rajda/task_1/specs/physical-ai-robotics/plan.md`
