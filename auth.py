import bcrypt
from db import get_db

def register(email, password):
    conn = get_db()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    hashed_str = hashed.decode("utf-8")

    try:
        cur.execute(
            "INSERT INTO users (email, hashed_password) VALUES (%s, %s)",
            (email, hashed_str)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Register error:", e)
        return False
    finally:
        cur.close()
        conn.close()

def login(email, password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, hashed_password FROM users WHERE email=%s",
        (email,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return None

    user_id, stored_hash = user

    # stored_hash is BYTEA, so we use it directly (tobytes() if it was memoryview, but psycopg2 usually returns bytes)
    if bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
        return user_id

    return None