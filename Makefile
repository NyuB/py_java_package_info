PYTHON=python3

test:
	$(PYTHON) -m unittest package_info.py

fmt:
	black package_info.py

fmt-check:
	black --diff --check package_info.py
