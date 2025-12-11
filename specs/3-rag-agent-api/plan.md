# Implementation Plan: RAG Agent & API Layer

**Feature**: RAG Agent & API Layer (Spec 3)
**Feature Branch**: `3-rag-agent-api`
**Created**: 2025-12-11
**Target Audience**: Backend engineers, DevOps, integration engineers

---

## Executive Summary

This plan outlines the implementation of a production-ready RAG agent service that combines OpenAI Agents SDK with FastAPI to deliver context-grounded responses to user queries. The agent retrieves relevant context from the Qdrant vector database (validated by Spec 2) and uses retrieved information to generate accurate, grounded answers. The service provides a REST API endpoint (`/api/v1/query`) that will be consumed by the frontend chatbot (Spec 4).

**Key Goals**:
- ✅ Implement OpenAI Agents SDK integration with Qdrant retrieval
- ✅ Build FastAPI endpoints with request/response validation
- ✅ Guarantee response grounding in retrieved context
- ✅ Support configurable retrieval parameters
- ✅ Implement comprehensive logging and observability
- ✅ Achieve <5 second p95 latency with concurrent query support
- ✅ Provide debugging and tracing capabilities

---

## Scope & Dependencies

### In Scope
1. OpenAI Agents SDK integration
2. Context retrieval from Qdrant
3. Context injection into agent reasoning
4. FastAPI HTTP interface with REST endpoints
5. Request validation and error handling
6. Concurrent query processing
7. Transient failure retry logic
8. Comprehensive structured logging
9. Query execution tracing and debugging
10. Configurable retrieval strategies
11. Multiple response modes (REST, streaming)
12. Performance monitoring and metrics

### Out of Scope
- Authentication/authorization (can be added as middleware later)
- Rate limiting (client-specific throttling in frontend)
- Persistent conversation history
- Multi-turn dialog management
- Response summarization beyond grounding
- Custom embedding models (fixed to Cohere)
- Alternative LLM providers (OpenAI only for Agent SDK)

### External Dependencies
- **OpenAI API**: GPT-4 or GPT-3.5-turbo via Agents SDK
- **Qdrant Cloud**: Populated collection with validated vectors from Specs 1-2
- **Cohere API**: For query embedding (same as ingestion)
- **FastAPI**: Web framework for HTTP interface
- **Python 3.8+**: Runtime environment
- **OpenAI Agents SDK**: Latest version

### Internal Dependencies
- **Spec 1 (Ingestion)**: Produces vector data in Qdrant
- **Spec 2 (Retrieval Testing)**: Validates vector quality
- **Spec 4 (Frontend)**: Consumes `/api/v1/query` endpoint
- **.env configuration**: API keys for OpenAI, Qdrant, Cohere

---

## Architecture & Design

### System Components

```
┌──────────────────────────────────────────────────────────┐
│ FastAPI Server (Spec 3: RAG Agent & API Layer)           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ ┌────────────────────────────────────────────────────┐  │
│ │ HTTP Interface Layer                               │  │
│ ├────────────────────────────────────────────────────┤  │
│ │ • QueryEndpoint: POST /api/v1/query                │  │
│ │ • HealthCheckEndpoint: GET /health                 │  │
│ │ • MetricsEndpoint: GET /metrics                    │  │
│ │ • RequestValidator: Input validation               │  │
│ │ • ResponseFormatter: Output formatting             │  │
│ └────────────────────────────────────────────────────┘  │
│                          ↓                               │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Agent Orchestration Layer                          │  │
│ ├────────────────────────────────────────────────────┤  │
│ │ • AgentExecutor: OpenAI Agents SDK wrapper         │  │
│ │ • ContextInjector: Insert retrieved context        │  │
│ │ • PromptBuilder: Construct system prompt           │  │
│ │ • ResponseMapper: Parse agent responses            │  │
│ └────────────────────────────────────────────────────┘  │
│                          ↓                               │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Retrieval & Embedding Layer                        │  │
│ ├────────────────────────────────────────────────────┤  │
│ │ • QueryEmbedder: Cohere embeddings                 │  │
│ │ • ContextRetriever: Qdrant search                  │  │
│ │ • RetryableQuerier: Transient failure retry        │  │
│ │ • RetrievalCache: Optional result caching          │  │
│ └────────────────────────────────────────────────────┘  │
│                          ↓                               │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Observability Layer                                │  │
│ ├────────────────────────────────────────────────────┤  │
│ │ • StructuredLogger: JSON-formatted logging         │  │
│ │ • ExecutionTracer: Request lifecycle tracing       │  │
│ │ • MetricsCollector: Performance metrics            │  │
│ │ • ErrorReporter: Error tracking and analysis       │  │
│ └────────────────────────────────────────────────────┘  │
│                                                           │
└──────────────────────────────────────────────────────────┘
      ↓ Queries ↓                   ↑ Responses ↑
   ┌─────────┴─────────┬─────────────────────┬──────────┐
   ↓                   ↓                     ↓          ↓
OpenAI API         Cohere API          Qdrant Cloud   Frontend
(GPT-4/3.5)      (Embeddings)         (Vectors)       (Spec 4)
```

