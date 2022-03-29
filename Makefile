.PHONY: clean clean-test clean-pyc clean-build dev venv help requirements-dev.txt
.DEFAULT_GOAL := help
-include .env

help:
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Setup dev environment
	pip install poetry
	poetry install
	poetry add pre-commit --dev
	pre-commit install
	poetry add ipykernel --dev
	poetry add jupyter --dev
	poetry add jupyterlab --dev