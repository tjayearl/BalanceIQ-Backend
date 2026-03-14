from db import get_db

def add_debt(user_id, title, amount, due_date, description=""):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO debts (user_id, title, amount, due_date, description) VALUES (%s, %s, %s, %s, %s)",
        (user_id, title, amount, due_date, description)
    )

    conn.commit()
    cur.close()
    conn.close()

def mark_debt_paid(user_id, debt_id):
    conn = get_db()
    cur = conn.cursor()

    # Check ownership
    cur.execute("SELECT id FROM debts WHERE id=%s AND user_id=%s", (debt_id, user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return False

    cur.execute(
        "UPDATE debts SET paid=TRUE WHERE id=%s AND user_id=%s",
        (debt_id, user_id)
    )

    conn.commit()
    cur.close()
    conn.close()
    return True

def list_debts(user_id, status=None):
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT id, title, description, amount, due_date, paid FROM debts WHERE user_id=%s"
    params = [user_id]
    if status == "paid":
        query += " AND paid=TRUE"
    elif status == "unpaid":
        query += " AND paid=FALSE"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def overdue_debts(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, amount, due_date FROM debts WHERE user_id=%s AND paid=FALSE AND due_date < NOW()", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows