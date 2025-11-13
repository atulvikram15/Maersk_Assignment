# React Chatbot Frontend

A modern, chatbot-style React interface for the Natural Language to SQL Query System.

## Features

- 🎨 Beautiful, modern UI with gradient design
- 💬 Chatbot-style conversation interface
- 📝 Markdown rendering for analysis responses
- 🔍 Expandable SQL query and data views
- 📱 Responsive design for mobile and desktop
- ⚡ Real-time conversation with session management
- 🎯 Syntax highlighting for SQL queries

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

3. **Make sure your Flask backend is running:**
   ```bash
   # In the main project directory
   python endpoints.py
   ```

   The backend should be running on `http://localhost:5000`

## Configuration

The frontend is configured to proxy API requests to `http://localhost:5000` (see `package.json`). If your backend runs on a different port, update the proxy setting or use environment variables.

## Usage

1. Open the app in your browser
2. Type a natural language query in the input box
3. Press Enter or click the send button
4. View the analysis, SQL query, and data results
5. Continue the conversation - the system remembers context automatically

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatInterface.js      # Main chat container
│   │   ├── MessageList.js        # Message list component
│   │   ├── Message.js            # Individual message component
│   │   ├── ChatInput.js          # Input component
│   │   └── LoadingIndicator.js  # Loading animation
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Features Explained

### Markdown Rendering
The analysis text from Gemini is rendered with full markdown support:
- Headers (H1, H2, H3)
- Bold and italic text
- Lists (ordered and unordered)
- Code blocks with syntax highlighting
- Blockquotes

### Session Management
- Sessions are automatically managed by the backend
- Each conversation maintains context across messages
- No need to manually specify session IDs

### Expandable Details
- Click "View SQL Query & Data" to see the generated SQL
- View query results in a formatted table
- Shows first 10 rows with indication if more exist

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.


