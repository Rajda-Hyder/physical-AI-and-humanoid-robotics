# Data Model: Frontend-Backend Integration

**Date**: 2025-12-11
**Feature**: 4-frontend-integration
**Status**: Phase 1 Complete

---

## Overview

This document defines the data structures (entities, types, interfaces) used in the frontend chat widget and its integration with the FastAPI backend. All entities are designed to be serializable to/from JSON for HTTP communication.

---

## Entity Definitions

### 1. ChatMessage

**Purpose**: Represents a single message in the chat history (user query or AI response)

**Fields**:

```typescript
interface ChatMessage {
  id: string                    // UUID or sequential ID
  role: 'user' | 'assistant' | 'system'
  content: string              // Message text (may be markdown)
  timestamp: number            // Unix timestamp (ms)
  metadata?: {
    tokens?: number            // Token count (from backend)
    responseTime?: number      // Time to generate (ms)
    confidence?: number        // Relevance score (0-1) for assistant
  }
  sources?: ContextChunk[]     // Retrieved sources (assistant only)
  error?: {
    code: string              // Error code
    message: string           // User-friendly message
    retry?: boolean           // Whether retry is possible
  }
}
```

**Validation Rules**:
- `id`: Must be unique within session
- `role`: Exactly one of three values
- `content`: Non-empty string, max 10,000 characters (per spec edge case)
- `timestamp`: Positive integer
- `sources`: Array of valid ContextChunk objects (assistant messages only)

**State Transitions**:
```
User query → ChatMessage(role: 'user') [immediate display]
     ↓
API request sent → ChatMessage(role: 'assistant', content: '', metadata: {loading: true})
     ↓
Response received → ChatMessage updated with content + sources
     ↓
Error occurs → ChatMessage updated with error object
```

**Examples**:

```json
{
  "id": "msg-001",
  "role": "user",
  "content": "What is physical AI?",
  "timestamp": 1702329600000,
  "metadata": {}
}

{
  "id": "msg-002",
  "role": "assistant",
  "content": "Physical AI refers to artificial intelligence systems that interact with the physical world...",
  "timestamp": 1702329603000,
  "metadata": {
    "tokens": 156,
    "responseTime": 2341,
    "confidence": 0.87
  },
  "sources": [
    {
      "source_url": "/docs/chapter-1/intro#physical-ai",
      "relevance_score": 0.92,
      "text": "Physical AI (or embodied AI) refers to..."
    }
  ]
}

{
  "id": "msg-003",
  "role": "system",
  "content": "Request timed out. Please try again.",
  "timestamp": 1702329635000,
  "error": {
    "code": "TIMEOUT",
    "message": "Backend request exceeded 30 seconds",
    "retry": true
  }
}
```

---

### 2. QueryRequest

**Purpose**: HTTP request payload sent from frontend to backend API

**Fields**:

```typescript
interface QueryRequest {
  query: string                // User's question (required)
  context?: string             // Optional selected text or history
  conversation_id?: string     // Optional session identifier
  stream?: boolean             // Streaming response (SSE) vs. full
  metadata?: {
    source: 'chat' | 'selected-text'  // Query origin
    clientVersion?: string     // Widget version
    environment?: 'development' | 'production'
  }
}
```

**Validation Rules**:
- `query`: Non-empty, max 10,000 characters
- `context`: Max 5,000 characters (excerpt from documentation)
- `stream`: Boolean; defaults to false
- `conversation_id`: UUID format if provided

**Examples**:

```json
{
  "query": "How do I start with robotics?",
  "context": null,
  "stream": false,
  "metadata": {
    "source": "chat",
    "clientVersion": "1.0.0",
    "environment": "development"
  }
}

{
  "query": "Explain this concept",
  "context": "The concept of feedback loops in control systems...",
  "stream": true,
  "metadata": {
    "source": "selected-text",
    "clientVersion": "1.0.0"
  }
}
```

---

### 3. ResponsePayload

**Purpose**: HTTP response from backend containing answer and context

**Fields**:

```typescript
interface ResponsePayload {
  response_id: string               // UUID
  answer: string                    // Generated response (markdown)
  context_chunks: ContextChunk[]    // Retrieved documents
  metadata: {
    model: string                   // Model name (e.g., "gpt-4")
    tokens_used: number             // Total tokens
    response_time_ms: number        // Generation time
    timestamp: number               // Response time
    version: string                 // API version
  }
}
```

**Validation Rules**:
- `response_id`: UUID format
- `answer`: Non-empty string
- `context_chunks`: Array of valid ContextChunk objects
- Total payload size: Max 1MB (per spec constraint)

**Examples**:

