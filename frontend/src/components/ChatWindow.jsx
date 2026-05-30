import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ImagePanel from './ImagePanel';
import GroundingPanel from './GroundingPanel';
import VoiceInput from './VoiceInput';
import { sendChat, clearSession } from '../api/client';

const QUICK_ACTIONS = [
  { icon: '✝️', text: 'Trinity', prompt: 'Explain the Holy Trinity' },
  { icon: '📖', text: 'Verse', prompt: 'What is John 3:16 about?' },
  { icon: '🙏', text: 'Prayer', prompt: 'How should I pray?' },
  { icon: '💒', text: 'Salvation', prompt: 'How can I be saved?' },
];

const CONTAINER_STYLE = {
  maxWidth: '800px',
  margin: '0 auto',
  width: '100%',
};

function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const [voiceKey, setVoiceKey] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageToSend = null) => {
    const message = messageToSend || input.trim();
    if (!message || loading) return;

    setInput('');
    setLoading(true);

    setMessages((prev) => [...prev, { role: 'user', content: message }]);

    try {
      const response = await sendChat(message);

      setLastResponse({
        retrievedVerses: response.retrieved_verses || [],
        verifiedCitations: response.verified_citations || [],
        hallucinatedCitations: response.hallucinated_citations || [],
        judgeScores: response.judge_scores || {},
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.response,
          verdict: response.judge_verdict,
          isImageRequest: response.is_image_request,
          imageResult: response.image_result,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', verdict: 'FLAG' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    await clearSession();
    setMessages([]);
    setLastResponse(null);
    setInput('');
    setVoiceKey(k => k + 1);
  };

  const handleVoiceTranscript = (text) => {
    setInput(text);
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#0f0f1a',
      position: 'relative',
    }}>
      {/* Header */}
      <header style={{
        ...CONTAINER_STYLE,
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #4a7c59, #3d6b4a)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '22px',
            boxShadow: '0 4px 20px rgba(74, 124, 89, 0.3)',
          }}>
            ✝️
          </div>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: '600' }}>ChristianMind</h1>
            <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{
                width: '5px',
                height: '5px',
                borderRadius: '50%',
                background: '#4ade80',
              }} />
              Grounded in Scripture
            </div>
          </div>
        </div>

        <button
          onClick={handleClear}
          style={{
            padding: '8px 16px',
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '10px',
            color: 'rgba(255,255,255,0.6)',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'all 0.2s',
            fontFamily: 'inherit',
          }}
          onMouseOver={(e) => {
            e.target.style.background = 'rgba(255,255,255,0.08)';
            e.target.style.color = '#fff';
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'rgba(255,255,255,0.04)';
            e.target.style.color = 'rgba(255,255,255,0.6)';
          }}
        >
          New Chat
        </button>
      </header>

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{ ...CONTAINER_STYLE, flex: 1, padding: '24px' }}>
          {messages.length === 0 && (
            <div style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              minHeight: 'calc(100vh - 250px)',
            }}>
              <div style={{ fontSize: '42px', marginBottom: '20px' }}>✝️</div>
              <h2 style={{
                fontSize: '26px',
                fontWeight: '600',
                marginBottom: '10px',
                color: '#fff',
              }}>
                ChristianMind AI
              </h2>
              <p style={{
                fontSize: '14px',
                color: 'rgba(255,255,255,0.4)',
                maxWidth: '380px',
                lineHeight: '1.6',
                marginBottom: '32px',
              }}>
                Explore God's Word with theological depth and pastoral care
              </p>

              {/* Quick Actions */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px',
                maxWidth: '360px',
                width: '100%',
              }}>
                {QUICK_ACTIONS.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(action.prompt)}
                    style={{
                      padding: '14px 16px',
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.06)',
                      borderRadius: '14px',
                      color: '#fff',
                      fontSize: '13px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      transition: 'all 0.2s',
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = 'rgba(74, 124, 89, 0.15)';
                      e.target.style.borderColor = 'rgba(74, 124, 89, 0.3)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = 'rgba(255,255,255,0.03)';
                      e.target.style.borderColor = 'rgba(255,255,255,0.06)';
                    }}
                  >
                    <span style={{ fontSize: '18px' }}>{action.icon}</span>
                    <span>{action.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px',
              animation: 'slideUp 0.3s ease-out',
            }}>
              {msg.isImageRequest && msg.imageResult && (
                <ImagePanel imageResult={msg.imageResult} />
              )}
              {!msg.isImageRequest && (
                <MessageBubble
                  message={msg.content}
                  isUser={msg.role === 'user'}
                  verdict={msg.verdict}
                  citations={msg.role === 'assistant' && i === messages.length - 1
                    ? [...(lastResponse?.verifiedCitations || []), ...(lastResponse?.hallucinatedCitations || [])]
                    : []
                  }
                />
              )}
              {msg.role === 'assistant' && i === messages.length - 1 && lastResponse && !msg.isImageRequest && (
                <GroundingPanel
                  retrievedVerses={lastResponse.retrievedVerses}
                  verifiedCitations={lastResponse.verifiedCitations}
                  hallucinatedCitations={lastResponse.hallucinatedCitations}
                  judgeScores={lastResponse.judgeScores}
                />
              )}
            </div>
          ))}

          {loading && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '14px 18px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '16px',
              maxWidth: '280px',
              border: '1px solid rgba(255,255,255,0.04)',
            }}>
              <div style={{ display: 'flex', gap: '3px' }}>
                {[0, 1, 2].map((i) => (
                  <div key={i} style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: '#4a7c59',
                    animation: 'pulse 1.2s ease-in-out infinite',
                    animationDelay: `${i * 0.15}s`,
                  }} />
                ))}
              </div>
              <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px' }}>
                Thinking...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div style={{
        padding: '16px 24px 24px',
        background: 'rgba(15, 15, 26, 0.95)',
        borderTop: '1px solid rgba(255,255,255,0.04)',
      }}>
        <div style={{ ...CONTAINER_STYLE }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '20px',
            padding: '6px 6px 6px 18px',
            transition: 'all 0.2s',
          }}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask about the Bible, theology, or faith..."
              disabled={loading}
              rows={1}
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#fff',
                fontSize: '14px',
                padding: '10px 0',
                resize: 'none',
                fontFamily: 'inherit',
                overflow: 'hidden',
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />

            <VoiceInput key={voiceKey} onTranscript={handleVoiceTranscript} disabled={loading} />

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '14px',
                background: input.trim() && !loading
                  ? 'linear-gradient(135deg, #4a7c59, #3d6b4a)'
                  : 'rgba(255,255,255,0.06)',
                border: 'none',
                cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s',
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(0.7); opacity: 0.4; }
          50% { transform: scale(1); opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

export default ChatWindow;