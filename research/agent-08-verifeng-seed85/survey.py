#!/usr/bin/env python3
"""Timing survey and exact-receipt benchmark harness (verification engineering).

Times one or more read-only repository checks end to end, in fresh processes,
and records wall time, exit code and the SHA-256 of each check's stdout/stderr.
Receipt digests are the exactness anchor: an accelerated adapter must produce
byte-identical check output.

Usage:
    python3 -B research/agent-08-verifeng-seed85/survey.py --list
    python3 -B research/agent-08-verifeng-seed85/survey.py --only audit_cancellation
    python3 -B research/agent-08-verifeng-seed85/survey.py --output evidence/survey.json
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]

# Candidate read-only checks (no producer/regenerator steps). Command arrays are
# run with cwd=ROOT under the calling interpreter.
CANDIDATES = {
    # scripts/audit_*.py historical finite searches (`make verify-research`)
    'audit_bit_compression': ['scripts/audit_bit_compression.py'],
    'audit_mixed_point': ['scripts/audit_mixed_point.py'],
    'audit_early_sharing': ['scripts/audit_early_sharing.py'],
    'audit_split_centers': ['scripts/audit_split_centers.py'],
    'audit_block_carry': ['scripts/audit_block_carry.py'],
    'audit_joint_return': ['scripts/audit_joint_return.py'],
    'audit_fano_completion': ['scripts/audit_fano_completion.py'],
    'audit_fano_permutation': ['scripts/audit_fano_permutation.py'],
    'audit_rank_product_core': ['scripts/audit_rank_product_core.py'],
    'audit_stronger_screens': ['scripts/audit_stronger_screens.py'],
    'audit_subset_cores': ['scripts/audit_subset_cores.py'],
    'audit_cube_cores': ['scripts/audit_cube_cores.py'],
    'audit_shared_core': ['scripts/audit_shared_core.py'],
    'audit_general_guard': ['scripts/audit_general_guard.py'],
    'audit_disjoint_tensor': ['scripts/audit_disjoint_tensor.py'],
    'audit_core_limits': ['scripts/audit_core_limits.py'],
    'audit_affine_vectors': ['scripts/audit_affine_vectors.py'],
    'audit_block_core': ['scripts/audit_block_core.py'],
    'audit_complex_centers': ['scripts/audit_complex_centers.py'],
    'audit_inplace_side': ['scripts/audit_inplace_side.py'],
    'audit_parity_side': ['scripts/audit_parity_side.py'],
    'audit_prime_subset_limits': ['scripts/audit_prime_subset_limits.py'],
    # scripts/audit_*.py certificate audits (`make verify-certificates`)
    'audit_fused_block': ['scripts/audit_fused_block.py'],
    'audit_short_guards': ['scripts/audit_short_guards.py'],
    'audit_gather_schedules': ['scripts/audit_gather_schedules.py'],
    'audit_coded_carries': ['scripts/audit_coded_carries.py'],
    'audit_cancellation': ['scripts/audit_cancellation.py'],
    'audit_compact_controls': ['scripts/audit_compact_controls.py'],
    'audit_scratch_pooling': ['scripts/audit_scratch_pooling.py'],
    'audit_block_labels': ['scripts/audit_block_labels.py'],
    'audit_additive_labels': ['scripts/audit_additive_labels.py'],
    # known-expensive references (claimed by concurrent PRs; timing only)
    'audit_quadratic_affine': ['scripts/audit_quadratic_affine.py'],
    'audit_sparse_fusion': ['scripts/audit_sparse_fusion.py'],
    'audit_joint_frames': ['scripts/audit_joint_frames.py'],
    'audit_stage_pair': ['scripts/audit_stage_pair.py'],
    'audit_signed_sparse': ['scripts/audit_signed_sparse.py'],
    'audit_single_intersection': ['scripts/audit_single_intersection.py'],
    'audit_cyclic_topology': ['scripts/audit_cyclic_topology.py'],
    'audit_positive_side': ['scripts/audit_positive_side.py'],
    # standalone historical closures
    'ranked_pair_check': ['research/ranked-pair-verification/verify.py'],
    'machine_transfer_check': ['research/machine-transfer-verification/verify.py'],
    'supplier_consolidation_components': [
        'scripts/verify_supplier_consolidation.py', '--component-tests'],
    'selected_record_check': ['scripts/verify_selected_result.py'],
    # remaining make-surface generators (verify-certificates / verify-ternary)
    'prime_field_network': ['scripts/prime_field_network.py'],
    'complex_network': ['scripts/complex_network.py'],
    'fast_gaussian': ['scripts/fast_gaussian.py'],
    'certify': ['scripts/certify.py'],
    'search_network': ['scripts/search_network.py'],
    'make_patch': ['scripts/make_patch.py'],
    'nonadjacent': ['scripts/nonadjacent.py'],
    'make_nonadjacent_patch': ['scripts/make_nonadjacent_patch.py'],
    'tune_routing': ['scripts/tune_routing.py'],
    'research_networks': ['scripts/research_networks.py'],
    'search_network_variants': ['scripts/search_network_variants.py'],
    'block_label_targets': ['scripts/block_label_targets.py'],
    'small_block_witness': ['scripts/small_block_witness.py'],
    'incidence_network': ['scripts/incidence_network.py'],
    'make_incidence_patch': ['scripts/make_incidence_patch.py'],
    'search_incidence_partitions': ['scripts/search_incidence_partitions.py'],
    'dag_network': ['scripts/dag_network.py'],
    'make_dag_patch': ['scripts/make_dag_patch.py'],
    'shared_point_network': ['scripts/shared_point_network.py'],
    'make_shared_point_patch': ['scripts/make_shared_point_patch.py'],
    'paired_network': ['scripts/paired_network.py'],
    'make_paired_patch': ['scripts/make_paired_patch.py'],
    'prepare_layers': ['scripts/prepare_layers.py'],
    'compact_control_layer': ['scripts/compact_control_layer.py'],
    'make_compact_control_patch': ['scripts/make_compact_control_patch.py'],
    'reuse_network': ['scripts/reuse_network.py'],
    'make_reuse_patch': ['scripts/make_reuse_patch.py'],
    'complex_compression': ['scripts/complex_compression.py'],
    'make_complex_compression_patch': ['scripts/make_complex_compression_patch.py'],
    'audit_ternary_side': ['scripts/audit_ternary_side.py'],
    'make_ternary_patch': ['scripts/make_ternary_patch.py'],
    'controlled_bit_rank_moment': ['scripts/controlled_bit_rank_moment.py',
                                   '--output', 'certificates/controlled-bit-rank-moment.json'],
    'batched_network': ['scripts/batched_network.py', '--output',
                        'certificates/batched-network.json', '--summary'],
    'audit_positive_skip_exact': ['scripts/audit_positive_skip_exact.py'],
    'audit_community_candidate_check': ['scripts/audit_community_candidate.py', '--check',
                                        'docs/research/community-audit-arithmetic.json'],
    'audit_followup_candidate_check': ['scripts/audit_followup_candidate.py', '--candidate-root',
                                       '.', '--check', 'docs/research/community-followup-arithmetic.json'],
    'audit_joint_candidate_check': ['scripts/audit_joint_candidate.py', '--check',
                                    'docs/research/community-round2-arithmetic.json'],
    'audit_pair_candidate_check': ['scripts/audit_pair_candidate.py', '--check',
                                   'docs/research/community-pair-arithmetic.json'],
    'pin_text_writes_check': ['research/agent-08-verifeng-seed85/pin_text_writes.py', '--check'],
}


def run_one(name, argv, timeout):
    cmd = [sys.executable, '-B'] + argv
    start = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=timeout)
        elapsed = time.monotonic() - start
        return dict(name=name, command=argv, seconds=round(elapsed, 3),
                    exit_code=proc.returncode, timed_out=False,
                    stdout_sha256=hashlib.sha256(proc.stdout).hexdigest(),
                    stderr_sha256=hashlib.sha256(proc.stderr).hexdigest(),
                    stdout_bytes=len(proc.stdout), stderr_bytes=len(proc.stderr))
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return dict(name=name, command=argv, seconds=round(elapsed, 3),
                    exit_code=None, timed_out=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--only', action='append', help='Run only these candidate names')
    p.add_argument('--repeat', type=int, default=1, help='Timed repetitions per candidate')
    p.add_argument('--timeout', type=float, default=600.0)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    names = a.only or list(CANDIDATES)
    unknown = [n for n in names if n not in CANDIDATES]
    if unknown:
        raise SystemExit(f'Unknown candidates: {unknown}')
    records = []
    for name in names:
        for rep in range(a.repeat):
            rec = run_one(name, CANDIDATES[name], a.timeout)
            rec['rep'] = rep
            records.append(rec)
            print(f"{name} rep{rep}: {rec['seconds']}s "
                  f"exit={rec.get('exit_code')} timeout={rec['timed_out']}", flush=True)
    if a.output:
        out = a.output if a.output.is_absolute() else ROOT / a.output
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(interpreter=sys.version, platform=sys.platform,
                       candidates={k: v for k, v in CANDIDATES.items() if k in names},
                       records=records)
        out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8', newline='\n')
        print('wrote', out)


if __name__ == '__main__':
    main()
