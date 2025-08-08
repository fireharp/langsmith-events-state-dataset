from langsmith import Client
from utils import ls_client, DATASET_NAME, DATASET_ID

def main():
    client: Client = ls_client()

    # Use existing dataset by ID
    try:
        ds = client.read_dataset(dataset_id=DATASET_ID)
        print(f"Using existing dataset '{ds.name}' (id={ds.id})")
    except Exception:
        # Fallback: create new dataset if ID not found
        ds = client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Map (user state, events[]) to state-machine actions[]"
        )
        print(f"Created new dataset '{DATASET_NAME}' (id={ds.id})")

    examples = [
        {
            "inputs": {
                "state": {},
                "events": [
                    {"type": "form_event", "source": "app", "ts": 1, "activity": "Intake submitted"},
                    {"type": "quiz_event", "source": "app", "ts": 2, "activity": "Quiz finished"},
                ],
            },
            "outputs": {"actions": ["QUESTIONNAIRE_COMPLETED"]},
        },
        {
            "inputs": {
                "state": {"eligibility": "checkoutProcess"},
                "events": [
                    {"type": "payment_event", "source": "stripe", "ts": 3, "activity": "Payment succeeded"}
                ],
            },
            "outputs": {"actions": ["CHECKOUT_SUCCESS"]},
        },
        {
            "inputs": {
                "state": {"monitoring": "idle", "flags": {"hypertension_risk": True}},
                "events": [
                    {"type": "health_event", "source": "app", "ts": 4, "activity": "High blood pressure reported"}
                ],
            },
            "outputs": {"actions": ["MONITOR_HEALTH"]},
        },
    ]

    client.create_examples(dataset_id=ds.id, examples=examples)
    print(f"Added {len(examples)} examples to dataset '{ds.name}' (id={ds.id})")

if __name__ == "__main__":
    main()