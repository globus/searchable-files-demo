install: .venv
	.venv/bin/python setup.py develop
	-rm searchable-files
	ln -s ".venv/bin/searchable-files" searchable-files

lint:
	pre-commit run -a

.venv:
	virtualenv --python=python3 .venv
	.venv/bin/python -m pip install -U pip setuptools

clean:
	find -name '*.pyc' -delete
	-rm searchable-files
	-rm -r .venv
	-rm -r dist
	-rm -r *.egg-info