### Request Flow

```
Frontend Request (Spec 4)
        ↓
POST /api/v1/query
├─ query: "How do robots learn?"
├─ context: "selected text..." (optional)
└─ parameters: {top_k: 5, min_score: 0.5}
        ↓
[Request Validation]
        ↓
[Query Embedding] → Cohere API
        ↓
[Context Retrieval] → Qdrant Search
        ↓ (Top-5 relevant documents with scores)
[Context Injection] → System Prompt
        ↓
[Agent Execution] → OpenAI Agents SDK
        ├─ Tool Call: retrieve() [if needed]
        └─ Response Generation: Grounded in context
        ↓
[Response Formatting] → JSON payload
        ├─ answer: str
        ├─ context: List[ContextChunk]
        ├─ sources: List[SourceAttribution]
        ├─ confidence: float
        └─ execution_trace: dict
        ↓
HTTP Response (200 OK)
        ↓
Frontend (Spec 4) displays response
```

### Key Entities

```
QueryRequest
├─ query_id: str (UUID)
├─ query: str (user question)
├─ context: Optional[str] (selected text)
├─ top_k: int (default 5, range 1-100)
├─ min_score: float (default 0.5, range 0.0-1.0)
├─ response_mode: str (rest or streaming)
├─ timestamp: datetime
└─ user_agent: str (from request headers)

RetrievedContext
├─ document_id: str
├─ source_url: str
├─ section_name: str
├─ relevance_score: float
├─ text_chunk: str
├─ metadata: dict
└─ rank: int

AgentResponse
├─ query_id: str
├─ answer: str (grounded response)
├─ context_chunks: List[RetrievedContext]
├─ confidence_score: float (0.0-1.0)
├─ execution_trace: dict
├─ latency_ms: float
├─ tokens_used: int
├─ timestamp: datetime
└─ status: str (success/error)

APIResponse (HTTP)
├─ request_id: str
├─ status: str (success/error)
├─ data: AgentResponse
├─ error: Optional[ErrorDetail]
├─ metadata: dict
└─ timestamp: datetime
```

---

## Technical Design

### Configuration Management (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# Qdrant Configuration
QDRANT_URL=https://<your-qdrant-instance>.qdrant.io:6333
QDRANT_API_KEY=<your-qdrant-api-key>
QDRANT_COLLECTION_NAME=robotics_knowledge_base

# Cohere Configuration
COHERE_API_KEY=<your-cohere-api-key>
COHERE_MODEL=embed-english-v3.0

# Retrieval Settings
DEFAULT_TOP_K=5
DEFAULT_MIN_SCORE=0.5
RETRIEVAL_TIMEOUT_SECONDS=10
MAX_CONTEXT_LENGTH=2000  # characters

# Agent Settings
AGENT_FRAMEWORK=openai-agents
AGENT_TIMEOUT_SECONDS=30
RESPONSE_GROUNDING_REQUIRED=true
ENABLE_AGENT_REASONING_TRACE=true

# FastAPI Settings
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_WORKERS=4
CORS_ORIGINS=["http://localhost:3000", "https://example.com"]

# Retry Configuration
RETRY_MAX_ATTEMPTS=3
RETRY_INITIAL_DELAY_MS=100
RETRY_MAX_DELAY_MS=5000
RETRY_EXPONENTIAL_BASE=2

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=agent_service.log
ENABLE_REQUEST_LOGGING=true
ENABLE_TRACE_LOGGING=true
```

### API Endpoints

**POST /api/v1/query**
```
Request:
{
  "query": "How do humanoid robots perceive their environment?",
  "context": "selected text from documentation",  // optional
  "top_k": 5,              // optional, default 5
  "min_score": 0.5,        // optional, default 0.5
  "response_mode": "rest"  // optional, rest or streaming
}

