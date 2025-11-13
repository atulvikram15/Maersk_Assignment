# Frontend Setup Guide

## Quick Start

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Install Backend Dependencies (if not already done)

```bash
# In the main project directory
pip install -r requirements.txt
```

### 3. Start the Backend Server

```bash
# In the main project directory
python endpoints.py
```

The backend will run on `http://localhost:5000`

### 4. Start the React Frontend

```bash
# In the frontend directory
npm start
```

The frontend will open automatically at `http://localhost:3000`

## Features

✅ **Beautiful Chatbot Interface** - Modern, gradient design with smooth animations  
✅ **Markdown Rendering** - Analysis text from Gemini is beautifully formatted with headers, lists, bold text, etc.  
✅ **SQL Query Viewer** - Expandable section to view generated SQL queries  
✅ **Data Table** - Formatted table view of query results  
✅ **Session Management** - Automatic conversation context (no manual session IDs needed)  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Real-time Updates** - Instant message delivery with loading indicators  

## Usage

1. Type your question in natural language
2. Press Enter or click the send button
3. View the analysis with beautiful markdown formatting
4. Click "View SQL Query & Data" to see technical details
5. Continue the conversation - context is automatically maintained

## Troubleshooting

### CORS Errors
- Make sure `flask-cors` is installed: `pip install flask-cors`
- The backend should have `CORS(app)` enabled (already added)

### Connection Errors
- Verify backend is running on port 5000
- Check that the proxy in `package.json` points to `http://localhost:5000`
- For production, update the API URL in `ChatInterface.js`

### Build Issues
- Make sure Node.js (v14+) is installed
- Try deleting `node_modules` and `package-lock.json`, then `npm install` again

## Production Build

To create a production build:

```bash
cd frontend
npm run build
```

The optimized files will be in `frontend/build/`


