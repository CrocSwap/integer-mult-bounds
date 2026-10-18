#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Uniform power-cost audit of Gareth Davidson's PR1671 symbolic duals.

The source-bound event/domain model is Aaron Wang/navinor's retained X4
implementation. Two column assemblies below share that model. The new
arithmetic proof imports neither PR1671's numerical checker nor a solver.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '418e40eb2572d930b58c1cf9b82b41c0fc7ee08d'
HEAD = 'ce130d291f5ab6dd801544886a16f62d42d86118'
WORD_SHA = 'c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8'
MODEL = 'research/complex-x4-frame-bound/model.py'
WORD = 'research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz'
PINS = 'research/gauge44-slots/construction/slots/SLOT-PINS-k8.json'
INPUTS = {MODEL, WORD, PINS}
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
RANKS = tuple(range(2, 10))
ZERO = (Q(0),) * 8
SQUARE = (Q(-4), Q(0), Q(1), Q(0), Q(0), Q(0), Q(0), Q(0))
A_MAX = Q(1, 32)
GRAPH = {
    'nodes': 'a5dfe9d076d0a56f20c6eeb5141839a5d3fec0d0e2727d9012bb70d1259de219',
    'domains': 'a0592d32ef9cfbcc272ddc82a6fc4f6ac8b87e721ff9ac92a8c7ad15a65513be',
    'edges': 'a4ff296752a5697f574fb55fe99d3016be9d1d73873321ba9b2cd9bbfbe67edd',
    'cones': 'f844c0e7e667935050e02beb151b0cb9a5b45fc912ea436afc7158c425814661',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('noninteger JSON number: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=bad, parse_constant=bad)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def source_inputs():
    source = parse((HERE / 'SOURCES.json').read_bytes())
    need(source['base_commit'] == BASE, 'source base')
    entries = source['files']
    provenance = {'certificates/selected-result.json', 'docs/research/agent-task-catalog.json'}
    need(len(entries) == len(INPUTS | provenance) and
         {r['path'] for r in entries} == INPUTS | provenance, 'source inventory')
    for row in entries:
        path = row['path']
        need(row['usage'] == ('input' if path in INPUTS else 'provenance'), 'source usage')
        if path in INPUTS:
            raw = (ROOT / path).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'live source SHA256')
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(blob == row['git_blob'], 'live source Git blob')
    predecessor = source['predecessor']
    need(predecessor['pr'] == 1671 and predecessor['head'] == HEAD, 'predecessor head')
    dual_pin = [r for r in predecessor['files'] if r['path'].endswith('/DUALS.json.gz')]
    need(len(dual_pin) == 1, 'dual source inventory')
    raw = (HERE / 'DUALS.json.gz').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == dual_pin[0]['sha256'], 'dual source SHA256')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == dual_pin[0]['git_blob'], 'dual source Git blob')
    dual = parse(gzip.decompress(raw))
    need(dual['schema'] == 'selected-k8-frame-duals-v1' and
         dual['word_sha256'] == WORD_SHA, 'dual word binding')
    raw = gzip.decompress((ROOT / WORD).read_bytes())
    pins = parse((ROOT / PINS).read_bytes())
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA == pins['word_sha256'], 'selected word binding')
    word = parse(raw)
    need(word['report']['R'] == 480 and word['report']['v'] == 112 and word['report']['h'] == 9,
         'selected word dimensions')
    need({int(r): n for r, n in word['report']['local_profile'].items()} == PROFILE,
         'selected word profile')
    model_module = types.ModuleType('retained_navinor_model')
    model_module.__file__ = str(ROOT / MODEL)
    # Frozen predecessor assertions stay enabled even under an optimized caller.
    exec(compile((ROOT / MODEL).read_bytes(), str(ROOT / MODEL), 'exec', optimize=0),
         model_module.__dict__)
    return model_module, word, dual


@lru_cache(None)
def span(frame):
    result = {0}
    for vector in frame:
        result |= {x ^ vector for x in result}
    return sum(1 << x for x in result)


def nested(left, right):
    return span(left) & ~span(right) == 0


