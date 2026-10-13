.PHONY: verify lean exact paper

verify: lean exact

lean:
	lake build

exact:
	python3 verify_exact.py

paper:
	tectonic --outdir . gaussian-parity-certificates.tex
