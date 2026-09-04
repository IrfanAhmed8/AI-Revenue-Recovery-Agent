from datetime import datetime

from app.get_failed_transaction import get_failed_transaction
from app.get_customer_context import get_customer_context
from app.execute_recovery_action import execute_recovery_action
from app.calculate_customer_risk import calculate_customer_risk
from app.build_context import build_ai_context
from app.get_ai_decision import get_ai_decision
from app.database import SessionLocal
from app.models import RecoveryAction


def run_recovery(failed_transaction_id: str):

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # 1. Get failed transaction
        # --------------------------------------------------

        failed_txn = get_failed_transaction(
            db,
            failed_transaction_id
        )

        if not failed_txn:
            return {
                "status": "failed",
                "reason": "failed_transaction_not_found"
            }

        # --------------------------------------------------
        # 2. Check for an existing recovery action
        # --------------------------------------------------

        existing_action = (
            db.query(RecoveryAction)
            .filter(
                RecoveryAction.failed_transaction_id
                == failed_transaction_id
            )
            .order_by(
                RecoveryAction.created_at.desc()
            )
            .first()
        )

        # ==================================================
        # EXISTING RECOVERY ACTION
        # ==================================================

        if existing_action:

            print(
                f"Existing recovery action found: "
                f"{existing_action.id}"
            )

            print(
                f"Current attempts: "
                f"{existing_action.attempts}/"
                f"{existing_action.attempt_limit}"
            )

            # --------------------------------------------------
            # Check attempt limit
            # --------------------------------------------------

            if (
                existing_action.attempts
                >= existing_action.attempt_limit
            ):

                print(
                    "Attempt limit reached. "
                    "No further recovery action."
                )

                return {
                    "status": "stopped",
                    "reason": "attempt_limit_reached",
                    "recovery_action_id": str(
                        existing_action.id
                    ),
                    "attempts": existing_action.attempts,
                    "attempt_limit":
                        existing_action.attempt_limit
                }

            # --------------------------------------------------
            # Increment attempt
            # --------------------------------------------------

            existing_action.attempts += 1

            print(
                f"Executing recovery retry: "
                f"{existing_action.attempts}/"
                f"{existing_action.attempt_limit}"
            )

            # --------------------------------------------------
            # Reuse the ORIGINAL AI decision
            # --------------------------------------------------

            decision = {
                "action": existing_action.action_type,
                "recovery_probability":
                    existing_action.recovery_probability,
                "confidence":
                    existing_action.confidence,
                "reason":
                    existing_action.decision_reason,
                "message":
                    existing_action.result
            }

            # --------------------------------------------------
            # Execute existing action
            # --------------------------------------------------

            result = execute_recovery_action(
                decision,
                failed_transaction_id
            )

            # --------------------------------------------------
            # Update recovery action
            # --------------------------------------------------

            existing_action.executed_at = datetime.utcnow()

            db.commit()

            return result

        # ==================================================
        # NEW RECOVERY ACTION
        # ==================================================

        print(
            "No existing recovery action found."
        )

        # --------------------------------------------------
        # 3. Get customer context
        # --------------------------------------------------

        customer = get_customer_context(
            db,
            failed_txn.customer_id
        )

        # --------------------------------------------------
        # 4. Calculate customer risk
        # --------------------------------------------------

        risk = calculate_customer_risk(customer)

        print(
            f"Calculated risk for customer "
            f"{customer['name']} "
            f"(ID: {failed_txn.customer_id}): "
            f"{risk}"
        )

        # --------------------------------------------------
        # 5. Build AI context
        # --------------------------------------------------

        ai_context = build_ai_context(
            failed_txn,
            customer,
            risk
        )

        print(
            f"Built AI context for failed transaction "
            f"{failed_transaction_id}: "
            f"{ai_context}"
        )

        # --------------------------------------------------
        # 6. Get AI decision
        # --------------------------------------------------

        decision = get_ai_decision(ai_context)

        print(
            f"Made AI decision for failed transaction "
            f"{failed_transaction_id}: "
            f"{decision}"
        )

        # --------------------------------------------------
        # 7. Execute new action
        # --------------------------------------------------
        
        result = execute_recovery_action(
            decision,
            failed_transaction_id
        )

        # --------------------------------------------------
        # 8. Save recovery action
        # --------------------------------------------------

        recovery_action = RecoveryAction(

            failed_transaction_id=failed_txn.id,

            action_type=decision["action"],

            decision_reason=decision["reason"],

            recovery_probability=(
                decision["recovery_probability"]
            ),

            confidence=decision["confidence"],

            status="executed",

            result=decision["message"],

            attempts=1,

            attempt_limit=3,

            executed_at=datetime.utcnow(),

            completed_at=datetime.utcnow()
        )

        db.add(recovery_action)

        db.commit()

        db.refresh(recovery_action)

        print(
            f"Created recovery action: "
            f"{recovery_action.id}"
        )

        return result

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()