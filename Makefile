init:
	pip install -r requirements.txt

demo:
	python -m esoteric --gui examples/dna.befunge

.PHONY: init demo
