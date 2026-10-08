.PHONY: verify note audit-note tuned-note reuse-note incidence-note dag-note shared-point-note paired-note compact-note fetch

verify:
	$(MAKE) partial-swap-producer partial-swap-certificate
	python3 scripts/prime_field_network.py
	python3 scripts/complex_network.py
	python3 scripts/fast_gaussian.py
	$(MAKE) batched-certificate batched-patch
	python3 scripts/certify.py
	python3 scripts/search_network.py
	python3 scripts/make_patch.py
	python3 scripts/nonadjacent.py
	python3 scripts/make_nonadjacent_patch.py
	python3 scripts/tune_routing.py
	python3 scripts/research_networks.py
	python3 scripts/search_network_variants.py
	python3 scripts/block_label_targets.py
	python3 scripts/audit_block_labels.py
	python3 scripts/audit_additive_labels.py
	python3 scripts/small_block_witness.py
	python3 scripts/incidence_network.py
	python3 scripts/make_incidence_patch.py
	python3 scripts/search_incidence_partitions.py
	python3 scripts/dag_network.py
	python3 scripts/make_dag_patch.py
	python3 scripts/shared_point_network.py
	python3 scripts/make_shared_point_patch.py
	python3 scripts/paired_network.py
	python3 scripts/make_paired_patch.py
	python3 scripts/prepare_layers.py
	python3 scripts/audit_sparse_fusion.py
	python3 scripts/audit_fused_block.py
	python3 scripts/audit_short_guards.py
	python3 scripts/audit_gather_schedules.py
	python3 scripts/audit_coded_carries.py
	python3 scripts/audit_cancellation.py
	python3 scripts/audit_joint_frames.py
	python3 scripts/audit_compact_controls.py
	python3 scripts/compact_control_layer.py
	python3 scripts/make_compact_control_patch.py
	python3 scripts/audit_scratch_pooling.py
	python3 scripts/reuse_network.py
	python3 scripts/make_reuse_patch.py
	python3 -m unittest discover -s tests -v
	git apply --check --directory=upstream patches/frozen-154.patch
	git apply --check --directory=upstream patches/balanced-153.patch
	git apply --check --directory=upstream patches/same-network-129.patch
	git apply --check --directory=upstream patches/h46-111.patch
	git apply --check --directory=upstream patches/h46-109.patch
	git apply --check --directory=upstream patches/h46-108.patch
	git apply --check --directory=upstream patches/h46-rational.patch
	git apply --check --directory=upstream patches/nonadjacent-layout.patch
	git apply --check --directory=upstream patches/frozen-nonadjacent-107.patch
	git apply --check --directory=upstream patches/h46-nonadjacent-78.patch
	git apply --check --directory=upstream patches/h46-nonadjacent-76.patch
	git apply --check --directory=upstream patches/h46-shared-side-75.patch
	git apply --check --directory=upstream patches/h46-incidence-67.patch
	git apply --check --directory=upstream patches/h46-dag-63.patch
	git apply --check --directory=upstream patches/h46-shared-point.patch
	git apply --check --directory=upstream patches/h50-paired-59.patch
	git apply --check --directory=upstream patches/compact-control-34.patch
	git apply --check --directory=upstream patches/batched-23.patch

note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/parameter-note.tex

audit-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/nonadjacent-axis-note.tex

tuned-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/routing-tuned-note.tex

reuse-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/stage-reuse-note.tex

incidence-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/incidence-note.tex

dag-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/dag-note.tex

shared-point-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/shared-point-note.tex

paired-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/paired-note.tex

compact-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/compact-control-note.tex

fetch:
	python3 scripts/fetch_upstream.py

.PHONY: batched-certificate batched-patch batched-note
PDFLATEX ?= pdflatex
TEX_ENGINE ?= pdflatex
TECTONIC ?= tectonic

batched-certificate:
	python3 scripts/controlled_bit_rank_moment.py --output certificates/controlled-bit-rank-moment.json > /dev/null
	python3 scripts/batched_network.py --output certificates/batched-network.json --summary

batched-patch:
	python3 scripts/make_batched_patch.py

batched-note:
	mkdir -p artifacts
ifeq ($(TEX_ENGINE),tectonic)
	$(TECTONIC) -Z search-path=$(CURDIR) --outdir artifacts notes/batched-23-note.tex
else
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/batched-23-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/batched-23-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/batched-23-note.tex
endif

.PHONY: partial-swap-producer partial-swap-certificate partial-swap-note
partial-swap-producer:
	python3 scripts/partial_swap_producer.py

partial-swap-certificate:
	python3 scripts/partial_swap_network.py

partial-swap-note:
	mkdir -p artifacts
ifeq ($(TEX_ENGINE),tectonic)
	$(TECTONIC) -Z search-path=$(CURDIR) --outdir artifacts notes/partial-swap-note.tex
else
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/partial-swap-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/partial-swap-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/partial-swap-note.tex
endif
