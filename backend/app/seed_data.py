from datetime import datetime, timedelta
from decimal import Decimal

from .database import SessionLocal
from .models import Customer, Payment, FailedTransaction


# ============================================================
# CUSTOMER CONFIGURATION
# failed_count is intentionally different for every customer
# ============================================================

CUSTOMERS = [
    {
        "name": "Irfan Jafri",
        "email": "jafriirfan36@gmail.com",
        "phone": "8424097584",
        "payment_count": 5,
        "failed_count": 1,
    },
    {
        "name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "9876500002",
        "payment_count": 6,
        "failed_count": 2,
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "9876500003",
        "payment_count": 7,
        "failed_count": 3,
    },
    {
        "name": "Amit Kumar",
        "email": "amit.kumar@example.com",
        "phone": "9876500004",
        "payment_count": 8,
        "failed_count": 4,
    },
    {
        "name": "Neha Singh",
        "email": "neha.singh@example.com",
        "phone": "9876500005",
        "payment_count": 9,
        "failed_count": 5,
    },
    {
        "name": "Arjun Mehta",
        "email": "arjun.mehta@example.com",
        "phone": "9876500006",
        "payment_count": 10,
        "failed_count": 6,
    },
    {
        "name": "Sneha Joshi",
        "email": "sneha.joshi@example.com",
        "phone": "9876500007",
        "payment_count": 11,
        "failed_count": 7,
    },
    {
        "name": "Vikram Shah",
        "email": "vikram.shah@example.com",
        "phone": "9876500008",
        "payment_count": 12,
        "failed_count": 8,
    },
    {
        "name": "Ananya Gupta",
        "email": "ananya.gupta@example.com",
        "phone": "9876500009",
        "payment_count": 15,
        "failed_count": 9,
    },
    {
        "name": "Rohan Verma",
        "email": "rohan.verma@example.com",
        "phone": "9876500010",
        "payment_count": 17,
        "failed_count": 10,
    },
]


PAYMENT_METHODS = [
    "upi",
    "card",
    "netbanking",
    "wallet",
]


ERRORS = [
    {
        "code": "INSUFFICIENT_FUNDS",
        "description": "Insufficient funds in customer account",
        "source": "bank",
        "step": "payment_authorization",
        "reason": "insufficient_funds",
        "probability": Decimal("0.8500"),
    },
    {
        "code": "BANK_DECLINED",
        "description": "The payment was declined by the bank",
        "source": "bank",
        "step": "payment_processing",
        "reason": "bank_declined",
        "probability": Decimal("0.7000"),
    },
    {
        "code": "GATEWAY_ERROR",
        "description": "Payment gateway did not respond successfully",
        "source": "razorpay",
        "step": "payment_gateway",
        "reason": "gateway_timeout",
        "probability": Decimal("0.9000"),
    },
    {
        "code": "AUTHENTICATION_ERROR",
        "description": "Payment authentication failed",
        "source": "customer",
        "step": "payment_confirmation",
        "reason": "authentication_failed",
        "probability": Decimal("0.5500"),
    },
    {
        "code": "BAD_REQUEST_ERROR",
        "description": "Payment request could not be processed",
        "source": "razorpay",
        "step": "payment_processing",
        "reason": "invalid_request",
        "probability": Decimal("0.3000"),
    },
]


def generate_amount(customer_number, payment_number):
    """
    Generates amount in paise.
    Example: 125000 = ₹1,250
    """

    return (
        50000
        + ((customer_number * 137 + payment_number * 791) % 1450000)
    )


def create_customers(session):
    """
    Create 10 customers.
    """

    customers = []

    for customer_data in CUSTOMERS:

        # Avoid duplicate customers if script is run again
        existing = (
            session.query(Customer)
            .filter(Customer.email == customer_data["email"])
            .first()
        )

        if existing:
            print(
                f"Customer already exists: "
                f"{customer_data['name']}"
            )
            customers.append(existing)
            continue

        customer = Customer(
            name=customer_data["name"],
            email=customer_data["email"],
            phone=customer_data["phone"],
        )

        session.add(customer)
        customers.append(customer)

    session.flush()

    return customers


