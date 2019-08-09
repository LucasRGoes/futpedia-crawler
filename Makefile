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
	python -m unittest tests.test_pipeline tests.test_requester tests.test_seekers tests.test_parsers tests.test_packers -vvv

integration-tests:

tests: unit-tests integration-tests

all: install tests
