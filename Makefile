init:
	pip install -r requirements.txt

demo:
	python -m esoteric --gui examples/dna.befunge

rec:
	SHELL=./befunge_demo.sh asciinema rec

.PHONY: init demo
