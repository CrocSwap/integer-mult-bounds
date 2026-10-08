#!/usr/bin/env python3
"""Dimension-parametric batching screen with explicit even-dimension matching.

Fast producer counts remain exploratory until an independent exact DAG audit.
PR #12 supplies the pinned Hamilton-cycle matching and generic log enclosure.
The retained h28 producer and every existing certificate remain unchanged.
"""
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT/'references/pr10/scripts'))
from controlled_bit_rank_moment import counts
from batched_bit_rank_moment import rational_log_bounds
from certify import Parameters
from fast_gaussian import fast_constraints, fast_margins
from compact_control_layer import layer_exponents
from ternary_split_search import Search
from ternary_top_split_search import screen, run_json
from ternary_star_resynthesis import resynthesize


def matching(h):
    ref = ROOT/'references/pr12'
    manifest = json.loads((ref/'SOURCE.json').read_text())
    name = 'research/geometric-dimensions/matching.py'
    path = ref/name
    if sha256(path.read_bytes()).hexdigest() != manifest['sha256'][name]:
        raise ValueError('Changed pinned matching source')
    spec = importlib.util.spec_from_file_location('pr12_dimension_matching', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.matching(h)


def log_upper(value):
    value = Q(value)
    if value < 1:
        raise ValueError('Expected logarithm argument at least one')
    exponent = 0
    while value > 2:
        value /= 2
        exponent += 1
    bound = exponent*rational_log_bounds(2)[1]+rational_log_bounds(value)[1]
    # Round outwards for a compact exact certificate, as in PR #12.
    return Q(-(-bound.numerator*10**9//bound.denominator), 10**9)


def moment(h, roles, a):
    n = counts(h=h, roles=roles)
    m, denominator = n['m'], n['W']*n['m']
    ratios = [Q(1, m)]+[Q(row['chunk_digits'], m) for row in n['recursive_blocks']]
    weights = [Q(n['singleton_calls'], denominator)]+[
        Q(row['copies']*row['chunk_digits'], denominator) for row in n['recursive_blocks']]
    logs = [log_upper(1/x) for x in ratios]
    if sum(weights) != 1-n['eta'] or not all(0 <= a*ell < 1 for ell in logs):
        raise ValueError('Invalid rank-mass or exponential range')
    upper = sum((w/(1-a*ell) for w, ell in zip(weights, logs)), Q(0))
    return dict(h=h, roles=roles, bit_saving=a, counts=n, normalized_widths=ratios,
                rank_mass_weights=weights, logarithm_upper_bounds=logs,
                moment_upper=upper, strict_gap=1-upper)


def assembly_screen(a):
    # Balance the Gaussian and bit margins, with exact downward rounding.
    delta = Q(1, 10**10)
    epsilon = Q(((1-delta)/(2+a)*10**12).__floor__(), 10**12)
    tau = 1-a
    p = Parameters(tau=tau, sigma=1-Q(7, 10**7), epsilon=epsilon, c=Q(1),
                   beta=Q(1, 1000), delta=delta, lam=tau+Q(1, 10**16),
                   lamp=tau+Q(2, 10**16), C1=Q(11999, 10000), kappa=Q(1, 10**12))
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    constraints = fast_constraints(p)
    constraints['packed_overhead'] = p.lam-exponents['internal']
    constraints['reserved_axes'] = p.lamp-exponents['preprocessing']
    if p.sigma >= p.tau or not all(x > 0 for x in constraints.values()):
        raise ValueError('Unchanged complex/interface regime no longer applies')
    margins = fast_margins(p)
    minimum = min(margins.values())
    units = -(-minimum.numerator*10**12//minimum.denominator)-1
    kappa = Q(units, 10**12)
    parameters = asdict(p)
    parameters['kappa'] = kappa
    return dict(kappa=kappa, parameters=parameters, minimum_margin=minimum,
                absorption_gap=minimum-kappa,
                factor_over_aligned=kappa/Q(1624, 10**12),
                scope='Arithmetic screen with unchanged h28 complex moment and guard.')


def rank(h, roles):
    low, high = 0, 600000  # a <= 6e-7, below retained complex saving.
    if moment(h, roles, Q(0))['strict_gap'] <= 0:
        return dict(positive_deficit=False)
    if moment(h, roles, Q(high, 10**12))['strict_gap'] > 0:
        raise ValueError('Increase exponent search bracket')
    while high-low > 1:
        middle = (low+high)//2
        if moment(h, roles, Q(middle, 10**12))['strict_gap'] > 0:
            low = middle
        else:
            high = middle
    return dict(positive_deficit=True, bit=moment(h, roles, Q(low, 10**12)),
                first_rejected_bit_saving=Q(high, 10**12),
                assembly=assembly_screen(Q(low, 10**12)))


def build_sweep_binaries(workdir):
    """Isolate the required 32-column extension from retained h28 sources."""
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    span = (HERE/'ternary_target_span_classes.cpp').read_text()
    if span.count('array<W,28>') != 2:
        raise ValueError('Unexpected retained Span layout')
    span = span.replace('array<W,28>', 'array<W,32>').replace('h<=28', 'h<=32')
    span = span.replace('5^14', '5^16').replace('if(h>28)', 'if(h>32)')
    if not 5**16 < (1 << 61)-1:
        raise ValueError('Deterministic minor bound failed')
    (workdir/'ternary_target_span_classes.cpp').write_text(span)
    (workdir/'ternary_stream_saturated_scratch.cpp').write_bytes(
        (HERE/'ternary_stream_saturated_scratch.cpp').read_bytes())
    (workdir/'ternary_stream_bilateral_scratch.cpp').write_bytes(
        (HERE/'ternary_stream_bilateral_scratch.cpp').read_bytes())
    star = (HERE/'ternary_star_demands.cpp').read_text()
    if 'if(h>31||h<8)' not in star:
        raise ValueError('Unexpected retained star dimension guard')
    (workdir/'ternary_star_demands.cpp').write_text(star.replace('if(h>31||h<8)', 'if(h>32||h<8)'))
    audit = (HERE/'ternary_dag_audit.cpp').read_text()
    if 'h>28' not in audit:
        raise ValueError('Unexpected retained DAG audit dimension guard')
    (workdir/'ternary_dag_audit.cpp').write_text(audit.replace('h>28', 'h>32'))
    (workdir/'ternary_target_fingerprint.cpp').write_bytes(
        (HERE/'ternary_target_fingerprint.cpp').read_bytes())
    binaries = {}
    for name in ('stream_saturated_scratch', 'stream_bilateral_scratch', 'star_demands', 'dag_audit'):
        binary = workdir/name
        subprocess.run(['c++', '-std=c++17', '-O3',
                        str(workdir/f'ternary_{name}.cpp'), '-o', str(binary)], check=True)
        binaries[name] = binary
    sources = ('ternary_target_span_classes.cpp', 'ternary_stream_saturated_scratch.cpp',
               'ternary_stream_bilateral_scratch.cpp',
               'ternary_star_demands.cpp', 'ternary_dag_audit.cpp',
               'ternary_target_fingerprint.cpp')
    manifest = dict(
        scope='Isolated sweep copies; retained source files unchanged',
        maximum_h=32, span_columns=32, minor_bound=5**16, prime=(1 << 61)-1,
        changes={'ternary_target_span_classes.cpp': '28 to32 columns and deterministic minor bound',
                 'ternary_star_demands.cpp': 'ground-size guard31 to32',
                 'ternary_dag_audit.cpp': 'ground-size guard28 to32'},
        original_sha256={name: sha256((HERE/name).read_bytes()).hexdigest() for name in sources},
        compiled_source_sha256={name: sha256((workdir/name).read_bytes()).hexdigest() for name in sources})
    (workdir/'SOURCE.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    return binaries


def finish_case(workdir, h, binaries, dual, depth=4):
    workdir = Path(workdir)
    result = {}
    original, dag = workdir/'dag.bin', workdir/'rewritten.bin'
    demands, templates = workdir/'star-demands.txt', workdir/'star-templates.bin'
    result['extract'] = run_json([binaries['star_demands'], original, demands], workdir/'stars.log')
    result['stars'] = resynthesize(demands, h, templates)
    result['rewrite'] = run_json([binaries['star_demands'], original, demands, templates, dag], workdir/'rewrite.log')
    targets = workdir/'rewritten-targets.bin'
    result['frames'] = run_json([dual, dag, workdir/'rewritten-unresolved.txt',
                                workdir/'rewritten-labels.bin', targets], workdir/'rewritten-frames.log')
    if not result['frames'].get('failed'):
        result['stream'] = run_json([binaries['stream_saturated_scratch'], dag, targets, depth,
                                    workdir/'saturated-links.bin', 'mixed'], workdir/'saturated.log')
        if not result['stream'].get('failed'):
            result['ranking'] = rank(h, result['stream']['new_roles'])
    result['status'] = 'FINGERPRINT DISCOVERY; EXACT SUPPORT AUDIT STILL REQUIRED'
    (workdir/'finished.json').write_text(json.dumps(result, indent=2, sort_keys=True, default=str)+'\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--h', type=int, required=True)
    p.add_argument('--splits', type=int, nargs='+', required=True)
    p.add_argument('--workdir', type=Path, required=True)
    p.add_argument('--finish-best', type=int, default=1)
    p.add_argument('--fingerprint', type=Path, default=Path('/private/tmp/ternary-target-fingerprint'))
    p.add_argument('--dual', type=Path, default=Path('/private/tmp/ternary-target-dual'))
    p.add_argument('--stream', type=Path, default=Path('/private/tmp/ternary-stream-reuse'))
    args = p.parse_args()
    if args.h > 32 or args.h < 8 or args.h % 2:
        p.error('Explicit screen supports even dimensions 8 through32')
    args.workdir.mkdir(parents=True, exist_ok=True)
    check = matching(args.h)
    (args.workdir/'matching.json').write_text(json.dumps(check, indent=2, sort_keys=True)+'\n')
    search = Search()
    candidates = []
    for split in args.splits:
        folder = args.workdir/f'h{args.h}-split{split}'
        result = screen(args.h, split, 'selected', search, folder,
                        args.fingerprint, args.dual, args.stream, 1, True)
        if not result.get('stream', {}).get('failed') and 'stream' in result:
            roles = result['stream']['new_roles']
            ranking = rank(args.h, roles)
            (folder/'ranking.json').write_text(json.dumps(ranking, indent=2, sort_keys=True, default=str)+'\n')
            candidates.append((roles, split, folder))
            print(json.dumps(dict(stage='shallow', h=args.h, split=split, roles=roles,
                                  a=str(ranking['bit']['bit_saving']),
                                  kappa=str(ranking['assembly']['kappa']))), flush=True)
        else:
            print(json.dumps(dict(stage='shallow-failed', h=args.h, split=split)), flush=True)
    binaries = build_sweep_binaries(args.workdir/'binaries')
    for _, split, folder in sorted(candidates)[:args.finish_best]:
        result = finish_case(folder, args.h, binaries, args.dual)
        if 'ranking' in result:
            print(json.dumps(dict(stage='saturated', h=args.h, split=split,
                                  roles=result['stream']['new_roles'],
                                  a=str(result['ranking']['bit']['bit_saving']),
                                  kappa=str(result['ranking']['assembly']['kappa']))), flush=True)
        else:
            print(json.dumps(dict(stage='saturated-failed', h=args.h, split=split)), flush=True)
