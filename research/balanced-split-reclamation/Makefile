.PHONY: verify replay test note

verify:
	python3 -B verify.py --rebuild
	python3 -B -m unittest discover -s . -p test_witness.py -v

replay:
	python3 -B verify.py

test:
	python3 -B -m unittest discover -s . -p test_witness.py -v

note:
	mkdir -p ../../build/balanced-split-reclamation/pdf
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../build/balanced-split-reclamation/pdf paper.tex
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../../build/balanced-split-reclamation/pdf paper.tex
	cp ../../build/balanced-split-reclamation/pdf/paper.pdf paper.pdf
