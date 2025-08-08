# LangSmith: (state, events[]) → actions[] dataset

Minimal toolkit for creating and using a LangSmith dataset where:
- **inputs**: `{ "state": <object>, "events": [<event>, ...] }`
- **outputs**: `{ "actions": ["STATE_MACHINE_EVENT", ...] }`

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env to add LANGSMITH_API_KEY (and optional LANGSMITH_ENDPOINT)
```

## Commands

```bash
# Create/seed dataset with a few labeled examples
make seed

# Run a local eval of your decider vs. labels in LangSmith
make eval
```

## Dataset name

Set once in `src/utils.py`:

```python
DATASET_NAME = "user-events-to-actions"
```

## Schema

```json
{
  "inputs": {
    "state": { "eligibility": "checkoutProcess", "flags": {"hypertension_risk": true} },
    "events": [
      {"type":"payment_event","source":"stripe","ts": 1723108123,"activity":"Payment succeeded"}
    ]
  },
  "outputs": { "actions": ["CHECKOUT_SUCCESS"] }
}
```

## Human labeling (lightweight)

1. Send live runs to LangSmith from your app.
2. In the LangSmith UI, queue tricky runs for Annotation (human review).
3. Convert reviewed runs or feedback into new dataset examples (curation loop).

Later you can automate: pull reviewed items via SDK and `create_examples(...)`.

## Typical pipeline usage

- **Training**: read inputs/outputs from this dataset → fit your model/rules.
- **Evaluation**: run your decider on the dataset and compute metrics (exact match or partial).
- **Curation**: mispredictions → annotation → back into dataset → retrain.