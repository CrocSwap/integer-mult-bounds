#!/usr/bin/env python3
"""Exact arithmetic screen of the all-rank slot-cost complete physical profile.

Uses PR63's paid profile, inherited PR48 logarithm enclosures and balanced
assembly (PR34 and successors). New directed Taylor bounds are documented in
this file. Prepared with OpenAI assistance. Inherited licenses apply.
Physical linkage is checked by the parent verifier; no full theorem or practical speedup claim is implied.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
import binary_frame_math as arithmetic
spec = importlib.util.spec_from_file_location('inherited_assembly', ROOT/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')
balanced = importlib.util.module_from_spec(spec)
spec.loader.exec_module(balanced)


def floor_scaled(x, denominator):
    return (x * denominator).numerator // (x * denominator).denominator


def ceiling_scaled(x, denominator):
    return -floor_scaled(-x, denominator)


def exact_moment(m, width, rows, saving, degree=8, rounding=10**40):
    """Bound sum n*t/(mW)*exp(saving*log(m/t)) entirely in Q.

    At 0 <= u <= v < 1, S_d(u) is a lower bound for exp(u).
    The tail at v has first term v^(d+1)/(d+1)!; successive ratios
    are at most v/(d+2). Thus S_d(v)+first/(1-v/(d+2)) is upper.
    Directed rounding per exp bound preserves both inequalities.
    The inherited logarithm helper encloses log(m/t) rationally.
    """
    assert type(saving) is Q and 0 < saving < 1 and degree >= 1
    lo, hi = Q(), Q()
    terms = {}
    for t, count in sorted(rows.items()):
        assert type(t) is int and type(count) is int and 0 < t < m and count > 0
        loglo, loghi = arithmetic.logs(Q(m, t))
        u, v = saving*loglo, saving*loghi
        assert 0 <= u <= v < 1
        lower = sum((u**j / factorial(j) for j in range(degree+1)), Q())
        upper = sum((v**j / factorial(j) for j in range(degree+1)), Q())
        upper += v**(degree+1)/factorial(degree+1)/(1-v/Q(degree+2))
        lower = Q(floor_scaled(lower, rounding), rounding)
        upper = Q(ceiling_scaled(upper, rounding), rounding)
        weight = Q(t*count, m*width)
        lo += weight*lower
        hi += weight*upper
        terms[t] = dict(weight=weight, log_lower=loglo, log_upper=loghi,
                        exp_lower=lower, exp_upper=upper)
    return dict(saving=saving, lower=lo, upper=hi, strict_gap=1-hi,
                degree=degree, rounding_denominator=rounding, terms=terms)


def assemble(bridge, saving, h, denominator):
    preliminary = balanced.assembly(bridge, saving, Q(1, denominator), h=h)
    kappa = Q(ceiling_scaled(preliminary['minimum_margin'], denominator)-1, denominator)
    accepted = balanced.assembly(bridge, saving, kappa, h=h)
    assert len(accepted['constraints']) == 47 and len(accepted['margins']) == 7
    assert all(v > 0 for v in accepted['constraints'].values())
    assert all(v > kappa for v in accepted['margins'].values())
    try:
        balanced.assembly(bridge, saving, kappa+Q(1, denominator), h=h)
    except balanced.InvalidAssembly as error:
        rejected = str(error)
    else:
        raise AssertionError('Next kappa grid unexpectedly passes')
    return dict(kappa=kappa, assembly=accepted,
                next_kappa=kappa+Q(1, denominator), next_kappa_rejection=rejected,
                eventual_bounds=balanced.cutoffs(bridge, accepted))


def build_certificate(profile_path, denominator=10**18, h=Q(1, 10**12)):
    profile_path = profile_path.resolve()
    source = json.loads(profile_path.read_text())
    profile = source['bit']
    bridge = source['finite_bridge']
    m, width = profile['m'], profile['W']
    rows = {int(t): n for t, n in profile['child_multiplicities'].items()}
    assert sum(t*n for t, n in rows.items()) == profile['total_rank']
    assert bridge['bit']['W'] == width
    low, high = 1, floor_scaled(Q(717, 10**7), denominator)
    assert exact_moment(m, width, rows, Q(low, denominator))['upper'] < 1
    assert exact_moment(m, width, rows, Q(high, denominator))['lower'] > 1
    steps = 0
    while low+1 < high:
        mid = (low+high)//2
        test = exact_moment(m, width, rows, Q(mid, denominator))
        if test['upper'] < 1:
            low = mid
        elif test['lower'] > 1:
            high = mid
        else:
            raise ArithmeticError('Rational bounds inconclusive: increase enclosure precision')
        steps += 1
    saving = Q(low, denominator)
    accepted = exact_moment(m, width, rows, saving)
    rejected = exact_moment(m, width, rows, Q(high, denominator))
    assert accepted['upper'] < 1 < rejected['lower']
    preferred = assemble(bridge, saving, h, denominator)
    coarse_denom = 10**11
    coarse_bit = Q(floor_scaled(saving, coarse_denom), coarse_denom)
    assert exact_moment(m, width, rows, coarse_bit)['upper'] < 1
    coarse = assemble(bridge, coarse_bit, h, coarse_denom)
    inherited_coarse = arithmetic.moment(m, width, rows, coarse_bit)
    inherited_next = arithmetic.moment(m, width, rows, coarse_bit+Q(1, coarse_denom))
    assert inherited_coarse['upper'] < 1 < inherited_next['lower']
    coarse['original_enclosure_control'] = dict(accepted_upper=inherited_coarse['upper'],
        next_bit_lower=inherited_next['lower'])
    # Same coarse grid/backoff as PR63 separates the structural gain from
    # the additional precision refinement suggested by the PR61 precedent.
    prior = Q(source['kappa'])
    pr65_path = ROOT/'research/reordered-rank-pair/arithmetic/certificate.json'
    pr65 = Q(json.loads(pr65_path.read_text())['preferred']['kappa'])
    paths = (Path(__file__), Path(__file__).with_name('audit.py'),
        ROOT/'scripts/experiments/binary_frame_math.py', Path(balanced.__file__), pr65_path)
    return dict(status='Exact finite conditional screen; physical linkage checked by parent verifier',
        profile_path=str(profile_path.relative_to(ROOT)),
        profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
        source_sha256={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in paths},
        grid_denominator=denominator, binary_search_steps=steps, bit_saving=saving,
        next_bit_saving=Q(high, denominator), accepted_moment=accepted, rejected_moment=rejected,
        preferred=preferred, coarse_grid_control=dict(bit_saving=coarse_bit, **coarse),
        comparison=dict(pr63_kappa=prior, pr65_kappa=pr65, kappa=preferred['kappa'],
            difference_pr65=preferred['kappa']-pr65,
            difference=preferred['kappa']-prior,
            structural_gain_on_original_grid=coarse['kappa']-prior,
            additional_precision_gain=preferred['kappa']-coarse['kappa']),
        proof_limits=['The complete physical profile is supplied; independent word and CRT replay are parent-verifier responsibilities.',
                     'The rational logarithm and exponential enclosure derivations are documented in README.md, not formally mechanized.',
                     'All-size compiler, routing, recovery, prime-selection and fixed-tape transfer remain inherited.',
                     'Neither global optimality nor measured practical speedup is claimed.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=Path, default=Path(__file__).resolve().parent.parent/'paired-candidate.json')
    parser.add_argument('--certificate', type=Path, default=Path(__file__).with_name('certificate.json'))
    parser.add_argument('--record', action='store_true', help='Regenerate certificate instead of comparing with recorded result')
    args = parser.parse_args()
    result = arithmetic.js(build_certificate(args.profile))
    if args.record:
        args.certificate.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert result == json.loads(args.certificate.read_text()), 'Arithmetic certificate changed'
    print(json.dumps(dict(status='PASS exact arithmetic', bit_saving=result['bit_saving'],
        kappa=result['preferred']['kappa'], constraints=47, margins=7,
        next_grid_controls='PASS', comparison=result['comparison']), indent=2))


if __name__ == '__main__':
    main()
