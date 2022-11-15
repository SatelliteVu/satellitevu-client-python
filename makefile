.DEFAULT_GOAL := help


.PHONY: bootstrap
bootstrap: ## Bootstrap local repository checkout
	@echo Set git commit message template…
	@git config commit.template .gitmessage

	@echo
	@echo Installing Python dependencies into Poetry managed virtualenv
ifeq (, $(shell which poetry))
$(error "No `poetry` in $$PATH, please install poetry https://python-poetry.org")
endif
	@poetry install
	@poetry env info

	@echo
	@echo Installing pre-commit hook
ifeq (, $(shell which pre-commit))
$(error "No `pre-commit` in $$PATH, please install pre-commit https://pre-commit.com")
endif
	@pre-commit install

	@echo
	@echo Checking nox
ifeq (, $(shell which nox))
$(error "No `nox` in $$PATH, please install it together with nox-poetry")
endif

	@echo
	@echo Checking Python versions
ifeq (, $(shell which python3.8))
	@echo "WARNING: No Python 3.8 found"
else
	@echo "INFO: Python 3.8 found"
endif
ifeq (, $(shell which python3.10))
	@echo "WARNING: No Python 3.10 found"
else
	@echo "INFO: Python 3.10 found"
endif


PHONY: test
test: ## Run tests with nox (multiple Python versions)
	nox --session=tests


PHONY: lint
lint: ## Run linting with nox
	nox --session=lint


.PHONY: help
help:
	@echo "Welcome to the SatelliteVu Platform Python SDK!"
	@echo
	@grep -E '^[\.a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
