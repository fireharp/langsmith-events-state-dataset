from langsmith import Client
from utils import ls_client, DATASET_NAME

def main():
    client: Client = ls_client()

    ds = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Map (user state, events[]) to state-machine actions[]"
    )

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
    print(f"Seeded {len(examples)} examples into dataset '{DATASET_NAME}' (id={ds.id})")

if __name__ == "__main__":
    main()