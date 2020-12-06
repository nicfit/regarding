all: build


## Data
PYTEST_ARGS ?=
PYPI_REPO ?= pypi

PROJECT_NAME = $(shell python ./setup.py --name 2> /dev/null)
VERSION = $(shell python ./setup.py --version 2> /dev/null)
RELEASE_NAME = $(shell python ./setup.py --release-name 2> /dev/null)
RELEASE_TAG = v$(VERSION)


## Build
build: regarding/__about__.py setup.py

regarding/__about__.py: pyproject.toml
	python -m regarding -o $@
	# Run again for bootstrapping new values
	python -m regarding -o $@

setup.py: pyproject.toml poetry.lock
	dephell deps convert --from pyproject.toml --to setup.py

# Note, this clean rule is NOT to be called as part of `clean`
clean-autogen:
	rm regarding/__about__.py setup.py


## Clean
clean: clean-test clean-dist
	rm -rf regarding.egg-info regarding/__pycache__


## Test
test:
	tox -e default -- $(PYTEST_ARGS)

test-all:
	tox --parallel=all -- $(PYTEST_ARGS)

test-dist: dist
	poetry check
	@for f in `find dist -type f -name ${PROJECT_NAME}-${VERSION}.tar.gz \
              -o -name \*.egg -o -name \*.whl`; do \
		twine check $$f ; \
	done

lint:
	tox -e lint

clean-test:
	rm -rf tests/__pycache__ .pytest_cache .tox


## Distribute
sdist: build
	poetry build --format sdist

bdist: build
	poetry build --format wheel

.PHONY: dist
dist: clean sdist bdist
	@# The cd dist keeps the dist/ prefix out of the md5sum files
	cd dist && \
	for f in $$(ls); do \
		md5sum $${f} > $${f}.md5; \
	done
	@ls dist

clean-dist:
	rm -rf dist
	find . -type f -name '*~' | xargs -r rm

check-manifest:
	check-manifest

check-version-tag:
	@if git tag -l | grep -E '^$(shell echo $${RELEASE_TAG} | sed 's|\.|.|g')$$' > /dev/null; then \
        echo "Version tag '${RELEASE_TAG}' already exists!"; \
        false; \
    fi

authors:

_pypi-release:
	poetry publish -r ${PYPI_REPO}


## Install
install: build
	poetry install --no-dev

install-dev: build
	poetry install


## Release
release: pre-release _freeze-release test-all dist _tag-release _pypi-release

pre-release: clean-autogen build install-dev info check-version-tag clean \
             test test-dist check-manifest authors  # changelog

BUMP ?= prerelease
bump-release: requirements
	poetry version $(BUMP)

requirements:
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


# Meta
info:
	@echo "VERSION: $(VERSION)"
	@echo "RELEASE_TAG: $(RELEASE_TAG)"
	@echo "RELEASE_NAME: $(RELEASE_NAME)"