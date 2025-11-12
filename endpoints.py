"""
API Endpoints for Natural Language to SQL Query System
This module contains Flask endpoints that call backend helper functions.
"""

from flask import Flask, request, jsonify
from backend import create_query_processor, QueryProcessor
import os
from typing import Dict, Any

app = Flask(__name__)

# Global query processor instance
query_processor: QueryProcessor = None


def init_app():
    """Initialize the Flask application and create query processor."""
    global query_processor
    try:
        query_processor = create_query_processor()
        print("Query processor initialized successfully")
    except Exception as e:
        print(f"Error initializing query processor: {e}")
        query_processor = None


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "query_processor_initialized": query_processor is not None
    }), 200


@app.route('/query', methods=['POST'])
def process_natural_language_query():
    """
    Process a natural language query and return SQL results with analysis.
    
    Request Body:
        {
            "query": "natural language query string"
        }
    
    Returns:
        JSON response containing:
            - sql_query: Generated SQL query
            - data: Query results
            - analysis: LLM analysis of results
            - error: Error message if any
    """
    if not query_processor:
        return jsonify({
            "error": "Query processor not initialized. Please check configuration."
        }), 500
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400
        
        query = data.get('query')
        if not query:
            return jsonify({
                "error": "Query parameter is required in request body"
            }), 400
        
        # Process the query
        result = query_processor.process_query(query)
        
        # Check for errors
        if result.get("error"):
            return jsonify({
                "error": result["error"],
                "sql_query": result.get("sql_query")
            }), 400
        
        # Return success response
        return jsonify({
            "sql_query": result["sql_query"],
            "data": result["data"],
            "analysis": result["analysis"],
            "row_count": len(result["data"]) if result["data"] else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/query/sql', methods=['POST'])
def execute_sql_query():
    """
    Execute a raw SQL query directly (for testing/debugging).
    Note: Only SELECT queries are allowed for safety.
    
    Request Body:
        {
            "sql": "SELECT * FROM orders LIMIT 10"
        }
    
    Returns:
        JSON response containing query results
    """
    if not query_processor:
        return jsonify({
            "error": "Query processor not initialized. Please check configuration."
        }), 500
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Request body is required"
            }), 400
        
        sql_query = data.get('sql')
        if not sql_query:
            return jsonify({
                "error": "SQL parameter is required in request body"
            }), 400
        
        # Ensure it's a SELECT query for safety
        if not sql_query.strip().upper().startswith('SELECT'):
            return jsonify({
                "error": "Only SELECT queries are allowed"
            }), 400
        
        # Execute the query
        query_results, error = query_processor.db.execute_query(sql_query)
        
        if error:
            return jsonify({
                "error": error,
                "sql_query": sql_query
            }), 400
        
        # Return success response
        return jsonify({
            "sql_query": sql_query,
            "data": query_results,
            "row_count": len(query_results) if query_results else 0
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "POST /query",
            "POST /query/sql"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    # Initialize the application
    init_app()
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 5000))
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=True)


