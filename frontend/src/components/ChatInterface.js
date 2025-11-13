import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (query) => {
    if (!query.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          ...(sessionId && { session_id: sessionId }),
          include_memory_context: true,
        }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Update session ID if provided
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.analysis || 'No analysis available',
        sqlQuery: data.sql_query,
        data: data.data,
        rowCount: data.row_count,
        memoryContext: data.memory_context || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>E-Commerce Operations-Assistant</h1>
        <p>Ask questions about your database in natural language</p>
        <button onClick={handleClearChat} className="clear-button">
          Clear Chat
        </button>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <div ref={messagesEndRef} />
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatInterface;

