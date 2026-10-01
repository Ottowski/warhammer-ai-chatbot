import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'
import remarkGfm from 'remark-gfm'

const API_URL = import.meta.env.VITE_API_URL ?? ''

// Internal markdown URL prefix used to tag in-app rule links.
const SPECIAL_RULE_LINK_PREFIX = '#special-rule='

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// Generate a regex pattern for matching a special rule, accounting for optional parenthetical content.
function specialRulePattern(rule) {
  return escapeRegExp(rule)
    .replace(/X\\\+/g, '[^)]*')
    .replace(/X/g, '[^)]*')
}

// Convert known special rule names in the text into clickable markdown links.
function linkifySpecialRules(text, specialRules) {
  if (!text || specialRules.length === 0) return text

  const orderedRules = [...specialRules].sort((left, right) => right.length - left.length)
  const pattern = orderedRules
    .map(rule => specialRulePattern(rule))
    .join('|')

  if (!pattern) return text

  const matcher = new RegExp(`(^|[^\\w\\[])(${pattern})(?=$|[^\\w\\]])`, 'g')

  // Convert known rule names into markdown links that our custom renderer can intercept.
  return text.replace(matcher, (_match, prefix, ruleName) => {
    return `${prefix}[${ruleName}](${SPECIAL_RULE_LINK_PREFIX}${encodeURIComponent(ruleName)})`
  })
}

// Recursively extract plain text from a React node, used for custom markdown rendering.
function getNodeText(node) {
  // Base case: if the node is a string or number, return it as a string.
  if (typeof node === 'string' || typeof node === 'number') {
    return String(node)
  }

  if (!node || !Array.isArray(node.props?.children)) {
    return typeof node?.props?.children === 'string' ? node.props.children : ''
  }

  return node.props.children.map(getNodeText).join('')
}

// Main application component
function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [appReady, setAppReady] = useState(false)
  const [specialRules, setSpecialRules] = useState([])
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

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

  useEffect(() => {
    async function loadSpecialRules() {
      try {
        // Fetch rule names once so message text can be auto-linkified consistently.
        const res = await fetch(`${API_URL}/special-rules`)
        if (!res.ok) return
        const data = await res.json()
        if (Array.isArray(data.special_rules)) {
          setSpecialRules(data.special_rules)
        }
      } catch (_) {}
    }

    loadSpecialRules()
  }, [])

  // Scroll to the bottom of the chat window whenever messages or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Handle sending a message when the user submits the form
  async function submitQuestion(question) {
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

  // Handle the form submission for sending a message
  async function sendMessage(e) {
    e.preventDefault()
    await submitQuestion(input.trim())
  }
  // Put a clicked special rule into the search field for editing or submission.
  function handleSpecialRuleClick(e, ruleName) {
    // Prevent the default link behavior and populate the input field with the clicked rule name.
    e.preventDefault()
    setInput(ruleName)
    inputRef.current?.focus()
  }

  const markdownComponents = {
    a({ href, children }) {
      const linkText = getNodeText({ props: { children } }).trim()
      const matchingRule = specialRules.find(rule => rule.toLowerCase() === linkText.toLowerCase())

      // Primary path: if visible link text matches a known special rule, force in-app query behavior.
      if (matchingRule) {
        return (
          <button
            type="button"
            className="rule-link"
            onClick={e => handleSpecialRuleClick(e, matchingRule)}
          >
            {children}
          </button>
        )
      }

      // Fallback path: support prefixed links emitted by linkifySpecialRules.
      if (href?.startsWith(SPECIAL_RULE_LINK_PREFIX)) {
        const ruleName = decodeURIComponent(href.slice(SPECIAL_RULE_LINK_PREFIX.length))
        return (
          <button
            type="button"
            className="rule-link"
            onClick={e => handleSpecialRuleClick(e, ruleName)}
          >
            {children}
          </button>
        )
      }

      return (
        <a href={href} target="_blank" rel="noreferrer">
          {children}
        </a>
      )
    },
  }

  return (
    <div className="app">
      <header className="header">
        <h1>TOW Arbiter</h1>
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
              ? <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>{linkifySpecialRules(msg.text, specialRules)}</ReactMarkdown>
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

      {!appReady && (
        <div className="init-banner">Initializing rule engine, please wait...</div>
      )}

      {/* Input form for the user to type their question */}
      <form className="input-row" onSubmit={sendMessage}>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={appReady ? 'Type your question here...' : 'Loading rules, input will unlock shortly...'}
          disabled={loading || !appReady}
        />
        <button type="submit" disabled={loading || !input.trim() || !appReady}>Send</button>
      </form>

    </div>
  )
}

export default App
