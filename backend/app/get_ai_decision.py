import os

from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal


load_dotenv()

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class AIDecision(BaseModel):

    action: Literal[
        "PAYMENT_LINK",
        "REMINDER",
        "ESCALATE_HUMAN",
        "PERSONALIZED_MESSAGE"
    ]

    recovery_probability: float = Field(
        ge=0,
        le=1
    )

    confidence: float = Field(
        ge=0,
        le=1
    )

    reason: str

    message: str


def get_ai_decision(ai_context):

    prompt = f"""
You are an AI Revenue Recovery Agent.

Your responsibility is to analyze a failed payment and decide
the most appropriate recovery intervention.

You MUST choose exactly ONE of these actions:

1. PAYMENT_LINK

Use this when:
- The payment is reasonably recoverable.
- The customer should receive a new payment opportunity.
- A new Razorpay Payment Link is appropriate.
- The failure does not require human intervention.

2. REMINDER

Use this when:
- The customer should be reminded to complete payment.
- The payment may still be recoverable.
- There is no strong reason to immediately escalate.
- A simple reminder is more appropriate than creating another
  payment attempt.

3. ESCALATE_HUMAN

Use this when:
- The transaction is high value or high risk.
- There have been multiple failed/recovery attempts.
- The failure appears unusual or difficult to resolve automatically.
- Continuing automated recovery could create unnecessary risk.
- Human intervention is more appropriate.

4. PERSONALIZED_MESSAGE

Use this when:
- The failure provides a useful customer-specific recommendation.
- The customer should be given guidance rather than simply
  receiving a generic reminder.
- For example, if a card-related failure occurs, suggest trying
  another available payment method.
- The message should be based only on information available
  in the transaction and customer context.

IMPORTANT RULES:

- Do not invent transaction information.
- Do not invent payment methods that are definitely available.
- If suggesting another payment method, phrase it as a suggestion
  such as "try another available payment method".
- Do not perform any payment action.
- Do not create a Razorpay payment link.
- Do not send any message.
- Only make the decision.
- The backend will execute the selected action.
- recovery_probability must be between 0 and 1.
- confidence must be between 0 and 1.
- reason must explain WHY the selected action is appropriate.
- message must be directly usable as a customer-facing message.
- The customer-facing message should be polite, concise and professional.
- Do not expose internal risk scores, AI terminology, database IDs,
  error codes or internal system information to the customer.

ACTION SELECTION GUIDANCE:

Temporary/transient failure:
→ Prefer PAYMENT_LINK or REMINDER.

Repeated failures:
→ Consider REMINDER or ESCALATE_HUMAN.

High-value/high-risk transaction:
→ Consider ESCALATE_HUMAN.

Card/payment-method related problem:
→ Consider PERSONALIZED_MESSAGE.

Low recovery probability:
→ Prefer ESCALATE_HUMAN rather than repeatedly attempting recovery.

Customer appears recoverable and another payment attempt is reasonable:
→ Prefer PAYMENT_LINK.

Customer already has an outstanding recovery action:
→ Prefer REMINDER instead of creating another payment opportunity.

Now analyze the following context:

{ai_context}

Return:

- action
- recovery_probability
- confidence
- reason
- message
"""

    try:

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": AIDecision,
                "temperature": 0
            }
        )

        decision = AIDecision.model_validate_json(
            response.text
        )
        print(f"Gemini AI decision: {decision}")
        return decision.model_dump()

    except Exception as e:

        print(
            f"Gemini AI decision failed: {e}"
        )

        # Safe fallback
        return {
            "action": "ESCALATE_HUMAN",

            "recovery_probability": 0.0,

            "confidence": 0.0,

            "reason": (
                "AI decision could not be generated. "
                "The transaction has been escalated for "
                "manual review as a safety measure."
            ),

            "message": (
                "We were unable to complete your payment. "
                "Our support team will review the issue "
                "and assist you shortly."
            )
        }