Response (200 OK):
{
  "request_id": "req_20251211_abc123",
  "status": "success",
  "data": {
    "query_id": "query_20251211_abc123",
    "answer": "Humanoid robots use multiple sensors including cameras, LiDAR, and tactile sensors... based on the retrieved documentation",
    "confidence_score": 0.87,
    "context": [
      {
        "rank": 1,
        "relevance_score": 0.94,
        "source_url": "https://docs.example.com/perception",
        "section_name": "Robot Vision Systems",
        "text_chunk": "Robot vision systems use camera arrays...",
        "metadata": {"module": "Module 2", "version": "1.0"}
      },
      // ... more context chunks
    ],
    "execution_trace": {
      "embedding_time_ms": 125,
      "retrieval_time_ms": 230,
      "agent_time_ms": 845,
      "total_time_ms": 1200,
      "tokens_used": 450,
      "context_injected": true,
      "grounding_verified": true
    }
  },
  "metadata": {
    "timestamp": "2025-12-11T15:30:45.123Z",
    "api_version": "v1"
  }
}

Error Response (4xx/5xx):
{
  "request_id": "req_20251211_abc123",
  "status": "error",
  "error": {
    "code": "RETRIEVAL_FAILED",
    "message": "Failed to retrieve context from vector database",
    "details": {
      "reason": "connection_timeout",
      "retry_count": 3,
      "timestamp": "2025-12-11T15:30:45.123Z"
    }
  }
}
```

**GET /health**
```
Response (200 OK):
{
  "status": "healthy",
  "checks": {
    "openai_api": "healthy",
    "qdrant": "healthy",
    "cohere_api": "healthy"
  },
  "timestamp": "2025-12-11T15:30:45.123Z"
}
```

**GET /metrics** (Prometheus format)
```
# HELP agent_requests_total Total requests processed
# TYPE agent_requests_total counter
agent_requests_total{status="success"} 1250
agent_requests_total{status="error"} 45

