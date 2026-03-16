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

# Add missing columns to users table
conn = get_db()
cur = conn.cursor()

try:
    # Add work_type column if it doesn't exist
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS work_type TEXT
    """)
    
    # Add currency column if it doesn't exist (though it should)
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'USD'
    """)
    
    # Add country column if it doesn't exist
    cur.execute("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS country TEXT DEFAULT 'US'
    """)
    
    conn.commit()
    print("Database migration completed successfully")
    
except Exception as e:
    print(f"Migration failed: {e}")
    conn.rollback()
    
finally:
    cur.close()
    conn.close()