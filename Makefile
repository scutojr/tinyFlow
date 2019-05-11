
# start a interactive terminal to mongodb of test envirenment
# start tests

# <<<< TO DEPRICATE
SHELL := /bin/bash

.PHONY: mongo_client
mongo_client:
	@mongo mongo_test_server:27017

.PHONY: tests
tests:
	echo xx # use nosetests to driven this procedure

.PHONY: help
help:
	@echo Usage: \
	make mongo_client
