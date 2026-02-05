from auth import register, login
from finance import add_transaction, get_balance, calculate_tax
from debts import add_debt
from notifications import notify, get_notifications

email = "me@example.com"
password = "123456"

print(f"Registering {email}...")
register(email, password)

print(f"Logging in {email}...")
user_id = login(email, password)
print(f"User ID: {user_id}")

if user_id:
    add_transaction(user_id, "income", 5000, "Salary")
    add_transaction(user_id, "expense", 1200, "Rent")
    print("Balance:", get_balance(user_id))
    print("Tax:", calculate_tax(user_id))
    add_debt(user_id, "Friend loan", 300, "2026-02-20")
    notify(user_id, "You added a new debt")
    print("Notifications:", get_notifications(user_id))