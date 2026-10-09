.PHONY: test verify
COMPLEX_ROOT ?= ../../build/butterfly-complex193
BIT_ROOT ?= ../../build/butterfly-bit202
OUTPUT ?= ../../build/butterfly-v7-run

test:
	python3 -B -m unittest test_public -v

verify: test
	python3 -B verify.py --complex-root "$(COMPLEX_ROOT)" --bit-root "$(BIT_ROOT)" --output "$(OUTPUT)"
