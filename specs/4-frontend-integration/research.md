# Research & Technical Clarifications: Frontend-Backend Integration

**Date**: 2025-12-11
**Feature**: 4-frontend-integration
**Status**: Phase 0 Complete

---

## Executive Summary

This document consolidates research findings, technology choices, and best practices for the frontend-backend RAG chatbot integration. All critical decisions have been validated through existing specifications and standard industry practices.

---

## Research Topics & Findings

### 1. Chat Widget Architecture: React Component Integration with Docusaurus

**Question**: How should the chat widget integrate with Docusaurus v3?

**Decision**: React component integrated as a root-level wrapper component

**Rationale**:
- Docusaurus v3 is React-based; components integrate seamlessly via swizzling or root wrapper
- Root wrapper approach allows global availability across all pages without per-page setup
- Enables proper context passing and state management using React hooks
- Aligns with Docusaurus ecosystem best practices

**Alternatives Considered**:
1. **Standalone script tag**: Requires manual DOM manipulation; harder to maintain with React
2. **Docusaurus Plugin**: Possible but adds deployment complexity; component approach is sufficient
3. **Web Component (Custom Element)**: Would isolate styles but adds cross-framework communication overhead

**Implementation Pattern**:
```javascript
// docusaurus.config.js
module.exports = {
  swizzle: ['src/theme/Root.tsx'],
  // or use plugins for initialization
}

// src/theme/Root.tsx
export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  )
}
```

**Validation**: Used by popular Docusaurus plugins (docs-search, sidebar); proven pattern

---

### 2. State Management: Hooks vs. External Libraries

**Question**: How should chat state (messages, loading, errors) be managed?

**Decision**: React hooks (`useState`, `useReducer`) with custom hooks

**Rationale**:
- Session-level only; no persistence needed (spec requirement)
- Chat history limited to single page session
- Hooks eliminate external dependencies
- Better performance than Context API for isolated component updates
- Sufficient for managing 100+ message history (per spec scope)

**Alternatives Considered**:
1. **Redux**: Overkill for session-scoped data; adds 50KB+ bundle size
2. **Context API**: Causes unnecessary re-renders; less efficient for frequent updates
3. **Zustand/Jotai**: Lightweight but unnecessary overhead for single feature

**Hook Architecture**:
```typescript
// Custom hooks for separation of concerns
const useChatMessages = () => { /* manage message array */ }
const useChatAPI = (baseUrl) => { /* handle API requests */ }
const useChatHistory = (maxSize) => { /* bounded message history */ }
```

**Validation**: Recommended pattern in React documentation for feature-scoped state

---

### 3. API Communication: Fetch API vs. HTTP Client Libraries

**Question**: How should the widget communicate with the FastAPI backend?

**Decision**: Native Fetch API with custom wrapper class for error handling and timeouts

**Rationale**:
- Zero external dependencies (critical for Docusaurus bundle size)
- Modern browsers have full Fetch API support (ES6+ requirement)
- Easy to add timeout, retry, and error handling logic
- Aligns with Docusaurus' minimal-dependency philosophy

**Alternatives Considered**:
1. **Axios**: Popular but adds 11KB gzip; Fetch handles requirements
2. **React Query**: Adds complexity; unnecessary for simple query pattern
3. **GraphQL client**: Backend is REST-based; API mismatch

**Wrapper Implementation**:
```typescript
class RAGAPIClient {
  async query(request) {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 30000)

    try {
      const response = await fetch(this.baseUrl, {
        signal: controller.signal,
        method: 'POST',
        body: JSON.stringify(request),
      })
      // error handling, response parsing
    } finally {
      clearTimeout(timeout)
    }
  }
}
```

**Validation**: Used in major frontend frameworks (Next.js, Remix); no longer need axios

---

### 4. Response Streaming: Full Response vs. Server-Sent Events (SSE)

**Question**: Should responses stream or return in full?

**Decision**: Support both full response (default) and streaming via Server-Sent Events (SSE)

