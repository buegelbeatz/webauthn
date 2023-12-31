 
  
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
BOOTSTRAP_LOCAL_CSS = $(SRC_DIR)/static/bootstrap.css
BOOTSTRAP_LOCAL_JS = $(SRC_DIR)/static/bootstrap.js

all: run

explore-architecture:
	@$(eval ARCHITECTURE := $(shell uname -m))

########### install

install-venv:
	test -d venv || $(PYTHON) -m venv venv

install-bootstrap:
	test -f $(BOOTSTRAP_LOCAL_CSS) || curl $(BOOTSTRAP_CSS) > $(BOOTSTRAP_LOCAL_CSS)
	test -f $(BOOTSTRAP_LOCAL_JS) || curl $(BOOTSTRAP_JS) > $(BOOTSTRAP_LOCAL_JS)

install: install-venv install-bootstrap
	. venv/bin/activate; \
	$(PIP) install -U pip 1>/dev/null; \
	$(PIP) install -r requirements.txt 1>/dev/null

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
		open https://${NGROK_DOMAIN}/auth/invite && \
		DOMAIN=${NGROK_DOMAIN} SECRET=${NGROK_DOMAIN} DATA=${PWD}/${DATA_DIR} uvicorn main:app --host 0.0.0.0 --reload

# Run tests
test: install
	. venv/bin/activate; \
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -p '*_test.py'
 
# Package the project
# package: build
# 	mkdir -p $(DIST_DIR)
# 	tar -czvf $(DIST_DIR)/project.tar.gz $(BUILD_DIR)
 
# Deploy the project
deploy: package
	# Add deployment steps here
 
# Lint the project
lint:
	$(PYTHON) -m pylint $(SRC_DIR)
 
# Check code style
checkstyle:
	$(PYTHON) -m pycodestyle $(SRC_DIR)

build: explore-architecture
	docker build -t buegelbeatz/webauthn:${ARCHITECTURE} .
	docker push buegelbeatz/webauthn:${ARCHITECTURE}
 

.PHONY: venv install activate deactivate