import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  X,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  ChevronRight,
  MessageSquare,
  Terminal,
  ShieldAlert,
  Loader2,
  CornerDownLeft,
} from 'lucide-react';
import { api } from '../api/client';

export default function AiAnalystDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'copilot',
      text: "🛡️ **GeoSentinel AI Intelligence Copilot Online.**\n\nI analyze real-time open-source intelligence, calculate mathematical risk indices, and evaluate strategic supply-chain chokepoints. How can I assist your operational briefing today?",
      citations: [],
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const promptChips = [
    'Summarize Red Sea maritime security risks',
    'What triggered recent alerts in Ukraine?',
    'Evaluate semiconductor supply-chain vulnerability in East Asia',
    'Show countries with critical risk breach',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim() || isLoading) return;

    const userMsg = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const res = await api.askChatCopilot(q);
      const botMsg = {
        id: `bot_${Date.now()}`,
        sender: 'copilot',
        text: res.response_markdown,
        citations: res.citations || [],
        followups: res.suggested_followups || [],
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'copilot',
          text: `⚠️ **Analytical Copilot Query Failed**: ${err.message || 'Unable to retrieve telemetry'}`,
          citations: [],
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[500px] bg-[#0D1422]/95 backdrop-blur-2xl border-l border-slate-800 shadow-2xl flex flex-col animate-slideLeft font-sans">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-[#080D17]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 font-mono flex items-center gap-2">
              <span>ASK GEOSENTINEL</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500/10 text-sky-400 font-mono border border-sky-500/20">
                RAG COPILOT
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Verifiable OSINT &amp; Decision Support Analyst</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className="text-[10px] font-mono text-slate-500 mb-1 px-1">
              {msg.sender === 'user' ? 'Operator' : 'GeoSentinel Copilot'} &bull; {msg.timestamp}
            </div>
            <div
              className={`max-w-[92%] rounded-2xl p-4 leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-sky-600 text-white font-medium rounded-tr-none shadow-md'
                  : 'bg-[#111C2D] border border-slate-800 text-slate-200 rounded-tl-none shadow-sm'
              }`}
            >
              <div className="whitespace-pre-line text-xs font-sans leading-relaxed">
                {msg.text}
              </div>

              {/* Primary Citations block */}
              {msg.citations?.length > 0 && (
                <div className="mt-3.5 pt-3 border-t border-slate-800">
                  <div className="text-[10px] font-mono uppercase text-sky-400 font-bold mb-2 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Verifiable Primary Citations ({msg.citations.length}):</span>
                  </div>
                  <div className="space-y-1.5">
                    {msg.citations.map((c, i) => (
                      <a
                        key={i}
                        href={c.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center justify-between p-2 rounded-lg bg-[#0D1422] hover:bg-slate-800 text-[11px] text-slate-300 hover:text-sky-300 border border-slate-800/80 transition-colors"
                      >
                        <span className="truncate pr-2 font-medium">
                          [{c.country_iso}] {c.title}
                        </span>
                        <ExternalLink className="w-3 h-3 text-sky-400 shrink-0" />
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up suggestions */}
              {msg.followups?.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-800">
                  <div className="text-[10px] text-slate-400 font-mono mb-1.5">Suggested Inquiries:</div>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.followups.map((fu, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(fu)}
                        className="text-[10px] px-2.5 py-1 rounded-md bg-[#0D1422] hover:bg-sky-500/20 text-slate-300 hover:text-sky-300 border border-slate-800 transition-colors font-mono"
                      >
                        {fu}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs font-mono text-sky-400 py-2 px-1 animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Consulting Knowledge Graph &amp; Ingested Feeds...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      {messages.length <= 2 && (
        <div className="px-4 py-2 border-t border-slate-800/80 bg-[#080D17]/50">
          <div className="text-[10px] font-mono text-slate-400 mb-1.5">Suggested Prompts:</div>
          <div className="flex flex-wrap gap-1.5">
            {promptChips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(chip)}
                className="text-[10px] px-2.5 py-1 rounded-md bg-[#111C2D] hover:bg-slate-800 text-slate-300 hover:text-sky-300 border border-slate-800 transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Composer */}
      <div className="p-3.5 border-t border-slate-800 bg-[#080D17]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask anything about global conflicts, assets, or chokepoints..."
            className="w-full pl-3 pr-10 py-2.5 rounded-xl bg-[#111C2D] border border-slate-800 text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-sky-500/60 focus:ring-1 focus:ring-sky-500/30 transition-all font-sans"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            className="absolute right-2 p-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white disabled:opacity-40 transition-colors"
          >
            <CornerDownLeft className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
