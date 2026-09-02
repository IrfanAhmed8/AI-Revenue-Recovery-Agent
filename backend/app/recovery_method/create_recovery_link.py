import os
import uuid

from datetime import datetime, timezone

from fastapi import HTTPException
from razorpay import Client

from app.database import SessionLocal

from app.models import (
    FailedTransaction,
    Customer,
    RecoveryAction
)


# --------------------------------------------------
# Razorpay client
# --------------------------------------------------

client = Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)


def create_payment_link_recovery(
    failed_transaction_id: str,
    ai_decision: dict
):

    db = SessionLocal()

    try:

        # ==================================================
        # 1. Find failed transaction
        # ==================================================

        failed_txn = (
    db.query(FailedTransaction)
    .filter(
        FailedTransaction.id == failed_transaction_id,
        FailedTransaction.recovery_status.in_([
            "pending",
            "action_required"
        ])
    )
    .first()
)

        if not failed_txn:
            raise HTTPException(
                status_code=404,
                detail="Pending failed transaction not found"
            )


        # ==================================================
        # 2. Find customer
        # ==================================================

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == failed_txn.customer_id
            )
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )


        # ==================================================
        # 3. Extract AI decision
        # ==================================================

        action = ai_decision.get("action")

        reason = ai_decision.get(
            "reason",
            "AI recommended a payment link recovery."
        )

        message = ai_decision.get(
            "message",
            "Please try completing your payment again."
        )

        recovery_probability = ai_decision.get(
            "recovery_probability"
        )

        confidence = ai_decision.get(
            "confidence"
        )


        # ==================================================
        # 4. Safety check
        # ==================================================

        if action != "PAYMENT_LINK" and action != "payment_link":

            raise ValueError(
                f"Invalid action for payment link recovery: {action}"
            )


        # ==================================================
        # 5. Generate Razorpay reference ID
        # ==================================================

        # Razorpay reference_id must be <= 40 characters

        reference_id = (
            f"REC_{uuid.uuid4().hex[:20]}"
        )


        # Example:
        #
        # REC_5efbe58569754217a755
        #
        # Length = 24 characters


        # ==================================================
        # 6. Create Razorpay Payment Link
        # ==================================================

        payment_link = client.payment_link.create({

            "amount": int(failed_txn.amount),

            "currency": failed_txn.currency,

            "description": (
                "Retry payment for failed transaction"
            ),

            "reference_id": reference_id,

            "customer": {
                "name": customer.name,
                "email": customer.email,
                "contact": customer.phone
            },

            "notify": {
                "sms": True,
                "email": True
            },

            "reminder_enable": True
        })


        # ==================================================
        # 7. Create RecoveryAction
        # ==================================================

        recovery_action = RecoveryAction(

            failed_transaction_id=failed_txn.id,

            action_type="payment_link",

            decision_reason=reason,

            recovery_probability=(
                recovery_probability
            ),

            confidence=confidence,

            status="sent",

            razorpay_reference_id=reference_id,

            razorpay_payment_link_id=(
                payment_link["id"]
            ),

            executed_at=datetime.now(timezone.utc),

            result=message,

            metadata_json={
                "ai_action": action,
                "ai_reason": reason,
                "customer_message": message
            }
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


        # ==================================================
        # 8. Update failed transaction
        # ==================================================

        failed_txn.recovery_status = (
            "action_required"
        )

        failed_txn.attempt_count = (
            failed_txn.attempt_count + 1
        )

        failed_txn.updated_at = (
            datetime.now(timezone.utc)
        )


        # ==================================================
        # 9. Commit everything
        # ==================================================

        db.commit()

        db.refresh(recovery_action)


        # ==================================================
        # 10. Return result
        # ==================================================

        return {

            "success": True,

            "action": "PAYMENT_LINK",

            "failed_transaction_id":
                str(failed_txn.id),

            "customer": {
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone
            },

            "amount":
                failed_txn.amount,

            "currency":
                failed_txn.currency,

            "failure_reason":
                failed_txn.error_reason,

            "recovery_probability":
                recovery_probability,

            "confidence":
                confidence,

            "reason":
                reason,

            "message":
                message,

            "reference_id":
                reference_id,

            "payment_link_id":
                payment_link["id"],

            "payment_link":
                payment_link["short_url"],

            "status":
                "payment_link_created"
        }


    except HTTPException:

        db.rollback()
        raise


    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    finally:

        db.close()