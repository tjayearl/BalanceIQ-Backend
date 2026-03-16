from db import get_db

conn = get_db()
cur = conn.cursor()

cur.execute("SELECT id, email, name FROM users")
users = cur.fetchall()

print("Current users in database:")
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]}")

cur.close()
conn.close()