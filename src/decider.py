from typing import Dict, List, Any

def decide_actions(state: Dict[str, Any], events: List[Dict[str, Any]]) -> List[str]:
    """
    Replace with your real policy/model. This is a deterministic stub that
    demonstrates gating on current state + event kinds.
    """
    kinds = {e.get("type") for e in events}
    actions: List[str] = []

    # Example policy:
    if (not state or state.get("eligibility") == "intakeQuestionnaire") and "quiz_event" in kinds:
        actions.append("QUESTIONNAIRE_COMPLETED")

    if state.get("eligibility") == "checkoutProcess" and "payment_event" in kinds:
        actions.append("CHECKOUT_SUCCESS")

    if "health_event" in kinds or state.get("flags", {}).get("hypertension_risk"):
        if "health_event" in kinds:
            actions.append("MONITOR_HEALTH")

    # Dedup while preserving order
    seen = set()
    return [a for a in actions if not (a in seen or seen.add(a))]