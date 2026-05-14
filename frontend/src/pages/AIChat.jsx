import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Loader2, User, Sparkles, BookOpen, AlertTriangle, Zap, MessageSquare, Info } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function AIChat({ user }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm your NeuroOps AI assistant. I'm here to help you manage your workspace more efficiently. You can ask me to summarize projects, list pending tasks, or even predict upcoming risks."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const formatContent = (content) => {
    // Simple formatter for bullet points and bold text
    return content.split('\n').map((line, i) => {
      if (line.startsWith('•') || line.startsWith('-') || line.startsWith('* ')) {
        return <div key={i} className="flex gap-2 items-start mt-1">
          <span className="text-primary-500 mt-1">•</span>
          <span>{line.replace(/^[•\-\*]\s*/, '')}</span>
        </div>;
      }
      if (line.includes('**')) {
        const parts = line.split('**');
        return <p key={i} className="mb-1">
          {parts.map((part, j) => j % 2 === 1 ? <strong key={j}>{part}</strong> : part)}
        </p>;
      }
      return <p key={i} className={line.trim() ? "mb-2" : "h-2"}>{line}</p>;
    });
  };

  const handleSend = async (forcedQuery) => {
    const query = forcedQuery || input;
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/ai/ask`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: query,
          user_id: user.id,
          company_id: user.company_id
        })
      });

      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer || "I'm sorry, I couldn't process that request right now."
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting to the intelligence server. Please ensure the backend is running."
      }]);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { id: 'create', label: 'Create high-priority task', icon: <Zap size={14} />, query: 'Create a new high-priority task: Finish the monthly report by Friday', adminOnly: true },
    { id: 'summary', label: 'Team performance summary', icon: <BookOpen size={14} />, query: 'Give me a summary of current team performance', adminOnly: true },
    { id: 'risk', label: 'Identify delayed tasks', icon: <AlertTriangle size={14} />, query: 'Which tasks are at risk of delay?', adminOnly: true },
    { id: 'help', label: 'What can you do?', icon: <Info size={14} />, query: 'What are your main capabilities?', adminOnly: false }
  ].filter(action => !action.adminOnly || (user.role === 'admin' || user.role === 'super_admin'));

  return (
    <div className="ai-chat-page">
      <div className="page-header flex justify-between items-center mb-6">
        <div>
          <h1 className="page-title flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-xl">
              <Bot size={24} className="text-primary-600" />
            </div>
            AI Assistant
          </h1>
          <p className="page-subtitle">Powered by NeuroOps Local Intelligence</p>
        </div>
        <div className="flex gap-2">
          <div className="badge badge-success">Online</div>
          <div className="badge badge-info">v2.1</div>
        </div>
      </div>

      <div className="ai-chat-grid">
        <div className="chat-main-container">
          <div className="chat-messages-scroll">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble-wrapper ${msg.role === 'user' ? 'user' : 'ai'}`}>
                <div className="chat-avatar">
                  {msg.role === 'user' ? <User size={20} /> : <Sparkles size={20} />}
                </div>
                <div className="chat-bubble">
                  {formatContent(msg.content)}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-bubble-wrapper ai">
                <div className="chat-avatar">
                  <Sparkles size={20} />
                </div>
                <div className="chat-bubble">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <div className="flex flex-wrap gap-2 mb-4">
              {quickActions.map(action => (
                <button 
                  key={action.id}
                  className="quick-suggestion-chip"
                  onClick={() => handleSend(action.query)}
                >
                  {action.icon}
                  {action.label}
                </button>
              ))}
            </div>
            
            <div className="chat-input-container">
              <MessageSquare size={18} className="text-gray-400" />
              <input
                type="text"
                className="chat-input-field"
                placeholder="Message NeuroOps AI..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && handleSend()}
              />
              <button
                className="chat-send-btn"
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        <div className="ai-chat-sidebar">
          <div className="card mb-4">
            <div className="card-header border-b pb-3 mb-3">
              <h3 className="card-title text-sm flex items-center gap-2">
                <Zap size={16} className="text-warning-500" />
                Capabilities
              </h3>
            </div>
            <div className="space-y-4">
              <div className="capability-item">
                <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Language</h4>
                <p className="text-sm">Natural language task parsing and creation.</p>
              </div>
              <div className="capability-item">
                <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Analytics</h4>
                <p className="text-sm">Real-time performance and workload summaries.</p>
              </div>
              <div className="capability-item">
                <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Predictions</h4>
                <p className="text-sm">Risk assessment and deadline suggestions.</p>
              </div>
            </div>
          </div>

          <div className="card bg-gray-900 text-white border-none">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-white/10 rounded-lg text-primary-400">
                <Bot size={20} />
              </div>
              <div>
                <h4 className="font-bold text-sm">SmartOS Core</h4>
                <p className="text-xs text-gray-400">Model: NeuroLlama-v2</p>
              </div>
            </div>
            <div className="h-1 bg-white/10 rounded-full mb-4">
              <div className="h-full bg-primary-500 rounded-full" style={{ width: '85%' }}></div>
            </div>
            <p className="text-xs text-gray-400">
              System is running at optimal capacity. Local processing enabled.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AIChat;