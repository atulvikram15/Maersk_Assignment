import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './Message.css';

const Message = ({ message }) => {
  const [showDetails, setShowDetails] = useState(false);

  if (message.type === 'user') {
    return (
      <div className="message user-message">
        <div className="message-content">
          <div className="message-text">{message.content}</div>
          <div className="message-time">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="message error-message">
        <div className="message-content">
          <div className="message-text">{message.content}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="message bot-message">
      <div className="message-avatar">🤖</div>
      <div className="message-content">
        <div className="message-text">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
              h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
              h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
              p: ({ children }) => <p className="markdown-p">{children}</p>,
              ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
              ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
              li: ({ children }) => <li className="markdown-li">{children}</li>,
              strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
              em: ({ children }) => <em className="markdown-em">{children}</em>,
              blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        
        {message.sqlQuery && (
          <div className="message-details">
            <button
              className="details-toggle"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? '▼' : '▶'} View SQL Query & Data
            </button>
            {showDetails && (
              <div className="details-content">
                <div className="sql-section">
                  <h4>SQL Query:</h4>
                  <SyntaxHighlighter
                    language="sql"
                    style={vscDarkPlus}
                    customStyle={{ borderRadius: '8px', padding: '12px' }}
                  >
                    {message.sqlQuery}
                  </SyntaxHighlighter>
                </div>
                {message.data && message.data.length > 0 && (
                  <div className="data-section">
                    <h4>Results ({message.rowCount} rows):</h4>
                    <div className="data-table-container">
                      <table className="data-table">
                        <thead>
                          <tr>
                            {Object.keys(message.data[0]).map((key) => (
                              <th key={key}>{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {message.data.slice(0, 10).map((row, idx) => (
                            <tr key={idx}>
                              {Object.values(row).map((value, i) => (
                                <td key={i}>
                                  {typeof value === 'object'
                                    ? JSON.stringify(value)
                                    : String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {message.data.length > 10 && (
                        <p className="data-more">
                          ... and {message.data.length - 10} more rows
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        <div className="message-time">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default Message;


