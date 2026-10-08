.PHONY: verify note audit-note tuned-note reuse-note incidence-note dag-note shared-point-note paired-note compact-note complex-note ternary-note fetch
.DEFAULT_GOAL := verify

.PHONY: community-audit-check
community-audit-check:
	python3 scripts/audit_community_candidate.py --check docs/research/community-audit-arithmetic.json

.PHONY: community-followup-check
community-followup-check:
	python3 scripts/audit_followup_candidate.py --candidate-root . --check docs/research/community-followup-arithmetic.json

.PHONY: verify-community verify-producers verify-certificates verify-ternary verify-tests
# CI runs these in separate checkouts. Keep local verification sequential:
# different groups regenerate certificates that another group may read.
verify:
	$(MAKE) verify-community
	$(MAKE) verify-producers
	$(MAKE) verify-certificates
	$(MAKE) verify-ternary
	$(MAKE) verify-research
	$(MAKE) verify-strips
	$(MAKE) verify-clones
	$(MAKE) verify-positive
	$(MAKE) verify-joint
	$(MAKE) verify-pair
	$(MAKE) verify-tests

verify-community: community-audit-check community-followup-check copied-reversed-producer copied-reversed-check copied-fixed-reversed-producer copied-fixed-reversed-check
	$(MAKE) copied-fixed-verify
	$(MAKE) climbed-48-verify

verify-producers:
	$(MAKE) stopped-product-verify
	$(MAKE) copied-centers-verify
	$(MAKE) structured-bulk-verify
	$(MAKE) endpoint-gauge-producer endpoint-gauge-certificate
	$(MAKE) partial-swap-producer partial-swap-certificate

verify-certificates:
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

verify-ternary:
	python3 scripts/complex_compression.py
	python3 scripts/make_complex_compression_patch.py
	python3 scripts/audit_ternary_side.py
	python3 scripts/make_ternary_patch.py

verify-tests:
	python3 scripts/run_isolated_tests.py
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
	git apply --check --directory=upstream patches/complex-compression-31.patch
	git apply --check --directory=upstream patches/ternary-30.patch
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

complex-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/complex-compression-note.tex

ternary-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/ternary-note.tex

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

.PHONY: endpoint-gauge-producer endpoint-gauge-certificate endpoint-gauge-note
endpoint-gauge-producer:
	python3 scripts/endpoint_gauge_producer.py

endpoint-gauge-certificate:
	python3 scripts/endpoint_gauge_network.py

endpoint-gauge-note:
	mkdir -p artifacts
ifeq ($(TEX_ENGINE),tectonic)
	$(TECTONIC) -Z search-path=$(CURDIR) --outdir artifacts notes/endpoint-gauge-note.tex
else
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/endpoint-gauge-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/endpoint-gauge-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/endpoint-gauge-note.tex
endif

.PHONY: endpoint-gauge-verify
endpoint-gauge-verify: endpoint-gauge-producer endpoint-gauge-certificate
	python3 -m unittest discover -s tests -p 'test_endpoint_gauge.py' -v

.PHONY: structured-bulk-producer structured-bulk-certificate structured-bulk-verify structured-bulk-note
structured-bulk-producer:
	python3 scripts/structured_bulk_producer.py

structured-bulk-certificate:
	python3 scripts/structured_bulk_network.py

structured-bulk-verify: structured-bulk-producer structured-bulk-certificate

structured-bulk-note:
	mkdir -p artifacts
ifeq ($(TEX_ENGINE),tectonic)
	$(TECTONIC) -Z search-path=$(CURDIR) --outdir artifacts notes/structured-bulk-note.tex
else
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/structured-bulk-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/structured-bulk-note.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error -output-directory=artifacts notes/structured-bulk-note.tex
endif

.PHONY: copied-centers-producer copied-centers-certificate copied-centers-verify
copied-centers-producer:
	python3 scripts/copied_centers_producer.py

copied-centers-certificate:
	python3 scripts/copied_centers_network.py

copied-centers-verify: copied-centers-producer copied-centers-certificate

.PHONY: copied-reversed-check copied-reversed-producer
copied-reversed-check:
	python3 research/copied-reversed/geometry.py
	python3 research/copied-reversed/witness.py
	python3 -m unittest discover -s tests -p 'test_copied_reversed.py' -v

copied-reversed-producer:
	mkdir -p build/copied-reversed/producer
	python3 scripts/copied_centers_producer.py --work-dir build/copied-reversed/producer --output build/copied-reversed/producer.json


