---
id: 1
title: Create Docusaurus Textbook Constitution
stage: constitution
date: 2025-12-06
surface: agent
model: gemini
feature: Physical AI & Humanoid Robotics Textbook
branch: master
user: default_user
command: /sp.constitution
labels: [constitution, docusaurus, rag-chatbot, ai-integrations, panaversity-hackathon]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: null
---

## Prompt

   Create a constitution for a Docusaurus-based textbook titled “Physical AI & Humanoid Robotics”.

Include sections: Vision, Mission, Core Principles, Success Criteria, Constraints, Stakeholders, Scope, Tools, AI Integrations, Brand Voice.

Context: This constitution is for Panaversity Hackathon I.

Core Requirements:
1. Book must be spec-driven using Spec-Kit Plus + Claude Code.
2. Build complete Docusaurus v3 textbook and deploy to GitHub Pages.
3. Integrate a RAG chatbot using:
   - OpenAI Agents / ChatKit SDK
   - FastAPI backend
   - Neon Serverless Postgres
   - Qdrant Cloud Free Tier
   The chatbot must answer questions about the book and also answer questions based only on selected text on the page.

Bonus Requirements (add as official requirements):
- Implement Claude Code Subagents + Reusable Agent Skills.
-  Implement Signup + Signin using Better-Auth and collect user hardware/software background.
-  Add “Personalize Content” button per chapter for logged-in users.
-  Add “Translate to Urdu” button per chapter.

Audience: Beginners to intermediate learners in Physical AI & Robotics.

Brand Voice: Clear, simple, hands-on, future-focused, startup-oriented, friendly tone.

Stakeholders: Panaversity Team (Zia, Rehan, Junaid, Wania), authors, readers, students, hackathon reviewers.

Generate full constitution in clean Spec-Kit Plus format.

## Response snapshot

Created the initial constitution for the 'Physical AI & Humanoid Robotics' textbook, defining vision, mission, core principles, success criteria, scope, tools, AI integrations, brand voice, and governance.

## Outcome

- ✅ Impact: Successfully established foundational governance and architectural guidelines for the project.
- 🧪 Tests: No specific tests for constitution creation, but internal consistency checks were performed.
- 📁 Files: Updated `.specify/memory/constitution.md`.
- 🔁 Next prompts: User will likely proceed with spec generation or further planning.
- 🧠 Reflection: Constitution created with all requested sections and core requirements. Versioned as 1.0.0. All templates assumed to be in sync for this initial version.

## Evaluation notes (flywheel)

- Failure modes observed: None observed.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
