from langsmith import Client
from utils import ls_client, DATASET_NAME
from decider import decide_actions

def main():
    client: Client = ls_client()
    examples = list(client.list_examples(dataset_name=DATASET_NAME))
    if not examples:
        print("No examples found. Run `make seed` first.")
        return

    exact = 0
    total = 0

    for ex in examples:
        state = ex.inputs.get("state", {}) or {}
        events = ex.inputs.get("events", []) or []
        gold = ex.outputs.get("actions", [])
        pred = decide_actions(state, events)

        total += 1
        ok = pred == gold
        exact += int(ok)

        print("=" * 60)
        print(f"Example: {ex.id}")
        print("State:      ", state)
        print("Events:     ", events)
        print("Gold:       ", gold)
        print("Pred:       ", pred)
        print("Match:      ", ok)

    print("\n---")
    print(f"Exact-match accuracy: {exact}/{total} ({(exact/total)*100:.1f}%)")

if __name__ == "__main__":
    main()