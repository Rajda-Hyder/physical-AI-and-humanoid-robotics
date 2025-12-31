/**
 * useChat Hook
 * Manages chat state and API communication
 */

import { useState, useCallback, useRef } from 'react'
import { getAPIClient, ChatMessage, ContextChunk, ResponsePayload, QueryRequest } from '../services/api-client'

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

  /**
   * Add a message to chat history
   */
  const addMessage = useCallback((message: ChatMessage) => {
    setState((prev) => {
      const messages = [...prev.messages, message]

      // Limit message history size
      if (messages.length > maxMessages) {
        messages.shift()
      }

      return { ...prev, messages }
    })
  }, [maxMessages])

  /**
   * Update the last assistant message
   */
  const updateLastMessage = useCallback((updates: Partial<ChatMessage>) => {
    setState((prev) => {
      if (prev.messages.length === 0) return prev

      const messages = [...prev.messages]
      const lastIdx = messages.length - 1
      messages[lastIdx] = { ...messages[lastIdx], ...updates }

      return { ...prev, messages }
    })
  }, [])

  /**
   * Clear all messages
   */
  const clearMessages = useCallback(() => {
    setState((prev) => ({ ...prev, messages: [] }))
  }, [])

  /**
   * Submit a query to the RAG chatbot
   */
  const submitQuery = useCallback(
    async (query: string, context?: string) => {
      if (!query.trim()) {
        setState((prev) => ({
          ...prev,
          error: 'Query cannot be empty',
        }))
        return
      }

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: query,
        timestamp: Date.now(),
      }
      addMessage(userMessage)

      // Create loading assistant message
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        sources: [],
      }
      addMessage(assistantMessage)

      setState((prev) => ({
        ...prev,
        loading: true,
        error: null,
      }))

      try {
        const request: QueryRequest = {
          question: query,
          top_k: 5,
          include_context: true,
        }

        const response: ResponsePayload = await apiClient.current.submitQuery(request)

        // Strict RAG validation: Only show answer if context was found
        if (!response.sources || response.sources.length === 0) {
          // No book content found - show error
          updateLastMessage({
            content: '',
            error: {
              code: 'NO_CONTEXT',
              message: 'Sorry, I cannot find the answer in the book.',
            },
          })

          setState((prev) => ({
            ...prev,
            loading: false,
            error: 'No relevant book content found',
          }))
          return
        }

        // Update assistant message with response
        updateLastMessage({
          content: response.context,
          sources: response.sources,
          timestamp: response.metadata.timestamp,
        })

        setState((prev) => ({
          ...prev,
          loading: false,
          error: null,
        }))
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'An error occurred while processing your query'

        // Update assistant message with error
        updateLastMessage({
          content: '',
          error: {
            code: 'ERROR',
            message: errorMessage,
          },
        })

        setState((prev) => ({
          ...prev,
          loading: false,
          error: errorMessage,
        }))
      }
    },
    [addMessage, updateLastMessage]
  )

  /**
   * Retry the last failed query
   */
  const retry = useCallback(() => {
    const messages = state.messages
    if (messages.length < 2) return

    // Find the last user message
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        const userMsg = messages[i]

        // Remove the failed assistant response
        setState((prev) => ({
          ...prev,
          messages: prev.messages.slice(0, -1),
        }))

        // Retry the query
        submitQuery(userMsg.content)
        return
      }
    }
  }, [state.messages, submitQuery])

  /**
   * Capture selected text from the page
   */
  const captureSelectedText = useCallback(() => {
    try {
      const selectedText = window.getSelection()?.toString() || ''
      setState((prev) => ({
        ...prev,
        selectedText: selectedText || null,
      }))
      return selectedText
    } catch {
      return null
    }
  }, [])

  /**
   * Insert selected text into query
   */
  const insertSelectedText = useCallback((query: string): string => {
    if (state.selectedText) {
      return `${query}\n\nContext: ${state.selectedText}`
    }
    return query
  }, [state.selectedText])

  return {
    // State
    messages: state.messages,
    loading: state.loading,
    error: state.error,
    selectedText: state.selectedText,

    // Actions
    submitQuery,
    retry,
    clearMessages,
    addMessage,
    updateLastMessage,
    captureSelectedText,
    insertSelectedText,
  }
}

export default useChat
