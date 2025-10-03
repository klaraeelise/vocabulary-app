"""
Database utilities for safe and consistent database operations.
Provides reusable functions with error handling, validation, and transaction management.
"""
import mysql.connector
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def get_db_cursor(dictionary=True, commit=True):
    """
    Context manager for database operations with automatic cleanup and error handling.
    
    Args:
        dictionary: If True, returns rows as dictionaries
        commit: If True, commits the transaction on success
        
    Yields:
        tuple: (connection, cursor) objects
        
    Example:
        with get_db_cursor() as (db, cursor):
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
    """
    from database import get_connection
    
    db = None
    cursor = None
    
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=dictionary)
        yield db, cursor
        
        if commit:
            db.commit()
            
    except mysql.connector.Error as e:
        if db:
            db.rollback()
        logger.error(f"Database error: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Dictionary containing the data to validate
        required_fields: List of field names that must be present
        
    Raises:
        ValueError: If any required field is missing or empty
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] and data[field] != 0:  # Allow 0 but not empty strings
            empty_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    if empty_fields:
        raise ValueError(f"Empty required fields: {', '.join(empty_fields)}")


def check_duplicate(table: str, field: str, value: Any, exclude_id: Optional[int] = None) -> bool:
    """
    Check if a value already exists in a table.
    
    Args:
        table: Name of the table to check
        field: Name of the field to check
        value: Value to check for
        exclude_id: Optional ID to exclude from check (for updates)
        
    Returns:
        bool: True if duplicate exists, False otherwise
    """
    with get_db_cursor(commit=False) as (db, cursor):
        if exclude_id:
            cursor.execute(
                f"SELECT COUNT(*) as count FROM {table} WHERE {field} = %s AND id != %s",
                (value, exclude_id)
            )
        else:
            cursor.execute(
                f"SELECT COUNT(*) as count FROM {table} WHERE {field} = %s",
                (value,)
            )
        
        result = cursor.fetchone()
        return result['count'] > 0


def insert_record(table: str, data: Dict[str, Any]) -> int:
    """
    Insert a record into a table and return the ID.
    
    Args:
        table: Name of the table
        data: Dictionary of field names and values
        
    Returns:
        int: ID of the inserted record
        
    Raises:
        mysql.connector.Error: If insertion fails
    """
    fields = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    values = tuple(data.values())
    
    query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
    
    with get_db_cursor() as (db, cursor):
        cursor.execute(query, values)
        record_id = cursor.lastrowid
        logger.info(f"Inserted record into {table} with ID {record_id}")
        return record_id


def update_record(table: str, record_id: int, data: Dict[str, Any]) -> bool:
    """
    Update a record in a table.
    
    Args:
        table: Name of the table
        record_id: ID of the record to update
        data: Dictionary of field names and values to update
        
    Returns:
        bool: True if update was successful
        
    Raises:
        mysql.connector.Error: If update fails
    """
    set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
    values = tuple(data.values()) + (record_id,)
    
    query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
    
    with get_db_cursor() as (db, cursor):
        cursor.execute(query, values)
        rows_affected = cursor.rowcount
        logger.info(f"Updated record {record_id} in {table} ({rows_affected} rows)")
        return rows_affected > 0


def safe_fetch_one(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    """
    Safely fetch a single record with error handling.
    
    Args:
        query: SQL query to execute
        params: Optional tuple of query parameters
        
    Returns:
        Optional[Dict]: Record as dictionary, or None if not found
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            cursor.execute(query, params or ())
            return cursor.fetchone()
    except mysql.connector.Error as e:
        logger.error(f"Query failed: {e}")
        return None


def safe_fetch_all(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Safely fetch all records with error handling.
    
    Args:
        query: SQL query to execute
        params: Optional tuple of query parameters
        
    Returns:
        List[Dict]: List of records as dictionaries
    """
    try:
        with get_db_cursor(commit=False) as (db, cursor):
            cursor.execute(query, params or ())
            return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Query failed: {e}")
        return []
