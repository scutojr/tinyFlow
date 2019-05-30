# TODO:
# 1. start a interactive terminal to mongodb of test envirenment
# 2. start tests

SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


.PHONY: mongo_client
mongo_client:
	@mongo mongo_test_server:27017

.PHONY: server_test
server_test:
	@python $(CWD)/wf -f $(CWD)/config/wf.ini.template

.PHONY: test
test: .unit

.unit:
	@dirUnit='tests/unit'; \
	for module in `ls $$dirUnit | grep -e '^test_'`; \
	do \
	    python $$dirUnit/$$module; \
	done;


.PHONY: help
help:
	@echo 'Usage: <command>'
	@echo ''
	@echo Command:
	@echo '    test'
	@echo '    server_test'
	@echo '    mongo_client'
