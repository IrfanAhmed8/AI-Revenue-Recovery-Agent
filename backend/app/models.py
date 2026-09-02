from sqlalchemy import (
    Column,
    BigInteger,
    Numeric,
    Text,
    ForeignKey,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    func
)
from sqlalchemy.dialects.postgresql import JSONB,UUID
import uuid
from .database import Base


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(String, nullable=False)

    payment_id = Column(String, nullable=False)

    order_id = Column(String, nullable=True)

    payment_status = Column(String, nullable=True)

    amount = Column(Integer, nullable=True)

    currency = Column(String, nullable=True)

    payload = Column(JSONB, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "payment_id",
            "event_type",
            name="uq_payment_event"
        ),
    )


class FailedTransaction(Base):
    __tablename__ = "failed_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )

    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id"),
        nullable=False,
        unique=True
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False
    )

    amount = Column(BigInteger, nullable=False)

    currency = Column(
        String(3),
        nullable=False
    )

    payment_method = Column(String(30))

    error_code = Column(String(100))

    error_description = Column(Text)

    error_source = Column(String(100))

    error_step = Column(String(100))

    error_reason = Column(String(100))

    recovery_status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    recovery_probability = Column(
        Numeric(5, 4)
    )

    attempt_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    recovered_amount = Column(
        BigInteger,
        default=0
    )

    failed_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    recovered_at = Column(
        DateTime(timezone=True)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    failed_transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("failed_transactions.id"),
        nullable=False
    )

    action_type = Column(
        String(50),
        nullable=False
    )

    decision_reason = Column(Text)

    recovery_probability = Column(
        Numeric(5, 4)
    )

    confidence = Column(
        Numeric(5, 4)
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending"
    )

    razorpay_reference_id = Column(
        String(100)
    )

    razorpay_payment_link_id = Column(
        String(100)
    )

    razorpay_payment_id = Column(
        String(100)
    )

    result = Column(Text)

    metadata_json = Column("metadata", JSONB)

    executed_at = Column(
        DateTime(timezone=True)
    )

    completed_at = Column(
        DateTime(timezone=True)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    attempts = Column(
    Integer,
    nullable=False,
    default=1
)

    attempt_limit = Column(
        Integer,
        nullable=False,
        default=3
    )


class RecoveredTransaction(Base):
    __tablename__ = "recovered_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )

    failed_transaction_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    payment_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    customer_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    amount = Column(
        BigInteger,
        nullable=False
    )

    currency = Column(
        String(3),
        nullable=False
    )

    original_failure_reason = Column(
        String(100)
    )

    recovery_method = Column(
        String(50)
    )

    razorpay_payment_link_id = Column(
        String(100)
    )

    razorpay_payment_id = Column(
        String(100)
    )

    razorpay_reference_id = Column(
        String(100)
    )

    recovered_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
class Customer(Base):
    __tablename__ = "customers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True
    )

    phone = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id"),
        nullable=False
    )

    amount = Column(
        BigInteger,
        nullable=False
    )

    currency = Column(
        String(3),
        nullable=False
    )

    razorpay_order_id = Column(String(100))
    razorpay_payment_id = Column(String(100))

    method = Column(String(30))

    status = Column(
        String(30),
        nullable=False
    )

    description = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    error_code = Column(String(100))
    error_description = Column(Text)
    error_source = Column(String(100))
    error_step = Column(String(100))
    error_reason = Column(String(100))