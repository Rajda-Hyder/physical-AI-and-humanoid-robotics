<!--
Sync Impact Report:
Version change: 0.0.0 → 1.0.0
Modified principles: None (initial creation)
Added sections: Vision, Mission, Success Criteria, Constraints, Stakeholders, Scope, Tools, AI Integrations, Brand Voice
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/sp.constitution.md: ✅ updated
Follow-up TODOs: None
-->
# Physical AI & Humanoid Robotics Textbook Constitution

## Vision
To democratize advanced knowledge in Physical AI and Humanoid Robotics, enabling beginners to intermediate learners to build and innovate.

## Mission
To provide a clear, simple, and hands-on Docusaurus-based textbook that integrates cutting-edge AI tools, fostering practical skills and future-focused thinking within the Panaversity Hackathon I context.

## Core Principles

### I. Spec-Driven Development
The textbook development MUST strictly adhere to Spec-Kit Plus + Claude Code, ensuring clear requirements, planning, and task management.

### II. Docusaurus First
The textbook MUST be built using Docusaurus v3, leveraging its features for structured content, versioning, and deployment to GitHub Pages.

### III. Integrated RAG Chatbot
A Retrieval-Augmented Generation (RAG) chatbot MUST be seamlessly integrated using OpenAI Agents / ChatKit SDK, FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier to provide intelligent assistance based on book content and selected text.

### IV. Claude Code Augmentation
Claude Code Subagents and Reusable Agent Skills MUST be implemented to enhance development workflows and provide advanced automation capabilities.

### V. Secure User Authentication
Signup and Signin MUST be implemented using Better-Auth, collecting essential user hardware/software background for personalized experiences.

### VI. Personalized Learning Experience
A "Personalize Content" button MUST be available per chapter for logged-in users, adapting the content to their preferences and background.

### VII. Multilingual Accessibility
A "Translate to Urdu" button MUST be implemented per chapter to ensure broader accessibility for diverse learners.

### VIII. Clear & Concise Content
Content MUST be presented in a clear, simple, hands-on, and future-focused manner, adhering to a startup-oriented and friendly brand voice.

## Success Criteria
- Complete Docusaurus v3 textbook deployed to GitHub Pages.
- Fully functional RAG chatbot integrated.
- Claude Code Subagents and Reusable Agent Skills implemented.
- Secure Signup/Signin with user background collection.
- "Personalize Content" and "Translate to Urdu" buttons fully functional per chapter.
- Positive feedback from beginners to intermediate learners regarding clarity and hands-on approach.

## Constraints
- Panaversity Hackathon I context.
- Deployment to GitHub Pages.
- Utilize specified AI technologies: OpenAI Agents / ChatKit SDK, FastAPI, Neon Serverless Postgres, Qdrant Cloud Free Tier.
- Utilize specified authentication: Better-Auth.

## Stakeholders
Panaversity Team (Zia, Rehan, Junaid, Wania), authors, readers, students, hackathon reviewers.

## Scope

### In Scope
- Development of "Physical AI & Humanoid Robotics" textbook content.
- Docusaurus v3 implementation and deployment.
- RAG chatbot integration.
- Claude Code Subagents + Reusable Agent Skills implementation.
- Better-Auth Signup + Signin with user background collection.
- "Personalize Content" button per chapter.
- "Translate to Urdu" button per chapter.

### Out of Scope
- Advanced AI research beyond RAG chatbot.
- Complex custom UI frameworks (Docusaurus provides sufficient).
- Non-GitHub Pages deployment methods.

## Tools
- Docusaurus v3
- Spec-Kit Plus + Claude Code
- OpenAI Agents / ChatKit SDK
- FastAPI
- Neon Serverless Postgres
- Qdrant Cloud Free Tier
- Better-Auth

## AI Integrations
- RAG Chatbot for book content and selected text queries (OpenAI Agents / ChatKit SDK, FastAPI, Neon Serverless Postgres, Qdrant Cloud Free Tier).
- Claude Code Subagents + Reusable Agent Skills for development automation.

## Brand Voice
Clear, simple, hands-on, future-focused, startup-oriented, friendly tone.

## Governance
Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan. All PRs/reviews MUST verify compliance. Complexity MUST be justified.

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06
