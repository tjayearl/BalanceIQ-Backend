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

def get_monthly_summary(user_id, month):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
        FROM transactions 
        WHERE user_id=%s AND to_char(created_at, 'YYYY-MM') = %s
    """, (user_id, month))
    income, expense = cur.fetchone()
    
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM debts WHERE user_id=%s AND to_char(due_date, 'YYYY-MM') = %s", (user_id, month))
    debts = cur.fetchone()[0]
    
    cur.close(); conn.close()
    return {"income": float(income), "expense": float(expense), "net_flow": float(income - expense), "debts_due": float(debts)}

def get_weekly_summary(user_id, week_start):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
        FROM transactions 
        WHERE user_id=%s AND created_at >= %s::date AND created_at < %s::date + interval '7 days'
    """, (user_id, week_start, week_start))
    income, expense = cur.fetchone()
    
    cur.close(); conn.close()
    return {"income": float(income), "expense": float(expense), "net_flow": float(income - expense)}

def get_yearly_summary(user_id, year):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
        FROM transactions 
        WHERE user_id=%s AND to_char(created_at, 'YYYY') = %s
    """, (user_id, year))
    income, expense = cur.fetchone()
    
    cur.close(); conn.close()
    return {"income": float(income), "expense": float(expense), "net_flow": float(income - expense)}

def get_spending_by_category(user_id, month):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT category, SUM(amount) FROM transactions 
        WHERE user_id=%s AND type='expense' AND to_char(created_at, 'YYYY-MM') = %s
        GROUP BY category
    """, (user_id, month))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return {row[0]: float(row[1]) for row in rows}

def get_income_vs_expense(user_id, month):
    summary = get_monthly_summary(user_id, month)
    return {"income": summary["income"], "expense": summary["expense"]}