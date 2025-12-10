# Data Model: Physical AI & Humanoid Robotics Textbook

**Phase**: 1 (Design & Contracts)
**Date**: 2025-12-10
**Source**: Feature Specification + Implementation Plan

---

## Overview

This document defines the data model for the Physical AI & Humanoid Robotics textbook, including content structure, metadata, and relationships. The model ensures RAG compatibility, supports personalization, and maintains alignment with the lesson format mandated by the Constitution.

---

## 1. Core Entities

### 1.1 Module Entity

**Purpose**: Represents a textbook module (chapter) grouping 3 lessons.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `moduleId` | string | ✅ | Unique identifier (e.g., `module-1`) |
| `moduleNumber` | number | ✅ | Sequential number (1–4) |
| `title` | string | ✅ | Module title (e.g., "Foundations of Physical AI") |
| `description` | string | ✅ | 1–2 sentence overview |
| `learningGoals` | string[] | ✅ | 3–5 bulleted learning goals |
| `learningOutcomes` | string[] | ✅ | 3–5 measurable outcomes |
| `icon` | string | ✅ | Icon identifier (e.g., `FoundationsIcon`) |
| `lessons` | Lesson[] | ✅ | Array of 3 lesson objects (see 1.2) |
| `duration` | string | ✅ | Total estimated time (e.g., "50–60 min") |
| `tags` | string[] | ✅ | Categories (e.g., `[physical-ai, robotics, beginner]`) |
| `order` | number | ✅ | Sidebar display order (1–4) |

**Example**:

```json
{
  "moduleId": "module-1",
  "moduleNumber": 1,
  "title": "Foundations of Physical AI",
  "description": "This module introduces fundamental concepts of Physical AI, differentiating it from traditional software AI and laying the groundwork for understanding embodied intelligence.",
  "learningGoals": [
    "Understand the definition of Physical AI",
    "Distinguish between software and embodied AI",
    "Identify key foundational concepts"
  ],
  "learningOutcomes": [
    "Define Physical AI",
    "Explain the differences between software and embodied AI",
    "Describe basic concepts necessary for physical AI systems"
  ],
  "icon": "FoundationsIcon",
  "lessons": [ /* see 1.2 */ ],
  "duration": "50–60 min",
  "tags": ["physical-ai", "robotics", "beginner", "module-1"],
  "order": 1
}
```

---

### 1.2 Lesson Entity

**Purpose**: Represents a single lesson within a module.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lessonId` | string | ✅ | Unique identifier (e.g., `lesson-1-1`) |
| `moduleId` | string | ✅ | Parent module ID (foreign key) |
| `number` | string | ✅ | Lesson number in format "M.L" (e.g., `1.1`) |
| `title` | string | ✅ | Lesson title |
| `description` | string | ✅ | 1–2 sentence overview |
| `file` | string | ✅ | MDX file path (e.g., `lesson-1-1-intro-to-physical-ai.mdx`) |
| `sidebar_position` | number | ✅ | Position within module (1–3) |
| `expectedSkills` | string[] | ✅ | Learning outcomes (e.g., "Define Physical AI") |
| `duration` | string | ✅ | Estimated time (e.g., "15–20 min") |
| `tags` | string[] | ✅ | Tags for search (e.g., `[lesson-1-1, beginner]`) |
| `sections` | Section[] | ✅ | 8-point lesson format sections (see 1.3) |
| `images` | Image[] | ⚠️ | Associated images for lesson |

**Example**:

```json
{
  "lessonId": "lesson-1-1",
  "moduleId": "module-1",
  "number": "1.1",
  "title": "Introduction to Physical AI",
  "description": "This lesson defines Physical AI, exploring its scope, applications, and historical context. It explains why AI needs a physical form to interact with the real world.",
  "file": "lesson-1-1-intro-to-physical-ai.mdx",
  "sidebar_position": 1,
  "expectedSkills": [
    "Define Physical AI",
    "Recognize common Physical AI applications"
  ],
  "duration": "15–20 min",
  "tags": ["lesson-1-1", "beginner", "module-1"],
  "sections": [ /* see 1.3 */ ],
  "images": [ /* see 1.4 */ ]
}
```

---

### 1.3 Section Entity (Lesson Structure)

**Purpose**: Represents the 8-point lesson format mandated by Constitution Section 2.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sectionType` | enum | ✅ | One of: `overview`, `objectives`, `core_concepts`, `hands_on`, `mindset`, `misconceptions`, `summary`, `questions` |
| `heading` | string | ✅ | H2 heading text (e.g., "Lesson Overview") |
| `content` | string | ✅ | Full markdown/MDX content for section |
| `subheadings` | Subheading[] | ⚠️ | H3 subheadings within section (for granular RAG chunking) |
| `images` | Image[] | ⚠️ | Images within section |
| `estimatedTokens` | number | ✅ | Token count (for RAG embedding planning) |

