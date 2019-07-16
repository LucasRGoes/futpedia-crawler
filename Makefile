########################
# Scrapedia's Makefile #
########################

VENV := $$(pip -V | grep -c "venv")

venv:
	@virtualenv venv

init:
	@if [ "$(VENV)" = "0" ]; then echo "Verify if 'make venv' and 'source venv/bin/activate' were run."; else pip3 install -r requirements.txt && pip3 install -e .; fi

test:
