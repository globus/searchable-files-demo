install: .venv
	.venv/bin/python setup.py -q develop
	rm -f searchable-files
	ln -s ".venv/bin/searchable-files" searchable-files

lint:
	pre-commit run -a

.venv:
	virtualenv --python=python3 .venv
	.venv/bin/python -m pip install -q -U pip setuptools

clean:
	find . -name '*.pyc' -delete
	rm -f searchable-files
	rm -rf .venv
	rm -rf dist
	rm -rf src/*.egg-info
