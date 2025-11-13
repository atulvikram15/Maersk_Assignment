import React from 'react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import './MessageList.css';

const MessageList = ({ messages, isLoading }) => {
  return (
    <div className="message-list">
      {messages.length === 0 && (
        <div className="welcome-message">
          <h2>👋 Welcome!</h2>
          <p>Ask me anything about your database in natural language.</p>
          <p className="example-queries">
            <strong>Try asking:</strong>
            <br />
            • "What are the top 5 product categories by revenue?"
            <br />
            • "Show me the average order value by state"
            <br />
            • "Which customers have the highest lifetime value?"
          </p>
        </div>
      )}
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  );
};

export default MessageList;


