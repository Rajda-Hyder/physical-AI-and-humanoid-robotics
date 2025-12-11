/**
 * TypeScript Type Definitions for Frontend-Backend RAG Chatbot Integration
 *
 * These types are used for compile-time type checking and provide the contract
 * between frontend and backend components.
 *
 * Generated from: data-model.md and openapi.yaml
 */

// ============================================================================
// MESSAGE AND CHAT TYPES
// ============================================================================

/**
 * Role of the message author
 */
export type MessageRole = 'user' | 'assistant' | 'system'

/**
 * A single message in the chat history
 */
export interface ChatMessage {
  /** Unique identifier within session */
  id: string

  /** Role of the message author */
  role: MessageRole

  /** Message content (may be markdown) */
  content: string

  /** Unix timestamp in milliseconds */
  timestamp: number

  /** Optional metadata about the message */
  metadata?: {
    /** Token count (from backend) */
    tokens?: number
    /** Time to generate response (milliseconds) */
    responseTime?: number
    /** Relevance confidence (0-1) for assistant messages */
    confidence?: number
  }

  /** Retrieved sources (assistant messages only) */
  sources?: ContextChunk[]

  /** Error information (system messages with errors) */
  error?: {
    /** Error code for identification */
    code: string
    /** User-friendly error message */
    message: string
    /** Whether retry is possible */
    retry?: boolean
  }
}

/**
 * Collection of all messages in current session
 */
export interface ChatHistory {
  /** All messages ordered by timestamp */
  messages: ChatMessage[]

  /** Session identifier */
  sessionId: string

  /** Session start timestamp */
  startTime: number

  /** Total message count */
  messageCount: number

  /** Total errors encountered */
  errorCount: number

  /** Maximum allowed messages */
  maxMessages: number
}

/**
 * UI state of the chat widget
 */
export type UIStatus = 'idle' | 'loading' | 'error' | 'success'

/**
 * Complete UI state
 */
export interface UIState {
  /** Current widget status */
  status: UIStatus

  /** Whether a request is being processed */
  loading: boolean

  /** Error state (null if no error) */
  error: {
    /** Error identifier */
    code: string
    /** User-friendly message */
    message: string
    /** Can user recover? */
    actionable: boolean
  } | null

  /** Currently selected text from page */
  selectedText: string | null

  /** Last submitted query */
  lastQuery: string | null

  /** Last response from backend */
  lastResponse: ResponsePayload | null

  /** Performance metrics */
  metrics: {
    /** Seconds since request sent */
    timeElapsed: number
    /** Total requests in session */
    requestsSent: number
    /** Total errors in session */
    errorsEncountered: number
  }
}

// ============================================================================
// API REQUEST TYPES
// ============================================================================

/**
 * Source of the query
 */
export type QuerySource = 'chat' | 'selected-text'

/**
 * Environment context
 */
export type Environment = 'development' | 'production'

/**
 * Metadata about the request
 */
export interface RequestMetadata {
  /** Origin of the query */
  source?: QuerySource

  /** Widget version number */
  clientVersion?: string

  /** Deployment environment */
  environment?: Environment
}

/**
 * HTTP request payload sent to backend
 */
export interface QueryRequest {
  /** User's question (required) */
  query: string

  /** Optional selected text or history context */
  context?: string | null

  /** Optional conversation identifier */
  conversation_id?: string | null

  /** Whether to stream response (SSE) or return full response */
  stream?: boolean

  /** Additional request metadata */
  metadata?: RequestMetadata
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

/**
 * A single retrieved source document
 */
export interface ContextChunk {
  /** URL to documentation section */
  source_url: string

  /** Relevance score (0-1, higher = more relevant) */
  relevance_score: number

  /** Text preview/excerpt */
  text: string

  /** Optional chunk metadata */
  metadata?: {
    /** Document title */
    title?: string
    /** Chapter or section name */
    chapter?: string
    /** When indexed (Unix timestamp) */
    timestamp?: number
  }
}

/**
 * Metadata in response
 */
export interface ResponseMetadata {
  /** AI model used */
  model: string

  /** Total tokens used */
  tokens_used: number

  /** Generation time (milliseconds) */
  response_time_ms: number

  /** Server timestamp */
  timestamp: number

  /** API version */
  version: string
}

/**
 * Complete response from backend
 */
export interface ResponsePayload {
  /** Unique response identifier */
  response_id: string

  /** Generated response (markdown) */
  answer: string

  /** Retrieved sources (ranked by relevance) */
  context_chunks: ContextChunk[]

  /** Response metadata */
  metadata: ResponseMetadata
}

// ============================================================================
// ERROR TYPES
// ============================================================================

/**
 * Error codes
 */
export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  SERVER_ERROR = 'SERVER_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  UNKNOWN = 'UNKNOWN'
}

