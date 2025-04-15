.PHONY: install
install: .venv
	.venv/bin/python -m pip install .
	rm -f searchable-files
	ln -s ".venv/bin/searchable-files" searchable-files

.venv:
	virtualenv --python=python3 .venv
	.venv/bin/python -m pip install -q -U pip setuptools

.PHONY: clean
clean:
	find -name '*.pyc' -delete
	rm -f searchable-files
	rm -rf .venv
	rm -rf dist
	rm -rf src/*.egg-info
