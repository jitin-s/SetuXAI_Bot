import React, { useState, useEffect, useRef } from 'react';
import { Send, RefreshCw, User, Globe, CheckCircle, AlertTriangle, Volume2, FileText, Headphones, Brain } from 'lucide-react';

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

const HELPLINES = [
  { service: 'Aadhaar Services', number: '1947', email: 'help@uidai.gov.in', note: 'Toll-Free 24x7' },
  { service: 'PAN Card Assistance', number: '1800-180-1961', email: 'tininfo@proteantech.in', note: 'NSDL / Protean' },
  { service: 'Driving License / RTO', number: '1800-180-0151', email: 'helpdesk-sarathi@gov.in', note: 'Parivahan RTO' },
  { service: 'Passport Seva Kendra', number: '1800-258-1800', email: 'jcpv.meaindia@gov.in', note: 'Toll-Free 8AM-10PM' },
  { service: 'Voter ID (EPIC)', number: '1950', email: 'complaints@eci.gov.in', note: 'Election Commission' },
  { service: 'Ration Card & NFSA', number: '1944 / 1800-180-2087', email: 'nfsa-helpdesk@gov.in', note: 'Food & Supplies' },
  { service: 'Ayushman Health Card', number: '14555 / 1800-111-565', email: 'abdm@nha.gov.in', note: 'PM-JAY Health' }
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
        setScanStatusMsg(`✓ Successfully learned website content from ${scanUrlInput}!`);
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
    <div style={{ overflowX: 'hidden', maxWidth: '100vw' }}>
      {/* FIXED NON-SCROLLABLE STICKY HEADER SECTION */}
      <div className="sticky-header-container">
        {/* Top Tricolor Banner */}
        <div className="tricolor-stripe">
          <div className="ts-orange" />
          <div className="ts-white" />
          <div className="ts-green" />
        </div>

        {/* Upper Taskbar */}
        <div className="gov-utility-taskbar">
          <div className="utility-left">
            <a href="#main-content">Skip to Main Content</a>
            <a href="#screen-reader">Screen Reader Access</a>
          </div>

          <div className="utility-right">
            {/* Website Self-Learning Sync Button */}
            <button
              className="tool-btn"
              onClick={() => setShowScannerModal(!showScannerModal)}
              style={{ background: '#2563eb', borderColor: '#3b82f6', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
            >
              <Brain size={12} /> Sync / Learn Website ({scannedWebsitesCount})
            </button>

            {/* Text Resizing Toolbar */}
            <div className="accessibility-toolbar">
              <span className="tb-label">Text:</span>
              <button className={`tool-btn ${fontSize === 'small' ? 'active' : ''}`} onClick={() => setFontSize('small')}>A-</button>
              <button className={`tool-btn ${fontSize === 'normal' ? 'active' : ''}`} onClick={() => setFontSize('normal')}>A</button>
              <button className={`tool-btn ${fontSize === 'large' ? 'active' : ''}`} onClick={() => setFontSize('large')}>A+</button>
            </div>

            {/* Theme Selector */}
            <div className="accessibility-toolbar">
              <span className="tb-label">Theme:</span>
              <button className={`tool-btn ${themeMode === 'standard' ? 'active' : ''}`} onClick={() => setThemeMode('standard')}>Standard</button>
              <button className={`tool-btn ${themeMode === 'contrast' ? 'active' : ''}`} onClick={() => setThemeMode('contrast')}>Contrast</button>
              <button className={`tool-btn ${themeMode === 'blue' ? 'active' : ''}`} onClick={() => setThemeMode('blue')}>Dark Blue</button>
            </div>
          </div>
        </div>

        {/* Main Portal Header */}
        <header className="gov-portal-header">
          <div className="header-brand-group">
            <div className="ashoka-emblem">S</div>
            <div className="brand-text">
              <h1>SetuX Online Helpdesk Assistant</h1>
              <p>Unified Helpdesk & Verification Directory for Citizen Identification Services</p>
            </div>
          </div>

          <button onClick={handleClear} className="tool-btn" style={{ padding: '0.4rem 0.75rem' }}>
            <RefreshCw size={12} style={{ display: 'inline', marginRight: 4 }} /> Clear
          </button>
        </header>

        {/* Website Self-Learning Bar Modal / Drawer */}
        {showScannerModal && (
          <div style={{ background: '#1e293b', borderBottom: '2px solid #2563eb', padding: '0.75rem 1rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, fontSize: '0.82rem' }}>
              <Brain size={15} color="#60a5fa" />
              Website Scanner:
            </div>
            <form onSubmit={handleScanWebsite} style={{ display: 'flex', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
              <input
                type="text"
                value={scanUrlInput}
                onChange={(e) => setScanUrlInput(e.target.value)}
                placeholder="Enter URL (e.g. https://setux.com)..."
                style={{ flex: 1, padding: '0.35rem 0.65rem', borderRadius: '4px', border: '1px solid #475569', background: '#0f172a', color: '#ffffff', fontSize: '0.82rem', minWidth: '0' }}
                disabled={scanning}
              />
              <button type="submit" className="send-btn" style={{ padding: '0 0.85rem', height: '30px', fontSize: '0.8rem' }} disabled={scanning || !scanUrlInput.trim()}>
                {scanning ? 'Scanning...' : 'Scan'}
              </button>
            </form>
            {scanStatusMsg && (
              <span style={{ fontSize: '0.78rem', color: scanStatusMsg.startsWith('✓') ? '#4ade80' : '#f87171' }}>
                {scanStatusMsg}
              </span>
            )}
          </div>
        )}

        {/* Notice Marquee Strip */}
        <div className="notice-marquee-strip">
          <span className="marquee-badge">LATEST NOTICE</span>
          <div className="marquee-text">
            Important Notice: All Aadhaar address updates and e-KYC PAN Card registrations are processed 100% online on SetuX. For biometrics & driving tests, book appointment slots live.
          </div>
        </div>
      </div>

      {/* Main Page Body */}
      <div className="gov-container" id="main-content">
        <div className="portal-grid-layout">
          
          {/* AI Helpdesk Chat Window (Positioned FIRST in DOM structure) */}
          <main className="chat-main-window">
            {/* CHAT BANNER HEADER WITH LANGUAGE BUTTON */}
            <div className="chat-banner-bar">
              <div style={{ fontWeight: 700, fontSize: '0.88rem', color: '#1e3a8a', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileText size={15} /> SetuX Online Helpdesk Assistant
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {/* Language Selector Dropdown inside Chat Box */}
                <div className="chat-lang-button-group">
                  <Globe size={13} color="#1e3a8a" />
                  <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#1e3a8a' }}>Lang:</span>
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

                <div style={{ fontSize: '0.75rem', color: '#15803d', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
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
                        style={{ background: 'none', border: 'none', cursor: 'pointer', marginTop: '0.4rem', color: speakingIndex === index ? '#2563eb' : '#64748b', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', fontWeight: 600 }}
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
              <div className="quick-chips-title">Frequent Citizen Document Services</div>
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

          {/* Official Helplines Directory Card (Positioned SECOND in DOM structure) */}
          <aside className="left-sidebar">
            <div className="gov-card">
              <div className="card-header">
                <Headphones size={15} /> Official Document Helplines
              </div>
              <div className="card-body">
                {HELPLINES.map((item, idx) => (
                  <div key={idx} className="helpline-row">
                    <div className="hr-title">{item.service}</div>
                    <div className="hr-phone">{item.number}</div>
                    <div className="hr-meta">{item.email} • {item.note}</div>
                  </div>
                ))}
              </div>
            </div>
          </aside>

        </div>
      </div>

      {/* Traditional Footer */}
      <footer className="gov-footer">
        <div className="footer-nav">
          <a href="#policies">Website Policies</a>
          <a href="#copyright">Copyright Policy</a>
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms & Conditions</a>
          <a href="#help">Help & Support</a>
          <a href="#feedback">Feedback</a>
        </div>
        <div className="footer-meta">
          Website Content Managed by SetuX Document Portal • Official Helpdesk & Verification Directory
          <br />
          © 2026 SetuX. All Rights Reserved.
        </div>
      </footer>
    </div>
  );
}
