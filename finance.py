from db import get_db

def add_transaction(user_id, t_type, amount, category, description=""):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO transactions (user_id, type, amount, category, description)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, t_type, amount, category, description)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_balance(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END),0) -
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END),0)
        FROM transactions
        WHERE user_id=%s
        """,
        (user_id,)
    )

    balance = cur.fetchone()[0]

    cur.close()
    conn.close()
    return balance

def calculate_tax(user_id, tax_rate=0.15):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE user_id=%s AND type='income'",
        (user_id,)
    )

    income = cur.fetchone()[0]
    cur.close()
    conn.close()

    return float(income) * tax_rate