**Example**:

```json
{
  "sectionType": "core_concepts",
  "heading": "Core Concepts",
  "content": "Physical AI refers to artificial intelligence systems integrated into physical robots or autonomous systems that interact with the real world. Unlike purely software-based AI (e.g., chatbots, recommendation systems), Physical AI must contend with ...",
  "subheadings": [
    {
      "heading": "What is Physical AI?",
      "content": "..."
    },
    {
      "heading": "Embodiment vs. Software AI",
      "content": "..."
    }
  ],
  "images": [],
  "estimatedTokens": 450
}
```

---

### 1.4 Image Entity

**Purpose**: Represents images used in lessons, with metadata for RAG and accessibility.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `imageId` | string | ✅ | Unique identifier (e.g., `img-lesson-1-1-robot-perception`) |
| `lessonId` | string | ✅ | Parent lesson ID |
| `filename` | string | ✅ | File name (e.g., `robot-perception.png`) |
| `path` | string | ✅ | Full path (e.g., `/static/img/module-1/lesson-1-1/robot-perception`) |
| `alt` | string | ✅ | Alt text for accessibility & RAG metadata |
| `caption` | string | ✅ | Figure caption (e.g., "Figure 1.1: Sensors enable robots to perceive...") |
| `formats` | object | ✅ | `{ webp: "...", png: "...", svg?: "..." }` |
| `width` | number | ✅ | Image width (px) |
| `height` | number | ✅ | Image height (px) |
| `sectionType` | enum | ⚠️ | Which 8-point section this image belongs to |
| `description` | string | ⚠️ | Longer description for RAG (if alt text too terse) |

**Example**:

```json
{
  "imageId": "img-lesson-1-1-robot-perception",
  "lessonId": "lesson-1-1",
  "filename": "robot-perception.png",
  "path": "/static/img/module-1/lesson-1-1/robot-perception",
  "alt": "Humanoid robot with labeled perception sensors including cameras, lidar, microphones, and force sensors",
  "caption": "Figure 1.1: Sensors enable robots to perceive their environment",
  "formats": {
    "webp": "/static/img/module-1/lesson-1-1/robot-perception.webp",
    "png": "/static/img/module-1/lesson-1-1/robot-perception.png"
  },
  "width": 1200,
  "height": 600,
  "sectionType": "core_concepts",
  "description": "This diagram illustrates the primary sensory systems of a typical humanoid robot, showing how different sensor modalities contribute to perception."
}
```

---

### 1.5 Frontmatter Entity (MDX Metadata)

**Purpose**: YAML frontmatter for each lesson MDX file, enabling Docusaurus metadata and RAG ingestion.

**Fields** (YAML):

```yaml
---
title: "Descriptive Lesson Title"
description: "A concise summary of the lesson content."
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

---

## 2. Content Structure (Directory & File Mapping)

### 2.1 Directory Layout

```
/docs
├── intro.mdx                        # Homepage intro (redirects to custom page)
├── _category_.json                  # Root sidebar config
│
├── module-1-foundations/
│   ├── _category_.json              # Module-level sidebar config
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
```

### 2.2 `_category_.json` Schema

**Purpose**: Docusaurus sidebar configuration for module grouping.

**Structure**:

```json
{
  "label": "Module 1: Foundations of Physical AI",
  "position": 1,
  "collapsed": false,
  "className": "module-category"
}
```

---

## 3. Component Data Models

### 3.1 ModuleCard Component Props

```typescript
interface ModuleCardProps {
  moduleNumber: number;
  title: string;
  description: string;
  icon: React.ReactNode;
  learningGoals: string[];
  lessonCount: number;
  onClick: () => void;
}
```

**Derived from**: Module entity (fields: `moduleNumber`, `title`, `description`, `icon`, `learningGoals`, `lessons.length`)

### 3.2 FeaturesSection Component Props

```typescript
interface Feature {
  title: string;
  description: string;
  icon: React.ReactNode;
}

