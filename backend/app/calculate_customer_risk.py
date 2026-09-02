def calculate_customer_risk(customer_context):

    total = customer_context["total_payments"]
    successful = customer_context["successful_payments"]

    if total == 0:
        return {
            "risk_score": 0.5,
            "risk_level": "UNKNOWN"
        }

    success_rate = successful / total

    risk_score = 1 - success_rate

    if risk_score < 0.3:
        risk_level = "LOW"
    elif risk_score < 0.6:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "success_rate": success_rate,
        "risk_score": risk_score,
        "risk_level": risk_level
    }