
from app.models import FailedTransaction
def get_failed_transaction(db, failed_transaction_id):
    return (
        db.query(FailedTransaction)
        .filter(FailedTransaction.id == failed_transaction_id)
        .first()
    )