interface FeaturesSectionProps {
  features: Feature[];
}
```

**Hardcoded Features**:
```typescript
const FEATURES: Feature[] = [
  {
    title: "Hands-on Learning",
    description: "Every lesson includes practical experiments and exercises to reinforce concepts through real-world application."
  },
  {
    title: "AI-Powered Insights",
    description: "An integrated RAG chatbot provides intelligent assistance based on the textbook content and your questions."
  },
  {
    title: "Real-World Robotics",
    description: "Content grounded in actual physical robots and humanoid systems, not just abstract theory."
  }
];
```

### 3.3 Figure Component Props

```typescript
interface FigureProps {
  src: string;
  alt: string;
  caption: string;
  width?: number;
  height?: number;
  srcSet?: string; // For responsive images
}
```

---

## 4. RAG Integration Data Model

### 4.1 RAG Chunk Schema (Qdrant Document)

**Purpose**: Structure for embedding and storing lesson content in Qdrant.

```json
{
  "id": "chunk-lesson-1-1-core-concepts-001",
  "content": "Physical AI refers to artificial intelligence systems integrated into physical robots...",
  "metadata": {
    "module_id": "module-1",
    "module_number": 1,
    "module_title": "Foundations of Physical AI",
    "lesson_id": "lesson-1-1",
    "lesson_number": "1.1",
    "lesson_title": "Introduction to Physical AI",
    "section_type": "core_concepts",
    "section_heading": "Core Concepts",
    "subsection_heading": "What is Physical AI?",
    "content_type": "text",
    "document_url": "https://[domain]/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai",
    "tags": ["physical-ai", "robotics", "beginner", "module-1", "lesson-1-1"],
    "estimated_read_time_min": 3,
    "difficulty_level": "beginner"
  },
  "vector": [ /* 1536-dim embedding */ ]
}
```

### 4.2 RAG Query Response Schema

**Purpose**: Chatbot response structure.

```json
{
  "query": "What is Physical AI?",
  "response": "Physical AI refers to artificial intelligence systems integrated into physical robots or autonomous systems...",
  "sources": [
    {
      "chunk_id": "chunk-lesson-1-1-core-concepts-001",
      "lesson_title": "Introduction to Physical AI",
      "section": "Core Concepts",
      "relevance_score": 0.92,
      "url": "https://[domain]/docs/module-1-foundations/lesson-1-1-intro-to-physical-ai#core-concepts"
    }
  ],
  "confidence": 0.88
}
```

---

## 5. Personalization & Translation Readiness

### 5.1 User Profile Data Model (Future, deferred to Phase 2)

**Purpose**: Support "Personalize Content" feature per Constitution Principle VI.

```json
{
  "userId": "user-123",
  "background": {
    "experience_level": "beginner", // beginner, intermediate, advanced
    "prior_knowledge": ["python", "robotics-basics"],
    "learning_style": "hands-on", // hands-on, visual, theoretical
    "interests": ["humanoid-robots", "ai"]
  },
  "personalization_preferences": {
    "example_style": "code", // code, diagrams, real-world
    "language_preference": "english",
    "content_depth": "standard" // brief, standard, detailed
  }
}
```

### 5.2 Translation Metadata (Future, deferred to Phase 2)

**Purpose**: Support "Translate to Urdu" feature per Constitution Principle VII.

```json
{
  "lesson_id": "lesson-1-1",
  "original_language": "en",
  "available_languages": ["en", "ur"],
  "translation_status": {
    "ur": {
      "status": "pending", // pending, in-progress, completed, review
      "translator": null,
      "last_updated": null,
      "revision": 0
    }
  },
  "translation_notes": "Ensure technical terms like 'embodied intelligence' are transliterated correctly."
}
```

---

## 6. Content Validation Rules

### 6.1 Lesson Validation

- [ ] Frontmatter contains all required fields (title, description, sidebar_position, tags)
- [ ] 8 sections present in correct order (overview, objectives, core_concepts, hands_on, mindset, misconceptions, summary, questions)
- [ ] Each section has at least 1 paragraph of content
- [ ] All images have alt text and captions
- [ ] No hardcoded hex colors or pixel values (except via CSS variables)
- [ ] Markdown syntax is valid (no broken links, lists, or code blocks)
- [ ] Content is beginner-friendly (no unexplained jargon)
- [ ] Concepts explicitly tied to Physical AI/robotics

### 6.2 Module Validation

- [ ] Module contains exactly 3 lessons
- [ ] All lessons follow sidebar_position order (1, 2, 3)
- [ ] Module title and description match spec
- [ ] Learning goals and outcomes are distinct and measurable

### 6.3 Image Validation

- [ ] All images have WebP and PNG formats
- [ ] Alt text is descriptive and concise (< 125 characters)
- [ ] Caption includes figure number (e.g., "Figure 1.1: ...")
- [ ] File sizes optimized (< 80KB for covers, < 30KB for lesson images)
- [ ] Image paths match structure: `/static/img/module-{n}/lesson-{n}-{m}/`

---

## 7. Relationships & Dependencies

```
Module (1) -->> (3) Lessons
Lesson (1) -->> (8) Sections
Section (1) -->> (N) Images
Section (1) -->> (N) Subheadings
Image (1) -->> (2+) Formats (WebP, PNG)
```

**Cardinality Notes**:
- Each module has exactly 3 lessons (not fewer, not more)
- Each lesson has exactly 8 sections (per Constitution Section 2)
- Each section can have multiple images and subheadings
- Each image must have at least WebP + PNG formats

---

## 8. Data Serialization & Storage

### 8.1 Docusaurus Storage (Source of Truth)

**Location**: `/docs/module-{n}/lesson-{n}-{m}.mdx`

**Format**: MDX (Markdown + React JSX)

**Frontmatter**: YAML block at top of file

**Example**:

```mdx
---
title: "Introduction to Physical AI"
description: "This lesson defines Physical AI..."
sidebar_position: 1
tags: [physical-ai, robotics, beginner, module-1, lesson-1-1]
---

