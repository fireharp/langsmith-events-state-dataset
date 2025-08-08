PY=python
IMAGE=lsevents

# Local Python commands
seed:
	$(PY) src/seed_dataset.py

eval:
	$(PY) src/eval_local.py

# Docker build
build:
	docker build -t $(IMAGE) .

# Docker CLI commands
d-seed:
	docker run --rm --env-file .env $(IMAGE) seed

d-list:
	docker run --rm --env-file .env $(IMAGE) list

d-list-5:
	docker run --rm --env-file .env $(IMAGE) list --limit 5

d-eval:
	docker run --rm --env-file .env $(IMAGE) eval

d-eval-verbose:
	docker run --rm --env-file .env $(IMAGE) eval --verbose

d-export:
	@mkdir -p exports
	docker run --rm --env-file .env -v "$$(pwd)/exports:/out" $(IMAGE) export --out /out/data.jsonl

d-add-example:
	@test -f new_example.json || (echo "Error: new_example.json not found" && exit 1)
	docker run --rm --env-file .env -v "$$(pwd):/work" -w /work $(IMAGE) add-example --file new_example.json

# Docker help
d-help:
	docker run --rm $(IMAGE) --help