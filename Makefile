PYTHON ?= python
VENV := .venv
TEST_APP ?= schedules

ifeq ($(OS),Windows_NT)
	PYTHON_VENV := $(VENV)/Scripts/python.exe
	PIP_VENV := $(VENV)/Scripts/pip.exe
else
	PYTHON_VENV := $(VENV)/bin/python
	PIP_VENV := $(VENV)/bin/pip
endif

MANAGE := $(PYTHON) tp_es/manage.py
MANAGE_VENV := $(PYTHON_VENV) tp_es/manage.py

.PHONY: requirements run clean test test-all coverage \
        venv venv-requirements run-venv test-venv coverage-venv

venv:
	$(PYTHON) -m venv $(VENV)

venv-requirements: venv
	$(PIP_VENV) install -r requirements.txt

requirements:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(MANAGE) runserver

run-venv: venv-requirements
	$(MANAGE_VENV) runserver

test:
	$(MANAGE) test $(TEST_APP)

test-all:
	$(MANAGE) test accounts schedules

test-venv: venv-requirements
	$(MANAGE_VENV) test $(TEST_APP)

coverage:
	$(PYTHON) -m coverage run --source='.' tp_es/manage.py test accounts schedules
	$(PYTHON) -m coverage report

coverage-venv: venv-requirements
	$(PYTHON_VENV) -m coverage run --source='.' tp_es/manage.py test accounts schedules
	$(PYTHON_VENV) -m coverage report

clean:
ifeq ($(OS),Windows_NT)
	@echo "Remova manualmente __pycache__ e arquivos .pyc no Windows."
else
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
endif