def create_payments(session, customers):
    """
    Create exactly 100 payments.
    """

    payments = []

    for customer_number, (customer, config) in enumerate(
        zip(customers, CUSTOMERS),
        start=1,
    ):

        for payment_number in range(
            1,
            config["payment_count"] + 1,
        ):

            # First N payments are failed.
            # Remaining payments are captured.
            is_failed = (
                payment_number <= config["failed_count"]
            )

            status = "failed" if is_failed else "captured"

            amount = generate_amount(
                customer_number,
                payment_number,
            )

            method = PAYMENT_METHODS[
                (payment_number - 1) % len(PAYMENT_METHODS)
            ]

            error = None

            if is_failed:
                error = ERRORS[
                    (payment_number - 1) % len(ERRORS)
                ]

            payment = Payment(
                customer_id=customer.id,
                amount=amount,
                currency="INR",

                razorpay_order_id=(
                    f"order_SYN_{customer_number:02d}_"
                    f"{payment_number:03d}"
                ),

                razorpay_payment_id=(
                    f"pay_{status.upper()}_"
                    f"{customer_number:02d}_"
                    f"{payment_number:03d}"
                ),

                method=method,
                status=status,

                description=(
                    f"Synthetic payment for "
                    f"{customer.name}"
                ),

                error_code=(
                    error["code"] if error else None
                ),

                error_description=(
                    error["description"]
                    if error else None
                ),

                error_source=(
                    error["source"]
                    if error else None
                ),

                error_step=(
                    error["step"]
                    if error else None
                ),

                error_reason=(
                    error["reason"]
                    if error else None
                ),

                created_at=(
                    datetime.utcnow()
                    - timedelta(
                        days=customer_number,
                        hours=payment_number,
                    )
                ),

                updated_at=(
                    datetime.utcnow()
                    - timedelta(
                        days=customer_number,
                        hours=payment_number,
                    )
                ),
            )

            session.add(payment)
            payments.append(payment)

    session.flush()

    return payments


def create_failed_transactions(session):
    """
    Build failed_transactions FROM payments.

    This is important:
    We do NOT randomly create failed_transaction IDs.
    We query payments where status = 'failed'.
    """

    failed_transactions = []

    failed_payments = (
        session.query(Payment)
        .filter(Payment.status == "failed")
        .all()
    )

    for payment in failed_payments:

        # Prevent duplicate failed_transaction
        existing = (
            session.query(FailedTransaction)
            .filter(
                FailedTransaction.payment_id == payment.id
            )
            .first()
        )

        if existing:
            continue

        # Find probability based on error reason
        probability = Decimal("0.6000")

        for error in ERRORS:
            if error["reason"] == payment.error_reason:
                probability = error["probability"]
                break

        failed_transaction = FailedTransaction(
            payment_id=payment.id,
            customer_id=payment.customer_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.method,

            error_code=payment.error_code,
            error_description=payment.error_description,
            error_source=payment.error_source,
            error_step=payment.error_step,
            error_reason=payment.error_reason,

            recovery_status="pending",
            recovery_probability=probability,

            attempt_count=0,
            recovered_amount=0,

            failed_at=payment.created_at,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

        session.add(failed_transaction)
        failed_transactions.append(failed_transaction)

    session.flush()

    return failed_transactions


def print_summary(session):
    """
    Print useful verification information.
    """

    customers = session.query(Customer).count()
    payments = session.query(Payment).count()
    failed = (
        session.query(Payment)
        .filter(Payment.status == "failed")
        .count()
    )
    captured = (
        session.query(Payment)
        .filter(Payment.status == "captured")
        .count()
    )
    failed_transactions = (
        session.query(FailedTransaction).count()
    )

    print()
    print("=" * 60)
    print("DATABASE SEED COMPLETE")
    print("=" * 60)

    print(f"Customers:           {customers}")
    print(f"Payments:            {payments}")
    print(f"Captured payments:   {captured}")
    print(f"Failed payments:     {failed}")
    print(f"Failed transactions: {failed_transactions}")

    print()
    print("Failed transactions by customer:")
    print("-" * 40)

    for customer in session.query(Customer).all():

        count = (
            session.query(FailedTransaction)
            .filter(
                FailedTransaction.customer_id
                == customer.id
            )
            .count()
        )

        print(
            f"{customer.name:<20}: {count}"
        )

    print("=" * 60)


def main():

    session = SessionLocal()

    try:

        print("Creating customers...")
        customers = create_customers(session)

        print("Creating payments...")
        create_payments(session, customers)

        print("Creating failed transactions...")
        create_failed_transactions(session)

        session.commit()

        print_summary(session)

    except Exception as e:

        session.rollback()

        print()
        print("ERROR:")
        print(e)

        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()