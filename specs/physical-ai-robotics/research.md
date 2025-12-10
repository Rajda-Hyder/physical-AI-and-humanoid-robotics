# Research Output: Physical AI & Humanoid Robotics Textbook

**Phase**: 0 (Research & Clarifications)
**Date**: 2025-12-10
**Source**: Implementation Plan Phase 0 unknowns

---

## Overview

This document consolidates research findings and decisions for all technical unknowns identified in the Implementation Plan. Each unknown has been resolved with a clear decision, rationale, and alternatives considered.

---

## 1. Book Cover Generation (AI-Generated Image)

### Decision
**Use DALL-E 3 API via OpenAI** to generate a high-quality book cover based on a detailed text prompt.

### Rationale
- DALL-E 3 produces publication-quality imagery suitable for a professional textbook
- No copyright concerns (AI-generated, user owns license)
- Can be regenerated/iterated quickly if branding changes
- Cost-effective (~$0.10/image with 1024×1792 resolution)
- Aligns with "Physical AI & Humanoid Robotics" theme seamlessly

### Alternatives Considered
1. **Midjourney** — High quality, but subscription-based ($20/month); slower iteration
2. **Stock Photography (Shutterstock/Getty)** — Generic, potentially low relevance to robotics/AI; licensing costs
3. **Manual Design (Graphic Designer)** — High cost ($500-2000), long turnaround; not scalable for hackathon context
4. **Open-source image generators (Stable Diffusion)** — Variable quality; requires self-hosting or API cost

### Implementation Details
- **Prompt**: "A stylized humanoid silhouette with intricate circuit patterns overlaid on the body. The figure is surrounded by a glowing network of data nodes and robotic/mechanical elements. Deep navy/purple gradient background transitioning to teal and aqua accents. Coral/red highlights suggesting energy. Professional, modern illustration style. Physics-inspired geometric lines. Clean, book-cover-ready composition."
- **Resolution**: 1200×1600px (3:4 aspect ratio for book cover)
- **Formats**: PNG (primary), WebP (optimized for web)
- **Storage**: `/static/img/cover/book-cover.png` (and `.webp`)

### Timeline
- Generation: 1–2 minutes via API
- Review & iteration: 2–3 rounds if needed
- Final approval: Human review required

---

## 2. Docusaurus v3 Configuration

### Decision
**Use Docusaurus 3.x with `@docusaurus/preset-classic` and TypeScript support.**

### Rationale
- **Latest stable version** with long-term support (v3 released 2023, maintained through 2025+)
- **Native TypeScript support** in v3 reduces build complexity and improves IDE support
- **React 18+ compatibility** ensures modern performance optimizations
- **MDX 2.0 included** for component-rich content (required for future personalize/translate buttons)
- **GitHub Pages deployment** is first-class citizen (requires minimal configuration)
- **Content versioning** built-in for future editions of the textbook

### Alternatives Considered
1. **Docusaurus v2** — Still maintained, but EOL approaching (2025); no native TS
2. **Next.js** — More flexible, but overkill for static content; requires deployment infrastructure
3. **Astro** — Good for static content, but smaller ecosystem; less content management features
4. **Hugo / Jekyll** — Lightweight, but weaker component support; less suited for interactive RAG integration later

### Configuration Highlights
```javascript
// docusaurus.config.js
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Learn to build and control embodied intelligence',
  baseUrl: '/',
  projectName: 'physical-ai-robotics',
  organizationName: '[panaversity]',
  presets: [
    ['@docusaurus/preset-classic', {
      docs: {
        sidebarPath: require.resolve('./sidebars.ts'),
        editUrl: 'https://github.com/[org]/physical-ai-robotics/edit/main/',
      },
      blog: false, // No blog; only docs
      theme: {
        customCss: require.resolve('./src/css/custom.css'),
      },
    }],
  ],
  themeConfig: {
    colorMode: { defaultMode: 'dark' }, // Align with brand (dark navy background)
    navbar: { /* custom branding */ },
    footer: { /* custom footer */ },
  },
  plugins: [
    // Future: @docusaurus/plugin-ideal-image for responsive images
    // Future: custom chatbot plugin for RAG integration
  ],
};
```

