/**
 * Chat Widget Component
 * Main chat interface for RAG chatbot
 */

import React, { useState, useRef, useEffect } from 'react'
import useChat from '../../hooks/useChat'
import './ChatWidget.css'

interface ChatWidgetProps {
  apiUrl?: string
  position?: 'bottom-right' | 'bottom-left'
  minimized?: boolean
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  apiUrl = 'http://localhost:8000',
  position = 'bottom-right',
  minimized: initialMinimized = true,
}) => {
  const [minimized, setMinimized] = useState(initialMinimized)
  const [inputValue, setInputValue] = useState('')
  const [timeElapsed, setTimeElapsed] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const chat = useChat({ apiUrl })

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chat.messages])

  // Timer for loading state
  useEffect(() => {
    if (!chat.loading) {
      setTimeElapsed(0)
      return
    }

    const interval = setInterval(() => {
      setTimeElapsed((t) => t + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [chat.loading])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputValue.trim()) return

    const query = chat.insertSelectedText(inputValue)
    await chat.submitQuery(query)
    setInputValue('')
  }

  const handleCaptureSelectedText = () => {
    const text = chat.captureSelectedText()
    if (text) {
      setInputValue(`${inputValue}\n\n[Selected: "${text}"]`)
    }
  }

  return (
    <div className={`chat-widget chat-widget-${position} ${minimized ? 'minimized' : 'expanded'}`}>
      {/* Header */}
      <div className="chat-header">
        <h3>📚 Textbook Assistant</h3>
        <button
          className="chat-toggle"
          onClick={() => setMinimized(!minimized)}
          aria-label={minimized ? 'Open chat' : 'Close chat'}
        >
          {minimized ? '✕' : '−'}
        </button>
      </div>

      {/* Chat Body */}
      {!minimized && (
        <div className="chat-body">
          {/* Messages */}
          <div className="chat-messages">
            {chat.messages.length === 0 ? (
              <div className="chat-placeholder">
                <p>👋 Hello! Ask me anything about the textbook.</p>
                <p className="text-small">Selected text from the page will be used as context.</p>
              </div>
            ) : (
              chat.messages.map((message) => (
                <div key={message.id} className={`chat-message chat-message-${message.role}`}>
                  <div className="message-header">
                    <span className="message-role">
                      {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
                    </span>
                    <span className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  {message.error ? (
                    <div className="message-error">
                      <p>❌ {message.error.message}</p>
                      <button onClick={chat.retry} className="retry-btn">
                        Retry
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="message-content">{message.content}</div>

                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="message-sources">
                          <details>
                            <summary>
                              📖 Sources ({message.sources.length})
                            </summary>
                            <div className="sources-list">
                              {message.sources.map((source, idx) => (
                                <div key={idx} className="source-item">
                                  <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="source-link"
                                  >
                                    {source.section || source.url}
                                  </a>
                                  <span className="source-score">
                                    Relevance: {(source.score * 100).toFixed(0)}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </details>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))
            )}

            {/* Loading Indicator */}
            {chat.loading && (
              <div className="chat-message chat-message-system">
                <div className="loading-indicator">
                  <span className="spinner"></span>
                  <span>Processing...</span>
                  {timeElapsed > 3 && <span className="wait-time">({timeElapsed}s)</span>}
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Error Alert */}
          {chat.error && (
            <div className="chat-error-alert">
              <p>⚠️ {chat.error}</p>
            </div>
          )}

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="chat-input-form">
            <div className="input-wrapper">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about the textbook content..."
                rows={3}
                disabled={chat.loading}
                className="chat-input"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleSubmit(e as any)
                  }
                }}
              />

              <div className="input-actions">
                <button
                  type="button"
                  onClick={handleCaptureSelectedText}
                  disabled={chat.loading}
                  className="action-btn capture-btn"
                  title="Use selected text as context"
                >
                  📌 Selected Text
                </button>

                <button
                  type="submit"
                  disabled={chat.loading || !inputValue.trim()}
                  className="action-btn submit-btn"
                >
                  {chat.loading ? '⏳ Loading...' : '✉️ Send'}
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

export default ChatWidget
