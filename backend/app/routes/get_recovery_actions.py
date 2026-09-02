from app.database import SessionLocal
from app.models import RecoveryAction


def get_recovery_actions():
    db = SessionLocal()

    try:
        actions = (
            db.query(RecoveryAction)
            .order_by(RecoveryAction.created_at.desc())
            .all()
        )

        completed_actions = [
            action
            for action in actions
            if action.status == "succeeded"
        ]

        pending_actions = [
            action
            for action in actions
            if action.status == "sent"
        ]

        return {
            "all": actions,
            "completed": completed_actions,
            "pending": pending_actions,
            "counts": {
                "all": len(actions),
                "completed": len(completed_actions),
                "pending": len(pending_actions),
            }
        }

    finally:
        db.close()