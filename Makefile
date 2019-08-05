# TODO:
# 1. start a interactive terminal to mongodb of test envirenment
# 2. start tests

SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


.PHONY: mongo_client
.PHONY: server_test
.PHONY: runner
.PHONY: test
.PHONY: install
.PHONY: help

.PHONY: dev_mq_client
.PHONY: dev_kill
.PHONY: dev_kill_runner


mongo_client:
	@mongo mongo_test_server:27017


server_test:
	@target=/var/run/tobot; \
	if [ ! -d "$$target" ]; \
	then \
	    mkdir $$target; \
	    for i in `seq 5`; \
		do \
		    mkdir -p $$target/$$i; \
	        cp $(CWD)/tests/workflows/* $$target/$$i; \
		done; \
	fi
	@python $(CWD)/bin/tobot.py -f $(CWD)/config/wf.ini.template


runner:
	@python $(CWD)/bin/runner.py -f $(CWD)/config/wf.ini.template


dev_mq_client:
	@stomp -H amq_test_server -P 61613


dev_kill_runner:
	@$(CWD)/dev-support/killer.sh runner

dev_kill:
	@$(CWD)/dev-support/killer.sh all


test: .unit

.unit:
	@dirUnit='tests/unit'; \
	for module in `ls $$dirUnit | grep -e '^test_'`; \
	do \
	    python $$dirUnit/$$module; \
	done;


install: .dependency

.dependency:
	@pip install -r requirements.txt


help:
	@echo 'Usage: <command>'
	@echo ''
	@echo Command:
	@echo '    test'
	@echo '    server_test'
	@echo '    mongo_client'
	@echo '    install'
	@echo '    dev_mq_client'
	@echo '    dev_kill'
	@echo '    dev_kill_runner'