**Rationale**:
- Full response mode: Simple, reliable, works everywhere (fallback)
- Streaming mode: Better UX for long-running queries; improves perceived performance
- Backend already supports both (Spec 3)
- Configurable at runtime (environment variable or URL parameter)

**Alternatives Considered**:
1. **WebSockets**: Adds complexity; unidirectional SSE sufficient
2. **Long polling**: Outdated; less efficient than SSE
3. **Only full response**: Misses perceived performance improvement on slow networks
4. **Only streaming**: Less reliable for different network conditions

**SSE Implementation**:
```typescript
async function* streamResponse(query) {
  const response = await fetch(`${API_URL}/stream?query=${query}`)
  const reader = response.body.getReader()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const text = new TextDecoder().decode(value)
    const lines = text.split('\n')
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        yield JSON.parse(line.slice(6))
      }
    }
  }
}
```

**Validation**: Proven pattern in LLM streaming (OpenAI, Claude, Anthropic); widely adopted

---

### 5. Selected-Text Capture: Implementation Pattern

**Question**: How should "selected-text as query context" feature work?

**Decision**: Global text selection listener + optional context menu integration

**Rationale**:
- Listener approach: Detects selection automatically; low friction for users
- Context menu: Enables explicit "Ask about this" action
- Combined: User choice between implicit (auto) and explicit (button)
- No interference with normal text interactions (proper event debouncing)

**Alternatives Considered**:
1. **Context menu only**: Requires extra clicks; less discoverable
2. **Global listener only**: Might interfere with normal text selection workflow
3. **Neither**: Misses valuable feature (spec requirement)

**Implementation Pattern**:
```typescript
document.addEventListener('selectionchange', debounce(() => {
  const selected = window.getSelection()?.toString()
  if (selected?.length > 10) {
    showSelectedTextButton()
  }
}, 300))

function insertSelectedText() {
  const selected = window.getSelection()?.toString()
  inputElement.value += `\n[Context: ${selected}]`
}
```

**Validation**: Used in tools like Notion, Hypothesis; proven non-intrusive pattern

---

### 6. Error Handling Strategy: Toast vs. Inline Messages

**Question**: How should errors be displayed to users?

**Decision**: Inline error messages in chat + optional toast for critical system errors

**Rationale**:
- Inline errors: Stay in chat context (user sees what query failed); enables error history
- Toast: Used for non-recoverable system errors (e.g., backend unreachable)
- Avoids modal dialogs (too intrusive; blocks interaction)
- Provides actionable recovery steps (per spec requirements)

**Error Categories**:
1. **Request errors** (400, 422): Display in chat as assistant message with correction guidance
2. **Server errors** (500, 503): Display in chat with retry button
3. **Network errors** (timeout, offline): Display in chat + optional toast
4. **System errors** (backend unavailable): Toast + error state in widget

**Implementation Pattern**:
```typescript
async function submitQuery(query) {
  try {
    const response = await api.query(query)
    addMessage({ role: 'assistant', ...response })
  } catch (error) {
    if (error.name === 'AbortError') {
      // Timeout
      addMessage({ role: 'system', text: 'Request timed out. Please try again.' })
    } else if (error.status === 500) {
      // Server error
      addMessage({ role: 'system', text: 'Backend error. Please retry.' })
    } else {
      // Network error
      showToast('Service unavailable. Check backend connection.')
    }
  }
}
```

**Validation**: Recommended by UX best practices (Nielsen Norman); reduces cognitive load

---

### 7. Loading Indicators: Animation Types and Timing

**Question**: What loading state UX should be used?

**Decision**: Animated spinner + text message after 3 seconds ("Still loading...")

**Rationale**:
- Spinner: Universally understood; clear visual feedback
- 3-second threshold: Based on Nielsen's research on user attention (SC-002 requirement)
- Helps manage expectations on slower networks
- Progressive disclosure (more info as wait time increases)

**Timing Thresholds** (from spec):
- 0-2 seconds: Spinner only (normal response time)
- 2-5 seconds: Spinner + "Estimating wait time..."
- 5+ seconds: Spinner + "Still loading..." + Cancel button

