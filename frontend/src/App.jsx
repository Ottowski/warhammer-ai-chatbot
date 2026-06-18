import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''
// Main application component
function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [appReady, setAppReady] = useState(false)
  const bottomRef = useRef(null)

  // Poll the backend for readiness status every 1.5 seconds until it reports ready
  useEffect(() => {
    let timer
    async function pollStatus() {
      // Check backend status
      try {
        const res = await fetch(`${API_URL}/status`)
        if (res.ok) {
          const data = await res.json()
          if (data.ready) { setAppReady(true); return }
        }
      } catch (_) {}
      timer = setTimeout(pollStatus, 1500)
    }
    // Start polling immediately
    pollStatus()
    return () => clearTimeout(timer)
  }, [])

  // Scroll to the bottom of the chat window whenever messages or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Handle sending a message when the user submits the form
  async function sendMessage(e) {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return
    // Add the user's question to the chat history
    setMessages(prev => [...prev, { role: 'user', text: question }])
    setInput('')
    setLoading(true)

    // Send the question to the backend and handle the response
    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      // Check for HTTP errors
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer, sources: data.sources }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', text: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Warhammer Rules Assistant</h1>
      </header>
      {/* Chat window displaying the conversation history */}
      <div className="chat-window">
        {messages.length === 0 && (
          <p className="placeholder">Ask a question about the Warhammer rules...</p>
        )}
        {/* Render each message in the chat history */}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.role === 'assistant'
              ? <ReactMarkdown>{msg.text}</ReactMarkdown>
              : <p>{msg.text}</p>
            }
            {/* If the assistant message includes sources, display them in a list */}
            {msg.sources && msg.sources.length > 0 && (
              <ul className="sources">
                {msg.sources.map((s, j) => (
                  <li key={j}>{s.source ?? s.file ?? 'Unknown source'}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {/* Show a loading indicator when waiting for the assistant's response */}
        {loading && <div className="message assistant loading"><span>...</span></div>}
        <div ref={bottomRef} />
      </div>

      {/* Input form for the user to type their question */}
      <form className="input-row" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your question here..."
          disabled={loading || !appReady}
        />
        <button type="submit" disabled={loading || !input.trim() || !appReady}>Send</button>
      </form>

    </div>
  )
}

export default App
