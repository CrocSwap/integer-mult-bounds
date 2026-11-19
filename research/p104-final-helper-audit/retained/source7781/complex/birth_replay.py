#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct calibrated rational helper births from the released #7776 supplier."""

from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha1, sha256
from math import gcd, lcm
from pathlib import Path
import argparse
import gzip
import json
import sys


HERE = Path(__file__).resolve().parent
SOURCE = Path('research/p104-dual-supplier-lift/complex')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def locked_source(root, journal):
    lock = json.loads((HERE.parent/'SOURCE-LOCK.json').read_bytes())['sources']['source']
    require(lock['commit'] == journal['source']['head']
            and lock['repository'] == journal['source']['repository'], 'source-lock commit and repository')
    paths = tuple((k, v) for k, v in lock['files'].items() if Path(k).is_relative_to(SOURCE))
    require(paths, 'original complex source inventory')
    for relative, pin in paths:
        raw = (root/relative).read_bytes()
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(sha256(raw).hexdigest() == pin['sha256'] and sha1(blob).hexdigest() == pin['blob'],
                f'changed original source {relative}')
    return root/SOURCE, len(paths)


@cache
def subspace(axes):
    values = {0}
    for a in axes:
        require(type(a) is int and 0 < a < 512 and a not in values, 'independent ambient chart axes')
        values.update(v ^ a for v in tuple(values))
    return frozenset(values)


def interior(a, c, b, spans):
    return spans[a] < spans[c] < spans[b] or spans[b] < spans[c] < spans[a]


def endpoint_map(layout, n):
    expected = [{i: Fraction(1)} for i in range(n)]
    hosted = set(layout['hosted']['Dports'])
    mains = set()
    for i, x in enumerate(layout['live']):
        y = x + 112
        mains.update((x, y))
        if i in hosted:
            expected[y][x] = Fraction(1)
        else:
            expected[x][y] = Fraction(-1)
            expected[y] = {x: Fraction(1, 2), y: Fraction(1, 2)}
    for x, y in zip(layout['hosted']['X2'], layout['hosted']['Y2'], strict=True):
        expected[x][y] = Fraction(-1)
        mains.update((x, y))
    require(len(mains) == 400 and len(layout['live']) == len(set(layout['ports'])) == 104,
            'complete retained main-port layout')
    return expected, mains


def transpose_rows(rows):
    result = [{} for _ in rows]
    for i, row in enumerate(rows):
        for j, q in row.items():
            result[j][i] = q
    return result