.PHONY: copied-fixed-reversed-check copied-fixed-reversed-producer
copied-fixed-reversed-check:
	python3 research/copied-fixed-reversed/geometry.py --full
	python3 research/copied-fixed-reversed/witness.py
	python3 -m unittest discover -s tests -p 'test_copied_fixed_reversed.py'

copied-fixed-reversed-producer:
	mkdir -p build/copied-fixed-reversed/producer
	python3 research/copied-fixed-reversed/producer.py --work-dir build/copied-fixed-reversed/producer --output build/copied-fixed-reversed/producer.json
	python3 research/copied-fixed-reversed/review/fixed25_copied_crt_audit.py --work-dir build/copied-fixed-reversed/producer --record build/copied-fixed-reversed/producer.json --profiler-source research/copied-fixed-reversed/full_profiles25.cpp --output build/copied-fixed-reversed/crt-audit.json


.PHONY: copied-fixed-verify copied-fixed-producer copied-fixed-check
copied-fixed-producer:
	python3 research/copied-fixed/producer.py

copied-fixed-check:
	python3 research/copied-fixed/audit.py
	python3 research/copied-fixed/verify.py --output research/copied-fixed/certificate.json
	python3 -m unittest discover -s tests -p 'test_copied_fixed.py' -v

copied-fixed-verify: copied-fixed-producer copied-fixed-check

.PHONY: climbed-48-verify climbed-48-producer climbed-48-check
climbed-48-producer:
	python3 research/climbed-48/producer.py

climbed-48-check:
	python3 research/climbed-48/witness.py --output research/climbed-48/certificate.json
	python3 -m unittest discover -s tests -p 'test_climbed_48.py' -v

climbed-48-verify: climbed-48-producer climbed-48-check

.PHONY: formal-verify formal-historical-verify formal-gaussian-verify
formal-verify: formal-historical-verify formal-gaussian-verify

formal-historical-verify:
	cd formal/lean && lake build
	python3 scripts/check_lean_axioms.py --project formal/lean --audit formal/lean/AuditAll.lean
	python3 formal/lean/sources.py
	python3 formal/open-prs/drift_A.py
	python3 formal/open-prs/drift_B.py --selftest
	python3 formal/open-prs/drift_C.py
	mkdir -p build/formal
	python3 formal/circuit/export_paired.py build/formal/paired50.json
	python3 -I formal/circuit/check_paired.py build/formal/paired50.json

formal-gaussian-verify:
	$(MAKE) -C research/gaussian-parity-synthesis verify
	python3 scripts/check_lean_axioms.py --project research/gaussian-parity-synthesis --audit research/gaussian-parity-synthesis/AuditAll.lean

.PHONY: verify-research
# Historical finite searches; no current witness or production certificates change.
verify-research:
	python3 scripts/audit_bit_compression.py
	python3 scripts/audit_mixed_point.py
	python3 scripts/audit_early_sharing.py
	python3 scripts/audit_split_centers.py
	python3 scripts/audit_stage_pair.py
	python3 scripts/audit_block_carry.py
	python3 scripts/audit_joint_return.py
	python3 scripts/audit_cyclic_topology.py
	python3 scripts/audit_fano_completion.py
	python3 scripts/audit_fano_permutation.py
	python3 scripts/audit_rank_product_core.py
	python3 scripts/audit_stronger_screens.py
	python3 scripts/audit_subset_cores.py
	python3 scripts/audit_cube_cores.py
	python3 scripts/audit_single_intersection.py
	python3 scripts/audit_shared_core.py
	python3 scripts/audit_general_guard.py
	python3 scripts/audit_disjoint_tensor.py
	python3 scripts/audit_core_limits.py
	python3 scripts/audit_affine_vectors.py
	python3 scripts/audit_block_core.py
	python3 scripts/audit_complex_centers.py
	python3 scripts/audit_inplace_side.py
	python3 scripts/audit_quadratic_affine.py
	python3 scripts/audit_signed_sparse.py
	python3 scripts/audit_positive_side.py
	python3 scripts/audit_parity_side.py
	python3 scripts/audit_prime_subset_limits.py
.PHONY: skip-frame-verify
skip-frame-verify:
	python3 scripts/experiments/verify_skip_frame.py