/**
 * Error response from backend or client
 */
export interface ErrorResponse {
  /** Error details */
  error: {
    /** Error code */
    code: ErrorCode | string
    /** Error message */
    message: string
    /** Additional details */
    details?: Record<string, unknown> | null
  }
}

/**
 * Client-side error with additional context
 */
export interface ClientError extends Error {
  code: ErrorCode | string
  statusCode?: number
  retryable?: boolean
}

// ============================================================================
// STREAMING RESPONSE TYPES
// ============================================================================

/**
 * Event type in streaming response
 */
export enum StreamEventType {
  START = 'start',
  TEXT = 'text',
  CONTEXT = 'context',
  METADATA = 'metadata',
  DONE = 'done',
  ERROR = 'error'
}

/**
 * Single event in Server-Sent Events stream
 */
export interface StreamEvent {
  type: StreamEventType
  data: unknown
}

/**
 * Parsed streaming response chunk
 */
export interface StreamChunk {
  type: 'start' | 'text' | 'context' | 'done' | 'error'
  content?: string
  chunks?: ContextChunk[]
  metadata?: ResponseMetadata
  error?: {
    code: string
    message: string
  }
}

// ============================================================================
// API CLIENT TYPES
// ============================================================================

/**
 * Options for API client configuration
 */
export interface APIClientConfig {
  baseUrl: string
  timeout?: number
  retries?: number
  debug?: boolean
}

/**
 * Response from a query (union of full response or streaming)
 */
export type QueryResponse = ResponsePayload | AsyncIterable<StreamChunk>

/**
 * Hook for chat queries
 */
export interface UseChatQueryOptions {
  baseUrl: string
  timeout?: number
  onStart?: () => void
  onProgress?: (chunk: StreamChunk) => void
  onSuccess?: (response: ResponsePayload) => void
  onError?: (error: ClientError) => void
}

// ============================================================================
// VALIDATION CONSTRAINTS
// ============================================================================

/**
 * Size and format constraints
 */
export const CONSTRAINTS = {
  // Query constraints
  query: {
    minLength: 1,
    maxLength: 10000,
  },

  // Context constraints
  context: {
    maxLength: 5000,
  },

  // Response constraints
  response: {
    maxLength: 50000,
    maxPayloadSize: 1024 * 1024, // 1MB
  },

  // Context chunk constraints
  chunk: {
    maxTextLength: 500,
    scoreMin: 0,
    scoreMax: 1,
  },

  // Chat history constraints
  history: {
    maxMessages: 500,
    maxChunksPerResponse: 10,
  },

  // Timeout constraints
  timeout: {
    default: 30000, // 30 seconds
    max: 120000, // 2 minutes
  },
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Generic API response wrapper
 */
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: ErrorResponse['error']
}

/**
 * Pagination support (for future use)
 */
export interface PaginationParams {
  page: number
  pageSize: number
}

/**
 * Generic list response (for future use)
 */
export interface ListResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Check if object is a valid ChatMessage
 */
export function isChatMessage(obj: unknown): obj is ChatMessage {
  if (typeof obj !== 'object' || obj === null) return false
  const msg = obj as Record<string, unknown>
  return (
    typeof msg.id === 'string' &&
    typeof msg.role === 'string' &&
    ['user', 'assistant', 'system'].includes(msg.role as string) &&
    typeof msg.content === 'string' &&
    typeof msg.timestamp === 'number'
  )
}

/**
 * Check if object is a valid ResponsePayload
 */
export function isResponsePayload(obj: unknown): obj is ResponsePayload {
  if (typeof obj !== 'object' || obj === null) return false
  const resp = obj as Record<string, unknown>
  return (
    typeof resp.response_id === 'string' &&
    typeof resp.answer === 'string' &&
    Array.isArray(resp.context_chunks) &&
    typeof resp.metadata === 'object'
  )
}

/**
 * Check if object is a valid ErrorResponse
 */
export function isErrorResponse(obj: unknown): obj is ErrorResponse {
  if (typeof obj !== 'object' || obj === null) return false
  const err = obj as Record<string, unknown>
  return (
    typeof err.error === 'object' &&
    err.error !== null &&
    typeof (err.error as Record<string, unknown>).code === 'string'
  )
}

// ============================================================================
// EXPORT ALL TYPES
// ============================================================================

export type {
  MessageRole,
  ChatMessage,
  ChatHistory,
  UIStatus,
  UIState,
  QuerySource,
  Environment,
  RequestMetadata,
  QueryRequest,
  ContextChunk,
  ResponseMetadata,
  ResponsePayload,
  ErrorResponse,
  ClientError,
  StreamEvent,
  StreamChunk,
  APIClientConfig,
  QueryResponse,
  UseChatQueryOptions,
  APIResponse,
  PaginationParams,
  ListResponse,
}
