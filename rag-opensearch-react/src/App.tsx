import { useState, useRef, useEffect } from "react";
import type { ChangeEvent, FormEvent } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:3000";
interface Message {
  role: "user" | "assistant";
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Olá! Como posso ajudar?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [pdfUploading, setPdfUploading] = useState(false);
  const [showTyping, setShowTyping] = useState(false);
  const [typingDots, setTypingDots] = useState("");
  const typingInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const typingTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (loading) {
      typingTimeout.current = setTimeout(() => {
        setShowTyping(true);
        let dots = 0;
        typingInterval.current = setInterval(() => {
          dots = (dots + 1) % 4;
          setTypingDots(".".repeat(dots));
        }, 400);
      }, 1000);
    } else {
      setShowTyping(false);
      setTypingDots("");
      if (typingTimeout.current) clearTimeout(typingTimeout.current);
      if (typingInterval.current) clearInterval(typingInterval.current);
    }
    return () => {
      if (typingTimeout.current) clearTimeout(typingTimeout.current);
      if (typingInterval.current) clearInterval(typingInterval.current);
    };
  }, [loading]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/ask-model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: data.answer || "Erro ao obter resposta." },
      ]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: "Erro ao conectar com a API." },
      ]);
    }
    setLoading(false);
  };

  const handlePdfUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPdfUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_URL}/index-pdf`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: data.message || "PDF enviado." },
      ]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: "Erro ao enviar PDF." },
      ]);
    }
    setPdfUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="main-layout">
      <aside className="linkedin-aside">
        <div className="iframe-block">
          <div className="iframe-title">ACESSE MEU CANAL</div>
          <iframe 
            width="100%"
            height="220"
            src="https://www.youtube.com/embed/6yjaBCn54Rg?si=CA5jaIUj7oIn20-y"
            title="YouTube video player"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            frameBorder="0"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
            className="youtube-iframe"
            ></iframe>
        </div>
        <div className="iframe-block">
          <div className="iframe-title"></div>
          <iframe
            width="100%"
            height="220"
            src="https://www.youtube.com/embed/eVnCa5wuwdU?si=_lkClooEkDSfEmfM"
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
            className="youtube-iframe"
          ></iframe>
        </div>
        <div className="iframe-block">
          <div className="iframe-title"></div>
          <iframe
            width="100%"
            height="220"
            src="https://www.youtube.com/embed/4po1TZp_bKs?si=O5HnJtqqnsF7u85A"
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
            className="youtube-iframe"
          ></iframe>
        </div>
      </aside>
      <div className="chatgpt-center-outer">
        <div className="chatgpt-center-window">
          <div className="chatgpt-container">
            <div className="chatgpt-header">RAG OpenSearch Chat</div>
            <div className="chatgpt-messages">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`chatgpt-message chatgpt-${msg.role}`}
                  style={{
                    alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                    maxWidth: "70%",
                    minWidth: "30%",
                    width: "auto",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.content}
                </div>
              ))}
              {showTyping && (
                <div className="chatgpt-message chatgpt-assistant chatgpt-typing" style={{alignSelf: "flex-start", maxWidth: "70%", minWidth: "30%", width: "auto"}}>
                  Digitando{typingDots}
                </div>
              )}
            </div>
            <form className="chatgpt-input-row" onSubmit={handleSend}>
              <button
                type="button"
                className="chatgpt-pdf-btn"
                title="Enviar PDF"
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                disabled={pdfUploading}
              >
                <span role="img" aria-label="PDF">📎</span>
              </button>
              <input
                type="file"
                accept="application/pdf"
                style={{ display: "none" }}
                ref={fileInputRef}
                onChange={handlePdfUpload}
              />
              <input
                className="chatgpt-input"
                type="text"
                placeholder="Digite sua pergunta..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              <button
                className="chatgpt-send-btn"
                type="submit"
                disabled={loading || !input.trim()}
              >
                ➤
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
