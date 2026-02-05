from db import get_db
from finance import get_balance, calculate_tax
import datetime

def notify(user_id, message):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (user_id, message))
    conn.commit()
    cur.close()
    conn.close()

def get_notifications(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT message, created_at, read FROM notifications WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def generate_notifications(user_id, days_before_due=3, low_balance_threshold=1000):
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Debt Due Soon
    target_date = datetime.date.today() + datetime.timedelta(days=days_before_due)
    cur.execute("""
        SELECT title, due_date FROM debts 
        WHERE user_id=%s AND paid=FALSE AND due_date >= CURRENT_DATE AND due_date <= %s
    """, (user_id, target_date))
    soon_debts = cur.fetchall()
    
    for title, due_date in soon_debts:
        days = (due_date - datetime.date.today()).days
        notify(user_id, f"Debt '{title}' is due in {days} days.")

    # 2. Debt Overdue
    cur.execute("SELECT title FROM debts WHERE user_id=%s AND paid=FALSE AND due_date < CURRENT_DATE", (user_id,))
    overdue_debts = cur.fetchall()
    
    for (title,) in overdue_debts:
        notify(user_id, f"Debt '{title}' is overdue!")

    cur.close()
    conn.close()

    # 3. Low Balance
    balance = get_balance(user_id)
    if balance < low_balance_threshold:
        notify(user_id, f"Balance is low: KES {balance}")

    # 4. Tax Due
    tax = calculate_tax(user_id)
    if tax > 0:
        notify(user_id, f"Your estimated tax of KES {tax} is due.")