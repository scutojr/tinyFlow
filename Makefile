# TODO:
# 1. start a interactive terminal to mongodb of test envirenment
# 2. start tests

# <<<< TO DEPRICATE
SHELL := /bin/bash
CWD := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))


.PHONY: mongo_client
mongo_client:
	@mongo mongo_test_server:27017

.PHONY: server_test
server_test:
	@python $(CWD)/wf -f $(CWD)/config/wf.ini.template

.PHONY: tests
tests:
	echo xx # use nosetests to driven this procedure

.PHONY: help
help:
	@echo 'Usage: <command>'
	@echo ''
	@echo Command:
	@echo '    server_test'
	@echo '    mongo_client'
