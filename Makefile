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