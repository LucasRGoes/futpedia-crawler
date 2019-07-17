########################
# Scrapedia's Makefile #
########################

VENV := $$(pip -V | grep -c "venv")

venv:
	@virtualenv venv

init:
	@if [ "$(VENV)" = "0" ]; then echo "Verify if 'make venv' and 'source venv/bin/activate' were run."; else pip install -r requirements.txt && pip install -e .; fi

test:
	# Unit Tests
	python -m unittest tests/unit/test_scraper.py