```json
{
  "response_id": "resp-uuid-12345",
  "answer": "# Physical AI\n\nPhysical AI refers to artificial intelligence systems that interact with physical environments through sensors and actuators...",
  "context_chunks": [
    {
      "source_url": "/docs/chapter-1/intro#physical-ai",
      "relevance_score": 0.95,
      "text": "Physical AI (or embodied AI) is..."
    },
    {
      "source_url": "/docs/chapter-2/sensors",
      "relevance_score": 0.87,
      "text": "Sensors enable robots to perceive..."
    }
  ],
  "metadata": {
    "model": "gpt-4-turbo",
    "tokens_used": 156,
    "response_time_ms": 2341,
    "timestamp": 1702329603000,
    "version": "1.0.0"
  }
}
```

---

### 4. ContextChunk

**Purpose**: A single source document retrieved by the RAG system

**Fields**:

```typescript
interface ContextChunk {
  source_url: string           // URL to documentation section
  relevance_score: number      // 0-1, confidence in relevance
  text: string                 // Text preview/excerpt
  metadata?: {
    title?: string             // Document title
    chapter?: string           // Chapter or section name
    timestamp?: number         // When indexed
  }
}
```

**Validation Rules**:
- `source_url`: Valid URL format
- `relevance_score`: Float between 0 and 1
- `text`: Non-empty, max 500 characters (preview size)
- Sources must be ranked by relevance_score (descending)

**Display Logic** (from spec SC-006):
- Show all chunks (max 5-10 per response)
- Rank by relevance_score (highest first)
- Visual hierarchy: font size, color (darker = higher confidence)
- Clickable link navigates to source_url

**Examples**:

```json
{
  "source_url": "/docs/chapter-1/intro#physical-ai",
  "relevance_score": 0.95,
  "text": "Physical AI (or embodied AI) refers to artificial intelligence systems that interact with physical environments...",
  "metadata": {
    "title": "Introduction to Physical AI",
    "chapter": "Chapter 1: Fundamentals"
  }
}

{
  "source_url": "/docs/chapter-2/robotics#actuators",
  "relevance_score": 0.78,
  "text": "Actuators are devices that move or control mechanisms in response to commands from the control system...",
  "metadata": {
    "title": "Robotics Hardware",
    "chapter": "Chapter 2: Robotics Fundamentals"
  }
}
```

---

### 5. UIState

**Purpose**: Component state for the chat widget UI

**Fields**:

```typescript
interface UIState {
  status: 'idle' | 'loading' | 'error' | 'success'
  loading: boolean              // Loading request
  error: {
    code: string               // Error identifier
    message: string            // User-friendly message
    actionable: boolean        // Can user recover?
  } | null
  selectedText: string | null   // Currently selected text
  lastQuery: string | null      // Last submitted query
  lastResponse: ResponsePayload | null  // Last response
  metrics: {
    timeElapsed: number        // Seconds since request sent
    requestsSent: number       // Total requests in session
    errorsEncountered: number  // Total errors in session
  }
}
```

**Validation Rules**:
- `status`: One of four values
- `loading`: True when status === 'loading'
- `error`: null when status !== 'error'
- `metrics`: All counts non-negative integers

**State Machine**:

```
IDLE → (user submits query) → LOADING
  ↓
  +→ (response received) → SUCCESS → IDLE
  │
  +→ (error occurs) → ERROR
       ↓
       +→ (user retries) → LOADING
       │
       +→ (user cancels) → IDLE
```

**Timeline Tracking** (for loading indicator):
- 0-2s: Show spinner only
- 2-5s: Show spinner + "Still loading..."
- 5+s: Show spinner + "Still loading..." + Cancel button

---

### 6. ChatHistory

**Purpose**: Collection of all messages in current session

**Fields**:

```typescript
interface ChatHistory {
  messages: ChatMessage[]       // Ordered by timestamp
  sessionId: string            // Session identifier
  startTime: number            // Session start timestamp
  messageCount: number         // Total messages (including system)
  errorCount: number           // Total errors in session
  maxMessages: number          // Hard limit (per requirements)
}
```

**Validation Rules**:
- Messages must be ordered by timestamp (ascending)
- `sessionId`: UUID format
- `messageCount`: Must equal `messages.length`
- No duplicate IDs within session
- Max 100+ messages (spec scope allows for history of 100+)

**Management Rules**:
- Session lifetime: Single page load (no persistence)
- Auto-clear: When user navigates away or closes widget
- Bounded: If exceeds max size, remove oldest message (FIFO)

---

## Type Definitions for API

### Request/Response Enums

```typescript
enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

enum QuerySource {
  CHAT = 'chat',
  SELECTED_TEXT = 'selected-text'
}

enum UIStatus {
  IDLE = 'idle',
  LOADING = 'loading',
  ERROR = 'error',
  SUCCESS = 'success'
}

enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  SERVER_ERROR = 'SERVER_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNKNOWN = 'UNKNOWN'
}
```

---

## API Contract Summary

### Endpoint: POST `/api/v1/query`

**Request**:
- Type: `QueryRequest`
- Content-Type: `application/json`
- Timeout: 30 seconds

