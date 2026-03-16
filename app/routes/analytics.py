from fastapi import APIRouter, Depends
from db import get_db
from typing import Dict

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/users/count")
async def get_user_count(db=Depends(get_db)) -> Dict[str, int]:
    """
    Get the total number of registered users.
    """
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    cur.close()
    return {"total_users": count}

@router.get("/transactions/count")
async def get_transaction_count(db=Depends(get_db)) -> Dict[str, int]:
    """
    Get the total number of transactions.
    """
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions")
    count = cur.fetchone()[0]
    cur.close()
    return {"total_transactions": count}

@router.get("/transactions/summary")
async def get_transaction_summary(db=Depends(get_db)) -> Dict[str, float]:
    """
    Get summary of total income and expenses.
    """
    cur = db.cursor()
    cur.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expenses
        FROM transactions
    """)
    result = cur.fetchone()
    cur.close()
    return {
        "total_income": float(result[0]),
        "total_expenses": float(result[1]),
        "net": float(result[0] - result[1])
    }
