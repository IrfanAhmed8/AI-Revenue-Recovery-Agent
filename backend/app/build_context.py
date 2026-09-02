def build_ai_context(failed_txn, customer, risk):

    return {
        "transaction": {
            "id": str(failed_txn.id),
            "amount": failed_txn.amount,
            "currency": failed_txn.currency,
            "status": failed_txn.recovery_status,
            "attempt_count": failed_txn.attempt_count,

            "payment_method": failed_txn.payment_method,

            "error_code": failed_txn.error_code,
            "error_description": failed_txn.error_description,
            "error_source": failed_txn.error_source,
            "error_step": failed_txn.error_step,
            "error_reason": failed_txn.error_reason
        },

        "customer": customer,

        "risk": risk
    }