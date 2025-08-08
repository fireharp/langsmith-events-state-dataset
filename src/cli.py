import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langsmith import Client

# Local helpers
from .utils import DATASET_NAME, DATASET_ID, ls_client
from .decider import decide_actions


def cmd_seed(args: argparse.Namespace) -> None:
    client: Client = ls_client()
    
    # Try to use existing dataset first
    dataset_name = args.dataset or DATASET_NAME
    try:
        # Try by ID if using default dataset
        if not args.dataset and DATASET_ID:
            ds = client.read_dataset(dataset_id=DATASET_ID)
            print(f"Using existing dataset '{ds.name}' (id={ds.id})")
        else:
            ds = client.read_dataset(dataset_name=dataset_name)
            print(f"Using existing dataset '{ds.name}' (id={ds.id})")
    except Exception:
        # Create new if not found
        ds = client.create_dataset(
            dataset_name=dataset_name,
            description="Map (user state, events[]) to state-machine actions[]",
        )
        print(f"Created new dataset '{ds.name}' (id={ds.id})")

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


def cmd_list(args: argparse.Namespace) -> None:
    client: Client = ls_client()
    dataset = args.dataset or DATASET_NAME
    items = list(client.list_examples(dataset_name=dataset))
    if args.limit:
        items = items[: args.limit]
    for ex in items:
        print(json.dumps(
            {
                "id": str(ex.id),
                "inputs": ex.inputs,
                "outputs": ex.outputs,
            },
            ensure_ascii=False,
        ))


def cmd_export(args: argparse.Namespace) -> None:
    client: Client = ls_client()
    dataset = args.dataset or DATASET_NAME
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out.open("w", encoding="utf-8") as f:
        for ex in client.list_examples(dataset_name=dataset):
            f.write(json.dumps({"inputs": ex.inputs, "outputs": ex.outputs}, ensure_ascii=False) + "\n")
            count += 1
    print(f"Exported {count} examples to {out}")


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_add_example(args: argparse.Namespace) -> None:
    """
    Adds a single example from a JSON file with structure:
    {
      "inputs": {"state": {...}, "events": [...]},
      "outputs": {"actions": [...]}
    }
    """
    client: Client = ls_client()
    dataset = args.dataset or DATASET_NAME
    ds = client.read_dataset(dataset_name=dataset)
    payload = _load_json(args.file)

    if not isinstance(payload, dict) or "inputs" not in payload or "outputs" not in payload:
        raise SystemExit("Invalid file: expected keys 'inputs' and 'outputs' at top level.")

    client.create_examples(dataset_id=ds.id, examples=[payload])
    print(f"Added example to dataset '{dataset}' from {args.file}")


def cmd_eval(args: argparse.Namespace) -> None:
    client: Client = ls_client()
    dataset = args.dataset or DATASET_NAME
    examples = list(client.list_examples(dataset_name=dataset))

    exact = 0
    for ex in examples:
        state = ex.inputs.get("state", {}) or {}
        events = ex.inputs.get("events", []) or []
        gold = ex.outputs.get("actions", [])
        pred = decide_actions(state, events)
        exact += int(pred == gold)

        if args.verbose:
            print(json.dumps({
                "id": str(ex.id),
                "state": state,
                "events": events,
                "gold": gold,
                "pred": pred,
                "match": pred == gold
            }, ensure_ascii=False))

    total = len(examples)
    pct = (exact / total * 100.0) if total else 0.0
    print(f"Exact-match: {exact}/{total} ({pct:.1f}%)")


def main() -> None:
    # Allow .env inside container if user mounts it
    load_dotenv()

    parser = argparse.ArgumentParser(prog="lsds", description="LangSmith dataset CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed", help="Seed dataset with sample examples")
    p_seed.add_argument("--dataset", help="Dataset name override")
    p_seed.set_defaults(func=cmd_seed)

    p_list = sub.add_parser("list", help="List examples")
    p_list.add_argument("--dataset", help="Dataset name override")
    p_list.add_argument("--limit", type=int, help="Max items")
    p_list.set_defaults(func=cmd_list)

    p_export = sub.add_parser("export", help="Export examples to JSONL")
    p_export.add_argument("--dataset", help="Dataset name override")
    p_export.add_argument("--out", required=True, help="Output file path (e.g., /out/data.jsonl)")
    p_export.set_defaults(func=cmd_export)

    p_add = sub.add_parser("add-example", help="Add one example from JSON file")
    p_add.add_argument("--dataset", help="Dataset name override")
    p_add.add_argument("--file", required=True, help="Path to JSON file with inputs/outputs")
    p_add.set_defaults(func=cmd_add_example)

    p_eval = sub.add_parser("eval", help="Evaluate local decider vs labels")
    p_eval.add_argument("--dataset", help="Dataset name override")
    p_eval.add_argument("--verbose", action="store_true")
    p_eval.set_defaults(func=cmd_eval)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()