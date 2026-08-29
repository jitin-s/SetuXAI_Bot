import React, { useState, useEffect, useRef } from 'react';
import { Send, RefreshCw, User, Globe, CheckCircle, AlertTriangle, Volume2, FileText, Brain } from 'lucide-react';

// Dynamic API_BASE: Uses http://localhost:8000 during local dev, and relative /api on Vercel production
const API_BASE = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://localhost:8000'
  : '';

const LANGUAGES = [
  { code: 'English', label: 'English' },
  { code: 'Hindi', label: 'Hindi (हिंदी)' },
  { code: 'Marathi', label: 'Marathi (मराठी)' },
  { code: 'Bengali', label: 'Bengali (বাংলা)' },
  { code: 'Tamil', label: 'Tamil (தமிழ்)' },
  { code: 'Telugu', label: 'Telugu (తెలుగు)' },
  { code: 'Gujarati', label: 'Gujarati (ગુજરાતી)' }
];

const QUICK_CHIPS = [
  "SetuX All Services & Fee List",
  "Aadhaar Address Update (₹50)",
  "Aadhaar Mobile Link (₹50)",
  "Apply New PAN Card (₹106)",
  "Apply New Driving License (₹250)",
  "Apply New Passport (₹350)",
  "Add Member to Ration Card (₹30)",
  "Ayushman Health Card (₹30)"
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Welcome to SetuX Citizen Assistance Helpdesk.\n\nHow may I assist you today with Document Services (Aadhaar, PAN Card, Driving License, Passport, Voter ID, Ration Card, Ayushman Card)?'
    }
  ]);
  const [input, setInput] = useState('');
  const [language, setLanguage] = useState('English');
  const [loading, setLoading] = useState(false);
  const [fontSize, setFontSize] = useState('normal');
  const [themeMode, setThemeMode] = useState('standard');
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const [scanUrlInput, setScanUrlInput] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanStatusMsg, setScanStatusMsg] = useState('');
  const [showScannerModal, setShowScannerModal] = useState(false);
  const [scannedWebsitesCount, setScannedWebsitesCount] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    document.documentElement.className = `font-${fontSize}`;
    document.body.className = themeMode !== 'standard' ? `theme-${themeMode}` : '';
    fetchLearnedStats();
  }, [fontSize, themeMode]);

  const fetchLearnedStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/learned-knowledge`);
      if (res.ok) {
        const data = await res.json();
        setScannedWebsitesCount(data.scanned_websites?.length || 0);
      }
    } catch (e) {}
  };

  const handleScanWebsite = async (e) => {
    e.preventDefault();
    if (!scanUrlInput.trim() || scanning) return;

    setScanning(true);
    setScanStatusMsg('Scanning website content...');

    try {
      const res = await fetch(`${API_BASE}/api/scan-website`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: scanUrlInput })
      });

      const data = await res.json();
      if (res.ok) {
        setScanStatusMsg(`✓ Learned website from ${scanUrlInput}!`);
        setScanUrlInput('');
        fetchLearnedStats();
        setTimeout(() => setShowScannerModal(false), 2000);
      } else {
        setScanStatusMsg(`Error: ${data.detail || 'Failed to scan website'}`);
      }
    } catch (err) {
      setScanStatusMsg('Connection error scanning website.');
    } finally {
      setScanning(false);
    }
  };

  const speakText = (text, index) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      if (speakingIndex === index) {
        setSpeakingIndex(null);
        return;
      }
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.onend = () => setSpeakingIndex(null);
      setSpeakingIndex(index);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSend = async (userMsgText) => {
    const query = userMsgText || input;
    if (!query.trim() || loading) return;

    const updatedMessages = [...messages, { sender: 'user', text: query }];
    setMessages(updatedMessages);
    if (!userMsgText) setInput('');
    setLoading(true);

    const assistantIndex = updatedMessages.length;
    setMessages([...updatedMessages, { sender: 'assistant', text: '' }]);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query, language, stream: true })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.replace('data: ', ''));
              if (data.token) {
                accumulatedText += data.token;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[assistantIndex] = { sender: 'assistant', text: accumulatedText };
                  return newMsgs;
                });
              }
            } catch (e) {}
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[assistantIndex] = {
          sender: 'assistant',
          text: `Connection error with SetuX Backend Server.\n\nPlease check server connection.`
        };
        return newMsgs;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    try {
      await fetch(`${API_BASE}/api/clear`, { method: 'POST' });
    } catch (e) {}
    setMessages([
      {
        sender: 'assistant',
        text: 'Session reset.\n\nHow can I help you today with SetuX document services?'
      }
    ]);
  };

  return (
    <div className="app-viewport-root">
      {/* STICKY TOP HEADER SECTION */}
      <div className="sticky-header-container">
        {/* Top Tricolor Banner */}
        <div className="tricolor-stripe">
          <div className="ts-orange" />
          <div className="ts-white" />
          <div className="ts-green" />
        </div>

        {/* Upper Utility Taskbar */}
        <div className="gov-utility-taskbar">
          <div className="utility-item">
            <button
              className="tool-btn sync-btn"
              onClick={() => setShowScannerModal(!showScannerModal)}
            >
              <Brain size={12} /> Sync Website ({scannedWebsitesCount})
            </button>
          </div>

          {/* Text Resizing Controls */}
          <div className="utility-item accessibility-toolbar">
            <span className="tb-label">Text:</span>
            <button className={`tool-btn ${fontSize === 'small' ? 'active' : ''}`} onClick={() => setFontSize('small')}>A-</button>
            <button className={`tool-btn ${fontSize === 'normal' ? 'active' : ''}`} onClick={() => setFontSize('normal')}>A</button>
            <button className={`tool-btn ${fontSize === 'large' ? 'active' : ''}`} onClick={() => setFontSize('large')}>A+</button>
          </div>

          {/* Theme Selector */}
          <div className="utility-item accessibility-toolbar">
            <span className="tb-label">Theme:</span>
            <button className={`tool-btn ${themeMode === 'standard' ? 'active' : ''}`} onClick={() => setThemeMode('standard')}>Standard</button>
            <button className={`tool-btn ${themeMode === 'contrast' ? 'active' : ''}`} onClick={() => setThemeMode('contrast')}>Contrast</button>
            <button className={`tool-btn ${themeMode === 'blue' ? 'active' : ''}`} onClick={() => setThemeMode('blue')}>Dark Blue</button>
          </div>
        </div>

        {/* Main Portal Header */}
        <header className="gov-portal-header">
          <div className="header-brand-group">
            <div className="ashoka-emblem">S</div>
            <div className="brand-text">
              <h1>SetuX Online Helpdesk Assistant</h1>
              <p>Unified Helpdesk Directory for Citizen Identification Services</p>
            </div>
          </div>

          <button onClick={handleClear} className="tool-btn clear-btn">
            <RefreshCw size={12} style={{ display: 'inline', marginRight: 3 }} /> Reset
          </button>
        </header>

        {/* Website Self-Learning Bar Modal / Drawer */}
        {showScannerModal && (
          <div className="scanner-modal-bar">
            <div className="scanner-modal-title">
              <Brain size={14} color="#60a5fa" />
              Scanner:
            </div>
            <form onSubmit={handleScanWebsite} className="scanner-modal-form">
              <input
                type="text"
                value={scanUrlInput}
                onChange={(e) => setScanUrlInput(e.target.value)}
                placeholder="Enter URL to crawl (e.g. https://setux.com)..."
                className="scanner-input"
                disabled={scanning}
              />
              <button type="submit" className="send-btn scanner-btn" disabled={scanning || !scanUrlInput.trim()}>
                {scanning ? '...' : 'Scan'}
              </button>
            </form>
            {scanStatusMsg && (
              <span className={`scanner-status ${scanStatusMsg.startsWith('✓') ? 'success' : 'error'}`}>
                {scanStatusMsg}
              </span>
            )}
          </div>
        )}

        {/* Notice Marquee Strip */}
        <div className="notice-marquee-strip">
          <span className="marquee-badge">NOTICE</span>
          <div className="marquee-text">
            All Aadhaar address updates & e-KYC PAN registrations are processed 100% online on SetuX.
          </div>
        </div>
      </div>

      {/* Main Page Body - 100% Focused on Chatbot */}
      <div className="gov-container">
        <main className="chat-main-window">
          {/* CHAT BANNER HEADER WITH LANGUAGE BUTTON */}
          <div className="chat-banner-bar">
            <div className="chat-banner-title">
              <FileText size={15} /> SetuX Online Helpdesk Assistant
            </div>
            
            <div className="chat-banner-actions">
              {/* Language Selector Dropdown inside Chat Box */}
              <div className="chat-lang-button-group">
                <Globe size={13} color="#1e3a8a" />
                <span className="chat-lang-label">Lang:</span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="chat-lang-dropdown"
                >
                  {LANGUAGES.map(lang => (
                    <option key={lang.code} value={lang.code}>{lang.label}</option>
                  ))}
                </select>
              </div>

              <div className="chat-active-indicator">
                ● Active
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.sender}`}>
                <div className="avatar">
                  {msg.sender === 'user' ? <User size={15} /> : 'S'}
                </div>
                <div className="message-bubble">
                  {msg.text.includes('100% Online') && (
                    <div className="badge-online">
                      <CheckCircle size={12} style={{ display: 'inline', marginRight: 4 }} />
                      100% Online Process
                    </div>
                  )}
                  {msg.text.includes('Offline Visit Required') && (
                    <div className="badge-offline">
                      <AlertTriangle size={12} style={{ display: 'inline', marginRight: 4 }} />
                      Offline Visit Required (Biometrics / Verification Slot)
                    </div>
                  )}
                  <div>{msg.text || (loading && index === messages.length - 1 ? 'Processing request...' : '')}</div>
                  
                  {msg.sender === 'assistant' && msg.text && (
                    <button
                      onClick={() => speakText(msg.text, index)}
                      title="Screen Reader Audio Readout"
                      className="speech-btn"
                      style={{ color: speakingIndex === index ? '#2563eb' : '#64748b' }}
                    >
                      <Volume2 size={12} /> {speakingIndex === index ? 'Speaking...' : 'Listen Audio'}
                    </button>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Service Links */}
          <div className="quick-chips-wrapper">
            <div className="quick-chips-title">Frequent Citizen Services</div>
            <div className="quick-chips">
              {QUICK_CHIPS.map((chipText, i) => (
                <button key={i} className="chip" onClick={() => handleSend(chipText)}>
                  {chipText}
                </button>
              ))}
            </div>
          </div>

          {/* Query Form Input */}
          <form
            className="chat-input-form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Enter query in ${language}... (e.g. How to update address?)`}
              className="chat-input"
              disabled={loading}
            />
            <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
              <Send size={14} /> Submit
            </button>
          </form>
        </main>
      </div>

      {/* Traditional Footer */}
      <footer className="gov-footer">
        <div className="footer-nav">
          <a href="#policies">Policies</a>
          <a href="#copyright">Copyright</a>
          <a href="#privacy">Privacy</a>
          <a href="#terms">Terms</a>
          <a href="#help">Help</a>
        </div>
        <div className="footer-meta">
          Website Content Managed by SetuX Document Portal
          <br />
          © 2026 SetuX. All Rights Reserved.
        </div>
      </footer>
    </div>
  );
}