def graph_checks(model):
    payloads = {
        'nodes': [[list(n), span(model.lo[n]), span(model.hi[n])] for n in sorted(model.lo)],
        'domains': [[list(n), sorted(span(f) for f in model.domain[n])] for n in sorted(model.domain)],
        'edges': [[list(a), list(b), k] for (a, b), k in sorted(model.edges.items())],
        'cones': [[k, span(f)] for k, f in sorted(model.ceil.items())],
    }
    need({k: digest(v) for k, v in payloads.items()} == GRAPH, 'complete graph binding')
    for node, domain in model.domain.items():
        k = len(model.hi[node]) - len(model.lo[node])
        need(k in (1, 2, 3), 'quotient dimension')
        need(len(domain) == len(set(domain)) == {1: 2, 2: 5, 3: 16}[k], 'complete subspace interval')
        need(all(nested(model.lo[node], f) and nested(f, model.hi[node]) for f in domain),
             'frame interval containment')
    need(len(model.gates) == 5413 and len(model.domain) == 1741, 'gate coverage')
    need(model.profile(model.baseline()) == PROFILE, 'literal baseline profile')
    # Every register's expected dimension increments telescope, also in the LP.
    mass = sum(len(model.hi[ch[-1]]) - len(model.lo[ch[0]]) for ch in model.chains.values())
    mass += sum(model.centre_children)
    need(mass == sum(r*n for r, n in PROFILE.items()) == 5586, 'fixed local mass')
    return mass


def dual_vectors(record, rows):
    allowed = {json.dumps(r) for r in rows}
    need(set(record['duals']) <= allowed, 'unknown dual row')
    result = {}
    for row in rows:
        values = record['duals'].get(json.dumps(row), {})
        need(all(d in {str(r) for r in RANKS} and type(v) is str for d, v in values.items()),
             'dual coefficient domain')
        result[row] = tuple(Q(values.get(str(d), '0')) for d in RANKS)
    return result


def direct_columns(model, component, dual):
    """Reassemble from graph edges, without component_problem(), lp() or their costs.

    Shared event/domain model; this is an independent column assembly, not an
    independent implementation of the source word or its cone conditions.
    """
    members = set(component)
    links = defaultdict(list)
    for (left, right), multiplicity in model.edges.items():
        if left in members:
            links[left].append((left, right, multiplicity, 0))
        if right in members:
            links[right].append((left, right, multiplicity, 1))
    result = {}
    for node in component:
        for frame in model.domain[node]:
            cost = [0] * 10
            residual = [-v for v in dual[('N', node)]]
            for left, right, multiplicity, side in links[node]:
                other = right if side == 0 else left
                if other in members:
                    q = dual[('M', left, right, side, frame)]
                    residual = [a+b for a, b in zip(residual, q)]
                else:
                    before, after = ((frame, model.lo[other]) if side == 0
                                     else (model.lo[other], frame))
                    need(nested(before, after), 'direct unary nesting')
                    jump = len(after) - len(before)
                    if jump:
                        cost[jump] += multiplicity
            residual = tuple(residual[d-2] + cost[d] for d in RANKS)
            result[('x', node, frame)] = (tuple(cost), residual)
    for (left, right), multiplicity in model.edges.items():
        if left not in members or right not in members:
            continue
        for before in model.domain[left]:
            for after in model.domain[right]:
                if not nested(before, after):
                    continue
                cost = [0] * 10
                jump = len(after) - len(before)
                if jump:
                    cost[jump] = multiplicity
                q0 = dual[('M', left, right, 0, before)]
                q1 = dual[('M', left, right, 1, after)]
                residual = tuple(cost[d] - q0[d-2] - q1[d-2] for d in RANKS)
                result[('y', left, right, before, after)] = (tuple(cost), residual)
    return result


def audit_lp(module, model, data):
    components = model.components()
    need(len(data['components']) == len(components) == 135, 'complete component coverage')
    histogram, stats, witnesses = Counter(), Counter(), {}
    total = Counter(model.fixed_profile())
    stream = hashlib.sha256()
    for ci, (component, record) in enumerate(zip(components, data['components'])):
        need(record['first'] == json.dumps(component[0]) and record['nodes'] == len(component),
             'component identity')
        labels, unary, pairs = model.component_problem(component)
        rows, rhs, columns = module.lp(labels, unary, pairs)
        dual = dual_vectors(record, rows)
        table = {}
        for key, cost, entries in columns:
            residual = [Q(cost[d]) for d in RANKS]
            for index, coefficient in entries:
                residual = [a-coefficient*b for a, b in zip(residual, dual[rows[index]])]
            need(key not in table, 'duplicate LP column')
            vector = tuple(residual)
            table[key] = (tuple(cost), vector)
            histogram[vector] += 1
            witnesses.setdefault(vector, {'component': ci, 'column': json.dumps(key)})
            stream.update(canonical([ci, key, cost, list(map(str, vector))]) + b'\n')
        need(table == direct_columns(model, component, dual), 'two column assemblies disagree')
        objective = tuple(sum((b*dual[row][d-2] for row, b in zip(rows, rhs)), Q(0)) for d in RANKS)
        baseline = module.assignment_cost(labels, unary, pairs,
                                          {n: model.baseline()[n] for n in component})
        need(objective == tuple(baseline[d] for d in RANKS), 'symbolic objective mismatch')
        total.update({d: baseline[d] for d in range(1, 10) if baseline[d]})
        stats.update(components=1, rows=len(rows), columns=len(columns))
    need(dict(total) == PROFILE, 'full fixed and variable profile coverage')
    need(dict(stats) == {'components': 135, 'rows': 17507, 'columns': 23004}, 'LP coverage')
    need(len(histogram) == 239 and histogram[ZERO] == 16564, 'residual coverage')
    return histogram, witnesses, dict(stats), stream.hexdigest()