### Implementation Details
- **Installation**: `npx create-docusaurus@latest --typescript`
- **Customization**: Swizzle theme components for logo, navbar, footer
- **Build target**: Static HTML (default), optimized for GitHub Pages

---

## 3. Design System & CSS Strategy

### Decision
**CSS Modules + Docusaurus design tokens, with NO hardcoded colors/spacing in component files.**

### Rationale
- **Maintainability**: Design changes localized to `variables.module.css`; no scattered magic numbers
- **Theming**: Easy to support future dark/light mode toggle (Constitution defers this to Phase 2, but architecture allows it)
- **Performance**: No runtime overhead (CSS-in-JS); all styles pre-compiled
- **Alignment with Constitution**: Principle VIII demands "clear & concise," which extends to codebase clarity
- **Docusaurus integration**: Built-in CSS variable support via `--ifm-*` variables; custom tokens extend this

### Alternatives Considered
1. **Tailwind CSS** — Rapid prototyping, but overkill for ~5 custom components; adds 50KB+ to bundle
2. **Styled-components / Emotion** — Runtime overhead; not needed for static content
3. **SASS/SCSS** — More verbose than CSS Modules; harder to enforce token usage
4. **Inline styles** — Anti-pattern; scattered across components

### Implementation Details

**File**: `src/css/variables.module.css`
```css
:root {
  /* Colors (exported from design brief) */
  --color-primary: #00D1B2;
  --color-secondary: #FF6B6B;
  --color-background: #1A1A2E;
  --color-text: #E0E0E0;
  --color-text-dark: #FFFFFF;
  --color-border: #2A2A3E;
  --color-hover: rgba(0, 209, 178, 0.1);

  /* Typography (modular scale: 1.25x ratio) */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
  --font-size-2xl: 2rem;
  --font-size-3xl: 2.5rem;
  --font-size-4xl: 3rem;

  /* Font families */
  --font-heading: 'Exo 2', 'Titillium Web', sans-serif;
  --font-body: 'Inter', 'Open Sans', sans-serif;
  --font-code: 'Fira Code', 'Roboto Mono', monospace;

  /* Spacing (modular scale: 0.5rem → 1rem → 2rem → 4rem) */
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 2rem;
  --spacing-lg: 4rem;

  /* Shadows */
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.2);

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
}
```

**Component Example**: `src/components/ModuleCard/ModuleCard.module.css`
```css
.card {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--spacing-md);
  transition: all var(--transition-normal);
}

.card:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

.title {
  font-family: var(--font-heading);
  font-size: var(--font-size-xl);
  color: var(--color-text-dark);
  margin-bottom: var(--spacing-sm);
}
```

**Enforcement**: Linter rule (ESLint + custom rule) to flag hardcoded hex colors or pixel values in `.tsx` files.

---

## 4. Image Optimization & Format Strategy

### Decision
**Use WebP as primary format with PNG fallback; implement responsive images via `<picture>` element.**

### Rationale
- **WebP compression**: 25–35% file size reduction vs. PNG; 50%+ vs. JPEG
- **Browser support**: WebP supported in all modern browsers (91%+ global); fallback for legacy browsers
- **Performance**: Reduced bandwidth improves LCP and CLS metrics (critical for SEO & user experience)
- **GitHub Pages compatible**: No server-side processing needed; works with static hosting

### Alternatives Considered
1. **JPEG only** — Smaller for photographs, but worse for illustrations; not suitable for hero images
2. **PNG only** — Larger files; no optimization
3. **AVIF format** — Better compression than WebP, but less browser support (85%); riskier for hackathon deadline
4. **Next.js Image component** — Would require Next.js instead of Docusaurus; out of scope

