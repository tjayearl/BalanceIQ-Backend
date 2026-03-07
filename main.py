from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

# Import your existing backend functions
from auth import register as auth_register, login as auth_login, create_session, validate_session, logout
from finance import (
    add_transaction, get_balance, calculate_tax, list_transactions, 
    edit_transaction, delete_transaction, get_monthly_summary, 
    get_weekly_summary, get_yearly_summary, get_spending_by_category, 
    get_income_vs_expense
)
from debts import add_debt, mark_debt_paid, list_debts, overdue_debts
from notifications import notify, get_notifications, generate_notifications

# -------------------------
# FastAPI app initialization
# -------------------------
app = FastAPI(title="BalanceIQ API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://balance-iq-gamma.vercel.app",
        "https://balanceiq-backend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Pydantic models
# -------------------------
class UserRegister(BaseModel):
    name: Optional[str] = ""
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TransactionCreate(BaseModel):
    type: str           # income / expense
    amount: float
    category: str
    description: Optional[str] = ""

class TransactionEdit(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None

class DebtCreate(BaseModel):
    description: str
    amount: float
    due_date: str       # "YYYY-MM-DD"

# -------------------------
# Phase 1: Auth Endpoints
# -------------------------
@app.post("/auth/register")
def register(user: UserRegister):
    success = auth_register(user.email, user.password, user.name)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed. Email may already be registered.")
    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login(user: UserLogin):
    user_id = auth_login(user.email, user.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_session(user_id)
    return {"access_token": token, "user_id": user_id, "token_type": "bearer"}

@app.post("/auth/logout")
def logout_user(token: str):
    logout(token)
    return {"message": "Logged out successfully"}

# -------------------------
# Phase 1: Transactions Endpoints
# -------------------------
@app.post("/transactions")
def create_transaction(user_id: int, tx: TransactionCreate):
    add_transaction(user_id, tx.type, tx.amount, tx.category, tx.description)
    return {"message": "Transaction added"}

@app.get("/transactions")
def get_transactions(user_id: int):
    return list_transactions(user_id)

@app.put("/transactions/{tx_id}")
def update_transaction(tx_id: int, tx: TransactionEdit):
    edit_transaction(tx_id, amount=tx.amount, category=tx.category, description=tx.description)
    return {"message": "Transaction updated"}

@app.delete("/transactions/{tx_id}")
def remove_transaction(tx_id: int):
    delete_transaction(tx_id)
    return {"message": "Transaction deleted"}

# -------------------------
# Phase 1: Debts Endpoints
# -------------------------
@app.post("/debts")
def create_debt(user_id: int, debt: DebtCreate):
    add_debt(user_id, debt.description, debt.amount, debt.due_date)
    return {"message": "Debt added"}

@app.get("/debts")
def get_user_debts(user_id: int, status: Optional[str] = "unpaid"):
    return list_debts(user_id, status)

@app.put("/debts/{debt_id}/pay")
def pay_debt(debt_id: int):
    mark_debt_paid(debt_id)
    return {"message": "Debt marked as paid"}

@app.get("/debts/overdue")
def get_overdue_debts(user_id: int):
    return overdue_debts(user_id)

# -------------------------
# Phase 2: Reports & Notifications
# -------------------------
@app.get("/notifications")
def notifications(user_id: int):
    generate_notifications(user_id)
    return get_notifications(user_id)

@app.get("/reports/monthly")
def monthly_report(user_id: int, month: str):
    return get_monthly_summary(user_id, month)

@app.get("/reports/weekly")
def weekly_report(user_id: int, week_start: str):
    return get_weekly_summary(user_id, week_start)

@app.get("/reports/yearly")
def yearly_report(user_id: int, year: str):
    return get_yearly_summary(user_id, year)

@app.get("/reports/spending")
def spending_report(user_id: int, month: str):
    return get_spending_by_category(user_id, month)

@app.get("/reports/income-expense")
def income_vs_expense_report(user_id: int, month: str):
    return get_income_vs_expense(user_id, month)

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def root():
    return {"message": "BalanceIQ API is running!"}