#!/usr/bin/env python3
"""Exact target alignment and a phase-corrected two-call prefix. Standard library only."""
from __future__ import annotations
import argparse
import hashlib
import types
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PINS = {
    'vendor/pr4688/verify.py': '99ff0beccd9a4e94cc607e02114d62b8ce0ea57ee00748b07ce0a0af91aec85e',
    'vendor/pr4688/README.md': '91d45b5af6063e30c6860a4cb46cfc44960ecd67f37c3bce9675924e30b89b4e',
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def load_engine():
    authenticated = {}
    for path, digest in PINS.items():
        payload = (ROOT / path).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == digest,
                'changed immutable predecessor: ' + path)
        authenticated[path] = payload
    path = ROOT / 'vendor/pr4688/verify.py'
    module = types.ModuleType('pinned_pr4688')
    module.__file__ = str(path)
    # Compile the exact authenticated bytes; never consult an existing .pyc.
    exec(compile(authenticated['vendor/pr4688/verify.py'], str(path), 'exec'), module.__dict__)
    return module

def monomial_compose(a, b):
    return (tuple(a[0][b[0][x]] for x in range(8)),
            tuple((b[1][x] + a[1][b[0][x]]) % 4 for x in range(8)))

def monomial_inverse(a):
    p = tuple(a[0].index(x) for x in range(8))
    return p, tuple(-a[1][p[x]] % 4 for x in range(8))

