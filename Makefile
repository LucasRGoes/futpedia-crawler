.PHONY: venv system-packages python-packages install unit-tests integration-tests tests package all

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
	python -m unittest tests.test_requesters tests.test_seekers tests.test_parsers tests.test_packers tests.test_pipeline -vvv

integration-tests:
	python -m unittest tests.test_scrapers -vvv

tests: unit-tests integration-tests

package:
	python setup.py sdist
	python setup.py bdist_wheel

all: install tests package
