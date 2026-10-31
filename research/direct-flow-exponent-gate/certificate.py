#!/usr/bin/env python3
"""Exact rational certificates for the full-flow limiting coefficient.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from pathlib import Path
from fractions import Fraction as Q
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from intervals import I, need, log_integer, rank_power

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALPHA = I('0.98981438244597', '0.98981438244599')
ROOT_EXPONENT = I('0.99731351095114', '0.99731351095116')


def inventory():
    path = ROOT/'research/direct-flow-leaf-walk/verify.py'
    tree = ast.parse(path.read_text())
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], 'id', None)
            if name in ('P', 'W', 'M'):
                values[name] = ast.literal_eval(node.value)
    need(set(values) == {'P', 'W', 'M'}, 'source inventory names')
    return values['P'], values['W'], values['M']


def moment(law, s, derivative=0):
    return sum((count*rank_power(rank, s)*log_integer(rank)**derivative
                for rank, count in law.items()), I(0))


def coefficient(paid, targets, s, alpha=ALPHA):
    ranks = sorted(set(paid)|set(targets))
    powers_a = {r: rank_power(r, alpha) for r in ranks}
    powers_s = {r: rank_power(r, s) for r in ranks}
    a = sum((paid[r]*powers_a[r] for r in paid), I(0))
    b = sum((targets[k]*powers_a[k] for k in targets), I(0))
    gap = a-b
    need(gap.lo > 0, 'strict tilted target gap')
    source, boundary, ds, db = I(0), I(0), I(0), I(0)
    for r, pr in paid.items():
        for k, wk in targets.items():
            lo, hi = sorted((r,k))
            v = pr*wk*(powers_a[lo]*powers_s[hi]-powers_a[hi]*powers_s[lo])
            dv = pr*wk*(powers_a[lo]*powers_s[hi]*log_integer(hi)
                         -powers_a[hi]*powers_s[lo]*log_integer(lo))
            if k > r:
                source, ds = source+v, ds+dv
            elif r > k:
                boundary, db = boundary+v, db+dv
    leaf = gap*sum((paid[r]*powers_s[r] for r in paid), I(0))
    dl = gap*sum((paid[r]*powers_s[r]*log_integer(r) for r in paid), I(0))
    exits, de = boundary+leaf, db+dl
    need(source.lo > 0 and exits.lo > 0, 'positive limiting masses')
    ratio = exits/source
    derivative = de/source-exits*ds/(source*source)
    return {'ratio': ratio, 'derivative': derivative, 'leaf_share': leaf/exits,
            'source': source, 'boundary': boundary, 'leaf': leaf,
            'ds': ds, 'de': de, 'gap': gap, 'q': b/a, 'a':a}


def numerical_certificate():
    paid, targets, m = inventory()
    a = log_integer(5)
    for endpoint, sign in [(ALPHA.lo,-1),(ALPHA.hi,1)]:
        f = moment(paid, I(endpoint), 1)-a*moment(paid, I(endpoint))
        need(f.hi < 0 if sign < 0 else f.lo > 0, 'alpha root bracket')
    for endpoint, sign in [(ROOT_EXPONENT.lo,-1),(ROOT_EXPONENT.hi,1)]:
        f = moment(targets,I(endpoint))-moment(paid,I(endpoint))
        need(f.hi < 0 if sign < 0 else f.lo > 0, 'raw root bracket')
    at_root = coefficient(paid, targets, ROOT_EXPONENT)
    need(at_root['ratio'].contains(1), 'exact root conservation')
    g = at_root['a']*(moment(targets,ROOT_EXPONENT,1)-moment(paid,ROOT_EXPONENT,1))/at_root['source']
    need(Q('120.37003050') < g.lo < g.hi < Q('120.37003054'), 'log-gap enclosure')
    need(Q('0.89892119') < at_root['leaf_share'].lo < at_root['leaf_share'].hi < Q('0.89892120'), 'leaf share enclosure')
    # F(s)=eta(s)-R(s) is positive exactly when the limiting sufficient test passes.
    bracket = [Q('0.99743801995'), Q('0.99743801998')]
    signs = []
    for s, wanted in zip(bracket,(-1,1)):
        c = coefficient(paid, targets, I(s))
        eta = s*rank_power(m,I(s-1))
        f = eta-c['ratio']
        need(f.hi < 0 if wanted < 0 else f.lo > 0, 'single-step threshold bracket')
        signs.append(f.decimal(15))
    # The derivative is strictly negative for R throughout [0.9973,1].
    upper_derivative = None
    for j in range(27):
        s = I(Q(9973+j,10000),Q(9974+j,10000))
        derivative = coefficient(paid,targets,s)['derivative']
        need(derivative.hi < 0, 'uniform monotonic ratio derivative')
        upper_derivative = derivative.hi if upper_derivative is None else max(upper_derivative,derivative.hi)
    # eta'(s)>0 here because eta'=m^(s-1)(1+s log m)>0.
    saving = I(1-bracket[1],1-bracket[0])
    explicit_s = Q('0.99744')
    explicit_margin = explicit_s*rank_power(m,I(explicit_s-1))-coefficient(paid,targets,I(explicit_s))['ratio']
    need(explicit_margin.lo > 0, 'rational scalar exponent .99744')
    return {'alpha': ALPHA.decimal(14), 'raw_exponent': ROOT_EXPONENT.decimal(14),
            'tilted_target_ratio': at_root['q'].decimal(12),
            'limiting_leaf_fraction_at_raw_root': at_root['leaf_share'].decimal(12),
            'limiting_log_gap_at_raw_root': g.decimal(10),
            'single_step_saving_threshold': saving.decimal(11),
            'threshold_endpoint_signs': signs,
            'ratio_derivative_upper': I(upper_derivative).decimal(6),
            'derivative_cells':27, 'explicit_scalar_exponent':'0.99744',
            'explicit_limit_margin':explicit_margin.decimal(12), 'no_new_kappa':True}


if __name__ == '__main__':
    import json
    print(json.dumps(numerical_certificate(),indent=2))
