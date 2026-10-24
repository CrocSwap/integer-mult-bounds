#!/usr/bin/env python3
"""Exact verifier: per-cut batching on arbitrary-height chronological forests.

Compares an independent multiplicative-polynomial census (batching.py) with
(i) a literal ordered-word/paid-position oracle written here and (ii) the
frozen #4483 Flow, whose bytes are authenticated before execution. Then it
checks least widths, unchanged normalized leaf cost, pooled-batch failures and
semantic rejection controls. Standard library only; no native admission.

Prepared with substantial AI assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement, product as cartesian
import hashlib
import json
from math import gcd, prod
from pathlib import Path
import sys
import tempfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import batching as B  # noqa: E402
from batching import require  # noqa: E402

# Executable predecessor bytes are pinned here as well as in SOURCES.json.
EXEC_PINS = {
    'research/rank-convergence/flow.py':
        'daad9e8e122e0521e0509cd5d36dca16eb5156289f1a77d19a85aa2020f4da8f',
    'research/direct-mixed-flow/flow.py':
        '460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a',
    'research/chronological-batch-width/batches.py':
        '73e7ab4a1925ee7d412d0f2b5d28b70f3a9e43e427c2ec6f6d89f193b84655ef',
}
PROFILE_SOURCE = 'research/higher-moment-strictification/RESULT.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def integer_record(value):
    raw = value.to_bytes(max(1, (value.bit_length()+7)//8), 'big')
    return {'bits': value.bit_length(), 'unsigned_big_endian_sha256': digest(raw)}


def compact_integers(value, limit=1 << 64):
    """Replace every integer above ``limit`` by its bit length and big-endian
    SHA256, so receipts digest unlimited integers without decimal strings."""
    if type(value) is int:
        if abs(value) <= limit:
            return value
        record = integer_record(abs(value))
        return record if value > 0 else {'negative': record}
    if isinstance(value, dict):
        return {k: compact_integers(v, limit) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [compact_integers(v, limit) for v in value]
    return value

# --------------------------------------------------------------------------
# Source authentication
# --------------------------------------------------------------------------

def authenticated(relative, sources):
    """Bytes of a SOURCES.json input row after SHA256 and Git-blob checks."""
    row = sources[relative]
    data = (ROOT/relative).read_bytes()
    require(digest(data) == row['sha256'], 'source SHA256 '+relative)
    blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(blob == row['git_blob'], 'source Git blob '+relative)
    if relative in EXEC_PINS:
        require(row['sha256'] == EXEC_PINS[relative], 'executable source pin '+relative)
    return data


def source_rows():
    rows = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']
    return {row['path']: row for row in rows if row['usage'] == 'input'}


def load_module(data, name, path, expected_sha):
    """Execute source bytes only after their SHA256 equals the pin."""
    require(digest(data) == expected_sha, 'changed executable source bytes')
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def load_predecessors(sources):
    check = {path: authenticated(path, sources) for path in sources}
    flow_path = ROOT/'research/rank-convergence/flow.py'
    flow = load_module(check['research/rank-convergence/flow.py'], '_adaptive_flow_4483',
                       flow_path, EXEC_PINS['research/rank-convergence/flow.py'])
    batches = load_module(check['research/chronological-batch-width/batches.py'],
                          '_chronological_batches_4507',
                          ROOT/'research/chronological-batch-width/batches.py',
                          EXEC_PINS['research/chronological-batch-width/batches.py'])
    return flow, batches, check


def expect_failure(function, fragment):
    try:
        function()
    except ValueError as exc:
        require(fragment in str(exc), 'expected rejection '+repr(fragment)+', got '+repr(str(exc)))
        return str(exc)
    raise ValueError('control accepted: '+fragment)


# --------------------------------------------------------------------------
# Independent literal oracle: ordered target words and each paid position
# --------------------------------------------------------------------------

def oracle_flow(targets, paid_word, cap, G, class_limit=300000):
    """Replay the forest from ordered target words and individual paid jobs.

    No Pascal coefficient, product-keyed polynomial or merged path count is
    used. A unit is an ordered target word of the class's remaining length
    whose product (with the path multiplier) fits cap; its weight is the
    product of rank multiplicities. A parent job and a child demand are the
    same job exactly when their words have the same rank multiset. Every paid
    position is processed separately and every child returns before the next
    position. A child with multiplier above cap contains no unit, hence
    neither do its descendants, and is not instantiated.
    """
    ranks = sorted(targets)
    cache = {}
    classes = 0

    def words(level, rho):
        """Weight of each ordered word of this length by its sorted content."""
        if (level, rho) not in cache:
            found = Counter()

            def extend(prefix, column, weight):
                if len(prefix) == level:
                    found[tuple(sorted(prefix))] += weight
                    return
                for k in ranks:
                    if rho*column*k <= cap:
                        extend(prefix+(k,), column*k, weight*targets[k])
            if rho <= cap:
                extend((), 1, 1)
            cache[(level, rho)] = found
        return cache[(level, rho)]

    def column(content):
        result = 1
        for k in content:
            result *= k
        return result

    def demand_of(level, rho):
        """Jobs requested by the units of words(level, rho): word plus a letter."""
        result = Counter()
        for content, weight in words(level, rho).items():
            for k in ranks:
                result[tuple(sorted(content+(k,)))] += targets[k]*weight
        return result

    out = {'roots': Counter(), 'inner': Counter(), 'boundary': Counter(),
           'leaves': Counter(), 'columns': Counter(), 'units': 0,
           'matched': 0, 'cuts': Counter()}

    def process(depth, rho, incoming):
        nonlocal classes
        classes += 1
        require(classes <= class_limit, 'oracle class limit')
        want = demand_of(G-depth, rho)
        for content, weight in want.items():
            require(incoming[content] <= weight, 'oracle incoming fits demand')
            missing = weight-incoming[content]
            if missing:
                out['roots' if depth == 0 else 'inner'][rho*column(content)] += missing
        here = words(G-depth, rho)
        for content, weight in here.items():
            out['units'] += weight
            out['columns'][rho*column(content)] += weight
        for r in paid_word:
            rr = rho*r
            if depth == G:
                for content, weight in here.items():
                    out['leaves'][rr*column(content)] += weight
                    out['cuts'][(depth, rho, r, rr*column(content), weight)] += 1
                continue
            child_want = demand_of(G-depth-1, rr)
            passed, local = Counter(), Counter()
            for content in here.keys() | child_want.keys():
                have, need = here.get(content, 0), child_want.get(content, 0)
                passed[content] = min(have, need)
                out['matched'] += min(have, need)
                if have > need:
                    local[rr*column(content)] += have-need
            for rank, weight in sorted(local.items()):
                out['boundary'][rank] += weight
                out['cuts'][(depth, rho, r, rank, weight)] += 1
            if rr <= cap:
                process(depth+1, rr, +passed)

    process(0, 1, Counter())
    out['classes'] = classes
    return {k: (+v if isinstance(v, Counter) and k != 'cuts' else v) for k, v in out.items()}


def paid_word(paid, reverse=False):
    word = [r for r in sorted(paid) for _ in range(paid[r])]
    return word[::-1] if reverse else word


def same_as_oracle(flow, oracle):
    """Compare every census component with the literal replay."""
    for mine, theirs in (('roots', 'roots'), ('inner', 'inner'), ('boundary', 'boundary'),
                         ('leaves', 'leaves'), ('columns', 'columns')):
        require(Counter(flow[mine]) == Counter(oracle[theirs]), 'literal oracle '+mine)
    require(flow['units'] == oracle['units'], 'literal oracle units')
    require(flow['matched'] == oracle['matched'], 'literal oracle matched jobs')
    require(B.compressed_cuts(flow) == oracle['cuts'], 'literal oracle cut multiset')
    return True


def same_as_source(flow, source):
    """Compare with the authenticated #4483 Flow receipt (sources, exits, splits)."""
    pairs = (('roots', 'root_sources'), ('inner', 'nonroot_sources'),
             ('sources', 'sources'), ('boundary', 'boundary_exits'),
             ('leaves', 'leaf_exits'), ('exits', 'exits'), ('columns', 'unit_columns'))
    for mine, theirs in pairs:
        require(Counter(flow[mine]) == Counter(source[theirs]), 'source Flow '+mine)
    for mine, theirs in (('units', 'units'), ('column_mass', 'column_mass'),
                         ('matched', 'matched_jobs')):
        require(flow[mine] == source[theirs], 'source Flow '+mine)
    return True


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

