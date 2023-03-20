stuff: clean build check install

build:
	@python -m build

clean:
	@rm -rf dist && rm -rf build && rm -rf *.egg-info

install:
	@pip uninstall django-milli -y && pip install dist/*.whl

upload:
	@twine upload dist/*

check:
	@twine check dist/*