.PHONY: joint-dual-verify
joint-dual-verify:
	python3 scripts/experiments/verify_joint_dual.py
	python3 -m unittest discover -s tests -p 'test_joint_reclaim.py' -v


.PHONY: skip-strips-verify skip-strips-producer skip-strips-check
skip-strips-producer:
	python3 research/skip-strips/producer.py

skip-strips-check:
	python3 research/skip-strips/audit.py
	python3 research/skip-strips/verify.py --output research/skip-strips/certificate.json
	cd research/skip-strips && python3 -m unittest discover -s ../../tests -p 'test_skip_strips.py' -v

skip-strips-verify: skip-strips-producer skip-strips-check

.PHONY: positive-skip-verify positive-skip-build positive-skip-check
positive-skip-build:
	python3 scripts/audit_positive_skip_exact.py

positive-skip-check:
	python3 research/positive-skip/witness.py --output research/positive-skip/certificate.json
	python3 -m unittest discover -s tests -p 'test_positive_skip.py' -v

positive-skip-verify: positive-skip-build positive-skip-check

.PHONY: split-skip-producer split-skip-check split-skip-verify
split-skip-producer:
	python3 research/split-skip/producer.py --work-dir build/split-skip --output build/split-skip-receipt.json

split-skip-check:
	python3 research/split-skip/witness.py
	python3 research/split-skip/independent_arithmetic.py
	python3 -m unittest discover -s tests -p 'test_split_skip.py' -v

split-skip-verify: split-skip-producer split-skip-check

.PHONY: skip-suffix-verify skip-suffix-producer skip-suffix-check
skip-suffix-producer:
	python3 research/skip-suffix/producer.py

skip-suffix-check:
	python3 research/skip-suffix/audit.py
	python3 research/skip-suffix/verify.py --output research/skip-suffix/certificate.json
	cd research/skip-suffix && python3 -m unittest discover -s ../../tests -p 'test_skip_suffix.py' -v

skip-suffix-verify: skip-suffix-producer skip-suffix-check

.PHONY: skip-clones-verify skip-clones-producer skip-clones-check
skip-clones-producer:
	python3 research/skip-clones/producer.py

skip-clones-check:
	python3 research/skip-clones/witness.py --output research/skip-clones/certificate.json
	python3 -m unittest discover -s tests -p 'test_skip_clones.py' -v

skip-clones-verify: skip-clones-producer skip-clones-check

.PHONY: verify-strips verify-clones verify-positive verify-joint formal-matrix-verify
verify-strips: skip-strips-verify skip-suffix-verify
verify-clones: skip-clones-verify split-skip-verify
verify-positive: positive-skip-verify
verify-joint: skip-frame-verify joint-dual-verify
	python3 scripts/audit_joint_candidate.py --check docs/research/community-round2-arithmetic.json

formal-verify: formal-matrix-verify
formal-matrix-verify:
	mkdir -p build
	cd research/matrix-exponent-synthesis && lake build
	python3 scripts/check_lean_axioms.py --project research/matrix-exponent-synthesis --audit research/matrix-exponent-synthesis/AuditAll.lean
	python3 research/matrix-exponent-synthesis/run_checks.py --work "$$(mktemp -d build/matrix-synthesis.XXXXXX)"
	python3 scripts/audit_joint_candidate.py --check docs/research/community-round2-arithmetic.json
	python3 scripts/audit_pair_candidate.py --check docs/research/community-pair-arithmetic.json

.PHONY: pair-assembly-verify pair-assembly-producer pair-assembly-check
pair-assembly-producer:
	python3 research/pair-assembly/producer.py

pair-assembly-check:
	python3 research/pair-assembly/audit.py
	python3 research/pair-assembly/verify.py --output research/pair-assembly/certificate.json
	python3 research/pair-assembly/frame/frame_verify.py
	cd research/pair-assembly && python3 -m unittest discover -s ../../tests -p 'test_pair_assembly.py' -v

pair-assembly-verify: pair-assembly-producer pair-assembly-check

.PHONY: verify-pair
verify-pair: pair-assembly-verify
	python3 scripts/audit_pair_candidate.py --check docs/research/community-pair-arithmetic.json

.PHONY: stopped-product-producer stopped-product-certificate stopped-product-verify
stopped-product-producer:
	python3 scripts/stopped_product_producer.py

stopped-product-certificate:
	python3 scripts/stopped_product_network.py

stopped-product-verify: stopped-product-producer stopped-product-certificate