### Implementation Details

**Image Pipeline**:
1. Designer/AI generates images (JPEG or PNG)
2. Optimize with ImageMagick:
   ```bash
   convert input.png -resize 1200x -quality 85 -format webp output.webp
   convert input.png -resize 1200x output.png
   ```
3. Store both formats in `/static/img/`
4. Use in Docusaurus/React via:
   ```tsx
   <picture>
     <source srcSet="/static/img/cover/book-cover.webp" type="image/webp" />
     <source srcSet="/static/img/cover/book-cover.png" type="image/png" />
     <img src="/static/img/cover/book-cover.png" alt="Book cover" />
   </picture>
   ```

**Responsive Image Handling**:
- Hero image: Generate 3 sizes (320px, 768px, 1280px widths)
- Lesson images: Generate 2 sizes (600px, 1200px widths)
- Use CSS media queries to load appropriate size

**File Size Targets**:
- Book cover: < 80KB (WebP) + < 150KB (PNG)
- Hero image: < 50KB (WebP) + < 100KB (PNG)
- Module icons: < 5KB each (SVG preferred)
- Lesson diagrams: < 30KB (WebP) + < 60KB (PNG)

---

## 5. Homepage Architecture

### Decision
**Implement custom React page (`src/pages/index.tsx`) as homepage overlay on Docusaurus theme.**

### Rationale
- **Full layout control**: Hero section with asymmetric cover + text layout requires custom React
- **Docusaurus integration**: Extends theme; inherits navbar, footer, typography
- **Reusability**: Components (Hero, ModuleCard, FeaturesSection) can be reused in other pages
- **Future extensibility**: Easy to add personalization, analytics, or chatbot widgets later
- **Performance**: Single React component; no extra bundle overhead

### Alternatives Considered
1. **MDX-based homepage (`docs/intro.mdx`)** — Simpler, but limited layout flexibility; hard to achieve asymmetric hero
2. **Swizzle Docusaurus Layout** — Would require modifying theme internals; fragile during upgrades
3. **Separate landing page + docs** — Two separate sites; complicates navigation and deployment

### Implementation Details

**File**: `src/pages/index.tsx`

```typescript
import React from 'react';
import Layout from '@theme/Layout';
import HomepageHero from '../components/HomepageHero/HomepageHero';
import FeaturesSection from '../components/FeaturesSection/FeaturesSection';
import ModuleGrid from '../components/ModuleGrid/ModuleGrid';

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="Learn to build and control the future of embodied intelligence"
    >
      <HomepageHero />
      <FeaturesSection />
      <ModuleGrid />
    </Layout>
  );
}
```

**Docusaurus Configuration** (to make index.tsx the homepage):
```javascript
// docusaurus.config.js
module.exports = {
  // ... other config
  plugins: [
    [
      '@docusaurus/plugin-ideal-image', // For responsive images
      { /* ... */ },
    ],
  ],
};
// Ensure docs/ has no index.mdx, or rename to intro.mdx
```

---

## 6. RAG Content Chunking Strategy

### Decision
**Implement section-level embeddings based on H2/H3 headings within lessons.**

### Rationale
- **Precision**: Enables "selected-text-only" answering; chatbot can respond to specific subsections
- **Granularity**: Reduces false positives; each section is a focused knowledge unit
- **Lesson structure alignment**: Constitution Section 2 mandates lessons follow 8-point format; each point becomes a section (H2)
- **Qdrant compatibility**: Section-level chunks (200–500 tokens) fit ideal range for embedding models

### Alternatives Considered
1. **Page-level chunks** — Entire lesson as one embedding; less precise retrieval
2. **Sentence-level chunks** — Too granular; loses context; poor retrieval quality
3. **Custom chunking rules** — Harder to implement; requires NLP preprocessing

### Implementation Details

