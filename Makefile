.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr reports/
	find . -path "*/features/steps/__pycache__" -exec rm -fr {} +
	find . -name "*.bdd.log" -exec rm -f {} +

lint: ## check style with flake8
	flake8 dbfpy3 tests

test: ## run all tests (traditional, TDD, and BDD)
	python -m unittest discover tests -v && behave

test-quick: ## run quick smoke tests (fast subset)
	python -m unittest discover tests -p "test_[!_]*" -v && behave --tags=@smoke

test-traditional: ## run traditional unit tests only
	python setup.py test

test-all: ## run tests on every Python version with tox
	tox

tdd: ## run TDD tests (unit tests)
	python -m unittest discover tests -p "test_*_tdd.py" -v

tdd-field: ## run TDD field parsing tests
	python -m unittest tests.test_field_parsing_tdd -v

tdd-header: ## run TDD header validation tests
	python -m unittest tests.test_header_validation_tdd -v

tdd-record: ## run TDD record operations tests
	python -m unittest tests.test_record_operations_tdd -v

tdd-error: ## run TDD error handling tests
	python -m unittest tests.test_error_handling_tdd -v

tdd-dbase3: ## run TDD dBase III comprehensive tests
	python -m unittest tests.test_dbase3_comprehensive_tdd -v

test-tdd: tdd ## alias for tdd target

bdd: ## run BDD tests with behave
	behave

bdd-verbose: ## run BDD tests with verbose output
	behave -D verbose=true

bdd-smoke: ## run smoke tests only (critical scenarios)
	behave --tags=smoke

bdd-regression: ## run regression test suite
	behave --tags=regression

bdd-wip: ## run work-in-progress scenarios
	behave -D wip=true --tags=wip

bdd-performance: ## run performance tests
	behave -D performance=true --tags=performance

bdd-report: ## run BDD tests and generate HTML report
	behave --format=html --outfile=reports/bdd_report.html

test-bdd: bdd ## alias for bdd target

coverage: ## check code coverage quickly with the default Python
	coverage run --source dbfpy3 setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/dbfpy3.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ dbfpy3
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