TOY_PROFILES = [
    ('overlap', {2: 1, 5: 1}, {1: 2, 4: 1}),
    ('collision', {2: 1, 4: 1, 8: 1}, {1: 2, 3: 1}),
    ('weighted', {2: 2, 3: 1}, {1: 1, 2: 2}),
    ('repeat', {2: 4, 3: 1}, {1: 6, 2: 2}),
]
HEIGHT_RULES = [('fixed', 0), ('fixed', 1), ('fixed', 2), ('fixed', 3),
                ('default',), ('adaptive', 2, 1, 1), ('adaptive', 2, 2, 1),
                ('adaptive', 3, 1, 1)]

GEOMETRIES = [
    # name, targets, paid, rule, maximum
    ('overlap-two-bit', {2: 1, 5: 1}, {1: 2, 4: 1}, ('adaptive', 2, 1, 1), 100),
    ('collision-two-bit', {2: 1, 4: 1, 8: 1}, {1: 2, 3: 1}, ('adaptive', 2, 1, 1), 100),
    ('repeat-two-bit', {2: 4, 3: 1}, {1: 6, 2: 2}, ('adaptive', 2, 1, 1), 100),
    ('repeat-default', {2: 4, 3: 1}, {1: 6, 2: 2}, ('default',), 100),
]
P7_GEOMETRIES = [
    # (the BENCHMARKS witness base 256 gives G=0 through rank 1,000; it is
    # exercised only by the census comparison below at its true boundaries)
    ('p7-two-bit-height', ('adaptive', 2, 1, 1), 1209),
    ('p7-four-base-height', ('adaptive', 4, 1, 1), 1209),
]
SURVEY = GEOMETRIES + [
    ('weighted-two-bit', {2: 2, 3: 1}, {1: 1, 2: 2}, ('adaptive', 2, 1, 1), 100),
    ('overlap-three', {2: 1, 5: 1}, {1: 2, 4: 1}, ('adaptive', 3, 1, 1), 100),
    ('overlap-g2', {2: 1, 5: 1}, {1: 2, 4: 1}, ('fixed', 2), 100),
    ('collision-g2', {2: 1, 4: 1, 8: 1}, {1: 2, 3: 1}, ('fixed', 2), 100),
    ('repeat-g2', {2: 4, 3: 1}, {1: 6, 2: 2}, ('fixed', 2), 100),
    ('repeat-g3', {2: 4, 3: 1}, {1: 6, 2: 2}, ('fixed', 3), 100),
    ('triple-g2', {2: 1, 3: 1, 5: 2}, {1: 3, 2: 1, 4: 2}, ('fixed', 2), 100),
    ('triple-two-bit', {2: 1, 3: 1, 5: 2}, {1: 3, 2: 1, 4: 2}, ('adaptive', 2, 1, 1), 100),
]