**Lesson Frontmatter** (for RAG metadata):
```yaml
---
title: "Introduction to Physical AI"
description: "Define Physical AI, exploring its scope, applications, and historical context."
sidebar_position: 1
tags: [physical-ai, robotics, beginner, module-1, lesson-1-1]
rag_sections:
  - type: "overview"
    heading: "Lesson Overview"
  - type: "objectives"
    heading: "Learning Objectives"
  - type: "core_concepts"
    heading: "Core Concepts"
  - type: "hands_on"
    heading: "Hands-On Section"
  - type: "mindset"
    heading: "Physical AI Mindset"
  - type: "misconceptions"
    heading: "Common Mistakes & Misconceptions"
  - type: "summary"
    heading: "Summary"
  - type: "questions"
    heading: "Practice / Reflection Questions"
---
```

**Lesson Structure Example**:
```mdx
## Lesson Overview

[Brief introduction to Physical AI and its relevance.]

## Learning Objectives

- Define Physical AI
- Recognize common Physical AI applications
- [... etc ...]

## Core Concepts

### What is Physical AI?

[Detailed explanation. Qdrant will chunk this subsection separately.]

### Embodiment vs. Software AI

[Another subsection chunk.]

## Hands-On Section

[Practical exercise or mini-experiment.]

## [... remaining sections ...]
```

**RAG Ingestion Pipeline** (Future, Phase 2+):
1. Extract lesson file → parse frontmatter + markdown
2. For each H2 section → create chunk with metadata (module, lesson, section_type)
3. Generate embedding via OpenAI / Qdrant
4. Store in Qdrant with metadata for filtering & retrieval

---

## 7. Single vs. Multi-Project Architecture

### Decision
**Use single Docusaurus project; RAG backend is separate (later phase).**

### Rationale
- **Phase 1 scope**: Focus on content structure, homepage, branding
- **Simplicity**: One repo, one build pipeline, one deployment target
- **RAG decoupling**: Backend (FastAPI + Qdrant) integrates via API; doesn't require shared source
- **Future flexibility**: Can split repos if needed, but unlikely given GitHub Pages constraints

### Alternatives Considered
1. **Monorepo (Docusaurus + FastAPI)** — Would require Docker, Vercel/Railway deployment (not GitHub Pages); overkill for Phase 1
2. **Separate frontend + backend repos** — Adds coordination overhead; unnecessary until Phase 2 (chatbot backend)

### Implementation Details
- **Main repo**: `physical-ai-robotics` (Docusaurus + static assets)
- **Future RAG backend repo**: `physical-ai-robotics-backend` (FastAPI, Qdrant, OpenAI integration)
- **Integration point**: Frontend calls chatbot API endpoint at `https://api.example.com/chat`

---

## Summary Table

| Unknown | Decision | Key Trade-off | Timeline |
|---------|----------|---------------|----------|
| Book Cover | DALL-E 3 API | Cost (~$0.10) vs. quality & speed | 1–2 min generation + review |
| Docusaurus Version | v3 + TypeScript | More complex config vs. future-proof | 30 min setup |
| CSS Strategy | CSS Modules + tokens | More verbose vs. maintainability | Ongoing (enforcement) |
| Image Format | WebP + PNG fallback | File size vs. browser support | Per-image optimization |
| Homepage | Custom React page | More code vs. full control | 2–3 hrs component dev |
| RAG Chunking | Section-level (H2/H3) | Less precision vs. retrieval accuracy | Enforced in lesson authoring |
| Architecture | Single Docusaurus | Coordination for future API vs. simplicity | Finalized |

---

## Outcomes & Next Steps

- ✅ All Phase 0 unknowns resolved
- ✅ Technical decisions documented with rationale
- ✅ Ready for Phase 1 (Design & Contracts)
- ⏭️ **Next**: Execute `/sp.tasks` to generate task breakdown for implementation

**Prepared by**: Claude Code (Spec-Driven Development)
**Validated by**: Implementation Plan Phase 0
**Date**: 2025-12-10
