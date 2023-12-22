 
  
# Makefile for Python project
 
# Environment variables
PYTHON = python3
#VENV_ACTIVATE=. venv/bin/activate
PIP = pip3
PORT = 8000
NGROK = ngrok
SRC_DIR = src
TEST_DIR = tests
DATA_DIR = .data

BOOTSTRAP_CSS = https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css
BOOTSTRAP_JS = https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js

all: run

########### install

install-venv:
	test -d venv || $(PYTHON) -m venv venv

install-bootstrap:
	test -f src/static/bootstrap.css || curl $(BOOTSTRAP_CSS) > src/static/bootstrap.css
	test -f src/static/bootstrap.js || curl $(BOOTSTRAP_JS) > src/static/bootstrap.js

install: install-venv install-bootstrap
	. venv/bin/activate; \
	$(PIP) install -U pip; \
	$(PIP) install -r requirements.txt

######### ngrok

stop-ngrok:
	@ps aux | grep ngrok | grep -v grep | sed -E 's/ +/ /g;' | cut -f2 -d' ' | xargs kill 2>/dev/null

start-ngrok: stop-ngrok
	@ngrok http $(PORT) 2>/dev/null 1>/dev/null &

fetch-ngrok-domain:
	@echo "Waiting 5 secondes..."
	@sleep 5 
	@echo "Fetching Ngrok domain..."
	@$(eval NGROK_DOMAIN := $(shell curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url' | sed 's,^https://,,g;s,/.*,,g;'))


############ run

run: start-ngrok install fetch-ngrok-domain
	@echo "${NGROK_DOMAIN}"
	@$(eval PWD := $(shell pwd))
	@. venv/bin/activate && cd src && \
		open https://${NGROK_DOMAIN}/admin && \
		DOMAIN=${NGROK_DOMAIN} SECRET=${NGROK_DOMAIN} DATA=${PWD}/${DATA_DIR} uvicorn main:app --host 0.0.0.0 --reload

# Run tests
test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -p '*_test.py'
 
# Package the project
package: build
	mkdir -p $(DIST_DIR)
	tar -czvf $(DIST_DIR)/project.tar.gz $(BUILD_DIR)
 
# Deploy the project
deploy: package
	# Add deployment steps here
 
# Lint the project
lint:
	$(PYTHON) -m pylint $(SRC_DIR)
 
# Check code style
checkstyle:
	$(PYTHON) -m pycodestyle $(SRC_DIR)
 

.PHONY: venv install activate deactivate