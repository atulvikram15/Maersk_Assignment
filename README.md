# Natural Language to SQL Query System

This system allows users to query a MySQL database using natural language. It uses Google Generative AI to convert natural language queries into SQL, executes them, and provides analytical insights.

## Project Structure

- `backend.py`: Contains all backend helper functions for database operations and LLM interactions
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
    "query": "What are the top 10 customers by total order value?"
}
```

**Response:**
```json
{
    "sql_query": "SELECT ...",
    "data": [...],
    "analysis": "Based on the query results...",
    "row_count": 10
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

## Example Usage

### Using curl:

```bash
# Health check
curl http://localhost:5000/health

# Natural language query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the total revenue by product category"}'

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
2. **Query Execution**: Safely executes SQL queries against MySQL database
3. **Data Analysis**: Uses LLM to analyze query results and provide insights
4. **Error Handling**: Comprehensive error handling for database and LLM errors
5. **Safety**: Only allows SELECT queries to prevent data modification

## Notes

- The system only executes SELECT queries for safety
- Make sure your Google API key has access to the Gemini Pro model
- The database connection is managed automatically
- All datetime objects are converted to ISO format strings in responses

## Troubleshooting

1. **Database Connection Error**: Check MySQL is running and credentials are correct
2. **API Key Error**: Verify your Google API key is set correctly
3. **Query Generation Error**: Check that your natural language query is clear and specific
4. **Import Error**: Make sure all dependencies are installed via `pip install -r requirements.txt`