**Response** (Success - 200):
- Type: `ResponsePayload`
- Content-Type: `application/json`

**Response** (Error - 400/422/500/503):
- Type: JSON with `error: { code, message }`
- Content-Type: `application/json`

**Streaming Response** (if stream=true):
- Type: Server-Sent Events
- Content-Type: `text/event-stream`
- Format: Multiple events, each with JSON data

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User Interface (React Components)                           │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ user types query
              ↓
┌─────────────────────────────────────────────────────────────┐
│ QueryInput Component                                        │
│ - Validates: length, characters                             │
│ - Prepares: QueryRequest object                             │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ submitQuery(request: QueryRequest)
              ↓
┌─────────────────────────────────────────────────────────────┐
│ API Client (fetch wrapper)                                  │
│ - Adds headers, timeout                                     │
│ - Sends POST to /api/v1/query                               │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ HTTP POST
              ↓
    ┌─────────────────────────┐
    │ FastAPI Backend (Spec 3)│
    │ /api/v1/query           │
    └─────────────┬───────────┘
                  │
                  │ processes query with RAG
                  ↓
                  returns ResponsePayload
                  │
              ↓
┌─────────────────────────────────────────────────────────────┐
│ Response Handler                                            │
│ - Parses ResponsePayload                                    │
│ - Creates ChatMessage (role: 'assistant')                  │
│ - Extracts ContextChunk array                              │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ addMessage(chatMessage)
              ↓
┌─────────────────────────────────────────────────────────────┐
│ Chat State (React hooks)                                    │
│ - Updates ChatHistory                                       │
│ - Updates UIState (success)                                │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ state change triggers re-render
              ↓
┌─────────────────────────────────────────────────────────────┐
│ ChatHistory Component                                       │
│ - Renders ChatMessage items                                │
│ - Renders SourcePanel with ContextChunk links             │
│ - Updates scroll position                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Constraints & Assumptions

**Size Constraints**:
- Message text: Max 10,000 chars (query), max 50,000 chars (response)
- Context text: Max 5,000 chars per chunk
- Response payload: Max 1MB total
- Chat history: Max 100+ messages in DOM (subject to browser memory)

**Format Constraints**:
- Timestamps: Unix milliseconds
- Scores: Float 0-1
- UUIDs: Standard UUID v4 format
- Markdown: CommonMark compatible

**Serialization**:
- All types must be JSON serializable
- Dates represented as ISO 8601 or Unix ms
- Circular references not allowed
- All required fields must be present (no null for required)

---

## Examples: Complete Flow

### Example 1: Basic Query

**User Input**: "What is robotics?"

**Flow**:
```json
// 1. User submits query
{
  "role": "user",
  "content": "What is robotics?",
  "timestamp": 1702329600000
}

// 2. QueryRequest sent to backend
{
  "query": "What is robotics?",
  "stream": false,
  "metadata": { "source": "chat" }
}

// 3. Backend ResponsePayload
{
  "response_id": "resp-uuid",
  "answer": "Robotics is the branch of technology...",
  "context_chunks": [
    {
      "source_url": "/docs/chapter-2/robotics",
      "relevance_score": 0.94,
      "text": "..."
    }
  ],
  "metadata": { "tokens_used": 120, "response_time_ms": 1800 }
}

// 4. Frontend ChatMessage (assistant)
{
  "role": "assistant",
  "content": "Robotics is the branch of technology...",
  "timestamp": 1702329602000,
  "sources": [...],
  "metadata": { "tokens": 120, "responseTime": 1800 }
}
```

### Example 2: Selected Text Query

**User Action**: Selects text "sensors are electronic devices" → Clicks "Ask RAG"

**Flow**:
```json
// 1. QueryRequest with context
{
  "query": "Tell me more about this",
  "context": "sensors are electronic devices",
  "metadata": { "source": "selected-text" }
}

// 2. Backend generates response grounded in selection
// 3. Frontend displays with context indicator
```

### Example 3: Error Handling

**Scenario**: Backend times out after 30 seconds

**Flow**:
```json
// 1. ChatMessage (system, error)
{
  "role": "system",
  "content": "Request timed out. Please try again.",
  "timestamp": 1702329635000,
  "error": {
    "code": "TIMEOUT",
    "message": "Backend request exceeded 30 seconds",
    "retry": true
  }
}

// 2. UIState updated
{
  "status": "error",
  "error": {
    "code": "TIMEOUT",
    "message": "Request timed out. Please try again.",
    "actionable": true
  }
}

// 3. User can click "Retry" to resubmit same query
```

---

## Next Steps (After Phase 1)

1. Generate API contracts in `contracts/` directory (OpenAPI)
2. Create `quickstart.md` with setup instructions
3. Proceed to Phase 2: Task generation with detailed acceptance criteria
4. Implementation begins with type definitions and API client

---

**Status**: ✅ Data model complete and validated
**Date Completed**: 2025-12-11