def arbitrary_inputs(net, expected):
    """Compute each rational coefficient exactly, using a common denominator per row."""
    inputs = {~i: (1, {i: 1}) for i in range(len(expected))}
    for k in net.schedule():
        terms = []
        for i, q in net.forms[k].items():
            denominator, values = inputs[i]
            if values:
                terms.append((q.numerator, denominator*q.denominator, values))
        denominator = lcm(*(d for _, d, _ in terms))
        row = {}
        for q, d, values in terms:
            weight = q*(denominator//d)
            for j, v in values.items():
                row[j] = row.get(j, 0) + weight*v
        row = {j:v for j, v in row.items() if v}
        common = gcd(denominator, *row.values())
        if k < net.first_output:
            inputs[k] = denominator//common, {j:v//common for j, v in row.items()}
        else:
            require({j: Fraction(v, denominator) for j, v in row.items()} == expected[k-net.first_output],
                    f'arbitrary input endpoint {k-net.first_output}')


def one_column(net, input_role):
    value = {~input_role: Fraction(1)}
    for node in net.schedule():
        q = sum((c*value[i] for i, c in net.forms[node].items() if i in value), Fraction(0))
        if q:
            value[node] = q
    return {k-net.first_output: str(v) for k, v in value.items() if k >= net.first_output}


def row_wire(row):
    return None if row is None else [[i,str(q)] for i,q in sorted(row.items())]


def apply_step(net, frames, spans, labels, step, supplier, birth):
    event = step['event']
    e, f = step['source_paid'], step['new_paid']
    c = event['split_chart']
    old = net.transpose() if step['descending'] else net
    a, b = old.moves[e]
    require([a,b] == step['old_paid_charts'] and type(f) is int and 0 <= f < old.first_output
            and f not in old.moves, 'paid subdivision preimage and fresh home')
    h = event['role']
    s, t = old.initial[h], old.final[h]
    require((s,t) == (event['source_chart'], event['return_chart'])
            and interior(a,c,b,spans) and interior(s,c,t,spans), 'nested paid and productive daughter charts')
    require([abs(len(frames[i])-len(frames[c])) for i in (a,b)] == step['paid_daughter_ranks']
            and [abs(len(frames[i])-len(frames[c])) for i in (s,t)] == step['target_daughter_ranks'],
            'literal rank split lists')
    fresh = len(old.initial)
    require(fresh == step['allocated_role'] and len(labels) > fresh, 'fresh independent input and output label')
    delta = old.forms | {f: old.forms[e], e: {f: Fraction(1)}}
    split = type(old)(old.first_output, old.initial, old.final,
                      old.moves | {f:(a,c), e:(c,b)}, delta)
    result = birth(split, event)
    omitted = birth(split, dict(event, pulse=[]))
    if step['descending']:
        result, omitted = result.transpose(), omitted.transpose()
    omitted_value = one_column(omitted, fresh)
    require(omitted_value != {fresh:'1'}, f'original output control for newly born owner {fresh}')
    affected = [k for k in sorted(net.forms.keys() | result.forms.keys()) if
                net.forms.get(k) != result.forms.get(k)]
    original_send = row_wire(old.forms[e])
    proof = dict(parent_sha256=digest(supplier.dump_graph(net, frames)), result_sha256=digest(supplier.dump_graph(result, frames)),
                 original_owner_label=labels[h], new_owner_label=labels[fresh],
                 original_oriented_paid_row=original_send, affected_rows=len(affected),
                 literal_row_delta_sha256=digest([[k,row_wire(net.forms.get(k)),row_wire(result.forms.get(k))]
                                                    for k in affected]),
                 omitted_fresh_input_row=omitted_value, expected_fresh_input_row={str(fresh):'1'})
    if 'replay' in step:
        normalized = json.loads(canonical(proof))
        differences = [key for key in normalized if normalized[key] != step['replay'].get(key)]
        require(normalized == step['replay'], f'exact ordered graph and omission receipt for paid {e}: {differences}')
    return result, proof


def charges(net, frames, spans, mains):
    paid = Counter()
    for a, b in net.moves.values():
        require(spans[a] < spans[b] or spans[b] < spans[a], 'all paid charts strictly nested')
        paid[abs(len(frames[a])-len(frames[b]))] += 1
    targets = Counter()
    for i, (a,b) in enumerate(zip(net.initial, net.final, strict=True)):
        if i not in mains:
            require(spans[a] < spans[b], 'positive same-owner productive target')
            targets[len(frames[b])-len(frames[a])] += 1
    return {'paid': dict(paid), 'targets': dict(targets)}


def write_word(path, document):
    raw = canonical(document)
    path.write_bytes(gzip.compress(raw, mtime=0))


def replay(root, out):
    journal = json.loads((HERE/'BIRTHS.json').read_bytes())
    directory, count = locked_source(root, journal)
    sys.path.insert(0, str(directory))
    import supplier
    from birth_event import apply_split as birth
    initial, initial_layout, net = supplier.build()
    require(digest(initial) == journal['source']['graph_sha256']
            and digest(initial_layout) == journal['source']['layout_sha256'], 'published exact #7776 graph and layout')
    frames = initial['frames']
    spans = [subspace(tuple(f)) for f in frames]
    original, mains = endpoint_map(initial_layout, len(net.initial))
    require(len(net.initial) == initial_layout['public'], 'original public count')
    protected = {i:(net.initial[i],net.final[i]) for i in mains}
    existing_labels = initial_layout['source_labels']
    next_label = 1+max(existing_labels)
    labels = existing_labels+list(range(next_label, next_label+len(journal['steps'])))
    steps = []
    for step in journal['steps']:
        require(step['event']['role'] not in mains, 'subdivided owner is an independent helper')
        net, evidence = apply_step(net, frames, spans, labels, step, supplier, birth)
        require(all((net.initial[i],net.final[i]) == b for i,b in protected.items()), '400 protected port roles')
        steps.append(evidence)
    word = supplier.dump_graph(net, frames)
    layout = dict(initial_layout, public=len(net.initial), source_labels=labels)
    require(digest(word) == journal['result']['graph_sha256'] and digest(layout) == journal['result']['layout_sha256'],
            'final canonical word and expanded caller layout')
    expected, _ = endpoint_map(layout, len(net.initial))
    require(expected[:len(original)] == original and len(set(labels)) == len(expected),
            'every original and newborn independent owner')
    arbitrary_inputs(net, expected)
    arbitrary_inputs(net.transpose(), transpose_rows(expected))
    inventory = charges(net, frames, spans, mains)
    require(canonical(inventory) == canonical(journal['result']['native_inventory']), 'exact paid and productive ranks')
    out.mkdir(parents=True,exist_ok=True)
    write_word(out/'WORD.json.gz', word)
    write_word(out/'LAYOUT.json.gz', layout)
    receipt = dict(source=journal['source'], result=journal['result'], source_files=count,
                   checked_coefficients_per_direction=len(expected)**2, omission_checks=len(steps), steps=steps)
    (out/'BIRTH-REPLAY.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    return receipt


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', required=True, type=Path, help='root of the published #7776 source cache')
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    result = replay(args.source_root, args.out)
    print(result['result']['graph_sha256'], result['checked_coefficients_per_direction'], result['omission_checks'])
