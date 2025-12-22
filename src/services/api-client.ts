/**
 * RAG Chatbot API Client
 * Handles HTTP communication with the FastAPI backend
 */

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  sources?: ContextChunk[]
  error?: {
    code: string
    message: string
  }
}

export interface ContextChunk {
  source_url: string
  relevance_score: number
  text: string
  metadata?: {
    title?: string
    chapter?: string
    [key: string]: any
  }
}

export interface ResponsePayload {
  response_id: string
  answer: string
  context_chunks: ContextChunk[]
  metadata: {
    model: string
    tokens_used: number
    response_time_ms: number
    timestamp: number
    version: string
  }
}

export interface QueryRequest {
  query: string
  context?: string | null
  conversation_id?: string | null
  stream?: boolean
}

class RAGChatAPIClient {
  private baseUrl: string
  private timeout: number
  private debug: boolean

  constructor(baseUrl?: string, timeout?: number) {
    this.baseUrl = baseUrl || (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000'
    this.timeout = timeout || parseInt((import.meta.env.VITE_API_TIMEOUT as string) || '30000')
    this.debug = (import.meta.env.VITE_DEBUG as string) === 'true'

    if (this.debug) {
      console.log('[RAGChat] API Client initialized', {
        baseUrl: this.baseUrl,
        timeout: this.timeout,
      })
    }
  }

  /**
   * Submit a query to the RAG chatbot
   */
  async submitQuery(request: QueryRequest): Promise<ResponsePayload> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      if (this.debug) {
        console.log('[RAGChat] Submitting query:', request.query)
      }

      const response = await fetch(`${this.baseUrl}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(
          error?.error?.message || `API error: ${response.statusText} (${response.status})`
        )
      }

      const data: ResponsePayload = await response.json()

      if (this.debug) {
        console.log('[RAGChat] Response received:', {
          id: data.response_id,
          answerLength: data.answer.length,
          sourcesCount: data.context_chunks.length,
          responseTimeMs: data.metadata.response_time_ms,
        })
      }

      return data
    } catch (error) {
      clearTimeout(timeoutId)

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error(`Request timeout after ${this.timeout}ms`)
        }
        throw error
      }

      throw new Error('Unknown error occurred')
    }
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`)
      return response.ok
    } catch {
      return false
    }
  }

  /**
   * Get API information
   */
  async getApiInfo(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/info`)
      if (!response.ok) {
        throw new Error('Failed to get API info')
      }
      return await response.json()
    } catch (error) {
      if (this.debug) {
        console.error('[RAGChat] Failed to get API info:', error)
      }
      throw error
    }
  }
}

// Singleton instance
let clientInstance: RAGChatAPIClient | null = null

export function getAPIClient(baseUrl?: string, timeout?: number): RAGChatAPIClient {
  if (!clientInstance) {
    clientInstance = new RAGChatAPIClient(baseUrl, timeout)
  }
  return clientInstance
}

export default RAGChatAPIClient
