from db import get_db

def notify(user_id, message):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
        (user_id, message)
    )

    conn.commit()
    cur.close()
    conn.close()

def get_notifications(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, message, read FROM notifications WHERE user_id=%s",
        (user_id,)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows