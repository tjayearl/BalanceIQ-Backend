from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, timedelta
import re

# helper dependency to extract and validate bearer token

def require_user_id(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split()[1]
    user_id = validate_session(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id

# Import your existing backend functions
from auth import register as auth_register, login as auth_login, create_session, validate_session, logout, get_user_profile
from finance import (
    add_transaction, get_balance, calculate_tax, list_transactions, 
    edit_transaction, delete_transaction, get_monthly_summary, 
    get_weekly_summary, get_yearly_summary, get_spending_by_category, 
    get_income_vs_expense
)
from db import get_db
from debts import add_debt, mark_debt_paid, list_debts, overdue_debts
from notifications import notify, get_notifications, generate_notifications
from app.routes.analytics import router as analytics_router

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

app.include_router(analytics_router)

# -------------------------
# Pydantic models
# -------------------------
class UserRegister(BaseModel):
    full_name: str = Field(alias='fullName')
    email: str
    password: str

    class Config:
        populate_by_name = True

    @validator('full_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not v or not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

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
    name: str
    lender: Optional[str] = ""
    amount: float
    due_date: str       # "YYYY-MM-DD"
    interest_rate: Optional[float] = 0

# Onboarding data models
class IncomeSource(BaseModel):
    source: Optional[str] = ""
    type: Optional[str] = ""
    amount: float

class ExpenseItem(BaseModel):
    description: Optional[str] = ""
    category: str
    amount: float

class DebtItem(BaseModel):
    name: str
    lender: Optional[str] = ""
    amount: float
    dueDate: Optional[str] = ""
    interestRate: Optional[float] = 0.0

class OnboardingData(BaseModel):
    workType: str
    currency: str
    country: Optional[str] = "US"
    incomes: List[IncomeSource] = []
    expenses: List[ExpenseItem] = []
    debts: List[DebtItem] = []

# -------------------------
# Phase 1: Auth Endpoints
# -------------------------
@app.post("/auth/register")
async def register_user(user: UserRegister):
    # Register a new user with full name
    success = auth_register(user.email.lower(), user.password, user.full_name)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed. Email may already be registered.")

    # Create a session token for the new user
    user_id = auth_login(user.email.lower(), user.password)
    token = create_session(user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "message": "Registration successful"
    }

@app.post("/auth/login")
async def login_user(user: UserLogin):
    user_id = auth_login(user.email.lower(), user.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_session(user_id)
    return {"access_token": token, "user_id": user_id, "token_type": "bearer"}

@app.post("/auth/logout")
def logout_user(user_id: int = Depends(require_user_id), authorization: str = Header(None)):
    # extract token again from header and remove session
    token = authorization.split()[1]
    logout(token)
    return {"message": "Logged out successfully"}

@app.get("/auth/profile")
async def get_user_profile(user_id: int = Depends(require_user_id)):
    """Get user profile"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, full_name, name, work_type, currency, country, created_at
        FROM users 
        WHERE id = %s
    """, (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    full_name = user[2] or user[3] or ""
    return {
        "id": user[0],
        "fullName": full_name,
        "email": user[1],
        "workType": user[4] or "Self-Employed",
        "currency": user[5] or "USD",
        "country": user[6] or "USA",
        "createdAt": str(user[7])
    }

@app.post("/auth/onboarding")
async def complete_onboarding(
    data: OnboardingData, 
    user_id: int = Depends(require_user_id)
):
    """Save user's onboarding preferences and initial data"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Update user profile with preferences
        cur.execute("""
            UPDATE users 
            SET work_type = %s, currency = %s, country = %s
            WHERE id = %s
        """, (data.workType, data.currency, data.country or "US", user_id))
        
        # Add initial income transactions
        for income in data.incomes:
            if income.amount > 0:
                cur.execute("""
                    INSERT INTO transactions (user_id, type, amount, category, description)
                    VALUES (%s, 'income', %s, %s, %s)
                """, (user_id, income.amount, income.type or "Other", income.source or "Income"))
        
        # Add initial expense transactions
        for expense in data.expenses:
            if expense.amount > 0:
                cur.execute("""
                    INSERT INTO transactions (user_id, type, amount, category, description)
                    VALUES (%s, 'expense', %s, %s, %s)
                """, (user_id, expense.amount, expense.category, expense.description or "Expense"))
        
        # Add initial debts
        for debt in data.debts:
            if debt.amount > 0:
                cur.execute("""
                    INSERT INTO debts (user_id, name, lender, amount, due_date, interest_rate, paid)
                    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                """, (user_id, debt.name, debt.lender or "", debt.amount, debt.dueDate or None, debt.interestRate or 0.0))
        
        conn.commit()
        
        return {
            "message": "Onboarding completed successfully",
            "user_id": user_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Onboarding failed: {str(e)}")
    finally:
        cur.close()
        conn.close()

# -------------------------
# Phase 1: Transactions Endpoints
# -------------------------
@app.post("/transactions")
def create_transaction(tx: TransactionCreate, user_id: int = Depends(require_user_id)):
    add_transaction(user_id, tx.type, tx.amount, tx.category, tx.description)
    return {"message": "Transaction added"}

@app.get("/transactions")
def get_transactions(user_id: int = Depends(require_user_id)):
    return list_transactions(user_id)

@app.put("/transactions/{tx_id}")
def update_transaction(tx_id: int, tx: TransactionEdit, user_id: int = Depends(require_user_id)):
    success = edit_transaction(user_id, tx_id, amount=tx.amount, category=tx.category, description=tx.description)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")
    return {"message": "Transaction updated"}

@app.delete("/transactions/{tx_id}")
def remove_transaction(tx_id: int, user_id: int = Depends(require_user_id)):
    success = delete_transaction(user_id, tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found or not owned by user")
    return {"message": "Transaction deleted"}

# -------------------------
# Phase 1: Debts Endpoints
# -------------------------
@app.post("/debts")
def create_debt(debt: DebtCreate, user_id: int = Depends(require_user_id)):
    add_debt(user_id, debt.name, debt.amount, debt.due_date, debt.lender, debt.interest_rate or 0)
    return {"message": "Debt added"}

@app.get("/debts")
def get_user_debts(user_id: int = Depends(require_user_id), status: Optional[str] = "unpaid"):
    return list_debts(user_id, status)

@app.put("/debts/{debt_id}/pay")
def pay_debt(debt_id: int, user_id: int = Depends(require_user_id)):
    success = mark_debt_paid(user_id, debt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Debt not found or not owned by user")
    return {"message": "Debt marked as paid"}

@app.get("/debts/overdue")
def get_overdue_debts(user_id: int = Depends(require_user_id)):
    return overdue_debts(user_id)

# -------------------------
# Tax Calculator Endpoint
# -------------------------
@app.post("/tax/calculate")
def calculate_tax_endpoint(user_id: int = Depends(require_user_id)):
    """Calculate estimated tax for the user"""
    tax_owed = calculate_tax(user_id)
    balance = get_balance(user_id)
    
    return {
        "tax_owed": tax_owed,
        "balance": balance,
        "user_id": user_id
    }

# -------------------------
# Phase 2: Reports & Notifications
# -------------------------
@app.get("/notifications")
def notifications(user_id: int = Depends(require_user_id)):
    generate_notifications(user_id)
    return get_notifications(user_id)

@app.get("/reports/monthly")
def monthly_report(month: str, user_id: int = Depends(require_user_id)):
    return get_monthly_summary(user_id, month)

@app.get("/reports/weekly")
def weekly_report(week_start: str, user_id: int = Depends(require_user_id)):
    return get_weekly_summary(user_id, week_start)

@app.get("/reports/yearly")
def yearly_report(year: str, user_id: int = Depends(require_user_id)):
    return get_yearly_summary(user_id, year)

@app.get("/reports/spending")
def spending_report(month: str, user_id: int = Depends(require_user_id)):
    return get_spending_by_category(user_id, month)

@app.get("/reports/income-expense")
def income_vs_expense_report(month: str, user_id: int = Depends(require_user_id)):
    return get_income_vs_expense(user_id, month)

# -------------------------
# Dashboard & Settings
# -------------------------
@app.get("/dashboard")
def get_dashboard(user_id: int = Depends(require_user_id)):
    balance = get_balance(user_id)
    tax_owed = calculate_tax(user_id)
    recent_transactions = list_transactions(user_id)[:5]  # Last 5 transactions
    return {
        "balance": balance,
        "tax_owed": tax_owed,
        "recent_transactions": recent_transactions
    }

@app.put("/settings/profile")
def update_profile(updates: dict, user_id: int = Depends(require_user_id)):
    # Allow updating name and country
    allowed_fields = {'name', 'country'}
    updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not updates:
        return {"message": "No valid fields to update"}
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        query = "UPDATE users SET " + ", ".join(f"{k}=%s" for k in updates.keys()) + " WHERE id=%s"
        cur.execute(query, list(updates.values()) + [user_id])
        conn.commit()
        return {"message": "Profile updated"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Update failed")
    finally:
        cur.close()
        conn.close()

@app.post("/onboarding/complete")
def complete_onboarding(user_id: int = Depends(require_user_id)):
    # Mark onboarding as complete (could add a field to users table)
    # For now, just return success
    return {"message": "Onboarding completed"}

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def root():
    return {"message": "BalanceIQ API is running!"}