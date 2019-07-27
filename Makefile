.PHONY: venv system-packages python-packages install unit-tests integration-tests tests all

venv:
	pip install --user virtualenv
	virtualenv venv

system-packages:
	sudo apt install python-pip -y

python-packages:
	pip install -r requirements.txt
	pip install -e .

install: system-packages python-packages

unit-tests:
	python -m unittest tests.test_scrapers

integration-tests:

tests: unit-tests integration-tests

all: install tests
