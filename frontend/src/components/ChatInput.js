import React, { useState, useRef, useEffect } from 'react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your database... (Press Enter to send, Shift+Enter for new line)"
          className="chat-input"
          rows={1}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? '⏳' : '➤'}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;


