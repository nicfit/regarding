SHELL := /bin/bash
.DEFAULT_GOAL := build

## User settings
PYTEST_ARGS ?= ./tests
PYPI_REPO ?= pypi

## Config
# FIXME: want to set name and version with only pne call to pdm
#FOO := $(shell read -r PROJECT_NAME VERSION  <<<$(pdm show --name --version | xargs))
#$(warning $(FOO))
PROJECT_NAME := $(shell python setup.py --name 2> /dev/null)
ifeq ($(strip $(PROJECT_NAME)),)
  $(error "PROJECT_NAME not set")
endif
VERSION := $(shell python setup.py --version 2> /dev/null)
ifeq ($(strip $(VERSION)),)
  $(error "VERSION not set")
endif
ABOUT_PY := regarding/__about__.py
RELEASE_NAME = $(shell sed -n "s/^release_name = \"\(.*\)\"/\1/p" pyproject.toml)
RELEASE_TAG = v$(VERSION)

ifdef TERM
  BOLD_COLOR := $(shell tput bold)
  HELP_COLOR := $(shell tput setaf 6)
  HEADER_COLOR := $(BOLD_COLOR)$(shell tput setaf 2)
  NO_COLOR := $(shell tput sgr0)
endif


all: clean build test  ## Build and test


help:  ## List all commands
	@printf "\n$(BOLD_COLOR)***** $(PROJECT_NAME) $(VERSION): Makefile help *****$(NO_COLOR)\n"
	@# This code borrowed from https://github.com/jedie/poetry-publish/blob/master/Makefile
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@printf "$(BOLD_COLOR)Options:$(NO_COLOR)\n"
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" PYTEST_ARGS "If defined PDB options are added when 'pytest' is invoked"
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" PYPI_REPO "The package index to publish, 'pypi' by default."
	@printf "$(HELP_COLOR)%-20s$(NO_COLOR) %s\n" BROWSER "HTML viewer used by docs-view/coverage-view"
	@echo ""



## Build
.PHONY: build
build: install ## Build the project
	@echo "$(HEADER_COLOR)Building $(PROJECT_NAME) $(VERSION)...$(NO_COLOR)"
	pdm build -d build
	$(MAKE) $(ABOUT_PY)

install:  ## Install the project
	@echo "$(HEADER_COLOR)Installing $(PROJECT_NAME) $(VERSION)...$(NO_COLOR)"
	pip install .

#
#setup.py: pyproject.toml poetry.lock
#	dephell deps convert --from pyproject.toml --to setup.py
#
$(ABOUT_PY): pyproject.toml
	python -m regarding -o $@
	# Run again for bootstrapping new values
	python -m regarding -o $@

## Clean
clean: clean-test clean-dist  ## Clean the project
	rm -rf build dist
	find -type d -name __pycache__ | xargs -r rm -rf
	rm -rf regarding.egg-info
	touch pyproject.toml


## Test
test:  ## Run tests with default python
	tox -e py -- $(PYTEST_ARGS)

test-all:  ## Run tests with all supported versions of Python
	tox --parallel=all -- $(PYTEST_ARGS)

coverage:
	tox -e coverage

coverage-view:
	@if [ ! -f build/tests/coverage/index.html ]; then \
		${MAKE} coverage; \
	fi
	@${BROWSER} build/tests/coverage/index.html



lint:  ## Check coding style
	tox -e lint

clean-test:  ## Clean test artifacts (included in `clean`)
	rm -rf .tox .coverage
	rm -rf tests/__pycache__ .pytest_cache


## Distribute
sdist:
	pdm build --no-wheel -d dist --no-clean

bdist:
	pdm build --no-sdist -d dist --no-clean

.PHONY: dist
dist: all lint sdist bdist check-manifest  ## Create source and binary distribution files
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	@cd dist && \
	for f in $$(ls); do \
		md5sum $${f} > $${f}.md5; \
	done
	@ls -l dist

clean-dist:  ## Clean distribution artifacts (included in `clean`)
	rm -rf dist
	find . -type f -name '*~' | xargs -r rm
	rm -rf .venv .pdm-build

#test-dist: dist
#	poetry check
#	@for f in `find dist -type f -name ${PROJECT_NAME}-${VERSION}.tar.gz \
#              -o -name \*.egg -o -name \*.whl`; do \
#		twine check $$f ; \
#	done

check-manifest:
	check-manifest
#
#_check-version-tag:
#	@if git tag -l | grep -E '^$(shell echo ${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
#        echo "Version tag '${RELEASE_TAG}' already exists!"; \
#        false; \
#    fi
#
#authors:
#	dephell generate authors

_pypi-release:
	pdm publish --skip-existing --no-build --dest=dist --repository=${PYPI_REPO}


## Release
#release: pre-release _freeze-release test-all dist _tag-release _pypi-release
releaseXXX: dist
	rm dist/*.md5
	$(MAKE) _pypi-release

#
#pre-release: clean-autogen build install-dev info _check-version-tag clean \
#             test test-dist authors changelog
#	@git status -s -b
#
#BUMP ?= prerelease
#bump-version: requirements
#	poetry version $(BUMP)
#	$(MAKE) build
#
#requirements:
#	poetry show --outdated
#	poetry update --lock
#	poetry export -f requirements.txt --output requirements.txt --all-extras --without-hashes
#	poetry export -f requirements.txt --output dev-requirements.txt --with=dev --without-hashes
#
#next-release: install-dev info
#
#_freeze-release:
#	@(git diff --quiet && git diff --quiet --staged) || \
#        (printf "\n!!! Working repo has uncommitted/un-staged changes. !!!\n" && \
#         printf "\nCommit and try again.\n" && false)
#
#_tag-release:
#	git tag -a $(RELEASE_TAG) -m "Release $(RELEASE_TAG)"
#	git push --tags origin
#
#changelog:
#	@echo "FIXME: changelog target not yet implemented"

VENV_NAME ?= dev-regarding
VENV_DIR ?= $(HOME)/.virtualenvs
VENV_ACTIVATE := $(VENV_DIR)/$(VENV_NAME)/bin/activate
devenv-clean:
	test -n "$(VENV_DIR)" && test -n "$(VENV_NAME)" && rm -r $(VENV_DIR)/$(VENV_NAME)

devenv:
	python -m venv --upgrade-deps $(VENV_DIR)/$(VENV_NAME)
	source $(VENV_ACTIVATE) && python -m pip install --editable .[dev]
	@printf "\n$(BOLD_COLOR)To activate the virtualenv:$(NO_COLOR) source $(VENV_ACTIVATE)\n"
	@printf "$(BOLD_COLOR)To deactivate the virtualenv:$(NO_COLOR) deactivate\n\n"

