'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { Message } from '@/types/api';
import Link from 'next/link';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const chatMutation = useMutation({
    mutationFn: (message: string) => api.agent.chat(message),
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: input },
        {
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources,
        },
      ]);
      setInput('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;
    chatMutation.mutate(input);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">AI Knowledge Agent</h1>
        <Link
          href="/settings"
          className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          Settings
        </Link>
      </header>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <h2 className="text-2xl font-semibold mb-2">Ask me anything</h2>
            <p className="text-sm">I have access to your Gmail and HubSpot data.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl p-4 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-white shadow-sm border border-gray-200'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-lg p-4 shadow-sm">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="border-t bg-white p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your emails, contacts, deals..."
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={chatMutation.isPending}
            />
            <button
              type="submit"
              disabled={chatMutation.isPending || !input.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
