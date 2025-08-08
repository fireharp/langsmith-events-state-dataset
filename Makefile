PY=python

seed:
	$(PY) src/seed_dataset.py

eval:
	$(PY) src/eval_local.py