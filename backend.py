"""
Backend module for Natural Language to SQL Query System
This module contains all the helper functions for database operations and LLM interactions.
"""

import os
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple, Any
import json
import re


class DatabaseConnection:
    """Handles MySQL database connection and operations."""
    
    def __init__(self, host: str = "localhost", port: int = 3306, 
                 database: str = "olist_db", user: str = "root", 
                 password: str = ""):
        """
        Initialize database connection parameters.
        
        Args:
            host: MySQL host
            port: MySQL port
            database: Database name
            user: MySQL username
            password: MySQL password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """
        Establish connection to MySQL database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query string
            
        Returns:
            Tuple of (results, error_message)
            results: List of dictionaries containing query results
            error_message: Error message if query fails
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None, "Database connection failed"
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            
            # Check if query is SELECT (has results) or INSERT/UPDATE/DELETE
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                # Convert datetime and other non-serializable objects to strings
                for row in results:
                    for key, value in row.items():
                        if hasattr(value, 'isoformat'):  # datetime objects
                            row[key] = value.isoformat()
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            row[key] = str(value)
                return results, None
            else:
                self.connection.commit()
                return [{"affected_rows": cursor.rowcount}], None
                
        except Error as e:
            return None, str(e)
        finally:
            if cursor:
                cursor.close()
    
    def get_schema_info(self) -> str:
        """
        Get database schema information for LLM context.
        
        Returns:
            str: Formatted schema information
        """
        schema_info = """
Database Schema for olist_db:

1. customers
   - customer_id (VARCHAR, PRIMARY KEY)
   - customer_unique_id (VARCHAR)
   - customer_zip_code_prefix (INT)
   - customer_city (VARCHAR)
   - customer_state (CHAR(2))

2. geolocation
   - geolocation_zip_code_prefix (INT)
   - geolocation_lat (DECIMAL)
   - geolocation_lng (DECIMAL)
   - geolocation_city (VARCHAR)
   - geolocation_state (CHAR(2))

3. sellers
   - seller_id (VARCHAR, PRIMARY KEY)
   - seller_zip_code_prefix (INT)
   - seller_city (VARCHAR)
   - seller_state (CHAR(2))

4. products
   - product_id (VARCHAR, PRIMARY KEY)
   - product_category_name (VARCHAR)
   - product_name_length (INT)
   - product_description_length (INT)
   - product_photos_qty (INT)
   - product_weight_g (INT)
   - product_length_cm (INT)
   - product_height_cm (INT)
   - product_width_cm (INT)

5. category_translation
   - product_category_name (VARCHAR, PRIMARY KEY)
   - product_category_name_english (VARCHAR)

6. orders
   - order_id (VARCHAR, PRIMARY KEY)
   - customer_id (VARCHAR, FOREIGN KEY -> customers.customer_id)
   - order_status (VARCHAR)
   - order_purchase_timestamp (DATETIME)
   - order_approved_at (DATETIME)
   - order_delivered_carrier_date (DATETIME)
   - order_delivered_customer_date (DATETIME)
   - order_estimated_delivery_date (DATETIME)

7. order_items
   - order_id (VARCHAR, FOREIGN KEY -> orders.order_id)
   - order_item_id (INT)
   - product_id (VARCHAR, FOREIGN KEY -> products.product_id)
   - seller_id (VARCHAR, FOREIGN KEY -> sellers.seller_id)
   - shipping_limit_date (DATETIME)
   - price (DECIMAL)
   - freight_value (DECIMAL)
   - PRIMARY KEY: (order_id, order_item_id)

8. order_payments
   - order_id (VARCHAR, FOREIGN KEY -> orders.order_id)
   - payment_sequential (INT)
   - payment_type (VARCHAR)
   - payment_installments (INT)
   - payment_value (DECIMAL)
   - PRIMARY KEY: (order_id, payment_sequential)

9. order_reviews
   - review_id (VARCHAR, PRIMARY KEY)
   - order_id (VARCHAR, FOREIGN KEY -> orders.order_id)
   - review_score (TINYINT)
   - review_comment_title (TEXT)
   - review_comment_message (TEXT)
   - review_creation_date (DATETIME)
   - review_answer_timestamp (DATETIME)
"""
        return schema_info


