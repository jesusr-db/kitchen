"""Database connectivity for Databricks SQL."""

import logging
from contextlib import contextmanager
from typing import Generator
from databricks import sql
from databricks.sql.client import Connection, Cursor

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages Databricks SQL connections with pooling."""
    
    def __init__(self):
        self._connection: Connection | None = None
    
    def _create_connection(self) -> Connection:
        """Create a new Databricks SQL connection."""
        if not settings.databricks_host or not settings.databricks_http_path:
            raise ValueError(
                "Databricks connection parameters not configured. "
                "Set DATABRICKS_HOST and DATABRICKS_HTTP_PATH environment variables."
            )
        
        logger.info(f"Creating connection to Databricks: {settings.databricks_host}")
        
        return sql.connect(
            server_hostname=settings.databricks_host,
            http_path=settings.databricks_http_path,
            access_token=settings.databricks_token,
        )
    
    def get_connection(self) -> Connection:
        """Get or create database connection."""
        if self._connection is None or not self._is_connection_alive():
            logger.info("Establishing new database connection")
            self._connection = self._create_connection()
        return self._connection
    
    def _is_connection_alive(self) -> bool:
        """Check if connection is still alive."""
        if self._connection is None:
            return False
        try:
            # Try a simple query to test connection
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.warning(f"Connection check failed: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            logger.info("Closing database connection")
            self._connection.close()
            self._connection = None


# Global connection instance
_db_connection = DatabaseConnection()


@contextmanager
def get_cursor() -> Generator[Cursor, None, None]:
    """
    Context manager for database cursor.
    
    Usage:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    """
    connection = _db_connection.get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


def execute_query(query: str, parameters: dict | None = None) -> list[dict]:
    """
    Execute a SQL query and return results as list of dictionaries.
    
    Args:
        query: SQL query string
        parameters: Optional parameters for parameterized query
    
    Returns:
        List of dictionaries with column names as keys
    """
    with get_cursor() as cursor:
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows and convert to dicts
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def close_connection():
    """Close the global database connection."""
    _db_connection.close()
