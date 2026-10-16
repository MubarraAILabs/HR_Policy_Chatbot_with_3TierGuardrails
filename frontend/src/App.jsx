import { useState } from "react";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const suggestions = [
  "How many sick leave days are allowed?",
  "What is the annual leave policy?",
  "How do I apply for leave?",
  "What is the attendance policy?"
];

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([{
    role: "assistant",
    answer: "Hello! I'm your HR Policy Assistant. Ask me about leave, attendance, holidays, benefits, or other topics covered by your company's HR policies.",
    sources: []
  }]);
  const [loading, setLoading] = useState(false);

  async function sendQuestion(value = question) {
    const cleaned = value.trim();
    if (!cleaned || loading) return;
    setMessages(prev => [...prev, { role: "user", answer: cleaned, sources: [] }]);
    setQuestion("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleaned })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      setMessages(prev => [...prev, { role: "assistant", answer: data.answer, sources: data.sources || [] }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: "assistant",
        answer: `Unable to get a response: ${error.message}. Check that the FastAPI backend is running.`,
        sources: []
      }]);
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(event) {
    event.preventDefault();
    sendQuestion();
  }

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand-mark">H</div>
      <div className="brand-copy"><strong>PeopleDesk</strong><span>HR POLICY ASSISTANT</span></div>
      <div className="sidebar-rule" />
      <div className="side-label">YOUR WORKSPACE</div>
      <div className="side-item active"><span>◉</span> Policy assistant</div>
      <div className="side-item"><span>◇</span> Company handbook</div>
      <div className="sidebar-bottom"><div className="status-dot" /><div><strong>AI assistant online</strong><small>Answers based on indexed policy docs</small></div></div>
    </aside>
    <section className="main-panel">
      <header className="topbar">
        <div><div className="eyebrow">PEOPLE OPERATIONS</div><h1>HR Policy Assistant</h1></div>
        <div className="secure-pill"><span>✓</span> Guardrails enabled</div>
      </header>
      <section className="chat-area">
        <div className="chat-intro">
          <div className="intro-icon">✳</div>
          <div className="eyebrow">YOUR HR COMPANION</div>
          <h2>How can I help you today?</h2>
          <p>Ask about company policies. Answers are grounded in the HR documents configured by your administrator.</p>
        </div>
        <div className="messages" aria-live="polite">
          {messages.map((message, index) => <article className={`message ${message.role}`} key={index}>
            <div className="avatar">{message.role === "assistant" ? "H" : "Y"}</div>
            <div className="message-content">
              <div className="message-label">{message.role === "assistant" ? "HR ASSISTANT" : "YOU"}</div>
              <div className="bubble">{message.answer}</div>
              {message.sources?.length > 0 && <div className="sources">
                <span className="source-heading">POLICY SOURCES</span>
                {message.sources.map(source => <span className="source-chip" key={source}>▤ {source}</span>)}
              </div>}
            </div>
          </article>)}
          {loading && <div className="loading-row"><span className="spinner" /> Checking policy documents and preparing an answer…</div>}
        </div>
        {messages.length <= 1 && <div className="suggestions">
          <div className="eyebrow">GET STARTED</div>
          <div className="suggestion-grid">{suggestions.map(item =>
            <button key={item} className="suggestion" onClick={() => sendQuestion(item)} disabled={loading}>
              <span>{item}</span><span className="suggestion-arrow">↗</span>
            </button>
          )}</div>
        </div>}
        <form className="composer" onSubmit={onSubmit}>
          <textarea value={question} onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSubmit(e); } }}
            placeholder="Ask about leave, benefits, attendance…" rows={2} maxLength={2000} aria-label="Your HR policy question" />
          <div className="composer-footer"><span>Answers may need HR confirmation. Don't enter sensitive personal data.</span>
            <button className="send-button" type="submit" disabled={loading || !question.trim()}>{loading ? "Sending…" : "Ask HR"} <span>↑</span></button>
          </div>
        </form>
        <footer>Powered by Gemini · Responses are checked against available policy sources</footer>
      </section>
    </section>
  </main>;
}
