from app.database import (
    SessionLocal,
)
from app.models import (
    FailedTransaction,
    RecoveryAction,
)
from datetime import datetime
def escalate_to_human(
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

        action_type="human_review",

        decision_reason=decision["reason"],

        recovery_probability=(
            decision["recovery_probability"]
        ),

        confidence=decision["confidence"],

        status="executed",

        result=decision["message"],

        executed_at=datetime.utcnow(),

        completed_at=datetime.utcnow(),
        attempts=1,
        attempt_limit=1,
    )

    db.add(recovery_action)

    failed_txn.recovery_status = "action_required"

    failed_txn.updated_at = datetime.utcnow()

    db.commit()

    return {
        "action": "ESCALATE_HUMAN",
        "status": "human_review_required",
        "reason": decision["reason"],
        "message": decision["message"]
    }