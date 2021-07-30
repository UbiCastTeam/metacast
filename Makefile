lint:
	flake8 .

test:
	python3 -m unittest discover tests/ -v
