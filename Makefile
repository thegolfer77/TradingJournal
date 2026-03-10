.PHONY: setup run test doctor

setup:
	bash install.sh

run:
	bash run.sh

test:
	. .venv/bin/activate && pytest -q

doctor:
	bash doctor.sh
