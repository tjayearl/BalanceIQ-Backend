from db import get_db

def add_debt(user_id, description, amount, due_date):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO debts (user_id, description, amount, due_date)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, description, amount, due_date)
    )

    conn.commit()
    cur.close()
    conn.close()

def mark_debt_paid(debt_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE debts SET paid=TRUE WHERE id=%s",
        (debt_id,)
    )

    conn.commit()
    cur.close()
    conn.close()