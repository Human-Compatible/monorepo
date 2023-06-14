PROJECTS := $(notdir $(wildcard workspaces/*))


.clean-venv:
	rm -rf .venv

.venv:
	poetry install --sync

init: .clean-venv .venv

test-%: .venv
	poetry install --sync --with $*
	poetry run pytest workspaces/$*

tests: .venv $(addprefix test-, $(PROJECTS))

test-isolated-%: .venv
	poetry install --sync --only $*
	poetry run pytest workspaces/$*

propagate: .venv
	poetry run python -m humancompatible