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

def list_transactions(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, type, amount, category, description, created_at FROM transactions WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def edit_transaction(transaction_id, **kwargs):
    conn = get_db()
    cur = conn.cursor()

    allowed = {'type', 'amount', 'category', 'description'}
    updates = {k: v for k, v in kwargs.items() if k in allowed}

    if updates:
        query = "UPDATE transactions SET " + ", ".join(f"{k}=%s" for k in updates.keys()) + " WHERE id=%s"
        cur.execute(query, list(updates.values()) + [transaction_id])
        conn.commit()

    cur.close()
    conn.close()

def delete_transaction(transaction_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id=%s", (transaction_id,))
    conn.commit()
    cur.close()
    conn.close()