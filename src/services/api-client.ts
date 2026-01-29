/**
 * RAG Chatbot API Client
 * Handles HTTP communication with the FastAPI backend
 */

import { API_CONFIG } from '../config/env'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  sources?: ContextChunk[]
  error?: { code: string; message: string }
}

export interface ContextChunk {
  url: string
  section: string
  score: number
}

export interface ResponsePayload {
  question: string
  answer: string
  context?: string | null
  sources?: ContextChunk[] | null
  metadata: { [key: string]: any }
}

export interface QueryRequest {
  question: string
  top_k?: number
  include_context?: boolean
}

class RAGChatAPIClient {
  private baseUrl: string
  private timeout: number
  private debug: boolean

  constructor(baseUrl?: string, timeout?: number) {
    // ✅ DO NOT add extra /api/v1 here, backend already has it
    this.baseUrl = (baseUrl || API_CONFIG.baseUrl).replace(/\/$/, '')
    this.timeout = timeout || API_CONFIG.timeout
    this.debug = API_CONFIG.debug

    if (this.debug) {
      console.log('[RAGChat] API Client initialized', {
        baseUrl: this.baseUrl,
        timeout: this.timeout,
      })
    }
  }

  async submitQuery(request: QueryRequest): Promise<ResponsePayload> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      if (this.debug) console.log('[RAGChat] Submitting query:', request.question)

      const payload = {
        question: request.question,
        context: null,
        conversation_id: null,
        stream: false,
      }

      if (this.debug) console.log('FINAL PAYLOAD →', JSON.stringify(payload))
      if (this.debug) console.log('API BASE URL =', this.baseUrl)

      const response = await fetch(`${this.baseUrl}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(
          error?.error?.message || `API error: ${response.statusText} (${response.status})`
        )
      }

      const data: ResponsePayload = await response.json()
      return data
    } catch (error: any) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') throw new Error(`Request timeout after ${this.timeout}ms`)
      throw error
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const res = await fetch(`${this.baseUrl}/health`)
      return res.ok
    } catch {
      return false
    }
  }
}

let clientInstance: RAGChatAPIClient | null = null
export function getAPIClient(baseUrl?: string, timeout?: number) {
  if (!clientInstance) clientInstance = new RAGChatAPIClient(baseUrl || API_CONFIG.baseUrl, timeout || API_CONFIG.timeout)
  return clientInstance
}
