#!/usr/bin/env python3
"""Replay selected finite checks of Swapnil Jain's pinned parallel project.

This is not a checker for its global analytic/fixed-tape transfer theorem.
Workers run separately because the reference has colliding module names.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / 'upstream'
TOOLCHAIN = 'leanprover/lean4:v4.31.0'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bit():
    sys.path[:0] = [str(SOURCE / 'independent/two-stage-bit'), str(SOURCE / 'scripts')]
    import rtgm
    from cert_rt import rt_histogram
    roles, ranks, circuit, graph = rtgm.side_ranks(23, 'search')
    # Reconstruct supports from the additions, without trusting the cached sup table.
    triples, args = graph['trip'], graph['args']
    masks = [sum(1 << i for i, t in enumerate(triples) if p in t) for p in range(23)]
    supports = {}
    for n in sorted(graph['active']):
        if args[n] is None:
            require(1 <= n <= len(triples), 'unknown input')
            supports[n] = 1 << (n - 1)
        else:
            x, y = args[n]
            require(x < n and y < n, 'non-topological addition')
            require(not supports[x] & supports[y], 'overlapping operands')
            supports[n] = supports[x] | supports[y]
        require(any(not supports[n] & ~m for m in masks), 'missing common point')
    require(len(graph['outputs']) == 3 * len(triples), 'side output count')
    for (c, t), n in graph['outputs'].items():
        require(c in t, 'wrong center')
        a, b = [p for p in t if p != c]
        require(supports[n] == masks[c] & ~masks[a] & ~masks[b], 'wrong exclusion output')
    require(set(graph['retained']) == set(range(23)), 'missing retained point total')
    for c, n in graph['retained'].items():
        require(supports[n] == masks[c], 'wrong retained point total')
    data = rt_histogram(23, roles, ranks)
    expected = json.loads((SOURCE / 'lean/round6-histograms.json').read_text())['bit']
    for key in ('m', 'W', 's'):
        require(data[key] == expected[key], 'bit ' + key)
    require(sorted(data['hist'].items()) == [tuple(p) for p in expected['hist']], 'bit histogram')
    return dict(h=23, roles=roles, active_nodes=len(supports), side_outputs=len(graph['outputs']),
                retained_outputs=len(graph['retained']), histogram_matches=True)


def complex_network():
    sys.path.insert(0, str(SOURCE / 'independent/complex-twostage'))
    from hist import build, label_dims
    from frames import Checker
    data = build(24, copied=True)
    circuit = data.pop('c')
    checker = Checker(circuit)
    require({n: len(checker.label(n)) for n in circuit.active} == label_dims(circuit),
            'complex label dimensions')
    checked = checker.run()
    require(checked['bad'] == 0, 'complex label failure')
    require(data['sum_ok'] and data['sum'] == data['s'], 'complex rank sum')
    require(data['maxrank'] < data['m'], 'complex guard child width')
    expected = json.loads((SOURCE / 'lean/round6-histograms.json').read_text())['cx']
    for key in ('m', 'W', 's'):
        require(data[key] == expected[key], 'complex ' + key)
    require(sorted(data['hist'].items()) == [tuple(p) for p in expected['hist']], 'complex histogram')
    return dict(h=24, roles=data['R'], labels=checked, histogram_matches=True)


def arithmetic():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from audit_community_candidate import moment, log_bounds
    results = {}
    for round_number in (5, 6):
        data = json.loads((SOURCE / f'lean/round{round_number}-histograms.json').read_text())
        moments = {}
        for name in ('bit', 'cx'):
            d = data[name]
            require(sum(w*n for w, n in d['hist']) == d['s'], 'rank sum')
            lo, hi = moment(d['m'], d['W'], d['hist'], Q(*d['a']))
            require(hi < 1, 'independent moment failed')
            moments[name] = dict(lower=str(lo), upper=str(hi), gap_lower=str(1-hi))
        # Signed rational reconstruction of all ten published assembly constraints
        # and all eight margins. No natural-number subtraction or floating logs.
        ab, ac = Q(*data['bit']['a']), Q(*data['cx']['a'])
        p = {k: Q(*v) if isinstance(v, list) else v for k, v in data['kappa'].items()}
        beta, eps, x, c1, kappa = (p[k] for k in ('beta', 'eps', 'x', 'c1', 'kappa'))
        tau, sigma = 1-ab, 1-ac
        chi = tau + (1-beta)*max(sigma-tau, 0)
        leaf = sigma + beta*(1-sigma)
        lam = max(tau, sigma, chi) + Q(1, 10**16)
        lamp = max(lam, leaf) + Q(1, 10**16)
        delta = Q(1, 10**22)/max(1, x)
        poly = (1+x)*delta
        cons = [lam-max(tau,sigma,chi), lamp-max(lam,leaf), 1-lamp,
                min(beta,1-beta), 1+x-eps*c1, 1+x-3*eps,
                Q(1), lamp-(2*eps-1)/eps, 1-eps, min(delta,Q(1,8)-delta)]
        margins = [1-eps, eps*(1-lamp), 1-eps-poly, 1-eps-poly,
                   1-eps-poly, eps, 1-eps-poly, max(eps,1-eps)*(1-tau)]
        require(all(c > 0 for c in cons), 'assembly constraint')
        require(kappa > 0 and all(g > kappa for g in margins), 'assembly margin')
        require(c1 >= 2 + p['mc']*log_bounds(Q(data['cx']['s']))[1], 'crude guard')
        results[str(round_number)] = dict(moments=moments, kappa=str(kappa),
                                          min_margin_gap=str(min(margins)-kappa),
                                          constraints=10, margins=8)
    return results


def formal():
    declarations = ['bit_rank_sum', 'bit_moment', 'cx_rank_sum', 'cx_moment', 'kappa_assembly']
    reports = {}
    # Generate in a temporary directory so the pinned reference stays untouched.
    with tempfile.TemporaryDirectory(prefix='swapnil-audit-') as tmp:
        tmp = Path(tmp)
        (tmp/'gen.py').write_bytes((SOURCE/'lean/gen.py').read_bytes())
        for number in (5, 6):
            src, dst = f'round{number}-histograms.json', f'Round{number}.lean'
            (tmp/src).write_bytes((SOURCE/'lean'/src).read_bytes())
            subprocess.run([sys.executable, str(tmp/'gen.py'), src, dst], check=True, capture_output=True)
            require((tmp/dst).read_bytes() == (SOURCE/'lean'/dst).read_bytes(), 'Lean generator drift')
            with (tmp/dst).open('a') as f:
                f.write('\n'+''.join('#print axioms '+n+'\n' for n in declarations))
            r = subprocess.run(['lean', '+'+TOOLCHAIN, str(tmp/dst)], check=True,
                               capture_output=True, text=True)
            for name in declarations:
                require(f"'{name}' does not depend on any axioms" in r.stdout, 'Lean axiom audit '+name)
            reports[str(number)] = dict(declarations=declarations, axioms=[], generator_matches=True)
    return dict(toolchain=TOOLCHAIN, rounds=reports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=['bit', 'complex', 'arithmetic'])
    parser.add_argument('--lean', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps({'bit': bit, 'complex': complex_network, 'arithmetic': arithmetic}[args.worker]()))
        return
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        require(hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() == digest, 'source drift: '+name)
    result = dict(source_commit=manifest['commit'], source_files=len(manifest['files']),
                  scope='Finite checks only; no end-to-end multiplication theorem or frontier update.')
    for mode in ('bit', 'complex', 'arithmetic'):
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', mode],
                           check=True, capture_output=True, text=True)
        result[mode] = json.loads(r.stdout)
    if args.lean:
        result['lean'] = formal()
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
