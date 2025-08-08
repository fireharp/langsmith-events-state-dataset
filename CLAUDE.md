# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a toolkit for managing LangSmith datasets with a specific (state, events) → actions schema pattern. It's designed for state machine event mapping and decision logic evaluation.

## Essential Commands

### Local Development
```bash
# Setup environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add LANGSMITH_API_KEY

# Core operations
make seed  # Seed dataset with examples
make eval  # Evaluate decider logic
```

### Docker Operations (Preferred)
```bash
# Build and run
make build           # Build Docker image
make d-seed          # Seed dataset via Docker
make d-eval          # Run evaluation
make d-eval-verbose  # Detailed evaluation output
make d-export        # Export dataset to ./exports/data.jsonl
make d-list          # List all examples
make d-add-example   # Add example from new_example.json
```

## Architecture & Key Components

### Data Flow Pattern
The system implements a deterministic decision pipeline:
1. **Input**: State object + array of events
2. **Processing**: `src/decider.py::decide_actions()` analyzes state and event types
3. **Output**: List of state machine action strings

### Core Module Responsibilities

**src/cli.py**: Docker CLI entry point with subcommands (seed, list, export, add-example, eval). Each command operates independently and connects to LangSmith via API.

**src/decider.py**: Contains the decision logic that maps (state, events) to actions. This is the primary customization point - replace the stub logic with actual business rules or ML model inference.

**src/utils.py**: Manages dataset configuration and LangSmith client initialization. Contains `DATASET_ID` and `DATASET_NAME` constants that determine which dataset to use.

### Dataset Schema
```json
{
  "inputs": {
    "state": { /* application state object */ },
    "events": [ /* array of event objects with type, source, ts, activity */ ]
  },
  "outputs": {
    "actions": [ /* array of action strings */ ]
  }
}
```

### Docker Architecture
- Base image: `python:3.11-slim`
- Entry point: `python -m src.cli`
- Mounts required: `/out` for exports, `/work` for input files
- Environment: Reads `.env` file for `LANGSMITH_API_KEY`

## Current Dataset Configuration

The repository is configured to use:
- Dataset Name: `events-state-ds-aug8`
- Dataset ID: `bae9bb4c-7c25-4427-9b0e-d013da94f281`

These are hardcoded in `src/utils.py`. The CLI will attempt to use the existing dataset by ID first, then fall back to creating a new one if not found.

## Extending the Decider

The current `decide_actions()` function in `src/decider.py` is a stub implementation. To customize:

1. Analyze the event types present in the events array
2. Consider the current state object properties
3. Apply business logic to determine appropriate actions
4. Return deduplicated list of action strings

The evaluation in `src/eval_local.py` and `src/cli.py::cmd_eval()` uses exact match comparison between predicted and gold actions.