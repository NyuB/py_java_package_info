PYTHON=python3

type-check:
	$(PYTHON) -m mypy package_info.py

test:
	$(PYTHON) -m unittest package_info.py

fmt:
	black package_info.py

fmt-check:
	black --diff --check package_info.py
