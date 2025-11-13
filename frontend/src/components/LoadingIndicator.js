import React from 'react';
import './LoadingIndicator.css';

const LoadingIndicator = () => {
  return (
    <div className="loading-message">
      <div className="message-avatar">🤖</div>
      <div className="message-content">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;


