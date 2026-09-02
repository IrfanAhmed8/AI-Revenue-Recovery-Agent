import os
import uuid
from app.database import (
    engine,
    Base,
    SessionLocal
)
from app.routes.get_recovery_actions import get_recovery_actions
from app.routes.fetch_recovered_transactions import fetch_recovered_transactions
from app.routes.fetch_info import fetch_info
from fastapi.middleware.cors import CORSMiddleware
from app import models
from datetime import datetime
import razorpay
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.routes.run_recovery import run_recovery
import json
import hmac
import hashlib
from app.models import (
    PaymentWebhook,
    Customer,
    Payment,
    FailedTransaction,
    RecoveryAction,
    RecoveredTransaction
)

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)    
Base.metadata.create_all(bind=engine)
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
templates = Jinja2Templates(directory="app/templates")

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)



class CreateOrderRequest(BaseModel):
    amount: int


@app.get("/")
def home():
    return {
        "message": "Razorpay webhook server is running"
    }


@app.get("/payment", response_class=HTMLResponse)
def payment_page(request: Request):
     return templates.TemplateResponse(
        request=request,
        name="payment.html",
        context={"request": request}
    )


@app.post("/create-order")
def create_order(request: CreateOrderRequest):
    try:
        order = client.order.create({
            "amount": request.amount,
            "currency": "INR",
            "receipt": "receipt_001"
        })

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):

    # -----------------------------------------
    # 1. Get raw request body
    # -----------------------------------------

    body = await request.body()

    received_signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not received_signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay signature"
        )

    # -----------------------------------------
    # 2. Verify Razorpay signature
    # -----------------------------------------

    expected_signature = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        received_signature,
        expected_signature
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay signature"
        )

    # -----------------------------------------
    # 3. Parse webhook
    # -----------------------------------------

    payload = json.loads(body)

    print("\n========== RAZORPAY WEBHOOK ==========")
    print(json.dumps(payload, indent=2))
    print("======================================\n")

    event_type = payload.get("event")

    payment = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    payment_id = payment.get("id")
    order_id = payment.get("order_id")
    payment_status = payment.get("status")
    amount = payment.get("amount")
    currency = payment.get("currency")
    payment_description = payment.get("description")

    db = SessionLocal()

    try:

        # -----------------------------------------
        # 4. Save raw webhook
        # -----------------------------------------

        existing = (
            db.query(PaymentWebhook)
            .filter(
                PaymentWebhook.payment_id == payment_id,
                PaymentWebhook.event_type == event_type
            )
            .first()
        )

        if existing:
            print("Webhook already exists.")
        else:

            webhook_record = PaymentWebhook(
                event_type=event_type,
                payment_id=payment_id,
                order_id=order_id,
                payment_status=payment_status,
                amount=amount,
                currency=currency,
                payload=payload
            )

            db.add(webhook_record)

            # Flush instead of commit.
            # This keeps everything in one transaction.
            db.flush()

            print(
                f"Webhook saved to PostgreSQL. "
                f"ID={webhook_record.id}"
            )

        # =====================================================
        # 5. RECOVERY LOGIC
        # =====================================================

        if (
            event_type == "payment.captured"
            and payment_description
            and payment_description.startswith("#")
        ):

            # Razorpay currently gives:
            #
            # "#TVAIBSHBdndzd4"
            #
            # Payment Link ID:
            #
            # "plink_TVAIBSHBdndzd4"

            payment_link_id = (
                f"plink_{payment_description[1:]}"
            )

            print(
                f"Recovery payment detected."
            )

            print(
                f"Payment Link ID: "
                f"{payment_link_id}"
            )

            # -----------------------------------------
            # 6. Find recovery action
            # -----------------------------------------

            recovery_action = (
                db.query(RecoveryAction)
                .filter(
                    RecoveryAction
                    .razorpay_payment_link_id
                    == payment_link_id
                )
                .first()
            )

            if not recovery_action:

                print(
                    "No recovery action found "
                    "for this payment link."
                )

            else:

                print(
                    f"Recovery action found: "
                    f"{recovery_action.id}"
                )

                # -----------------------------------------
                # 7. Find failed transaction
                # -----------------------------------------

                failed_txn = (
                    db.query(FailedTransaction)
                    .filter(
                        FailedTransaction.id
                        == recovery_action
                        .failed_transaction_id
                    )
                    .first()
                )

                if not failed_txn:

                    raise HTTPException(
                        status_code=404,
                        detail=(
                            "Failed transaction "
                            "not found"
                        )
                    )

                # -----------------------------------------
                # 8. Idempotency check
                # -----------------------------------------

                existing_recovery = (
                    db.query(RecoveredTransaction)
                    .filter(
                        RecoveredTransaction
                        .razorpay_payment_id
                        == payment_id
                    )
                    .first()
                )

                if existing_recovery:

                    print(
                        "Recovery already processed."
                    )

                else:

                    # -----------------------------------------
                    # 9. Create recovered transaction
                    # -----------------------------------------

                    recovered = RecoveredTransaction(

                        failed_transaction_id=
                            failed_txn.id,

                        payment_id=
                            failed_txn.payment_id,

                        customer_id=
                            failed_txn.customer_id,

                        amount=
                            failed_txn.amount,

                        currency=
                            failed_txn.currency,

                        original_failure_reason=
                            failed_txn.error_reason,

                        recovery_method=
                            "razorpay_payment_link",

                        razorpay_payment_link_id=
                            payment_link_id,

                        razorpay_payment_id=
                            payment_id,

                        razorpay_reference_id=
                            recovery_action
                            .razorpay_reference_id
                    )

                    db.add(recovered)

                    # -----------------------------------------
                    # 10. Update failed transaction
                    # -----------------------------------------

                    failed_txn.recovery_status = (
                        "recovered"
                    )

                    failed_txn.recovered_amount = (
                        amount
                    )

                    failed_txn.recovered_at = (
                        datetime.utcnow()
                    )

                    failed_txn.updated_at = (
                        datetime.utcnow()
                    )

                    # -----------------------------------------
                    # 11. Update recovery action
                    # -----------------------------------------

                    recovery_action.status = (
                        "succeeded"
                    )

                    recovery_action.razorpay_payment_id = (
                        payment_id
                    )

                    recovery_action.completed_at = (
                        datetime.utcnow()
                    )

                    recovery_action.result = (
                        "Payment successfully recovered"
                    )

                    print(
                        "================================"
                    )

                    print(
                        "PAYMENT RECOVERED SUCCESSFULLY"
                    )

                    print(
                        f"Failed transaction: "
                        f"{failed_txn.id}"
                    )

                    print(
                        f"Recovered amount: "
                        f"{amount}"
                    )

                    print(
                        f"Razorpay payment: "
                        f"{payment_id}"
                    )

                    print(
                        "================================"
                    )

        # -----------------------------------------
        # 12. Commit everything
        # -----------------------------------------

        db.commit()

        return {
            "status": "ok"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:

        db.rollback()

        print(
            f"Webhook processing error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()

@app.post("/recovery/{failed_transaction_id}/create-link")
def create_recovery_link(
    failed_transaction_id: str
):

    db = SessionLocal()

    try:

        # -----------------------------------------
        # 1. Find pending failed transaction
        # -----------------------------------------

        failed_txn = (
            db.query(FailedTransaction)
            .filter(
                FailedTransaction.id == failed_transaction_id,
                FailedTransaction.recovery_status == "pending"
            )
            .first()
        )

        if not failed_txn:
            raise HTTPException(
                status_code=404,
                detail="Pending failed transaction not found"
            )


        # -----------------------------------------
        # 2. Find customer
        # -----------------------------------------

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


        # -----------------------------------------
        # 3. Generate reference ID
        # -----------------------------------------

        reference_id = f"REC_{uuid.uuid4().hex[:20]}"


        # -----------------------------------------
        # 4. Create Razorpay Payment Link
        # -----------------------------------------

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


        # -----------------------------------------
        # 5. Store recovery action
        # -----------------------------------------

        recovery_action = RecoveryAction(

            failed_transaction_id=failed_txn.id,

            action_type="payment_link",

            decision_reason=(
                "Retry payment using Razorpay "
                "Payment Link"
            ),

            recovery_probability=(
                failed_txn.recovery_probability
            ),

            confidence=None,

            status="sent",

            razorpay_reference_id=reference_id,

            razorpay_payment_link_id=(
                payment_link["id"]
            ),

            executed_at=datetime.utcnow()
        )

        db.add(recovery_action)


        # -----------------------------------------
        # 6. Update failed transaction
        # -----------------------------------------

        failed_txn.recovery_status = (
            "action_required"
        )

        failed_txn.attempt_count = (
            failed_txn.attempt_count + 1
        )

        failed_txn.updated_at = datetime.utcnow()


        db.commit()

        db.refresh(recovery_action)


        # -----------------------------------------
        # 7. Return response
        # -----------------------------------------

        return {

            "success": True,

            "failed_transaction_id":
                str(failed_txn.id),

            "customer": {
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone
            },

            "amount":
                failed_txn.amount,

            "failure_reason":
                failed_txn.error_reason,

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

@app.post("/recovery/{failed_transaction_id}/run")
def run_recovery_endpoint(failed_transaction_id: str):
    return run_recovery(failed_transaction_id)

@app.get("/fetch-info")
def fetch_info_endpoint():
    return fetch_info(db=SessionLocal())

@app.get("/recovered-transactions")
def get_recovered_transactions():
    return fetch_recovered_transactions()
@app.get("/recovery-actions")
def get_recovery_actions_endpoint():
    return get_recovery_actions()