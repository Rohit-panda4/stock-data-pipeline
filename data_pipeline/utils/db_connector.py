import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Create and return a MySQL database connection.
    
    Returns:
        connection: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        
        if connection.is_connected():
            print("✓ Successfully connected to MySQL database")
            return connection
            
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def close_db_connection(connection):
    """
    Close the database connection.
    
    Args:
        connection: MySQL connection object to close
    """
    if connection and connection.is_connected():
        connection.close()
        print("✓ MySQL connection closed")

def execute_query(connection, query, params=None):
    """
    Execute a SQL query (INSERT, UPDATE, DELETE).
    
    Args:
        connection: MySQL connection object
        query: SQL query string
        params: Tuple of parameters for the query
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print(f"✓ Query executed successfully: {cursor.rowcount} row(s) affected")
        cursor.close()
        return True
    except Error as e:
        print(f"✗ Error executing query: {e}")
        return False

def fetch_query(connection, query, params=None):
    """
    Fetch data from database (SELECT queries).
    
    Args:
        connection: MySQL connection object
        query: SQL SELECT query string
        params: Tuple of parameters for the query
        
    Returns:
        list: List of tuples containing query results, or empty list if error
    """
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Error as e:
        print(f"✗ Error fetching data: {e}")
        return []