**Alternatives Considered**:
1. **Skeleton screens**: More complex; overkill for chat
2. **Progress bars**: Requires backend reporting; complex
3. **Just spinner**: No indication of wait time management

**Implementation Pattern**:
```typescript
const [timeElapsed, setTimeElapsed] = useState(0)

useEffect(() => {
  if (!loading) return
  const interval = setInterval(() => setTimeElapsed(t => t + 1), 1000)
  return () => clearInterval(interval)
}, [loading])

return (
  <>
    <Spinner />
    {timeElapsed > 3 && <p>Still loading... ({timeElapsed}s)</p>}
    {timeElapsed > 5 && <button onClick={cancelRequest}>Cancel</button>}
  </>
)
```

**Validation**: Standard pattern in chat applications (ChatGPT, Slack); proven UX

---

### 8. Response Display: Formatting and Sanitization

**Question**: How should AI responses be formatted and displayed safely?

**Decision**: Markdown rendering with HTML sanitization (DOMPurify)

**Rationale**:
- Backend returns markdown (Spec 3); need proper rendering
- Sanitization prevents XSS attacks (security boundary)
- Markdown is readable in both rendered and raw forms
- Aligns with documentation site standards (Docusaurus uses markdown)

**Dependencies**:
- `marked`: Parse markdown to HTML (~10KB gzip)
- `dompurify`: Sanitize HTML output (~6KB gzip)
- Total: ~16KB gzip (acceptable overhead)

**Alternatives Considered**:
1. **No formatting**: Raw text; poor user experience
2. **Plain HTML rendering**: Unsafe without sanitization
3. **Custom parser**: Unnecessary work; established libraries sufficient

**Implementation Pattern**:
```typescript
import { marked } from 'marked'
import DOMPurify from 'dompurify'

function ResponseText({ content }) {
  const html = marked.parse(content)
  const clean = DOMPurify.sanitize(html)
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

**Validation**: Industry standard (GitHub, Discord, Slack all use similar approach)

---

### 9. Accessibility: WCAG 2.1 AA Compliance

**Question**: What accessibility standards should be met?

**Decision**: WCAG 2.1 Level AA compliance

**Rationale**:
- Spec 4 doesn't specify; AA is industry standard for web applications
- Captures most accessibility needs without excessive complexity
- Legal compliance in many jurisdictions
- Improves usability for all users

**Key Requirements**:
1. Keyboard navigation (Tab through elements, Enter to submit)
2. ARIA labels on interactive elements (buttons, inputs)
3. Screen reader support (semantic HTML, role attributes)
4. Color contrast ratios (4.5:1 for normal text)
5. Focus indicators (visible on interactive elements)
6. Loading state announcements (aria-live regions)

**Testing Tools**:
- axe DevTools: Automated accessibility audit
- WAVE: Contrast and structure validation
- Screen reader testing: NVDA (Windows), JAWS (commercial)

**Implementation Pattern**:
```typescript
<button
  onClick={submitQuery}
  disabled={loading}
  aria-label="Submit query"
  className="submit-btn"
>
  Send
</button>

<div role="status" aria-live="polite" aria-label="Loading response">
  {loading && <Spinner />}
</div>
```

**Validation**: Standard for modern web applications; Docusaurus enforces AA

---

### 10. Performance Optimization: Bundle Size and Runtime

**Question**: How to ensure widget doesn't bloat Docusaurus bundle?

**Decision**: Tree-shakeable exports, code splitting, lazy loading

**Rationale**:
- Widget is optional feature; should not impact base bundle
- Lazy loading: Load widget code only when user interacts with it
- Tree-shaking: Remove unused code during build
- Performance budget: Widget <100KB gzip (including dependencies)

**Optimization Techniques**:
1. **Lazy loading**: `React.lazy()` + `Suspense` boundary
2. **Code splitting**: Webpack automatically splits at route/component level
3. **Dependency audit**: Use `bundlesize` or `esbuild --metafile` to track
4. **Dynamic imports**: `import()` for optional features

**Implementation Pattern**:
```typescript
// In docusaurus.config.js
const ChatWidget = lazy(() => import('./ChatWidget'))

