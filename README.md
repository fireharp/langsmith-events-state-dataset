# LangSmith: (state, events[]) → actions[] dataset

🚀 **Production-ready toolkit** for creating and managing LangSmith datasets with a (state, events) → actions schema.

- **Dockerized CLI**: Zero Python setup required
- **inputs**: `{ "state": <object>, "events": [<event>, ...] }`
- **outputs**: `{ "actions": ["STATE_MACHINE_EVENT", ...] }`

## Quick Start

### Option 1: Local Python
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env to add LANGSMITH_API_KEY

# Create/seed dataset with examples
make seed

# Run local eval of your decider
make eval
```

### Option 2: Docker (Recommended)
```bash
# Setup
cp .env.example .env
# edit .env to add LANGSMITH_API_KEY

# Build the Docker image
make build

# Docker CLI commands
make d-seed           # Seed dataset with examples
make d-list           # List all examples
make d-list-5         # List first 5 examples
make d-eval           # Run evaluation
make d-eval-verbose   # Run evaluation with details
make d-export         # Export to ./exports/data.jsonl
make d-add-example    # Add example from new_example.json
```

### Option 3: Docker Compose
```bash
docker-compose run seed     # Seed dataset
docker-compose run list     # List examples
docker-compose run eval     # Run evaluation
docker-compose run export   # Export to ./exports/data.jsonl
```

## Docker CLI Usage

The Docker image provides a complete CLI with multiple subcommands:

```bash
# Build image
docker build -t lsevents .

# Seed dataset
docker run --rm --env-file .env lsevents seed

# List examples (with optional limit)
docker run --rm --env-file .env lsevents list --limit 5

# Export dataset to JSONL
mkdir -p exports
docker run --rm --env-file .env -v "$(pwd)/exports:/out" lsevents export --out /out/data.jsonl

# Add single example from JSON file
cat > new_example.json <<'EOF'
{
  "inputs": {
    "state": {"eligibility": "intakeQuestionnaire"},
    "events": [{"type":"quiz_event","source":"app","ts":10,"activity":"Quiz finished"}]
  },
  "outputs": { "actions": ["QUESTIONNAIRE_COMPLETED"] }
}
EOF
docker run --rm --env-file .env -v "$(pwd):/work" -w /work lsevents add-example --file new_example.json

# Evaluate decider
docker run --rm --env-file .env lsevents eval --verbose
```

## Dataset Configuration

Set in `src/utils.py`:

```python
DATASET_NAME = "events-state-ds-aug8"
DATASET_ID = "bae9bb4c-7c25-4427-9b0e-d013da94f281"  # Optional: use existing dataset
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

## Production Deployment

The Docker image is designed for:
- **CI/CD pipelines**: GitHub Actions, GitLab CI, Jenkins
- **Scheduled jobs**: Kubernetes CronJobs, Cloud Run, AWS Batch
- **Data pipelines**: Export datasets for training, import from production logs
- **Team collaboration**: Consistent environment across all developers

## License

MIT