## Lesson Overview

[Content in markdown]

## Learning Objectives

- Define Physical AI
- [...]

## Core Concepts

### What is Physical AI?

[Content...]

## [... remaining 5 sections ...]
```

### 8.2 RAG Storage (Future)

**Location**: Qdrant Cloud Free Tier

**Format**: JSON documents with vector embeddings

**Sync Process** (Phase 2+):
1. Export all `.mdx` files
2. Parse frontmatter + section headings
3. Generate embeddings per section
4. Upload to Qdrant with metadata
5. Index for fast retrieval

### 8.3 Metadata Export (Homepage Components)

**Location**: `src/data/modules.ts` (generated or manually maintained)

**Format**: TypeScript constant

**Example**:

```typescript
export const MODULES: Module[] = [
  {
    moduleId: "module-1",
    moduleNumber: 1,
    title: "Foundations of Physical AI",
    description: "Essential concepts...",
    icon: FoundationsIcon,
    learningGoals: [
      "Understand Physical AI definition",
      "Distinguish software vs. embodied AI",
      "Identify core concepts"
    ],
    lessons: [
      { lessonId: "lesson-1-1", number: "1.1", title: "..." },
      // ... lessons 1.2, 1.3
    ]
  },
  // ... modules 2-4
];
```

---

## 9. Summary

| Entity | Count | Source of Truth | RAG Role |
|--------|-------|-----------------|----------|
| Modules | 4 | `/docs/module-*/` | Metadata only |
| Lessons | 12 | `/docs/module-*/lesson-*.mdx` | Content + chunks |
| Sections | 96 (12 × 8) | Within lesson MDX | Granular chunks |
| Images | 30–40 | `/static/img/` | Metadata (alt+caption) |

**Validation**: All content adheres to Constitution Section 2 (lesson format), Section 3 (Docusaurus structure), and Section 4 (RAG readiness).

**Next Steps**: Phase 2 (`/sp.tasks`) will break down implementation into testable, actionable tasks.

---

**Prepared by**: Claude Code (Spec-Driven Development)
**Date**: 2025-12-10
