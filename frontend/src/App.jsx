import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [appReady, setAppReady] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    let timer
    async function pollStatus() {
      try {
        const res = await fetch(`${API_URL}/status`)
        if (res.ok) {
          const data = await res.json()
          if (data.ready) { setAppReady(true); return }
        }
      } catch (_) {}
      timer = setTimeout(pollStatus, 1500)
    }
    pollStatus()
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage(e) {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return

    setMessages(prev => [...prev, { role: 'user', text: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
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

      <div className="chat-window">
        {messages.length === 0 && (
          <p className="placeholder">Ask a question about the Warhammer rules...</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.role === 'assistant'
              ? <ReactMarkdown>{msg.text}</ReactMarkdown>
              : <p>{msg.text}</p>
            }
            {msg.sources && msg.sources.length > 0 && (
              <ul className="sources">
                {msg.sources.map((s, j) => (
                  <li key={j}>{s.source ?? s.file ?? 'Unknown source'}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {loading && <div className="message assistant loading"><span>...</span></div>}
        <div ref={bottomRef} />
      </div>

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
