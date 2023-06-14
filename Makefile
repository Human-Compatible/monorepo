PROJECTS := $(notdir $(wildcard workspaces/*))


.clean:
	rm -rf .venv

.venv:
	poetry install --sync

init: .venv
	poetry run pre-commit install

pre-commit: .venv
	poetry run pre-commit run --all-files

test-%: .venv
	poetry run pytest workspaces/$*

tests: .venv $(addprefix test-, $(PROJECTS))

test-isolated-%: .venv
	poetry install --sync --only $*
	poetry run pytest workspaces/$*

propagate: .venv
	poetry run python -m humancompatible
