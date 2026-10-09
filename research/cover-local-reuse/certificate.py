#!/usr/bin/env python3
"""Exact composition of optimized physical local reuse with PR130/PR132 cover.

PR130 Cayley cover and weighted bit interface: icekylinx, with OpenAI
GPT-6 Astra/Codex assistance. Paired lockstep first-stage cover: Avi Eisenberg
(ikeboy, PR132) with Anthropic Claude assistance. Physical gate frames and
compensated birth-cut reuse integration: eumemic (PR129/PR131) with OpenAI
Codex assistance and jamesyc (PR124). Radical-complement lifting, phase-aware
role compilation, donor-chain shrinking, recipient frame snapping, and
per-bank literal reflection audit: Thomas Marchand (PR133) with Google
Antigravity assistance. PR117, PR124, PR130, PR131, PR132, PR134 and all
source notices retained. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / 'research/cyclic-deferred'
sys.path.insert(0, str(ROOT / 'scripts'))
import three_stage_cover_network as inherited
from partial_swap_network import moment
from structured_bulk_assembly import assembly, js
KGRID = 10**15
BGRID = 10**12
STOP = Q(1, 10**6)


def load(name): return json.loads((LOCAL / name).read_text())
def digest(path): return sha256(path.read_bytes()).hexdigest()


def cover_profile():
    local = load('complex-profile.json'); audit = load('reflection-audit.json')
    geom = json.loads((HERE / 'geometry-audit.json').read_text())
    h, v, R = (local[k] for k in ('h', 'v', 'R'))
    assert (h, v, R) == (24, 2024, 26549)
    assert local['virtual_R'] == 28705 and local['reused_roles'] == 2156
    assert audit['R'] == R and audit['virtual_R'] == local['virtual_R'] and audit['reused_roles'] == local['reused_roles']
    for key in ('child_multiplicities', 'physical_auxiliary_source_frames',
                'source_data_histogram', 'target_data_histogram', 'internal_role_histogram'):
        assert audit[key] == local[key], key
    for key in ('exact_arbitrary_dirty_cancellation_by_dependency_cut', 'physical_aliased_numeric_replay',
                'exact_birth_cut_invariants', 'literal_frame_incidences_both_directions',
                'reflected_residual_rank_histogram_equal', 'completed_core_source_inventory_bound',
                'completed_core_pre_exterior_frames_full', 'reflected_core_active_frames_complement_source',
                'bounded_chunk_coefficients'):
        assert audit[key] is True, key
    assert geom['stage1_pairing_involution_checked'] is True and geom['actual_h24_port_triples_checked'] == v
    assert audit['source_sha256'] == digest(LOCAL / 'complex_deferred.py')
    assert audit['audit_sha256'] == digest(LOCAL / 'reflection_audit.py')
    inventory = local['physical_auxiliary_source_frames']
    assert sum(row['count'] for row in inventory) == R
    N = v * v
    remaining = Counter({int(r): n for r, n in local['child_multiplicities'].items()})
    # Remove exactly the two-stage data bridges, endpoint copies and exterior
    # class. All physical source/target moves and copied centers stay local.
    removed = Counter({(h - 1)**2: 2 * N, 1: N})
    for row in inventory:
        removed[h * h - h + len(row['basis'])] += 2 * v * row['count']
    remaining.subtract(removed)
    assert all(type(n) is int and n >= 0 and n % (2 * v) == 0 for n in remaining.values())
    H = {r: n // (2 * v) for r, n in remaining.items() if n}
    assert all(0 < r < h for r in H)
    src_data = Counter({int(r): n for r, n in local['source_data_histogram'].items()})
    tgt_data = Counter({int(r): n for r, n in local['target_data_histogram'].items()})
    H_int = Counter({int(r): n for r, n in local['internal_role_histogram'].items()})
    assert src_data == Counter({h - 1: v})
    assert all(0 < r < h and n > 0 for r, n in tgt_data.items())
    assert all(0 < r <= h and n > 0 for r, n in H_int.items())
    assert Counter(H) == src_data + tgt_data + H_int
    m = 3 * h - 2; w = 2 * v + 3 * R; ell = h * (h - 1)
    children = Counter({r: 3 * n for r, n in H.items()})
    exteriors = Counter()
    for row in inventory:
        exteriors[m - h + len(row['basis'])] += 3 * row['count']
    children.update(exteriors)
    rank = sum(r * n for r, n in children.items())
    assert w * m - rank == 2 * v - 3 * ell == 2392
    assert max(children) == 68 and all(0 < r < m and n > 0 for r, n in children.items())

    # Paired lockstep first-stage cover (PR132): coordinate involution exchanging
    # e_i and e_{24+i} for i < 24 maps A into B + C orthogonally to A.
    perm = list(range(m))
    for i in range(h): perm[i], perm[h + i] = h + i, i
    assert all(perm[perm[x]] == x for x in range(m))
    assert all(perm[i] >= h for i in range(h))
    w2 = 4 * v + 5 * R
    paired_exteriors = Counter()
    for row in inventory:
        d = len(row['basis'])
        paired_exteriors[m - 2 * h + 2 * d] += row['count']
        paired_exteriors[m - h + d] += 4 * row['count']
    paired_children = Counter(paired_exteriors)
    for r, n in H_int.items():
        paired_children[2 * r] += n
        paired_children[r] += 4 * n
    for r, n in (src_data + tgt_data).items():
        paired_children[r] += 6 * n
    rank2 = sum(r * n for r, n in paired_children.items())
    assert w2 * m - rank2 == 2 * (2 * v - 3 * ell) == 4784
    assert max(paired_children) == 68 and all(0 < r < m and n > 0 for r, n in paired_children.items())
    paired_per_pair = dict(roles_per_pair=w2, rank_per_pair=rank2, deficit_per_pair=w2 * m - rank2,
        maxchild=max(paired_children), exterior_child_multiplicities=dict(sorted(paired_exteriors.items())),
        child_multiplicities=dict(sorted(paired_children.items())))

    return dict(h=h, v=v, R=R, virtual_R=local['virtual_R'], reused_roles=local['reused_roles'],
        m=m, roles_per_vertex=w, rank_per_vertex=rank, deficit_per_vertex=w * m - rank,
        maxchild=max(children), center_loss_per_invocation=ell,
        source_data_histogram=dict(sorted(src_data.items())),
        target_data_histogram=dict(sorted(tgt_data.items())),
        internal_role_histogram=dict(sorted(H_int.items())),
        local_child_multiplicities=dict(sorted(H.items())),
        removed_two_stage_child_multiplicities=dict(sorted(removed.items())),
        exterior_child_multiplicities=dict(sorted(exteriors.items())),
        child_multiplicities=dict(sorted(children.items())),
        paired_per_pair=paired_per_pair,
        local_profile_sha256=digest(LOCAL / 'complex-profile.json'),
        reflection_receipt_sha256=digest(LOCAL / 'reflection-audit.json'),
        geometry_audit_sha256=digest(HERE / 'geometry-audit.json'))


def solve_saving(m, w, children):
    def contracts(n):
        try: moment(m, w, children, Q(n, BGRID), True)
        except ValueError: return False
        return True
    lo, hi = 0, 10**9
    assert contracts(lo) and not contracts(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if contracts(mid): lo = mid
        else: hi = mid
    b = Q(lo, BGRID)
    return b, moment(m, w, children, b, True)


def solve_assembly(b, bridge):
    a = min(inherited.AB, (1 - STOP) * b - Q(1, 10**14))
    def accepts(n):
        try: assembly(a, b, bridge, Q(n, KGRID), beta=STOP)
        except AssertionError: return False
        return True
    low, high = 0, int(b * KGRID) + 1
    assert accepts(low) and not accepts(high)
    while high - low > 1:
        mid = (low + high) // 2
        if accepts(mid): low = mid
        else: high = mid
    k = Q(low, KGRID)
    result = assembly(a, b, bridge, k, beta=STOP)
    assert not accepts(low + 1)
    assert len(result['strict_constraints']) == 47 and len(result['margins']) == 7
    return a, k, result


def exact():
    p = cover_profile(); m = p['m']
    n = m // 2
    vertices = 2**(m - 1 + (n - 1)**2) * prod(2**(2 * i) - 1 for i in range(1, n))
    assert vertices % 2 == 0
    row = json.loads((ROOT / 'certificates/three-stage-cover-complex-input.json').read_text())
    assert row['R'] == p['virtual_R'] and row['total_M_operations'] == 118451
    audit = load('reflection-audit.json')
    bit = inherited.bit_certificate(json.loads((ROOT / 'certificates/three-stage-cover-bit-input.json').read_text()))

    # 1. Unpaired three-stage cover certificate (direct comparison with PR130 / PR131)
    w1, children1 = p['roles_per_vertex'], p['child_multiplicities']
    b_unpaired, cm_unpaired = solve_saving(m, w1, children1)
    phase_unpaired = dict(m=m, N=vertices * p['v'], W=vertices * w1, total_rank=vertices * p['rank_per_vertex'],
        deficit=vertices * p['deficit_per_vertex'], vertices_per_stage=vertices, maxchild=p['maxchild'],
        group_order_bits=vertices.bit_length(), per_vertex=p, **cm_unpaired)
    bridge_unpaired = inherited.finite_bridge(phase_unpaired, row)
    assert bridge_unpaired['complex']['local_group_upper'] >= audit['conservative_local_G'] >= audit['expanded_scalar_operations_per_stage']
    bridge_unpaired['complex'].update(physical_R=p['R'], virtual_R=p['virtual_R'],
        independently_audited_local_scalar_operations=audit['expanded_scalar_operations_per_stage'],
        local_scalar_guard_from_reflection=audit['conservative_local_G'],
        scalar_contract='Virtual-role reserve covers all compensated readouts and inverse chronology; actual persistent stock and finite routers use physical roles.')
    a_unpaired, k_unpaired, result_unpaired = solve_assembly(b_unpaired, bridge_unpaired)
    unpaired_cover = dict(kappa=k_unpaired, complex_saving=b_unpaired, assembly_bit_saving=a_unpaired,
        actual_bit_saving=inherited.AB, complex=phase_unpaired, finite_bridge=bridge_unpaired, assembly=result_unpaired)

    # 2. Paired lockstep first-stage cover certificate (PR132 + optimized physical local reuse)
    pp = p['paired_per_pair']
    w2, children2, rank2 = pp['roles_per_pair'], pp['child_multiplicities'], pp['rank_per_pair']
    b_paired, cm_paired = solve_saving(m, w2, children2)
    pairs = vertices // 2
    phase_paired = dict(m=m, N=vertices * p['v'], W=pairs * w2, total_rank=pairs * rank2,
        deficit=pairs * pp['deficit_per_pair'], vertices_per_stage=vertices, pairs_per_stage=pairs,
        maxchild=pp['maxchild'], group_order_bits=vertices.bit_length(), per_pair=pp, **cm_paired)
    bridge_paired = inherited.finite_bridge(phase_paired, row)
    assert bridge_paired['complex']['local_group_upper'] >= audit['conservative_local_G'] >= audit['expanded_scalar_operations_per_stage']
    bridge_paired['complex'].update(physical_R=p['R'], virtual_R=p['virtual_R'], paired_first_stage_vertices=True,
        independently_audited_local_scalar_operations=audit['expanded_scalar_operations_per_stage'],
        local_scalar_guard_from_reflection=audit['conservative_local_G'],
        scalar_contract='Virtual-role reserve covers all compensated readouts and inverse chronology; actual persistent stock and finite routers use physical roles with paired lockstep Stage-1 auxiliary banks.')
    a_paired, k_paired, result_paired = solve_assembly(b_paired, bridge_paired)

    return dict(status='Conditional PR130 cover with independently audited physical local frames and compensated reuse',
        kappa=k_unpaired, complex_saving=b_unpaired, assembly_bit_saving=a_unpaired, actual_bit_saving=inherited.AB,
        retracted_paired_lockstep_kappa=k_paired, retracted_paired_lockstep_complex_saving=b_paired,
        profile=p, complex=phase_unpaired, bit=bit, finite_bridge=bridge_unpaired, assembly=result_unpaired,
        unpaired_cover=unpaired_cover,
        retracted_paired_lockstep_cover=dict(
            status='Retracted PR132/PR134 lockstep pairing accounting retained for historical comparison only; see #132#issuecomment-6073516734',
            kappa=k_paired, complex_saving=b_paired, assembly_bit_saving=a_paired,
            complex=phase_paired, finite_bridge=bridge_paired, assembly=result_paired),
        next_grid_rejections=dict(complex='1e-12 enclosure', kappa='1e-15 assembly'),
        scope='Finite local word and complete unpaired cover and assembly arithmetic. PR130 group geometry, weighted local-ring compilation, uniform batching and borrowed rows remain explicit written proof dependencies, together with inherited analytic/tape interfaces. PR132 first-stage lockstep pairing is marked retracted.')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); args = ap.parse_args()
    result = js(exact()); path = HERE / 'certificate.json'
    if args.write: path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else: assert result == json.loads(path.read_text()), 'Frozen cover certificate mismatch'
    print('PASS unpaired kappa', result['kappa'], float(Q(result['kappa'])), 'unpaired complex', result['complex_saving'],
          '47 constraints, 7 margins', flush=True)


if __name__ == '__main__': main()
