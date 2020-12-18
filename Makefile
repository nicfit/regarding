PYTEST_ARGS ?=
PYPI_REPO ?= pypi

PROJECT_NAME = $(shell python ./setup.py --name 2> /dev/null)
VERSION = $(shell python ./setup.py --version 2> /dev/null)
RELEASE_NAME = $(shell python ./setup.py --release-name 2> /dev/null)
RELEASE_TAG = v$(VERSION)
ABOUT_PY = regarding/__about__.py

all: build test  ## Build and test


# Meta
help: ## List all commands
	@# This code borrowed from https://github.com/jedie/poetry-publish/blob/master/Makefile
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Options:"
	@printf "\033[36m%-20s\033[0m %s\n" PYTEST_ARGS "If defined PDB options are added when 'pytest' is invoked"
	@printf "\033[36m%-20s\033[0m %s\n" PYPI_REPO "The package index to publish, 'pypi' by default."
	@printf "\033[36m%-20s\033[0m %s\n" BROWSER "HTML viewer used by docs-view/coverage-view"

info:  ## Show project metadata
	@echo "VERSION: $(VERSION)"
	@echo "RELEASE_TAG: $(RELEASE_TAG)"
	@echo "RELEASE_NAME: $(RELEASE_NAME)"
	poetry show


## Build
.PHONY: build
build: $(ABOUT_PY) setup.py  ## Build the project

setup.py: pyproject.toml poetry.lock
	dephell deps convert --from pyproject.toml --to setup.py

$(ABOUT_PY): pyproject.toml
	python -m regarding -o $@
	# Run again for bootstrapping new values
	python -m regarding -o $@

# Note, this clean rule is NOT to be called as part of `clean`
clean-autogen:
	-rm $(ABOUT_PY) setup.py


## Clean
clean: clean-test clean-dist  ## Clean the project
	rm -rf regarding.egg-info
	find -type d -name __pycache__ | xargs -r rm -rf


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

test-dist: dist
	poetry check
	@for f in `find dist -type f -name ${PROJECT_NAME}-${VERSION}.tar.gz \
              -o -name \*.egg -o -name \*.whl`; do \
		twine check $$f ; \
	done

lint:  ## Check coding style
	tox -e lint

clean-test:  ## Clean test artifacts (included in `clean`)
	rm -rf .tox
	rm -rf tests/__pycache__ .pytest_cache


## Distribute
sdist: build
	poetry build --format sdist

bdist: build
	poetry build --format wheel

.PHONY: dist
dist: clean sdist bdist  ## Create source and binary distribution files
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	@cd dist && \
	for f in $$(ls); do \
		md5sum $${f} > $${f}.md5; \
	done
	@ls dist

clean-dist:  ## Clean distribution artifacts (included in `clean`)
	rm -rf dist
	find . -type f -name '*~' | xargs -r rm

check-manifest:
	check-manifest

_check-version-tag:
	@if git tag -l | grep -E '^$(shell echo ${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi

authors:
	dephell generate authors

_pypi-release:
	poetry publish -r ${PYPI_REPO}


## Install
install: build  ## Install project and dependencies
	poetry install --no-dev

install-dev: build  ## Install projec, dependencies, and developer tools
	poetry install


## Release
release: pre-release _freeze-release test-all dist _tag-release _pypi-release

pre-release: clean-autogen build install-dev info _check-version-tag clean \
             test test-dist check-manifest authors changelog
	@git status -s -b

BUMP ?= prerelease
bump-version: requirements
	poetry version $(BUMP)
	$(MAKE) build

requirements:
	poetry show --outdated
	poetry update --lock
	poetry export -f requirements.txt --output requirements.txt

next-release: install-dev info

_freeze-release:
	@(git diff --quiet && git diff --quiet --staged) || \
        (printf "\n!!! Working repo has uncommitted/un-staged changes. !!!\n" && \
         printf "\nCommit and try again.\n" && false)

_tag-release:
	git tag -a $(RELEASE_TAG) -m "Release $(RELEASE_TAG)"
	git push --tags origin

changelog:
	@echo "FIXME: changelog target not yet implemented"
