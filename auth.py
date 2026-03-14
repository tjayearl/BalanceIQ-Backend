import bcrypt
from db import get_db
import secrets
import datetime


def register(email, password, name="", country="US"):
    conn = get_db()
    cur = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    hashed_str = hashed.decode("utf-8")

    try:
        cur.execute(
            "INSERT INTO users (email, hashed_password, name, country) VALUES (%s, %s, %s, %s)",
            (email, hashed_str, name, country)
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

    # psycopg2 may return bytes, memoryview, or str depending on column type.
    # convert everything to bytes so bcrypt.checkpw works reliably.
    if isinstance(stored_hash, memoryview):
        stored_hash = stored_hash.tobytes()
    elif isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if bcrypt.checkpw(password.encode(), stored_hash):
        return user_id

    return None

def create_session(user_id, duration_hours=8):
    """Creates a new session for a user and returns a session token."""
    token = secrets.token_hex(16)
    expires_at = datetime.datetime.now() + datetime.timedelta(hours=duration_hours)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user_id, token, expires_at)
        )
        conn.commit()
        return token
    except Exception as e:
        conn.rollback()
        print(f"Session creation error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def validate_session(token):
    """Validates a session token and returns the user_id if valid."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT user_id FROM sessions WHERE token=%s AND expires_at > NOW()",
            (token,)
        )
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Session validation error: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def logout(token):
    """Deletes a session token to log a user out."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sessions WHERE token=%s", (token,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Logout error: {e}")
    finally:
        cur.close()
        conn.close()

def get_user_profile(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, email, name, country, work_type, currency, created_at FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return {
            "id": user[0],
            "email": user[1],
            "name": user[2],
            "country": user[3],
            "workType": user[4],
            "currency": user[5],
            "created_at": user[6]
        }
    return None