# HELP agent_latency_ms Request latency in milliseconds
# TYPE agent_latency_ms histogram
agent_latency_ms_bucket{le="500"} 1100
agent_latency_ms_bucket{le="1000"} 1200
agent_latency_ms_bucket{le="5000"} 1250
agent_latency_ms_bucket{le="+Inf"} 1295
```

---

## Implementation Phases

### Phase 1: FastAPI Infrastructure & Endpoints (Weeks 1-2)
**Deliverables**:
- [ ] FastAPI application structure with middleware
- [ ] Request validation using Pydantic models
- [ ] Response formatting and serialization
- [ ] Health check endpoint
- [ ] CORS configuration
- [ ] Error handling and HTTP status codes
- [ ] Structured logging infrastructure
- [ ] Unit tests for endpoints
- [ ] Configuration via .env file

**Success Metrics**:
- FastAPI server starts without errors
- Endpoints respond correctly to valid/invalid requests
- All endpoints documented with OpenAPI/Swagger
- Request/response validation working
- Health check operational

### Phase 2: Context Retrieval & Injection (Weeks 2-3)
**Deliverables**:
- [ ] QueryEmbedder using Cohere API
- [ ] ContextRetriever with Qdrant integration
- [ ] RetryableQuerier with exponential backoff
- [ ] ContextInjector for system prompt construction
- [ ] Retrieval parameter configuration
- [ ] Caching layer for frequently accessed context
- [ ] Error handling for API failures
- [ ] Unit and integration tests

**Success Metrics**:
- Context retrieval works consistently
- Retry logic successfully handles transient failures
- Context injected correctly into prompts
- Latency acceptable for retrieval layer

### Phase 3: Agent Integration & Response Generation (Weeks 3-4)
**Deliverables**:
- [ ] OpenAI Agents SDK integration
- [ ] AgentExecutor with system prompt
- [ ] ResponseMapper for agent output parsing
- [ ] Confidence scoring logic
- [ ] Response grounding verification
- [ ] Token usage tracking
- [ ] Trace logging for agent execution
- [ ] Support for streaming responses
- [ ] Integration tests with sample queries

**Success Metrics**:
- Agent generates responses successfully
- Responses grounded in retrieved context
- Confidence scores meaningful (0.0-1.0 range)
- Token usage tracked accurately
- Streaming mode functional

### Phase 4: Observability & Optimization (Weeks 4-5)
**Deliverables**:
- [ ] Structured logging with all required fields
- [ ] Execution tracing for request lifecycle
- [ ] Metrics collection (latency, error rates, tokens)
- [ ] Performance profiling and optimization
- [ ] Load testing (50+ concurrent queries)
- [ ] Comprehensive test suite (unit + integration)
- [ ] Documentation (API, architecture, deployment)
- [ ] Production readiness checklist

**Success Metrics**:
- All SC-001 to SC-010 success criteria validated
- p95 latency <5 seconds
- 50 concurrent queries handled successfully
- 100% grounding verification
- Metrics exposed and queryable
- Test coverage >85%

---

## Success Criteria Implementation

| Criterion | Implementation Strategy |
|-----------|------------------------|
| **SC-001**: p95 latency <5 seconds | Profile each component; optimize Cohere API batching; async execution |
| **SC-002**: 50 concurrent queries, 100% success | FastAPI async handlers; connection pooling; concurrency tuning |
| **SC-003**: 100% context injection | ContextInjector verifies all queries inject context before agent execution |
| **SC-004**: 100% response grounding | ResponseVerifier checks answers reference retrieved context |
| **SC-005**: Proper input validation | Pydantic models validate all request fields; helpful error messages |
| **SC-006**: All 7 edge cases handled | Explicit handlers for each case (empty context, rate limit, etc.) |
| **SC-007**: All steps logged | StructuredLogger captures embedding, retrieval, agent, formatting steps |
| **SC-008**: Zero concurrent query cross-contamination | Request-scoped context; no shared state between queries |
| **SC-009**: Transient failure recovery | RetryableQuerier with exponential backoff (max 3 attempts) |
| **SC-010**: Response determinism (<20% variance) | Log seed values; test repeated queries with same parameters |

---

## Risk Analysis & Mitigation

### Top 3 Risks

**Risk 1: OpenAI API Rate Limiting or Cost Overruns**
- **Impact**: Service becomes unavailable or costs exceed budget
- **Mitigation**: Implement request throttling, response caching, rate limit awareness
- **Monitoring**: Track token usage and costs; alert on unusual patterns

**Risk 2: Qdrant Vector Database Connection Issues**
- **Impact**: Retrieval fails; agent cannot ground responses
- **Mitigation**: Health checks, connection pooling, retry logic with exponential backoff
- **Monitoring**: Track connection failures; maintain redundant connections if possible

**Risk 3: Agent Generates Non-Grounded Responses**
- **Impact**: Chatbot provides incorrect or hallucinated information
- **Mitigation**: Implement response grounding verification; timeout on long generation; prompt engineering
- **Monitoring**: Log grounding verification results; flag low-confidence responses

---

## Operational Readiness

### Deployment Checklist
- [ ] .env file configured with valid API keys
- [ ] FastAPI server tested locally
- [ ] Endpoints verified against Swagger/OpenAPI
- [ ] Health checks passing for all dependencies
- [ ] Logging and metrics collection operational
- [ ] Database backups in place
- [ ] Error handling and recovery tested

### Monitoring & Alerts
```
Key metrics:
- Request latency (p50, p95, p99)
- Error rate by type
- Concurrent active queries
- Token usage per hour
- API failure rates (OpenAI, Qdrant, Cohere)
- Context retrieval accuracy
- Response grounding success rate

