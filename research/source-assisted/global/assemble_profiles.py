#!/usr/bin/env python3
"""Price complete supplied profiles and perform the exact balanced assembly.

New integration for icekylinx: GPT-6 Astra, 2026-10-09. Apache-2.0.
The rational enclosures are retained from icekylinx's three_stage_cover_network.py;
the balanced assembly is PR168's paired_cube_assembly.py (eumemic, Anthropic
Claude assistance), retaining the RaD/hipotures balanced prefix and PR23 gates.

This tool certifies arithmetic and binds the supplied construction receipts.
It is not a substitute for regenerating their exact flow and boundary checks.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = HERE.parent / "public/pr168_fd25adb7"
GRID = 1 << 120
SELECT_GRID = 10**10
OLD = Q(384599, SELECT_GRID)
BAD = Q(1, 10**16)
BASE = Q(4609169, SELECT_GRID)


def serial(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): serial(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [serial(v) for v in x]
    return x


def up(x):
    return Q((x.numerator*GRID+x.denominator-1)//x.denominator, GRID)


def log_upper(x):
    assert x >= 1
    p = 0
    while x >= 2:
        x /= 2
        p += 1
    def small(y):
        z = (y-1)/(y+1)
        return (2*sum((z**(2*j+1)/(2*j+1) for j in range(32)), Q(0))
                + 2*z**65/(65*(1-z*z)))
    return up(p*small(Q(2))+small(x))


def exp_upper(u):
    assert 0 <= u < 3
    return up(1+u+u*u/(2*(1-u/3)))


def normalize(data):
    p = data.get("combined_fixed_boundary_profile") or data
    m = int(p.get("m", 3*int(p.get("h",0))))
    W = Q(p.get("W_per_vertex", p.get("W", p.get("new_W"))))
    hist = {int(r): Q(n) for r, n in p["child_histogram"].items() if int(r) and n}
    delta = Q(p.get("deficit_per_vertex", p.get("delta", p.get("deficit"))))
    assert all(0 < r < m and n > 0 for r, n in hist.items())
    mass = sum((r*n for r, n in hist.items()), Q(0))
    assert m*W-mass == delta > 0
    return dict(m=m, W=W, delta=delta, histogram=hist,
                mass=mass, edge_count=sum(hist.values()), maxchild=max(hist))


def numerical_root(p):
    lo, hi = 0., .02
    while sum(float(n)*r*math.expm1(hi*math.log(p['m']/r))
              for r, n in p['histogram'].items()) < float(p['delta']):
        hi *= 2
    for _ in range(85):
        a = (lo+hi)/2
        excess = math.fsum(float(n)*r*math.expm1(a*math.log(p['m']/r))
                           for r, n in p['histogram'].items())
        if excess < float(p['delta']):
            lo = a
        else:
            hi = a
    return lo


def moment(p, a, bit=False):
    m, W = p['m'], p['W']
    good = sum((n*r/(W*m)*exp_upper(a*log_upper(Q(m, r)))
                for r, n in p['histogram'].items()), Q(0))
    extra = (BAD*32*m*m*p['edge_count']/(W*m)*exp_upper(a*log_upper(Q(m)))) if bit else Q(0)
    return dict(saving=a, ideal_moment_upper=good, bad_moment_upper=extra,
                strict_gap_lower=1-good-extra,
                strict_gap_lower_decimal=float(1-good-extra))


def select(p, bit=False):
    root = numerical_root(p)
    ticks = int(root*SELECT_GRID)
    while True:
        result = moment(p, Q(ticks, SELECT_GRID), bit)
        if result['strict_gap_lower'] > 0:
            break
        ticks -= 1
    result['numerical_root_for_discovery_only'] = root
    result['counts'] = p
    if bit:
        assert Q(2*p['m']**3, 2**80) < BAD
        a = result['saving']
        edge = a/(1+a-OLD)
        beta = Q(edge.numerator*10**12//edge.denominator+1, 10**12)
        effective = (1-beta)*a+beta*OLD
        assert effective < beta < 1-effective
        result.update(atom_exponent=beta, ordinary_leaf_saving=OLD,
                      effective_saving=effective,
                      effective_saving_decimal=float(effective))
    return result


def construction_receipts(cdata, bdata, bit_lifts, proof):
    """Reject a raw modular screen and bind the selected constructive proofs."""
    checks = cdata['contract_checks']
    for name in ('all_fresh_columns_equal_identity',
                 'source_controls_at_paid_parity_frames',
                 'original_source_V_before_all_controls',
                 'controls_before_original_K', 'all_centers_in_phase1',
                 'all_target_cap_reads_in_phase2', 'target_chains_nested'):
        assert checks[name] is True, name
    assert checks['checked_source_columns'] == checks['checked_target_rows'] == cdata['v']
    assert cdata['scalar_denominator_lcm'] == '2'
    assert cdata['terminal_sink_substitutions'] == 0
    cp = Path(cdata['exact_lift_certificate_path'])
    if not cp.is_file():
        cp = HERE.parent / cp
    assert cp.is_file(), 'The exact complex lift certificate must be present'
    assert sha256(cp.read_bytes()).hexdigest() == cdata['exact_lift_certificate_sha256']
    low = bdata['source_aligned_rewrite']
    assert low['exact_high_boundary_and_suffix_unchanged'] is True
    assert low['exact_rank3_resource_counts_unchanged'] is True
    chosen = bdata['combined_fixed_boundary_profile']
    assert chosen['paired_donors_deleted'] == 0
    assert chosen['retained_gauges'] == 3960 and chosen['retained_pairs'] == 1760
    assert chosen['child_histogram']['60'] == 2200
    lifts = json.loads(bit_lifts.read_text())
    assert lifts['source_commit'] == 'fd25adb7fbaa12ee761d02c733c54d1d2a7687ee'
    assert lifts['instances'] == 2640
    assert all(value is True for value in lifts['checks'].values())
    proof_paths = (proof, HERE/'COMMON_FRAME_LIFT_AND_GLOBAL_CONTRACT.txt',
                   HERE.parent/'bit/SOURCE_ALIGNED_BIT_WORD.txt', bit_lifts)
    def label(path):
        try:
            return str(path.resolve().relative_to(HERE.parent))
        except ValueError:
            return path.name
    return dict(
        status='Constructive exact flow and fixed-boundary proofs; literal globally renumbered program/replay remains a downstream integration task',
        complex_lift_certificate_sha256=cdata['exact_lift_certificate_sha256'],
        complex_endpoint_checks=checks,
        bit_high_boundary_sha256=low['high_boundary_and_suffix_sha256'],
        bit_low_instances_sha256=lifts['instance_sha256'],
        bit_low_checks=lifts['checks'],
        proof_sha256={label(p):sha256(p.read_bytes()).hexdigest()
                      for p in proof_paths})


def assemble(c, b, source, proof):
    # The finite bridge is deliberately overcharged. Its derivation is in
    # FINITE_BRIDGE.txt; the integers below are exact powers, not estimates.
    assert proof.is_file(), 'The physical/finite bridge proof must be present'
    assert c['counts']['m'] <= 72 and b['counts']['m'] <= 72
    assert c['counts']['W'] < 10**7 and b['counts']['W'] < 10**7
    assert 2*c['counts']['maxchild'] < c['counts']['m']
    coefficient, degree = 20161, 10**6
    bridge = dict(
        proof=proof.name,
        representation='Exact powers of two with proved dominating bounds',
        semantic=dict(G=dict(base=2, exponent=30000),
                      E=dict(base=2, exponent=100000),
                      B_upper=dict(base=2, exponent=100001),
                      C0=dict(base=2, exponent=210000), C1=1,
                      strict_literal_gap=1, induction_gap_lower=1),
        rows=dict(coefficient=coefficient, degree=degree,
                  suffix_slope=4*degree,
                  degree_gap=Q(degree)-Q(51*coefficient,25)))
    eta, stop = Q(1,10**8), Q(1,10**9)
    a = min(b['effective_saving'], (1-stop)*c['saving']-Q(1,SELECT_GRID))
    q = a*(1-2*eta)
    minimum = (1-eta)*q/(1+q)
    kappa = Q(minimum.numerator*SELECT_GRID//minimum.denominator, SELECT_GRID)
    if kappa == minimum:
        kappa -= Q(1, SELECT_GRID)
    ap = source / 'scripts/paired_cube_assembly.py'
    spec = importlib.util.spec_from_file_location('retained_balanced_assembly', ap)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = module.assembly(a,c['saving'],bridge,kappa,eta=eta,beta=stop)
    assert len(out['strict_constraints']) == 47 and len(out['margins']) == 7
    assert out['minimum_margin'] == minimum
    return dict(finite_bridge=bridge, assembly=out,
                kappa=kappa, kappa_decimal=float(kappa),
                reviewed_baseline=BASE, fixed_doubling_target=2*BASE,
                ratio_to_reviewed_baseline=kappa/BASE,
                ratio_to_reviewed_baseline_decimal=float(kappa/BASE),
                doubling_achieved=kappa >= 2*BASE,
                assembly_source_sha256=sha256(ap.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex', type=Path, required=True)
    parser.add_argument('--bit', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=PIN)
    parser.add_argument('--proof', type=Path, default=HERE/'FINITE_BRIDGE.txt')
    parser.add_argument('--bit-lifts', type=Path, default=HERE.parent/'bit/source_aligned_lifts.json')
    parser.add_argument('--output', type=Path, default=HERE/'global_certificate.json')
    parser.add_argument('--moments-only', action='store_true')
    args = parser.parse_args()
    paths = dict(complex=args.complex,bit=args.bit)
    data = {kind: json.loads(path.read_text()) for kind,path in paths.items()}
    profiles = {kind: normalize(value) for kind,value in data.items()}
    c,b = select(profiles['complex']),select(profiles['bit'],True)
    out = dict(author='GPT-6 Astra',
               status='Exact arithmetic; construction and finite bridge are explicit proof dependencies',
               complex=c,bit=b,
               source_sha256={kind:sha256(path.read_bytes()).hexdigest() for kind,path in paths.items()},
               arithmetic='32-term rational logarithm enclosure; rational exponential majorant; upward 2^120 rounding')
    if not args.moments_only:
        out['construction_receipts'] = construction_receipts(data['complex'],data['bit'],args.bit_lifts,args.proof)
        out.update(assemble(c,b,args.source,args.proof))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(serial(out),indent=2)+'\n')
    summary = dict(complex_saving=float(c['saving']),
                   complex_gap=c['strict_gap_lower_decimal'],
                   bit_coarse_saving=float(b['saving']),
                   bit_gap=b['strict_gap_lower_decimal'],
                   bit_effective_saving=b['effective_saving_decimal'])
    if not args.moments_only:
        summary.update(kappa=out['kappa_decimal'],
                       ratio=out['ratio_to_reviewed_baseline_decimal'],
                       doubling_achieved=out['doubling_achieved'])
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