def p7_profile(sources):
    data = authenticated(PROFILE_SOURCE, sources)
    bench = json.loads(authenticated('research/rank-convergence/BENCHMARKS.json', sources))
    case = next(c for c in bench['cases'] if c['name'] == 'p7')
    require(case['source'] == PROFILE_SOURCE and case['profile_key'] == 'invoice_oracle',
            'BENCHMARKS p7 profile source')
    invoice = json.loads(data)['invoice_oracle']
    parse = lambda h: {int(k): v for k, v in h.items()}
    targets, paid = parse(invoice['targets']), parse(invoice['paid'])
    require(sum(targets.values()) == 7688 and sum(paid.values()) == 55998, 'p7 census')
    return targets, paid, case['witness']


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def source_receipt(Flow, targets, paid, n, G):
    return Flow(targets, paid, n, G).merged()


def census_equalities(Flow):
    """Polynomial census == literal oracle == authenticated #4483 Flow."""
    stats = Counter()
    features = Counter()
    for name, targets, paid in TOY_PROFILES:
        m = max(targets)
        word = paid_word(paid)
        heavy = sum(paid.values()) > 5
        for factor in ((1, 2, 3, 4, 5, 8) if heavy else (1, 2, 3, 4, 5, 6, 8, 11)):
            for extra in ((0, m-1) if not heavy else (0,)):
                n = factor*m+extra
                for rule in HEIGHT_RULES:
                    G = B.height(rule, targets, n)
                    if G > (2 if heavy else 6):
                        continue
                    flow = B.census(targets, paid, n//m, G)
                    oracle = oracle_flow(targets, word, n//m, G)
                    same_as_oracle(flow, oracle)
                    same_as_closed(flow, closed_form(targets, paid, n//m, G))
                    if (name, G) in (('overlap', 2), ('weighted', 3)):
                        same_as_oracle(flow, oracle_flow(targets, word[::-1], n//m, G))
                    try:
                        source = source_receipt(Flow, targets, paid, n, G)
                    except ValueError as exc:
                        require('Empty arbitrary-height flow' in str(exc), 'source rejection reason')
                        expect_failure(lambda: B.check_ledger(flow, targets, paid, n),
                                       'nonempty arbitrary-height flow')
                        stats['empty_flows_rejected_by_both'] += 1
                        continue
                    same_as_source(flow, source)
                    B.check_ledger(flow, targets, paid, n)
                    stats['flows'] += 1
                    stats['oracle_classes'] += oracle['classes']
                    features['empty_roots'] += not flow['roots']
                    features['empty_parent_later_components'] += flow['empty_parent_feeds'] > 0
                    features['inner_sources'] += bool(flow['inner'])
                    features['boundary_exits'] += bool(flow['boundary'])
                    features['repeated_cut_occurrences'] += any(c[5] > 1 for c in flow['cuts'])
                    features['height_above_default'] += G > B.height(('default',), targets, n)
                    features['target_product_collisions'] += has_collision(targets, G, n//m)
    return {**stats, **features}


def ordered_products(histogram, length, cap):
    """Ordered words of one length by product, truncated at cap (all ranks >= 1)."""
    result = Counter({1: 1})
    for _ in range(length):
        following = Counter()
        for column, count in result.items():
            for rank, weight in histogram.items():
                if column*rank <= cap:
                    following[column*rank] += count*weight
        result = following
    return result


def closed_form(targets, paid, cap, G):
    """Cut sizes, root and inner sources straight from the proof's formulas.

    With F_h the ordered-target-word polynomial, a present parent product c at
    class (d, rho) and paid rank r (rr = rho*r) leaves at rank rr*c with size
        Q = sum over k | c with rr*(c/k) > cap of W_k F_{G-d-1}(c/k),
    a leaf class (d = G) leaves one unit at rank rr, and an absent parent
    product c (rho*c > cap) adds to the fresh sources at rank rr*c the amount
        sum over k | c with rr*(c/k) <= cap of W_k F_{G-d-1}(c/k).
    Nothing here classifies jobs by content or reuses a flow data structure.
    """
    F = [ordered_products(targets, h, cap) for h in range(G+1)]
    roots, inner, cuts = Counter(), Counter(), Counter()
    for column, count in F[G].items():
        for k, weight in targets.items():
            roots[k*column] += weight*count
    for d in range(G+1):
        for rho, occurrences in ordered_products(paid, d, cap).items():
            for r, repeats in paid.items():
                rr, copies = rho*r, occurrences*repeats
                if d == G:
                    cuts[(d, rho, r, rr, 1)] += copies
                    continue
                below = F[G-d-1]
                for c, parent in F[G-d].items():
                    if rho*c <= cap:
                        size = sum(w*below.get(c//k, 0) for k, w in targets.items()
                                   if c % k == 0 and rr*(c//k) > cap)
                        if size:
                            cuts[(d, rho, r, rr*c, size)] += copies
                # Absent parents: products c = c'*k with c' eligible below.
                fresh = Counter()
                for cprime, count in below.items():
                    if rr*cprime <= cap:
                        for k, w in targets.items():
                            if rho*cprime*k > cap:
                                fresh[cprime*k] += w*count
                for c, amount in fresh.items():
                    inner[rr*c] += copies*amount
    return {'roots': +roots, 'inner': +inner, 'cuts': cuts}


def same_as_closed(flow, formula):
    require(Counter(flow['roots']) == formula['roots'], 'closed form roots')
    require(Counter(flow['inner']) == formula['inner'], 'closed form inner sources')
    require(B.compressed_cuts(flow) == formula['cuts'], 'closed form cuts')
    return True


def has_collision(targets, G, cap):
    """Two distinct same-length target multisets share a product <= cap."""
    for level in range(1, G+1):
        seen = {}
        for content in combinations_with_replacement(sorted(targets), level):
            column = prod(content)
            if column <= cap and seen.setdefault(column, content) != content:
                return True
    return False


COLLISION = ({2: 1, 4: 1, 8: 1}, {1: 1, 5: 1}, 128, 2)


EMPTY_PARENT = ({2: 1, 5: 1}, {1: 2, 4: 1}, 10, 2)


def collision_witness():
    """(2,8) and (4,4) share column 16 and leave the same cut at paid rank 5.

    Both distinct contents exit one cut at rank 80; merging them is part of the
    policy (one batch per rank per cut), and the split fault must be caught.
    """
    targets, paid, n, G = COLLISION
    cap = n//max(targets)
    flow = B.census(targets, paid, cap, G)
    oracle = oracle_flow(targets, paid_word(paid), cap, G)
    same_as_oracle(flow, oracle)
    require(has_collision(targets, G, cap), 'collision witness collides')
    merged = [c for c in flow['cuts'] if c[3] == 80 and c[2] == 5 and c[0] == 0]
    require(len(merged) == 1 and merged[0][4] == 2, 'colliding contents form one cut of size 2')
    split = B.census(targets, paid, cap, G, frozenset({'split-collisions'}))
    require(len(split['cuts']) > len(flow['cuts']), 'split fault separates collisions')
    return flow, split, oracle




def p7_census(Flow, targets, paid, witness):
    """Real profile: the witness height boundary and a two-bit-base height."""
    rows = []
    for rule, ns in ((('adaptive', witness['height_base'], witness['a'], witness['b']),
                      (121, 30975, 30976, 31000, 60000)),
                     (('adaptive', 2, 1, 1), (121, 241, 242, 363, 484, 1209))):
        for n in ns:
            G = B.height(rule, targets, n)
            flow = B.census(targets, paid, n//max(targets), G)
            same_as_source(flow, source_receipt(Flow, targets, paid, n, G))
            B.check_ledger(flow, targets, paid, n)
            rows.append({'n': n, 'height': G, 'sources': sum(flow['sources'].values()),
                         'cuts': len(flow['cuts']), 'empty_root': not flow['roots'],
                         'empty_parent_feeds': flow['empty_parent_feeds']})
    return rows


def minimality_bruteforce():
    count = 0
    for b1, b2, q1, q2 in cartesian(range(1, 9), range(1, 9), range(1, 7), range(1, 7)):
        brute = next(a for a in range(1, b1*b2+1) if a*q1 % b1 == 0 and a*q2 % b2 == 0)
        require(B.multiplier([b1, b2], [(0, q1), (1, q2)]) == brute, 'least multiplier')
        count += 1
    return count


def rational_recurrence(targets, paid, rule, result):
    """Normalized leaf cost from aggregate inventories, independent of widths."""
    m = max(targets)
    cost = [Fraction(k) for k in range(m)]
    flows = result['flows']
    for n in range(m, len(result['widths'])):
        f = flows[(n//m, B.height(rule, targets, n))]
        cost.append((sum(q*cost[n-s] for s, q in f['sources'].items())
                     + sum(q*cost[e] for e, q in f['exits'].items()))
                    / sum(f['sources'].values()))
        require(cost[n] == Fraction(result['leaves'][n], result['widths'][n]),
                'rational leaf recurrence')
        require(cost[n] == Fraction(result['nested_leaves'][n], result['nested'][n]),
                'unchanged normalized leaf cost')
    return True


def summarize(name, targets, paid, rule, maximum, result):
    records = result['records']
    gains = sum(r['width'] < r['nested_width'] for r in records)
    for r in records:
        require(r['nested_width'] % r['width'] == 0, 'least width divides nested width')
    gaps = {p: dict(v) for p, v in result['gaps'].items()}
    return {'name': name, 'rule': list(rule), 'maximum': maximum,
            'targets': {str(k): v for k, v in sorted(targets.items())},
            'paid': {str(k): v for k, v in sorted(paid.items())},
            'compiled_ranks': len(records),
            'batch_constraints': sum(r['batches'] for r in records),
            'cuts': sum(r['cuts'] for r in records),
            'strict_width_gains': gains,
            'width': integer_record(result['widths'][-1]),
            'nested_width': integer_record(result['nested'][-1]),
            'leaves': integer_record(result['leaves'][-1]),
            'nested_leaves': integer_record(result['nested_leaves'][-1]),
            'normalized_leaf_cost_unchanged': True,
            'record_sha256': digest(canonical(compact_integers(records))),
            'pooling_gaps': gaps}


def compile_geometry(name, targets, paid, rule, maximum):
    result = B.compile_widths(targets, paid, maximum, rule)
    rational_recurrence(targets, paid, rule, result)
    return result, summarize(name, targets, paid, rule, maximum, result)


def default_recovery(batches, targets, paid, maximum):
    """The default-height specialization reproduces #4507's widths and leaves."""
    mine = B.compile_widths(targets, paid, maximum, ('default',))
    old = batches.compile_widths(targets, paid, maximum)
    require(mine['widths'] == old['widths'] and mine['nested'] == old['nested_widths']
            and mine['leaves'] == old['leaves'], '#4507 default-height recovery')
    return True


def controls(Flow, results):
    rejected = {}

    def reject(name, function, fragment):
        rejected[name] = expect_failure(function, fragment)

    # Census faults on a forest with no root unit, later components below an
    # empty class, inner sources, boundary exits and repeated paid positions.
    targets, paid, n, G = EMPTY_PARENT
    cap = n//max(targets)
    truth = B.census(targets, paid, cap, G)
    require(not truth['roots'] and truth['inner'] and truth['boundary']
            and truth['empty_parent_feeds'] > 0 and any(c[5] > 1 for c in truth['cuts']),
            'empty-parent witness exercises every class')
    oracle = oracle_flow(targets, paid_word(paid), cap, G)
    same_as_oracle(truth, oracle)
    B.check_ledger(truth, targets, paid, n)
    for fault in ('drop-empty-parent', 'drop-boundary', 'drop-leaf', 'ignore-path-multiplier'):
        reject('census fault '+fault+' versus literal oracle',
               lambda fault=fault: same_as_oracle(
                   B.census(targets, paid, cap, G, frozenset({fault})), oracle),
               'literal oracle')
    for fault in ('drop-boundary', 'drop-leaf'):
        bad = B.census(targets, paid, cap, G, frozenset({fault}))
        reject('census fault '+fault+' versus ledger',
               lambda bad=bad: B.check_ledger(bad, targets, paid, n),
               'formal rank-invoice cancellation')
    # Suppressing the empty parent also disagrees with the authenticated Flow.
    bad = B.census(targets, paid, cap, G, frozenset({'drop-empty-parent'}))
    reject('suppressed empty class versus source Flow',
           lambda: same_as_source(bad, source_receipt(Flow, targets, paid, n, G)), 'source Flow')
    # Target-product collisions: distinct contents with one product form one cut.
    collide, split, collision_oracle = collision_witness()
    reject('split target-product collision',
           lambda: same_as_oracle(split, collision_oracle), 'literal oracle')
    # Tampered executable bytes fail before execution.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'tampered_flow.py'
        data = (ROOT/'research/rank-convergence/flow.py').read_bytes()+b'\nraise RuntimeError("ran")\n'
        path.write_bytes(data)
        reject('tampered flow bytes rejected before execution',
               lambda: load_module(data, 'tampered', path,
                                   EXEC_PINS['research/rank-convergence/flow.py']),
               'changed executable source bytes')
    # Pooled policies: each relaxed multiplier passes its own rows (positive
    # fixture) but leaves an actual chronological cut incomplete.
    chosen = {}
    for geometry, (result, summary) in results.items():
        for policy, gap in summary['pooling_gaps'].items():
            if gap['first'] and policy not in chosen:
                chosen[policy] = (geometry, result, gap['first'])
    specs = {g[0]: (g[1], g[2], g[3]) for g in GEOMETRIES}
    specs.update({g[0]: (*P7_PROFILE_CACHE['p7'][:2], g[1]) for g in P7_GEOMETRIES})
    for policy, (geometry, result, first) in sorted(chosen.items()):
        widths, flow_n = result['widths'], first['n']
        tg, pd, rule = specs[geometry]
        flow = B.census(tg, pd, flow_n//max(tg), B.height(rule, tg, flow_n))
        rows = B.batch_rows(flow, flow_n)
        pooled = B.multiplier(widths, B.batch_rows(flow, flow_n, policy))
        B.check_rows(widths, B.batch_rows(flow, flow_n, policy), pooled)
        reject('pooling '+policy+' ('+geometry+' n='+str(flow_n)+')',
               lambda: B.check_rows(widths, rows, pooled), 'whole chronological batch')
    # A bad multiplier: remove one prime factor from the least value.
    result = results['repeat-two-bit'][0]
    widths = result['widths']
    n = 60
    flow = B.census({2: 4, 3: 1}, {1: 6, 2: 2}, n//3, B.height(('adaptive', 2, 1, 1), {2: 4, 3: 1}, n))
    rows = B.batch_rows(flow, n)
    a = B.multiplier(widths, rows)
    require(a > 1, 'nontrivial multiplier fixture')
    p = next(q for q in range(2, a+1) if a % q == 0)
    B.check_rows(widths, rows, a)
    B.check_rows(widths, rows, 2*a)  # positive: any multiple is valid
    reject('multiplier missing a prime factor', lambda: B.check_rows(widths, rows, a//p),
           'whole chronological batch')
    reject('zero multiplier', lambda: B.check_rows(widths, rows, 0), 'positive replication')
    reject('boolean multiplier', lambda: B.check_rows(widths, rows, True), 'positive replication')
    reject('zero batch count', lambda: B.multiplier([1], [(0, 0)]), 'positive batch count')
    reject('boolean batch count', lambda: B.multiplier([1], [(0, True)]), 'positive batch count')
    reject('future rank', lambda: B.multiplier([1], [(1, 1)]), 'smaller rank')
    reject('zero width', lambda: B.multiplier([0], [(0, 1)]), 'positive supplier width')
    reject('paid rank equal to target maximum',
           lambda: B.validate({2: 1, 5: 1}, {5: 1}, 10), 'strict rank contract')
    reject('non-integer multiplicity', lambda: B.validate({2: 1.0, 5: 1}, {1: 1}, 10),
           'positive integer histogram')
    # Dropped repeated-occurrence leaf cost breaks cost preservation.
    bad = B.compile_widths({2: 4, 3: 1}, {1: 6, 2: 2}, 40, ('adaptive', 2, 1, 1), False)
    reject('omitted repeated-occurrence leaf cost',
           lambda: rational_recurrence({2: 4, 3: 1}, {1: 6, 2: 2}, ('adaptive', 2, 1, 1), bad),
           'rational leaf recurrence')
    # Perturbed receipts are rejected by the ledger.
    flow = B.census({2: 1, 5: 1}, {1: 2, 4: 1}, 4, 2)
    n = 20
    for label, mutate, fragment in (
            ('false root credit', lambda f: f['roots'].update({10: 1}), 'root/inner source partition'),
            ('false unit column', lambda f: f['columns'].update({1: 1}), 'unit column count'),
            ('missing cut', lambda f: f['cuts'].pop(), 'cut inventory equals exit inventory')):
        def run(mutate=mutate):
            clone = {k: (Counter(v) if isinstance(v, Counter) else list(v) if isinstance(v, list) else v)
                     for k, v in flow.items()}
            mutate(clone)
            B.check_ledger(clone, {2: 1, 5: 1}, {1: 2, 4: 1}, n)
        reject(label, run, fragment)
    return rejected


P7_PROFILE_CACHE = {}


def main_result():
    sources = source_rows()
    flow_module, batches, _ = load_predecessors(sources)
    Flow = flow_module.Flow
    require(sources.keys() >= set(EXEC_PINS), 'executable sources declared')
    targets7, paid7, witness = p7_profile(sources)
    P7_PROFILE_CACHE['p7'] = (targets7, paid7, witness)

    equalities = census_equalities(Flow)
    require(equalities['flows'] > 0 and equalities['empty_roots'] > 0
            and equalities['empty_parent_later_components'] > 0
            and equalities['repeated_cut_occurrences'] > 0
            and equalities['height_above_default'] > 0, 'fixtures exercise all classes')
    p7_rows = p7_census(Flow, targets7, paid7, witness)
    require(any(r['empty_parent_feeds'] for r in p7_rows), 'real-profile empty parent')
    brute = minimality_bruteforce()
    for name, t, p, rule, maximum in GEOMETRIES:
        if rule == ('default',):
            default_recovery(batches, t, p, maximum)
    default_recovery(batches, {2: 1, 5: 1}, {1: 2, 4: 1}, 60)

    results = {}
    for name, t, p, rule, maximum in GEOMETRIES:
        results[name] = compile_geometry(name, t, p, rule, maximum)
    for name, rule, maximum in P7_GEOMETRIES:
        results[name] = compile_geometry(name, targets7, paid7, rule, maximum)
    for policy in ('aggregate', 'occurrences', 'leaf-pooled'):
        require(any(s['pooling_gaps'][policy]['first'] for _, s in results.values()),
                'a real pooling gap for '+policy)
    require(any(s['strict_width_gains'] for _, s in results.values()), 'strict width gain')
    rejected = controls(Flow, results)
    first = results['overlap-two-bit'][0]
    table = [{k: v for k, v in r.items() if k in ('n', 'height', 'multiplier', 'sources',
                                                   'width', 'nested_width', 'leaves')}
             for r in first['records'][:24]]
    return {'schema': 'adaptive-chronological-batching/v1',
            'claim_type': 'conditional batch-level transfer and exact finite accounting',
            'no_new_kappa': True, 'no_convergence_or_native_admission_claim': True,
            'source_sha256': {p: r['sha256'] for p, r in sorted(sources.items())},
            'census_equalities': equalities, 'real_profile_census': p7_rows,
            'brute_force_minimality_cases': brute,
            'geometries': [s for _, s in results.values()],
            'small_table_overlap_two_bit': table,
            'rejected_controls': sorted(rejected)}


def survey():
    """Authoring aid: print pooling-gap and width-gain statistics per geometry."""
    sources = source_rows()
    targets7, paid7, witness = p7_profile(sources)
    rows = [(n, t, p, r, m) for n, t, p, r, m in SURVEY]
    rows += [(n, targets7, paid7, r, m) for n, r, m in P7_GEOMETRIES]
    for name, t, p, rule, maximum in rows:
        result = B.compile_widths(t, p, maximum, rule)
        s = summarize(name, t, p, rule, maximum, result)
        print(json.dumps({'name': name, 'gains': s['strict_width_gains'],
                          'ranks': s['compiled_ranks'], 'cuts': s['cuts'],
                          'width_bits': s['width']['bits'], 'nested_bits': s['nested_width']['bits'],
                          'gaps': {k: [v['ranks_with_gap'], v['first'] and v['first']['n']]
                                   for k, v in s['pooling_gaps'].items()}}), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='authoring only: replace RESULT.json')
    ap.add_argument('--survey', action='store_true', help='authoring only: print gap survey')
    args = ap.parse_args()
    if args.survey:
        survey()
        return
    result = json.loads(canonical(compact_integers(main_result())))
    target = HERE/'RESULT.json'
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n',
                          encoding='utf-8', newline='\n')
    else:
        require(result == json.loads(target.read_text(encoding='utf-8')),
                'committed result matches fresh replay')
    print('PASS_ADAPTIVE_CHRONOLOGICAL_BATCHING flows='+str(result['census_equalities']['flows'])
          +' controls='+str(len(result['rejected_controls'])))


if __name__ == '__main__':
    main()