Alert thresholds:
- p95 latency >5000ms (warning), >10000ms (critical)
- Error rate >5% (warning), >10% (critical)
- Concurrent queries >50 (warning), >100 (critical)
- Daily token cost >budget (critical)
```

### Runbooks

**Issue**: Requests timeout (>5 seconds p95)
1. Check which component is slow (embedding, retrieval, or agent)
2. Review OpenAI API latency on their dashboard
3. Check Qdrant Cloud status
4. Consider reducing max context length or top-k
5. Profile with sample queries to identify bottleneck
6. Consider upgrading OpenAI plan or Qdrant tier

**Issue**: Non-grounded responses detected
1. Review specific response that failed grounding check
2. Examine retrieved context vs. answer
3. Adjust agent temperature or prompt engineering
4. Consider stricter grounding verification
5. Log as incident for analysis

**Issue**: API rate limit errors from OpenAI
1. Check OpenAI dashboard for current usage
2. Implement or reduce request batching
3. Enable response caching for common queries
4. Throttle requests if near limit
5. Consider upgrading to higher tier

---

## Evaluation & Validation

### Definition of Done
- ✅ All FR-001 to FR-015 functional requirements implemented
- ✅ All SC-001 to SC-010 success criteria validated
- ✅ p95 latency <5 seconds demonstrated
- ✅ 50 concurrent queries handled successfully
- ✅ 100% response grounding verified
- ✅ All 7 edge cases handled without crashes
- ✅ Comprehensive logging and tracing functional
- ✅ Metrics exposed and queryable
- ✅ Test coverage >85%
- ✅ Documentation complete
- ✅ Ready for Frontend integration (Spec 4)

### Testing Strategy

**Unit Tests**
- Query embedding and formatting
- Context retrieval and mapping
- Retry logic and backoff calculation
- Response parsing and validation
- Error handling for each edge case
- Grounding verification logic

**Integration Tests**
- End-to-end query processing (embedding → retrieval → agent → response)
- Concurrent query execution with isolation verification
- API endpoint request/response validation
- Health check functionality
- Streaming response mode

**Performance Tests**
- Single query latency <5 seconds p95
- Concurrent query handling (50+ simultaneous)
- Memory usage under load
- Token usage accuracy
- Cache effectiveness (if implemented)

**Validation Tests**
- Response grounding (manual spot-checks)
- Context relevance verification
- Error message clarity
- API contract compliance

---

## Timeline & Milestones

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1-2  | Phase 1: FastAPI Infrastructure | Endpoints, validation, logging |
| 2-3  | Phase 2: Context Retrieval | Embeddings, retrieval, injection |
| 3-4  | Phase 3: Agent Integration | Response generation, grounding |
| 4-5  | Phase 4: Observability & Optimization | Metrics, tests, documentation |

**Ready for**: Spec 4 (Frontend Integration) implementation and connection

---

## Next Steps

1. ✅ Specification complete and validated (20/20 checklist passing)
2. 🔜 Implement Phase 1: FastAPI infrastructure (start with endpoint setup)
3. 🔜 Implement Phase 2: Context retrieval and embedding
4. 🔜 Implement Phase 3: Agent integration with OpenAI SDK
5. 🔜 Complete observability and testing
6. 🔜 Integrate with Spec 4 (Frontend) when both ready

---

## Key Decisions & Trade-offs

### Decision 1: OpenAI Agents SDK Required
- **Choice**: Use OpenAI Agents SDK as specified (not LangChain or other frameworks)
- **Rationale**: User-specified requirement; latest agent capabilities
- **Trade-off**: Vendor lock-in; must use OpenAI LLMs

### Decision 2: Context Grounding Requirement
- **Choice**: Mandatory grounding verification; all responses must reference retrieved context
- **Rationale**: Prevents hallucination; ensures accuracy and trustworthiness
- **Trade-off**: May limit creative or synthesized responses; verification adds latency

### Decision 3: Session-Level, No Persistence
- **Choice**: Stateless query processing; no multi-turn conversation history
- **Rationale**: Simpler implementation; each query independent
- **Trade-off**: Cannot maintain context across queries; suitable for single-turn Q&A

### Decision 4: Async/Concurrent Architecture
- **Choice**: FastAPI with async handlers for concurrent query support
- **Rationale**: Handles multiple simultaneous requests efficiently
- **Trade-off**: More complex than synchronous code; requires understanding of async patterns

### Decision 5: JSON Logging Format
- **Choice**: Structured logging with JSON output for all events
- **Rationale**: Machine-parseable; integrates with log aggregation systems
- **Trade-off**: Less human-readable in raw logs; requires JSON parser for analysis

---

## Dependencies & Integration Points

```
Spec 3: RAG Agent & API Layer
        ├─ (consumes from)
        │   ├─ Spec 1: Ingestion Pipeline (vectors in Qdrant)
        │   ├─ Spec 2: Retrieval Testing (validates vector quality)
        │   ├─ OpenAI API (agent response generation)
        │   └─ Cohere API (query embeddings)
        │
        └─ (provides to)
            └─ Spec 4: Frontend Integration (HTTP API endpoint /api/v1/query)
```

---

**Status**: Ready for Phase 1 implementation
**Confidence Level**: High
