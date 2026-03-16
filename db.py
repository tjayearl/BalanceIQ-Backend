import psycopg2
import os

def get_db():
    """
    Returns a fresh database connection with autocommit enabled.
    This prevents transaction isolation issues that cause phantom reads.
    """
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # Fix: Render uses postgres:// but psycopg2 needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(database_url, sslmode="require")
    else:
        conn = psycopg2.connect(
            dbname="balanceiq",
            user="balanceuser",
            password="balancepass",
            host="localhost"
        )
    
    # CRITICAL: Enable autocommit
    # Without this, each connection starts a transaction automatically,
    # and SELECT queries may see stale data from before the transaction started
    conn.autocommit = True
    
    return conn