def dyadic_down(value, bits):
    scale = 1 << bits
    return Q((value.numerator * scale) // value.denominator, scale)


@lru_cache(None)
def log_bounds(n):
    """Independent ln(n) enclosure by binary range reduction and atanh.

    Remaining atanh tail after j terms is bounded by
    z^(2j+1)/((2j+1)(1-z^2)); all computation is rational.
    """
    need(type(n) is int and 1 <= n <= 9, 'log domain')
    def series(z):
        need(0 <= z <= Q(1, 3), 'atanh domain')
        if not z:
            return Q(0), Q(0)
        total, power, j = Q(0), z, 0
        while True:
            total += power / (2*j+1)
            power *= z*z
            j += 1
            tail = power / ((2*j+1)*(1-z*z))
            if tail < Q(1, 1 << 144):
                return total, total+tail
    k = n.bit_length()-1
    base = 1 << k
    l2, u2 = series(Q(1, 3))
    lo, hi = series(Q(n-base, n+base))
    return dyadic_down(2*k*l2+2*lo, 128), -dyadic_down(-2*k*u2-2*hi, 128)


def slope_lower_polynomial(vector):
    """Lower bound for sum v_d*d*(exp(-a ln d)-1)/a, a>0.

    Nine exponential terms give a lower bound, eight give an upper bound.
    Choose by the coefficient sign, then round each log power in the
    direction appropriate for its signed polynomial coefficient.
    """
    result = [Q(0)] * 9
    for d, weight in zip(RANKS, vector):
        if not weight:
            continue
        terms = 9 if weight > 0 else 8
        lo, hi = log_bounds(d)
        for k in range(1, terms+1):
            multiplier = Q((-1)**k) * weight*d / factorial(k)
            result[k-1] += multiplier * (lo if multiplier > 0 else hi)**k
    return result


def bernstein(power_coefficients, endpoint):
    n = len(power_coefficients)-1
    return tuple(sum((power_coefficients[i] * endpoint**i * Q(comb(j, i), comb(n, i))
                      for i in range(j+1)), Q(0)) for j in range(n+1))


def uniform_certificate(vector, endpoint=A_MAX):
    need(Q(0) < endpoint and endpoint*log_bounds(9)[1] < 1, 'alternating-series range')
    need(len(vector) == 8, 'residual dimension')
    if vector == ZERO:
        return {'proof': 'identically-zero'}
    if vector == SQUARE:
        # 4*(4^-a-1) - 8*(2^-a-1) = 4*(1-2^-a)^2.
        return {'proof': '4*(1-2^-a)^2'}
    coefficients = bernstein(slope_lower_polynomial(vector), endpoint)
    margin = dyadic_down(min(coefficients), 96)
    need(margin > 0, 'uniform Bernstein positivity failed')
    return {'proof': 'degree-8-Bernstein', 'slope_lower_bound': str(margin)}


def root_floor(value, exponent):
    """Integer-only root enclosure, used for the out-of-range control."""
    need(type(value) is int and value >= 0 and type(exponent) is int and exponent > 0,
         'root domain')
    lo, hi = 0, 1 << ((value.bit_length()+exponent-1)//exponent)
    while hi-lo > 1:
        mid = (lo+hi)//2
        if mid**exponent <= value:
            lo = mid
        else:
            hi = mid
    need(lo**exponent <= value < (lo+1)**exponent, 'integer root enclosure')
    return lo


def power_boundary(vector):
    """Exact residual interval at a=1/20, after removing the positive 73^a."""
    scale = 1 << 96
    lower = upper = Q(0)
    for d, weight in zip(RANKS, vector):
        if not weight:
            continue
        radicand = d**19 * scale**20
        integer = root_floor(radicand, 20)
        lo, hi = Q(integer, scale)-d, Q(integer+1, scale)-d
        lower += weight * (lo if weight > 0 else hi)
        upper += weight * (hi if weight > 0 else lo)
    need(upper < 0, 'power-boundary counterexample must be negative')
    return [str(lower), str(upper)]


def alternative_optimum(model):
    """One distinct legal frame assignment, with exactly the same paid profile."""
    baseline = model.baseline()
    touching = defaultdict(list)
    for (left, right), mult in model.edges.items():
        touching[left].append((left, right, mult))
        touching[right].append((left, right, mult))
    def current(node):
        return baseline.get(node, model.lo[node])
    for node in sorted(model.domain):
        for candidate in model.domain[node]:
            if candidate == baseline[node]:
                continue
            change = Counter()
            for left, right, mult in touching[node]:
                before, after = current(left), current(right)
                x = candidate if left == node else before
                y = candidate if right == node else after
                if not nested(x, y):
                    break
                old, new = len(after)-len(before), len(y)-len(x)
                if old:
                    change[old] -= mult
                if new:
                    change[new] += mult
            else:
                if not any(change.values()):
                    altered = dict(baseline)
                    altered[node] = candidate
                    need(model.profile(altered) == PROFILE, 'alternative optimum full replay')
                    return {'gate': list(node), 'before': list(baseline[node]),
                            'after': list(candidate), 'profile': {str(r): n for r, n in PROFILE.items()}}
    raise ValueError('no distinct optimum fixture found')


def run():
    module, word, duals = source_inputs()
    model = module.Model(word)
    mass = graph_checks(model)
    histogram, witnesses, stats, columns_digest = audit_lp(module, model, duals)
    proofs = []
    by_kind = Counter()
    for vector, count in sorted(histogram.items()):
        proof = uniform_certificate(vector)
        by_kind[proof['proof']] += count
        proofs.append({'residual': list(map(str, vector)), 'columns': count, **proof})
    concave_vector = (Q(-3), Q(1), Q(0), Q(0), Q(0), Q(0), Q(0), Q(0))
    hinge = [min(r, 2) for r in range(10)]
    concave_value = sum(v*(hinge[d]-d*hinge[1]) for d, v in zip(RANKS, concave_vector))
    need(concave_vector in histogram and concave_value == -1, 'concave boundary fixture')
    power_vector = (Q(0), Q(8), Q(1), Q(-4), Q(0), Q(0), Q(0), Q(0))
    need(power_vector in histogram, 'power boundary source column')
    boundaries = {
        'all_concave': {'price': hinge, 'residual': list(map(str, concave_vector)),
                        'value': str(concave_value), **witnesses[concave_vector]},
        'a_one_twentieth': {'a': '1/20', 'residual': list(map(str, power_vector)),
                           'value_interval': power_boundary(power_vector), **witnesses[power_vector]},
        'meaning': 'The published dual fails outside the certified cone/range; neither fixture proves a better feasible frame assignment.',
    }
    return {
        'schema': 'selected-k8-uniform-frame-audit-v1',
        'status': 'PASS_SELECTED_K8_UNIFORM_FRAME_AUDIT',
        'predecessor_head': HEAD, 'word_sha256': WORD_SHA, 'duals_payload_sha256': digest(duals),
        'graph_sha256': GRAPH, 'column_stream_sha256': columns_digest,
        'a_interval': ['0', str(A_MAX)], 'strict_interval': '0 < a <= 1/32',
        'local_mass': mass, 'baseline_profile': {str(r): n for r, n in PROFILE.items()},
        'lp': stats, 'distinct_residual_vectors': len(proofs),
        'columns_by_proof': dict(sorted(by_kind.items())), 'residual_proofs': proofs,
        'distinct_frame_same_profile': alternative_optimum(model),
        'boundaries': boundaries,
        'scope': 'Uniform fixed-word frame LP optimum and uniqueness of the optimal paid histogram. Shared pinned event/domain model; no physical supplier, new kappa or full multiplication theorem.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(canonical(parse(path.read_bytes())) == canonical(result), 'result receipt mismatch')
    print(result['status'], 'columns=23004 vectors=239 interval=0..1/32 optimal_profile_unique',
          'no_new_kappa receipt='+digest(result))


if __name__ == '__main__':
    main()