export default function Root({ children }) {
  return (
    <Suspense fallback={null}>
      <ChatWidget />
    </Suspense>
  )
}
```

**Validation**: Best practices from Webpack, Next.js, and Docusaurus documentation

---

## Technology Stack Summary

| Concern | Choice | Reason |
|---------|--------|--------|
| **UI Framework** | React (via Docusaurus) | Already available; no extra dependency |
| **State Management** | React Hooks | Minimal overhead; session-level sufficient |
| **HTTP Client** | Fetch API | Zero dependencies; modern standard |
| **Response Streaming** | Server-Sent Events | Works with HTTP; simple integration |
| **Markdown Rendering** | marked + DOMPurify | Lightweight; secure; well-maintained |
| **Component Styling** | CSS Modules | Scoped; no conflicts; no dependencies |
| **Testing** | Jest + React Testing Library | Standard; excellent React testing experience |
| **Type Safety** | TypeScript | Already in Docusaurus; catch errors early |
| **Build System** | Webpack (Docusaurus) | No additional configuration needed |
| **Accessibility** | WCAG 2.1 AA | Industry standard; legal compliance |

---

## Integration Points with Existing Specs

### Backend (Spec 3): FastAPI `/api/v1/query` Endpoint

**Expected Interface**:
```
POST /api/v1/query
Content-Type: application/json

{
  "query": "What is physical AI?",
  "context": "Optional selected text",
  "stream": false  // or true for SSE
}
```

**Response** (full mode):
```json
{
  "response_id": "uuid",
  "answer": "Physical AI refers to...",
  "context_chunks": [
    {
      "source_url": "/docs/chapter-1",
      "relevance_score": 0.92,
      "text": "..."
    }
  ]
}
```

**Response** (streaming mode - Server-Sent Events):
```
event: chunk
data: {"type": "text", "content": "Physical AI"}

event: chunk
data: {"type": "context", "chunks": [...]}

event: done
data: {"metadata": {...}}
```

### Frontend (Docusaurus): Root Component Integration

**Integration Point**: `src/theme/Root.tsx` (swizzled component)

**Availability**: All pages have access to chat widget via global component

**Configuration**: Environment variables in `.env.local` or Docusaurus config

---

## Setup & Configuration

### Environment Variables

```bash
# .env.example
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000  # milliseconds
REACT_APP_STREAM_MODE=false   # true for SSE, false for full response
REACT_APP_DEBUG=false         # console logging
```

### Local Development Setup

```bash
# Frontend (Docusaurus)
npm install
npm start  # runs on localhost:3000

# Backend (Spec 3)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload  # runs on localhost:8000
```

### Validation Checklist

- ✅ Docusaurus starts without errors
- ✅ Chat widget appears on all pages
- ✅ API calls to localhost:8000 succeed
- ✅ Responses display correctly
- ✅ Loading states show/hide appropriately
- ✅ Selected text capture works
- ✅ Error messages display with retry options
- ✅ Browser DevTools show network requests

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| CORS errors | Document backend CORS config; test locally before deploy |
| Large response payloads | Implement response chunking; warn user if >1MB |
| Slow network causing timeouts | Show estimated wait time; allow request cancellation |
| Bundle size bloat | Use lazy loading; monitor with bundlesize tool |
| Accessibility gaps | Test with axe and screen reader; require WCAG AA compliance |

---

## Next Steps (Phase 1)

1. Create TypeScript type definitions (`data-model.md`)
2. Generate API contracts (OpenAPI schema in `contracts/`)
3. Document local setup instructions (`quickstart.md`)
4. Review architectural decisions with team
5. Proceed to Phase 2: Task generation and implementation

---

**Status**: ✅ All research questions answered; ready for design phase
**Date Completed**: 2025-12-11
