from app.models import Customer, Payment
def get_customer_context(db, customer_id):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    payments = (
        db.query(Payment)
        .filter(Payment.customer_id == customer_id)
        .all()
    )

    return {
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "total_payments": len(payments),
        "successful_payments": sum(
            p.status == "captured" for p in payments
        ),
        "failed_payments": sum(
            p.status == "failed" for p in payments
        )
    }