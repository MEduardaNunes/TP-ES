requirements:
	pip install -r requirements.txt

run:
	if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		venv/bin/pip install -r requirements.txt; \
	fi
	venv/bin/python tp_es/manage.py runserver

clean: 
	rm -rf venv


.PHONY: run_tests coverage

run_tests:
	python tp_es/manage.py test accounts

coverage:
	coverage run --source='.' tp_es/manage.py test accounts
	coverage report