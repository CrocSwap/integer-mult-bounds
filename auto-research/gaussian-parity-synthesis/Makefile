PYTHON ?= python3
.PHONY: verify lean exact image paper
verify: lean exact image
lean:
	lake build
exact:
	$(PYTHON) verify_phase_endpoint.py
	$(PYTHON) verify_precision_profile.py
image:
	$(PYTHON) verify_mixed_center_image.py --output work/image-audit
	$(PYTHON) verify_adapter.py --dag work/image-audit/mixed28.bin
paper:
	tectonic community-parity-synthesis.tex
