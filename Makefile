SHELL := /bin/bash

all: init test

init:
	@python setup.py develop
	@pip install --quiet -r requirements.txt

test:
	rm -f .coverage
	@nosetests -sv --with-coverage ./tests/
