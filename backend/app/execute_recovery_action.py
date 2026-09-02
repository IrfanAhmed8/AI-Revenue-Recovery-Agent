from app.recovery_method.create_recovery_link import create_payment_link_recovery
from app.recovery_method.send_recovery_reminder import send_recovery_reminder
from app.recovery_method.escalate_to_human import escalate_to_human
from app.recovery_method.send_personlized_message import send_personalized_message
from app.database import SessionLocal
def execute_recovery_action(
    decision,
    failed_transaction_id
):
    db = SessionLocal()

    action = decision["action"]

    if action == "PAYMENT_LINK" or action =="payment_link":

        return create_payment_link_recovery(    
            failed_transaction_id,
            decision
        )

    elif action == "REMINDER" or action == "reminder":

        return send_recovery_reminder(
            db,
            failed_transaction_id,
            decision
        )

    elif action == "ESCALATE_HUMAN" or action == "escalate_human":

        return escalate_to_human(
            db,
            failed_transaction_id,
            decision
        )

    elif action == "PERSONALIZED_MESSAGE" or action == "personalized_message":

        return send_personalized_message(
            db,
            failed_transaction_id,
            decision
        )

    else:

        raise ValueError(
            f"Unknown recovery action: {action}"
        )