class LLMQueryGenerator:
    """Handles LLM interactions for SQL query generation."""
    
    def __init__(self, api_key: str):
        """
        Initialize Google Generative AI client.
        
        Args:
            api_key: Google Generative AI API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.schema_info = None
    
    def set_schema_info(self, schema_info: str):
        """Set database schema information."""
        self.schema_info = schema_info
    
    def generate_sql_query(self, natural_language_query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate SQL query from natural language using LLM.
        
        Args:
            natural_language_query: User's natural language query
            
        Returns:
            Tuple of (sql_query, error_message)
        """
        prompt = f"""You are a SQL query generator for a MySQL database. 
Given the following database schema and a natural language question, generate ONLY a valid MySQL SQL query.

Database Schema:
{self.schema_info}

Rules:
1. Generate ONLY the SQL query, no explanations or markdown formatting
2. Use proper JOINs when needed
3. Use appropriate WHERE clauses for filtering
4. Use aggregate functions (COUNT, SUM, AVG, etc.) when appropriate
5. Handle NULL values properly
6. Use proper table and column names from the schema
7. Return only SELECT queries (read-only operations)
8. Do not include any text before or after the SQL query
9. If the query requires grouping, use GROUP BY appropriately
10. Use LIMIT if the user asks for top N or limited results

Natural Language Query: {natural_language_query}

SQL Query:"""

        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up the SQL query - remove markdown code blocks if present
            sql_query = re.sub(r'```sql\n?', '', sql_query, flags=re.IGNORECASE)
            sql_query = re.sub(r'```\n?', '', sql_query)
            sql_query = sql_query.strip()
            
            # Check if query is empty
            if not sql_query:
                return None, "Generated SQL query is empty. Please rephrase your question."
            
            # Ensure it's a SELECT query for safety
            if not sql_query.upper().strip().startswith('SELECT'):
                return None, "Generated query is not a SELECT query. Only read operations are allowed."
            
            return sql_query, None
            
        except Exception as e:
            return None, f"Error generating SQL query: {str(e)}"
    
    def analyze_data(self, query: str, data: List[Dict], natural_language_query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Analyze query results using LLM and provide insights.
        
        Args:
            query: The SQL query that was executed
            data: Query results as list of dictionaries
            natural_language_query: Original natural language query
            
        Returns:
            Tuple of (analysis, error_message)
        """
        # Limit data size for LLM analysis (to avoid token limits)
        # If data is too large, analyze only the first 100 rows and provide summary
        max_rows_for_analysis = 100
        data_for_analysis = data[:max_rows_for_analysis] if len(data) > max_rows_for_analysis else data
        total_rows = len(data)
        
        # Convert data to JSON string for LLM
        data_str = json.dumps(data_for_analysis, indent=2)
        
        data_info = f"Total rows: {total_rows}" if total_rows > max_rows_for_analysis else f"Total rows: {total_rows}"
        if total_rows > max_rows_for_analysis:
            data_info += f" (showing first {max_rows_for_analysis} rows for analysis)"
        
        prompt = f"""You are an experienced data analyst. Analyze the following query results and provide meaningful insights.
        
{data_info}

Original Question: {natural_language_query}

SQL Query Executed: {query}

Query Results:
{data_str}

Please provide the below according to the original question:
1. A summary of the data
2. Key insights and trends
3. Any notable patterns or anomalies
4. Business implications if applicable
5. Recommendations based on the data

Format your response in a clear, structured manner. Be concise but informative."""

        try:
            response = self.model.generate_content(prompt)
            analysis = response.text.strip()
            return analysis, None
            
        except Exception as e:
            return None, f"Error analyzing data: {str(e)}"


class QueryProcessor:
    """Main class that orchestrates the query processing pipeline."""
    
    def __init__(self, db_config: Dict[str, Any], api_key: str):
        """
        Initialize QueryProcessor with database and LLM configurations.
        
        Args:
            db_config: Database configuration dictionary
            api_key: Google Generative AI API key
        """
        self.db = DatabaseConnection(**db_config)
        self.llm = LLMQueryGenerator(api_key)
        
        # Set schema info for LLM
        schema_info = self.db.get_schema_info()
        self.llm.set_schema_info(schema_info)
        
        # Connect to database
        self.db.connect()
    
    def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Process a natural language query end-to-end.
        
        Args:
            natural_language_query: User's natural language query
            
        Returns:
            Dictionary containing:
                - sql_query: Generated SQL query
                - data: Query results
                - analysis: LLM analysis of results
                - error: Error message if any
        """
        result = {
            "sql_query": None,
            "data": None,
            "analysis": None,
            "error": None
        }
        
        # Step 1: Generate SQL query from natural language
        sql_query, error = self.llm.generate_sql_query(natural_language_query)
        if error:
            result["error"] = error
            return result
        
        result["sql_query"] = sql_query
        
        # Step 2: Execute SQL query
        data, error = self.db.execute_query(sql_query)
        if error:
            result["error"] = f"SQL execution error: {error}"
            return result
        
        result["data"] = data
        
        # Step 3: Analyze data using LLM
        analysis, error = self.llm.analyze_data(sql_query, data, natural_language_query)
        if error:
            result["error"] = f"Analysis error: {error}"
            return result
        
        result["analysis"] = analysis
        
        return result
    
    def close(self):
        """Close database connection."""
        self.db.disconnect()


# Helper function to initialize QueryProcessor with environment variables
def create_query_processor() -> QueryProcessor:
    """
    Create and initialize QueryProcessor with configuration from environment variables.
    
    Environment Variables:
        - GOOGLE_API_KEY: Google Generative AI API key (required)
        - DB_HOST: MySQL host (default: localhost)
        - DB_PORT: MySQL port (default: 3306)
        - DB_NAME: Database name (default: olist_db)
        - DB_USER: MySQL username (default: root)
        - DB_PASSWORD: MySQL password (default: empty)
    
    Returns:
        QueryProcessor instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME", "olist_db"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "")
    }
    
    return QueryProcessor(db_config, api_key)

