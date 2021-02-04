VERSION := 0.1.0

clean:
	-rm -rf dist
	-rm -rf env

patch:
	git aftermerge patch || exit 1

minor:
	git aftermerge minor || exit 1

major:
	git aftermerge major || exit 1


fmt:
	poetry run black .  || exit 1

lint:
	poetry run flake8 . || exit 1

test: clean fmt lint
	poetry run pytest || exit 1

build: test
	poetry build

deploytest: build
	python3 -m venv env
	./env/bin/pip install wheel
	./env/bin/pip install dist/django-ngmailbox-\$(VERSION).tar.gz
	-echo "source ./env/bin/activate"

serve: 
	bash ./devenv/start_firefox.sh & 
	poetry run python manage.py runserver

dev:
	bash ./devenv/start_dev.sh &
	poetry run python manage.py runserver

migrations:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

# Not setup yet
#deploy: build
#       poetry publish -r focus


