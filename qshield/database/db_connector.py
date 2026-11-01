"""
db_connector.py
MySQL connection manager for Q-SHIELD.
Uses mysql-connector-python with connection pooling.
"""

import mysql.connector
from mysql.connector import pooling
from config import config


# Create a connection pool (reuses connections for performance)
_pool = None


def _create_pool():
    """Initialize the MySQL connection pool."""
    global _pool
    if _pool is None:
        db_config = config.db_config
        _pool = pooling.MySQLConnectionPool(
            pool_name="qshield_pool",
            pool_size=5,
            pool_reset_session=True,
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        )
    return _pool


def get_db():
    """
    Get a MySQL connection from the pool.
    
    Returns:
        mysql.connector.connection.MySQLConnection
    """
    pool = _create_pool()
    return pool.get_connection()


def init_db():
    """
    Initialize the database by executing schema.sql.
    Call this once at application startup.
    """
    import os

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.exists(schema_path):
        print("Warning: schema.sql not found.")
        return

    with open(schema_path, "r") as f:
        sql = f.read()

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Execute each statement separately
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
        print("Database initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
    finally:
        cursor.close()
        conn.close()