import psycopg2
import os

def get_db():
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # Fix: Render uses postgres:// but psycopg2 needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(database_url, sslmode="require")
    else:
        return psycopg2.connect(
            dbname="balanceiq",
            user="balanceuser",
            password="balancepass",
            host="localhost"
        )