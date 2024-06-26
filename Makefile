run:
	NEXUS_SECRET_KEY=abc123 NEXUS_DEBUG=1 ES_DJANGO_PASS=ES4LRC!! ./nexus/manage.py runserver 127.0.0.1:8000

init_run:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

migrate:
	./nexus/manage.py makemigrations
	./nexus/manage.py migrate