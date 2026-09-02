from sqlalchemy import func
from app.models  import FailedTransaction, RecoveredTransaction, RecoveryAction
def fetch_info(db):
    failed_count = (
        db.query(func.count(FailedTransaction.id))
        .scalar()
    )

    failed_amount = (
        db.query(func.coalesce(func.sum(FailedTransaction.amount), 0))
        .scalar()
    )

    recovered_count = (
        db.query(func.count(RecoveredTransaction.id))
        .scalar()
    )
    action_count=(
        db.query(func.count(RecoveryAction.id))
        .scalar()
    )

    recovered_amount = (
        db.query(func.coalesce(func.sum(RecoveredTransaction.amount), 0))
        .scalar()
    )
    total_actions=(db.query(func.count(RecoveryAction.id)).scalar())
    recovery_rate=round((recovered_count)/action_count*100, 2) if action_count>0 else 0

    return {
        "failed_transactions": failed_count,
        "failed_amount": float(failed_amount),
        "recovered_transactions": recovered_count,
        "recovered_amount": float(recovered_amount),
        "recovery_rate": recovery_rate,
        "total_actions": total_actions
    }