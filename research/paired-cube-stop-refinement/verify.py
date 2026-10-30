#!/usr/bin/env python3
"""Exact stopping/assembly refinement of reviewed main; Apache-2.0.

Prepared with substantial OpenAI Codex assistance. Construction: icekylinx,
an664, eumemic, Zhihao Chen and Swapnil Jain. Related toll refinements:
gupt1156 PR148 and Abhinav Ramachandran PR158. See README.md.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Run without optimized Python: inherited assertions are required')
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from audit_community_candidate import log_bounds, exp_bounds, require
import paired_cube_network as pc
from structured_bulk_assembly import assembly, js

BASE = 'd1d6c070f5a8c684727ee7ec35d930f9ebfa9758'
GRID = 10**15
ATOM_GRID = 10**18
COARSE = Q(115441418341, 250000000000000)
ATOM = Q(230785143998139, 500000000000000000)
ETA = Q(1, 10**14)
KAPPA = Q(115286146679, 250000000000000)
HERE = Path(__file__).resolve().parent


def enclosed_moment(profile, saving, contaminated=False):
    """Both bounds on the actual power moment, including the full fallback.

    Independent of pc.exact_moment: 80-term atanh / 12-term exp bounds
    with outward decimal rounding, proved in README.md.
    """
    m, W = profile['m'], profile['W_per_vertex']
    entries = dict(profile['child_multiplicities'])
    if contaminated:
        # Coefficient of exp(a log(m)): each ideal edge gets all 32m^2
        # rank-one fallback children on fraction BAD. Nothing is subtracted.
        entries[1] = entries.get(1, 0) + pc.BAD * 32*m*m * profile['edge_count']
    lower = upper = Q(0)
    for r, n in sorted(entries.items()):
        require(0 < r < m and n > 0, 'Proper children')
        l, u = log_bounds(Q(m, r))
        lower += Q(n*r, W*m) * exp_bounds(saving*l)[0]
        upper += Q(n*r, W*m) * exp_bounds(saving*u)[1]
    return lower, upper


def rejected(fn):
    try:
        fn()
    except (AssertionError, ValueError):
        return True
    return False


def certificate():
    baseline = pc.certificate()  # Hash-bound bit reconstruction + full bridge.
    saved = json.loads((ROOT/'certificates/paired-cube-network.json').read_text())
    require(js(baseline) == saved, 'Reproduce complete reviewed certificate')
    for path, digest in baseline['source_sha256'].items():
        require(sha256((ROOT/path).read_bytes()).hexdigest() == digest,
                'Reviewed source pin: '+path)
    b = dict(baseline['bit'])
    profile = b['counts']
    lower, upper = enclosed_moment(profile, COARSE, True)
    next_lower, next_upper = enclosed_moment(profile, COARSE+Q(1,GRID), True)
    require(upper < 1 < next_lower, 'Two-sided certified coarse root bracket')
    require(COARSE > pc.COARSE, 'Strictly stronger coarse supplier')
    require(b['rank_mass_upper_per_vertex'] < profile['m']*profile['W_per_vertex'],
            'Contaminated rank moment retained')
    edge = COARSE/(1+COARSE-pc.OLD)
    require(ATOM == Q((edge*ATOM_GRID).__floor__()+1,ATOM_GRID), 'First strict atom grid')
    a = (1-ATOM)*COARSE+ATOM*pc.OLD
    require(0 < a < ATOM < 1-a, 'Both strict tolls with all costs paid')
    theta_below = ATOM-Q(1,ATOM_GRID)
    require(theta_below <= (1-theta_below)*COARSE+theta_below*pc.OLD,
            'Previous atom grid violates strict adapter toll')
    phase = baseline['complex']
    cl, cu = enclosed_moment(phase['counts'], pc.AC)
    require(cu < 1, 'Independent unchanged complex supplier')
    require(a < (1-pc.PHASE_STOP)*pc.AC-Q(1,10**10), 'Phase ceiling is slack')
    bridge = dict(baseline['finite_bridge'])
    bridge['bit_uniform'] = dict(bridge['bit_uniform'], coarse_saving=COARSE,
                                atom_beta=ATOM, ordinary_saving=a)
    result = assembly(a,pc.AC,bridge,KAPPA,eta=ETA,beta=pc.PHASE_STOP)
    require(len(result['strict_constraints']) == 47 and len(result['margins']) == 7,
            'Complete downstream constraints and costs')
    g = result['minimum_margin']
    require(KAPPA == Q((g*GRID).__floor__(),GRID) < g, 'Strict selected headline grid')
    require(rejected(lambda: assembly(a,pc.AC,bridge,KAPPA+Q(1,GRID),eta=ETA,
                                     beta=pc.PHASE_STOP)), 'Next kappa grid rejected')
    require(rejected(lambda: assembly(a,pc.AC,bridge,KAPPA,eta=Q(0),
                                     beta=pc.PHASE_STOP)), 'Zero-slack eta rejected')
    # Analytic upper bound for this fixed contaminated profile and retained
    # assembly family only: theta>a implies a<coarse/(1+coarse-OLD), and
    # g<a/(1+2a). Monotonicity and the moment root bracket bound the supremum.
    next_coarse = COARSE+Q(1,GRID)
    ceiling = next_coarse/(1+3*next_coarse-pc.OLD)
    require(0 < ceiling-KAPPA < Q(2,GRID), 'Within two headline grid units of scoped ceiling')
    b.update(coarse_saving=COARSE,effective_saving=a,atom_exponent=ATOM,
             coarse=dict(saving=COARSE,exponent=1-COARSE,moment_lower=lower,
                         moment_upper=upper,strict_gap=1-upper,
                         includes_full_rare_class_fallback=True),
             strict_gap=1-upper)
    # Remove the historical separate ideal/fallback enclosure fields; the new
    # two-sided moment explicitly encloses their sum.
    b.pop('added_bad_moment_upper')
    sources = dict(baseline['source_sha256'])
    for path in (HERE/'verify.py',HERE/'README.md',ROOT/'scripts/audit_community_candidate.py'):
        sources[str(path.relative_to(ROOT))] = sha256(path.read_bytes()).hexdigest()
    return dict(status='Conditional parameter refinement of reviewed paired cubes',
        reviewed_base=BASE,kappa=KAPPA,previous_kappa=pc.KAPPA,
        absolute_improvement=KAPPA-pc.KAPPA,relative_improvement=KAPPA/pc.KAPPA-1,
        bit=b,complex=phase,finite_bridge=bridge,assembly=result,
        independent_complex_moment=dict(lower=cl,upper=cu),
        controls=dict(next_coarse_saving=next_coarse,next_coarse_moment_lower=next_lower,
            next_coarse_moment_upper=next_upper,strict_atom_boundary=edge,
            rejected_atom=theta_below,adapter_toll_gap=ATOM-a,
            borrowing_toll_gap=1-a-ATOM,next_kappa_rejected=True,zero_eta_rejected=True,
            scoped_supremum_upper=ceiling,scoped_upper_minus_kappa=ceiling-KAPPA),
        source_sha256=sources,
        scope='Same reviewed finite words, gauges, dirty restoration, shared banks, '
              'rare fallback, routers, reserve and semantic guard. Retains all analytic, '
              'uniform-recursion, exact-recovery and fixed-tape hypotheses. '
              'No global optimum, priority or complete formal multiplication proof claimed.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',type=Path)
    args=parser.parse_args()
    data=js(certificate())
    if args.check:
        require(data == json.loads(args.check.read_text()), 'Certificate reproduces byte-for-byte data')
    text=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(text)
    if not args.output and not args.check:
        print(text,end='')
    else:
        print('PASS kappa='+str(KAPPA)+' = 0.000461144586716; exact moments, strict tolls, 47 constraints, 7 margins and negative controls')


if __name__ == '__main__':
    main()
