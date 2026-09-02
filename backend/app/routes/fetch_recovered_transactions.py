from app.database import SessionLocal
from app.models import RecoveryAction,RecoveredTransaction
def fetch_recovered_transactions():
    db = SessionLocal()
    try:
        
        recovered_transactions = db.query(RecoveredTransaction).all()
        return recovered_transactions
    finally:
        db.close()