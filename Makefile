.PHONY: setup run test doctor

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	bash scripts/run.sh

test:
	. .venv/bin/activate && pytest -q

doctor:
	bash scripts/doctor.sh