def monomial_checks(m):
    identity = (tuple(range(8)), (0,) * 8)
    phase = (identity[0], tuple(x.bit_count() % 4 for x in range(8)))
    u, v = (tuple(m.U_PERM), identity[1]), (tuple(m.V_PERM), identity[1])
    P = monomial_compose(phase, monomial_compose(u, phase))
    Q = monomial_compose(phase, monomial_compose(v, phase))
    ratio = monomial_compose(monomial_inverse(P), Q)
    power = identity
    powers = []
    for k in range(4):
        powers.append(power)
        power = monomial_compose(ratio, power)
    require(power == identity and all(x != identity for x in powers[1:]), 'ratio order is not four')
    # The ratio equals S^{-1} U^{-1} V S as an actual monomial, not merely projectively.
    conjugate = monomial_compose(monomial_inverse(phase),
                    monomial_compose(monomial_inverse(u), monomial_compose(v, phase)))
    require(ratio == conjugate, 'ratio conjugacy')
    traces = []
    for p, e in powers:
        trace = (0, 0)
        for x in range(8):
            if p[x] == x:
                trace = m.add(trace, m.I_POWERS[e[x]])
        traces.append(trace)
    require(traces == [(8, 0), (2, 0), (4, 0), (2, 0)], 'ratio traces')
    # Exact polynomial multiplication, reduced using R^4 = I.
    product = [0] * 4
    for degree, coefficient in enumerate((1, -2, 4, -8)):
        product[degree] += coefficient
        product[(degree + 1) % 4] += 2 * coefficient
    require(product == [-15, 0, 0, 0], 'all-width inverse polynomial')
    bad_phases = list(ratio[1])
    bad_phases[1] = (bad_phases[1] + 1) % 4
    bad_ratio = (ratio[0], tuple(bad_phases))
    bad_power = identity
    for _ in range(4):
        bad_power = monomial_compose(bad_ratio, bad_power)
    require(bad_power != identity, 'wrong monomial phase must fail fourth-power check')
    return {'P': {'permutation': P[0], 'phase_exponents_mod4': P[1]},
            'Q': {'permutation': Q[0], 'phase_exponents_mod4': Q[1]},
            'R': {'permutation': ratio[0], 'phase_exponents_mod4': ratio[1]},
            'R_order': 4, 'traces_R_powers': traces,
            'eigenvalue_multiplicities_1_minus1_i_minusi': [4, 2, 1, 1],
            'inverse_polynomial_product': product,
            'negative_control': 'one changed R phase fails R^4=I'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write the deterministic exact report')
    parser.add_argument('--check', type=Path, help='require exact equality with a stored JSON report')
    args = parser.parse_args()
    m = load_engine()
    # Unchanged predecessor replay includes independent exterior-minor calibration,
    # the paid-call cap and target ranks, and its seven negative controls.
    m.main()
    D = m.lift_direction(1)
    K = m.compose(m.lift_direction(4), m.compose(m.lift_direction(2), D))
    phases = [m.I_POWERS[(x.bit_count() + sum(t.bit_count() for t in subset)) % 4]
              for x, subset in m.BASIS]
    def phase_columns(columns):
        return [{i: m.mul(phases[i], value) for i, value in column.items()} for column in columns]
    def repaired_branch(permutation):
        return m.compose(D, phase_columns(m.apply_permutation(permutation, phase_columns(D))))
    def complex_scale(columns, coefficient):
        return [{i: m.mul(coefficient, value) for i, value in column.items()} for column in columns]
    old_A = m.compose(D, m.apply_permutation(m.U_PERM, D))
    old_B = m.compose(D, m.apply_permutation(m.V_PERM, D))
    old = m.add_columns(old_A, m.scale_columns(old_B, 2))
    A, B = repaired_branch(m.U_PERM), repaired_branch(m.V_PERM)
    new = m.add_columns(A, m.scale_columns(B, 2))
    pencil = [m.add_columns(A, complex_scale(B, coefficient))
              for coefficient in ((2, 0), (-2, 0), (0, 2), (0, -2))]
    records = []
    print('mask oldPhi oldJoint newPhi newJoint branchJoints pencilRanks', flush=True)
    for mask in m.CUTS:
        inside = m.cut_indices(mask)
        target = m.project(K, inside)
        old_rows, new_rows = m.project(old, inside), m.project(new, inside)
        old_phi, new_phi = m.rank_exact(old_rows), m.rank_exact(new_rows)
        # Put the structured target rows first to keep Gaussian intermediates small.
        old_joint = m.rank_exact(target + old_rows)
        new_joint = m.rank_exact(target + new_rows)
        branch_joints = [m.rank_exact(target + m.project(branch, inside)) for branch in (A, B)]
        pencil_ranks = [m.rank_exact(m.project(value, inside)) for value in pencil]
        expected_old_joint = 280 if mask in (3, 6, 7) else 224
        require((old_phi, old_joint, new_phi, new_joint) == (160, expected_old_joint, 160, 224),
                'prefix/target alignment at mask ' + str(mask))
        require(branch_joints == [224, 224], 'termwise all-width alignment at mask ' + str(mask))
        require(pencil_ranks == [160] * 4, 'four-point pencil at mask ' + str(mask))
        record = {'mask': mask, 'N_dimension': len(inside), 'target_rank': 224,
                  'old_prefix_rank': old_phi, 'old_target_joint_rank': old_joint,
                  'old_missing_target_dimensions': old_joint - old_phi,
                  'new_prefix_rank': new_phi, 'new_target_joint_rank': new_joint,
                  'new_missing_target_dimensions': new_joint - new_phi,
                  'new_single_branch_target_joint_ranks': branch_joints,
                  'new_pencil_ranks_coefficients_2_minus2_2i_minus2i': pencil_ranks,
                  'width6_lifted_prefix_rank': sum(w*r for w,r in zip((4,2,1,1), pencil_ranks)),
                  'width6_lifted_target_and_joint_rank': 8 * 224}
        records.append(record)
        print(mask, old_phi, old_joint, new_phi, new_joint, branch_joints, pencil_ranks, flush=True)
    require(records[1]['old_missing_target_dimensions'] + 4 * 224 == 1016,
            'five-array remaining deficit')
    require(1016 > 12 * 80, 'original prefix obstruction')
    require(records[1]['new_missing_target_dimensions'] + 4 * 224 == 12 * 80,
            'repaired remaining deficit')
    monomials = monomial_checks(m)
    residual_path = ROOT / 'verify_residual.py'
    residual = types.ModuleType('independent_residual')
    residual.__file__ = str(residual_path)
    exec(compile(residual_path.read_bytes(), str(residual_path), 'exec'), residual.__dict__)
    residual_report = residual.verify()
    report = {'schema_version': 1,
              'source_pr': 4688, 'source_head': '264c4b3cb13c82d171de352ecf60486dfb8d2bd4',
              'source_sha256': PINS,
              'scope': 'two-call prefix and necessary continuation conditions; no completed unit or new exponent',
              'arithmetic': 'Gaussian integer elimination over Q(i), no numerical rank tolerance',
              'cuts': records, 'monomial_inverse': monomials,
              'exact_residual_interface': residual_report,
              'all_extra_widths': {'extra_width_variable': 'r >= 0',
                 'prefix_rank_each_lifted_cut': '160*8^r',
                 'target_and_joint_rank_each_lifted_cut': '224*8^r',
                 'proof': 'four eigenvalues of relative branch matrix; four-point pencil ranks and termwise kernel inclusion'},
              'original_five_array_remaining_deficit': 1016,
              'remaining_twelve_call_capacity': 960,
              'repaired_five_array_remaining_deficit': 960,
              'result': 'PASS'}
    # Normalize tuples before comparing the JSON encoding.
    report = json.loads(json.dumps(report))
    if args.check:
        require(json.loads(args.check.read_text()) == report, 'stored report mismatch')
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('PASS_PHASE_PREFIX_TARGET_ALIGNMENT', flush=True)

if __name__ == '__main__':
    main()
