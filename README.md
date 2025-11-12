# Natural Language to SQL Query System

This system allows users to query a MySQL database using natural language. It uses Google Generative AI to convert natural language queries into SQL, executes them, and provides analytical insights.

## Project Structure

- `backend.py`: Contains all backend helper functions for database operations, LLM interactions, and conversation orchestration
- `conversation_memory.py`: FAISS-based conversational memory manager
- `endpoints.py`: Contains Flask API endpoints that call backend functions
- `olist_schema.sql`: Database schema for the Olist e-commerce dataset
- `requirements.txt`: Python dependencies

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (with defaults)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=olist_db
DB_USER=root
DB_PASSWORD=your_password
PORT=5000
MEMORY_STORE_DIR=memory_store
MEMORY_SESSION_TOP_K=4
MEMORY_GLOBAL_TOP_K=2
MEMORY_SIMILARITY_THRESHOLD=0.5
MEMORY_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 3. Set Up MySQL Database

1. Make sure MySQL is installed and running
2. Create the database and tables using the schema file:

```bash
mysql -u root -p < olist_schema.sql
```

3. Import your data into the database (if you have CSV files)

### 4. Run the Application

```bash
python endpoints.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and the query processor is initialized.

**Response:**
```json
{
    "status": "healthy",
    "message": "API is running",
    "query_processor_initialized": true
}
```

### 2. Process Natural Language Query

**POST** `/query`

Convert natural language to SQL, execute it, and get analysis.

**Request Body:**
```json
{
    "query": "What are the top 10 customers by total order value?",
    "session_id": "optional-existing-session-id",
    "reset_session": false,
    "include_memory_context": true
}
```

**Response:**
```json
{
    "session_id": "session_ab12cd34ef56",
    "sql_query": "SELECT ...",
    "data": [...],
    "analysis": "Based on the query results...",
    "row_count": 10,
    "memory_context": [
        {
            "session_id": "session_ab12cd34ef56",
            "timestamp": "2025-11-12T09:00:11.215Z",
            "user_query": "Which customers ordered the most?",
            "sql_query": "SELECT ...",
            "analysis": "Top customers last discussed...",
            "data_preview": "[{...}]",
            "similarity": 0.84,
            "context_snippet": "Context #1 (current session): ..."
        }
    ]
}
```

### 3. Execute Raw SQL Query

**POST** `/query/sql`

Execute a raw SQL query directly (SELECT queries only).

**Request Body:**
```json
{
    "sql": "SELECT * FROM orders LIMIT 10"
}
```

**Response:**
```json
{
    "sql_query": "SELECT * FROM orders LIMIT 10",
    "data": [...],
    "row_count": 10
}
```

### 4. List Memory Sessions

**GET** `/memory/sessions`

Retrieve the list of stored conversational sessions.

**Response:**
```json
{
    "count": 2,
    "sessions": [
        {
            "session_id": "session_ab12cd34ef56",
            "count": 3,
            "latest_timestamp": "2025-11-12T09:15:21.817Z"
        }
    ]
}
```

### 5. Retrieve Session History

**GET** `/memory/<session_id>`

Fetch the stored memory entries for a specific session ID.

**Response:**
```json
{
    "session_id": "session_ab12cd34ef56",
    "count": 3,
    "entries": [
        {
            "timestamp": "2025-11-12T09:15:21.817Z",
            "user_query": "What were the top categories last month?",
            "sql_query": "SELECT ...",
            "analysis": "Category insights...",
            "data_preview": "[{...}]"
        }
    ]
}
```

## Example Usage

### Using curl:

```bash
# Health check
curl http://localhost:5000/health

# Natural language query (new session)
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the total revenue by product category"}'

# Follow-up using the returned session_id
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
        "session_id": "session_ab12cd34ef56",
        "query": "Drill down into the top category and show average basket size"
      }'

# Inspect stored memory
curl http://localhost:5000/memory/session_ab12cd34ef56

# Raw SQL query
curl -X POST http://localhost:5000/query/sql \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM orders LIMIT 5"}'
```

### Using Python:

```python
import requests

# Natural language query
response = requests.post('http://localhost:5000/query', json={
    'query': 'What is the average order value?'
})
print(response.json())
```

## Features

1. **Natural Language to SQL**: Converts user queries in plain English to SQL
2. **Conversational Memory**: FAISS-backed vector store recalls prior exchanges for context-aware answers
3. **Query Execution**: Safely executes SQL queries against MySQL database
4. **Data Analysis**: Uses LLM to analyze query results and provide insights
5. **Personalized Sessions**: Supports auto-generated and user-defined session IDs with persistence across restarts
6. **Safety**: Only allows SELECT queries to prevent data modification

## Conversation Workflow

- **Auto session (default)**: If you omit `session_id`, the API creates a fresh session ID and returns it in the response. Reuse that ID to continue the same thread; omit it again to start a new thread while still benefiting from cross-session recall.
- **Manual session override**: Provide your own `session_id` (e.g., user name or project code) to resume a persistent conversation, even after restarting the server.
- **Session reset**: Pass `reset_session: true` with a `session_id` to clear stored memory for that session and start over.
- **History inspection**: Use `GET /memory/sessions` and `GET /memory/<session_id>` to review stored context for debugging or auditing.

## Notes

- The system only executes SELECT queries for safety
- Make sure your Google API key has access to the Gemini Pro model
- The database connection is managed automatically
- All datetime objects are converted to ISO format strings in responses
- Conversational memory is persisted in `memory_store/` (ignored by git) so context survives restarts

## Troubleshooting

1. **Database Connection Error**: Check MySQL is running and credentials are correct
2. **API Key Error**: Verify your Google API key is set correctly
3. **Query Generation Error**: Check that your natural language query is clear and specific
4. **Import Error**: Make sure all dependencies are installed via `pip install -r requirements.txt`
5. **Memory Index Error**: Delete the `memory_store/` directory if the FAISS index becomes corrupted (a new store will be created automatically)


