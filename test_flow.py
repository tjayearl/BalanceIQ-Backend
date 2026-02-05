from auth import register, login
from finance import add_transaction, get_balance, calculate_tax, get_monthly_summary, get_spending_by_category, get_weekly_summary, get_yearly_summary, get_income_vs_expense
from debts import add_debt
from notifications import notify, get_notifications, generate_notifications

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
    
    print("Generating automatic notifications...")
    generate_notifications(user_id)
    print("Notifications:", get_notifications(user_id))

    print("Monthly Summary (2026-02):", get_monthly_summary(user_id, "2026-02"))
    print("Spending by Category (2026-02):", get_spending_by_category(user_id, "2026-02"))
    print("Weekly Summary (start 2026-02-01):", get_weekly_summary(user_id, "2026-02-01"))
    print("Yearly Summary (2026):", get_yearly_summary(user_id, "2026"))
    print("Income vs Expense (2026-02):", get_income_vs_expense(user_id, "2026-02"))