#!/usr/bin/env python3
"""Exact pricing of the PR364 kernel and component-retiming extension with 100 physical replicas.

This certifies arithmetic only. The word's structural checks and inherited
all-size interfaces must be supplied separately. No fallback charge is removed.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import struct
import sys
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise SystemExit("Assertions must be enabled")
sys.set_int_max_str_digits(0)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def serial(obj):
    if isinstance(obj, Q):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return list(map(serial, obj))
    return obj


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refine(word, package):
    engines = package / 'code/engines'
    first = load('refine_moment', engines / 'moment.py')
    second = load('refine_second', engines / 'base_two_moment.py')
    outer = load('refine_outer', engines / 'outer.py')
    state = json.loads((word / '249-states.json').read_text())
    frames = json.loads((word / 'frames.json').read_text())['frames']
    dim = {int(k): len(v['B']) for k, v in frames.items()}
    local = collections.Counter()
    copies = erases = 0
    for op, a, b, c, f, z in struct.iter_unpack('<6i', (word / '249-records.bin').read_bytes()):
        if op == 0 and f > 0:
            local[f] += 1
        elif op == 2:
            local[z] += 1
            copies += 1
        elif op == 3:
            erases += 1
    assert copies == erases == 20
    v, n, h, m, norm = state['v'], state['n'], 20, 100, 20
    assert v == 960
    residual = sum(dim[state['final'][str(r)]] - dim[state['initial'][str(r)]] for r in range(2*v, n))
    hist = collections.Counter({r: 5*norm*count for r, count in local.items()})
    for r in (38, 19, 42, 4):
        hist[r] += 2*v*norm
    width = Q(4*v*h + residual, h)*norm
    assert width.denominator == 1
    width = int(width)
    assert m*width - sum(r*count for r, count in hist.items()) == norm*(4*v-5*h*(h-2))
    root = first.certify(hist, m, width, True)
    coarse = Q(root['lower'])
    next_coarse = coarse + Q(1, 10**24)
    fallback_calls = 32*m*m*sum(hist.values())

    def both(x):
        left = first.moment(hist, m, width, x, True)
        lo, hi = second.moment(m, width, list(hist.items()), x)
        flo, fhi = second.moment(m, width, [(1, fallback_calls)], x)
        right = lo + Q(1, 10**16)*flo, hi + Q(1, 10**16)*fhi
        return left, right

    admitted = both(coarse)
    excluded = both(next_coarse)
    assert all(x[1] < 1 for x in admitted)
    assert all(x[0] > 1 for x in excluded)
    eta, beta = Q(1, 10**24), Q(1, 10**9)
    complex_saving = Q(876248285600677, 10**18)
    assert coarse < (1-beta)*complex_saving
    chain = [Q(384599, 10**10)]
    for _ in range(8):
        old = chain[-1]
        new = (1-coarse)*coarse + coarse*old
        assert old < new < coarse < 1-new
        assert 1-new-coarse*(1-old) > 0
        chain.append(new)
    bridge = dict(
        semantic=dict(C0=dict(base=2, exponent=210000), strict_literal_gap=1),
        rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)),
    )
    q = chain[-1]*(1-2*eta)
    minimum = (1-eta)*q/(1+q)
    grid = 10**27
    ticks = minimum*grid
    kappa = Q((ticks.numerator-1)//ticks.denominator, grid)
    assembly = outer.assembly(chain[-1], complex_saving, bridge, kappa, eta, beta)
    assert len(assembly['strict_constraints']) == 47
    assert min(assembly['strict_constraints'].values()) > 0
    try:
        outer.assembly(chain[-1], complex_saving, bridge, kappa+Q(1,grid), eta, beta)
    except AssertionError:
        pass
    else:
        raise AssertionError('Adjacent grid point admitted')
    baseline = Q(160987957846297, 200000000000000000)
    return dict(
        status='PASS_EXTENSION_ARITHMETIC_REQUIRES_STRUCTURAL_ADMISSION',
        source_hashes={p.name:sha(p) for p in (word/'249-records.bin',word/'249-states.json',word/'frames.json')},
        engine_hashes={p.name:sha(p) for p in engines.glob('*.py')},
        local_histogram=dict(sorted(local.items())), histogram=dict(sorted(hist.items())),
        residual=residual, m=m, width=width, coarse=coarse,
        next_coarse=next_coarse, admitted=admitted, excluded=excluded,
        fallback_density=Q(1,10**16), fallback_calls=fallback_calls,
        eta=eta,beta=beta,chain=chain,assembly=assembly,kappa=kappa,
        kappa_float=float(kappa),gain_over_pr366=kappa-baseline, gain_over_pr364=kappa-Q(201219842699733,250000000000000000),
        scope='Kernel and component-retiming extension pricing at 100 physical replicas with full inherited fallback. The exact same word must pass structural replay; all-size compiler, charts, routing, restored-row, precision/recovery, prime supply, and analytic interfaces remain conditional. No unconditional multiplication theorem or native finite admission is claimed.',
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=Path)
    parser.add_argument('package', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = refine(args.word, args.package)
    args.output.write_text(json.dumps(serial(result), indent=2, sort_keys=True)+'\n')
    print(result['status'], result['kappa'], result['kappa_float'], 'gain', float(result['gain_over_pr364']), flush=True)
