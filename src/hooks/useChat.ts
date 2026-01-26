import { useState, useCallback, useRef } from 'react'
import {
  getAPIClient,
  ChatMessage,
  ResponsePayload,
  QueryRequest,
} from '../services/api-client'

export interface UseChatOptions {
  apiUrl?: string
  timeout?: number
  maxMessages?: number
}

export interface UseChatState {
  messages: ChatMessage[]
  loading: boolean
  error: string | null
  selectedText: string | null
}

export function useChat(options: UseChatOptions = {}) {
  const maxMessages = options.maxMessages || 100
  const apiClient = useRef(getAPIClient(options.apiUrl, options.timeout))

  const [state, setState] = useState<UseChatState>({
    messages: [],
    loading: false,
    error: null,
    selectedText: null,
  })

  // -----------------------------
  // ✅ Function: Add new message
  // -----------------------------
  const addMessage = useCallback(
    (message: ChatMessage) => {
      setState((prev) => {
        const messages = [...prev.messages, message]
        if (messages.length > maxMessages) messages.shift()
        return { ...prev, messages }
      })
    },
    [maxMessages]
  )

  // -----------------------------
  // ✅ Function: Update last message (keep for retry/error updates)
  // -----------------------------
  const updateLastMessage = useCallback((updates: Partial<ChatMessage>) => {
    setState((prev) => {
      if (prev.messages.length === 0) return prev
      const messages = [...prev.messages]
      messages[messages.length - 1] = {
        ...messages[messages.length - 1],
        ...updates,
      }
      return { ...prev, messages }
    })
  }, [])

  const clearMessages = useCallback(
    () => setState((prev) => ({ ...prev, messages: [] })),
    []
  )

  // -----------------------------
  // ✅ Function: Submit Query
  // -----------------------------
  const submitQuery = useCallback(
    async (query: string, context?: string) => {
      if (!query.trim()) {
        setState((prev) => ({ ...prev, error: 'Query cannot be empty' }))
        return
      }

      // -----------------------------
      // ✅ Add user message
      // -----------------------------
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: query,
        timestamp: Date.now(),
      }
      addMessage(userMessage)

      // -----------------------------
      // ✅ Add empty assistant message (will update later)
      // -----------------------------
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        sources: [],
      }
      addMessage(assistantMessage)

      setState((prev) => ({ ...prev, loading: true, error: null }))

      try {
        // -----------------------------
        // ✅ CHANGE HERE: Only one API call
        // -----------------------------
        const request: QueryRequest = {
          question: query,
          top_k: 5,
          include_context: true,
        }

        const response: ResponsePayload =
          await apiClient.current.submitQuery(request)

        // -----------------------------
        // ✅ CHANGE HERE: Do NOT use response.data, use response directly
        // -----------------------------
        updateLastMessage({
          content: response.answer || 'No relevant book content found.', // fallback text
          sources: Array.isArray(response.sources) ? response.sources : [],
          timestamp: Date.now(),
        })

        setState((prev) => ({ ...prev, loading: false, error: null }))
      } catch (error: any) {
        const errorMessage =
          error.message || 'An error occurred while processing your query'
        updateLastMessage({
          content: '',
          error: { code: 'ERROR', message: errorMessage },
        })
        setState((prev) => ({ ...prev, loading: false, error: errorMessage }))
      }
    },
    [addMessage, updateLastMessage]
  )

  // -----------------------------
  // ✅ Helper: Insert selected text
  // -----------------------------
  const insertSelectedText = (text: string) => text

  // -----------------------------
  // ✅ Helper: Capture selected text from page
  // -----------------------------
  const captureSelectedText = () => {
    return window.getSelection()?.toString() || ''
  }

  return {
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    selectedText: state.selectedText,
    submitQuery,
    clearMessages,
    addMessage,
    updateLastMessage,
    insertSelectedText,
    captureSelectedText,
  }
}

export default useChat
