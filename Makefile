.PHONY: verify note audit-note tuned-note reuse-note incidence-note dag-note shared-point-note paired-note compact-note complex-note fast-gaussian-note aligned-bit-note fetch

verify:
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
	python3 scripts/complex_network.py
	python3 scripts/make_complex_circuit_patch.py
	python3 scripts/fast_gaussian.py
	python3 scripts/make_fast_gaussian_patch.py
	python3 scripts/aligned_bit_network.py
	python3 scripts/make_aligned_bit_patch.py
	python3 scripts/prime_field_network.py
	python3 scripts/make_prime_field_patch.py
	python3 scripts/audit_kappa_targets.py
	python3 scripts/experiments/bit_breakthrough_affine_centers.py
	python3 scripts/experiments/label_breakthrough_polynomial_screen.py
	python3 scripts/experiments/assembly_breakthrough_guard.py --output certificates/assembly-breakthrough-guard.json
	python3 scripts/experiments/ternary_direction.py
	python3 scripts/experiments/ternary_depth_exchange.py --output certificates/ternary-depth.json
	python3 scripts/experiments/ternary_reuse_core2.py
	python3 scripts/ternary_reuse_network.py
	python3 scripts/ternary_fused_network.py
	python3 scripts/batched_stream_network.py
	python3 scripts/dimension30_stream_network.py
	python3 scripts/source_frame_stream_network.py --producer certificates/dimension30-stream-producer.json
	python3 scripts/experiments/complex_all_residuals.py --output certificates/complex-all-residuals.json
	python3 scripts/experiments/batched_role_targets.py --output certificates/batched-role-targets.json
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
	git apply --check --directory=upstream patches/complex-circuit-31.patch
	git apply --check --directory=upstream patches/fast-gaussian-30.patch
	git apply --check --directory=upstream patches/aligned-bit-30.patch
	git apply --check --directory=upstream patches/prime-field28.patch

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
	tectonic --outdir artifacts notes/complex-circuit-note.tex

fast-gaussian-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/fast-gaussian-note.tex

aligned-bit-note:
	mkdir -p artifacts
	tectonic --outdir artifacts notes/aligned-bit-note.tex

fetch:
	python3 scripts/fetch_upstream.py

.PHONY: nested-stream-verify
nested-stream-verify:
	python3 research/nested-stream/verify.py --full
	python3 research/nested-stream/make_patch.py
	python3 -m unittest discover -s tests -p test_nested_stream.py -v

.PHONY: partial-swap-ternary-verify
partial-swap-ternary-verify:
	python3 research/partial-swap-ternary/witness.py --full
	python3 research/partial-swap-ternary/make_patch.py
	python3 -m unittest discover -s tests -p test_partial_swap_ternary.py -v
