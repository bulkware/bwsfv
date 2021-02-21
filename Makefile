scripts := $(wildcard src/*.py)
tests := $(wildcard tests/*.py)

all: clean checkstyle dist

checkstyle: $(scripts) $(tests) setup.py
	find . -name "*.py" -exec pycodestyle \{\} \; | tee checkstyle

dist: $(scripts) $(tests) setup.py
	python3 setup.py sdist --format=gztar

clean:
	find . -name "*.pyc" -delete
	rm -rf *.egg-info
	rm -rf dist
	rm -f checkstyle
