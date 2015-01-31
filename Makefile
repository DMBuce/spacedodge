PYTHON_VERSION := 3.4

.PHONY: all
all: lineyspace deps

.PHONY: lineyspace
lineyspace: env/lib/python$(PYTHON_VERSION)/site-packages/lineyspace env/bin/lineyspace

.PHONY: deps
deps: env/lib/python$(PYTHON_VERSION)/site-packages/pygame

pygame:
	hg clone https://bitbucket.org/pygame/pygame

env:
	virtualenv -p python3 env

env/lib/python$(PYTHON_VERSION)/site-packages/pygame: env pygame
	./env/bin/python pygame/setup.py install || exit 0

env/lib/python$(PYTHON_VERSION)/site-packages/lineyspace: env
	./env/bin/python setup.py install

env/bin/lineyspace: env/lib/python$(PYTHON_VERSION)/site-packages/lineyspace/runner.py
	chmod +x env/lib/python$(PYTHON_VERSION)/site-packages/lineyspace/runner.py
	ln -s ../lib/python$(PYTHON_VERSION)/site-packages/lineyspace/runner.py env/bin/lineyspace

.PHONY: clean
clean:
	rm -rf build env

