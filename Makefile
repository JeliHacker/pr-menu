.PHONY: dev test

dev:
	python3 -m pr_menu

test:
	python3 -m unittest discover -s tests -v
