from app.database import (
    SessionLocal,
)
from app.models import (
    FailedTransaction,
    RecoveryAction,
)
from datetime import datetime
def send_recovery_reminder(
    db,
    failed_transaction_id,
    decision
):

    failed_txn = (
        db.query(FailedTransaction)
        .filter(
            FailedTransaction.id == failed_transaction_id
        )
        .first()
    )

    if not failed_txn:
        raise ValueError(
            "Failed transaction not found"
        )

    recovery_action = RecoveryAction(

        failed_transaction_id=failed_txn.id,

        action_type="reminder",

        decision_reason=decision["reason"],

        recovery_probability=(
            decision["recovery_probability"]
        ),

        confidence=decision["confidence"],

        status="sent",

        result=decision["message"],

        executed_at=datetime.utcnow(),

        completed_at=datetime.utcnow()
    )

    existing_action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.failed_transaction_id == failed_txn.id
            )
            .first()
        )
    
    if not existing_action:
        db.add(recovery_action)

        db.commit()

    return {
        "action": "REMINDER",
        "status": "sent",
        "reason": decision["reason"],
        "message": decision["message"]
    }