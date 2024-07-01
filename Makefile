install-with-cache:
	pip3 install -r requirements.txt

install-with-no-cache:
	pip3 install -r requirements.txt --no-cache

runserver:
	python3 manage.py runserver

tests:
	pytest

makemigrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

createsuperuser:
	python3 manage.py createsuperuser --email=admin@gmail.com
