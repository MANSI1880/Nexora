'use client';

import React, { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/chat';
import { ChatResponse } from '@/types/api';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  metadata?: ChatResponse;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'ai',
      content: 'Hello! I am Nexora, your AI IT Service Desk agent. How can I help you today?',
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(userMessage.content);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: response.response,
        metadata: response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: 'Unable to connect to Nexora. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-white max-w-4xl mx-auto border-x border-gray-200 shadow-sm">
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-900 rounded-bl-none'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>

              {message.metadata && message.role === 'ai' && (
                <div className="mt-3 pt-3 border-t border-gray-200 space-y-2 text-xs">
                  <div className="flex flex-wrap gap-2">
                    <Badge color="blue">{message.metadata.intent}</Badge>
                    <Badge color="gray">{Math.round(message.metadata.confidence * 100)}% confidence</Badge>
                    <Badge color={message.metadata.status === 'success' ? 'green' : 'red'}>
                      {message.metadata.status}
                    </Badge>
                  </div>
                  
                  {message.metadata.ticket_id && (
                    <Card className="mt-2 bg-white/80 p-2 text-gray-800">
                      <span className="font-medium">Ticket Created:</span> {message.metadata.ticket_id}
                    </Card>
                  )}
                  
                  {message.metadata.action && (
                    <Card className="mt-2 bg-white/80 p-2 text-gray-800">
                      <span className="font-medium">Action:</span> {message.metadata.action}
                    </Card>
                  )}

                  {message.metadata.sources && message.metadata.sources.length > 0 && (
                    <div className="mt-2 text-gray-500">
                      <span className="font-medium">Sources: </span>
                      {message.metadata.sources.join(', ')}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3 rounded-bl-none flex space-x-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your issue here..."
            className="flex-1 appearance-none block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            disabled={isLoading}
          />
          <Button type="submit" isLoading={isLoading} className="px-6 py-3 shrink-0">
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}
