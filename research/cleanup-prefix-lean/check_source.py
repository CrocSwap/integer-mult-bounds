#!/usr/bin/env python3
"""Bind a finite CK cleanup fixture to retained sources; no producer imports.

The Python/source/JSON bridge is executable evidence, not a Lean theorem.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/complex-k492-owner-repair/'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def integer(x, label):
    require(type(x) is int, 'integer required: ' + label)
    return x


def normalize(event, n):
    require(type(event) is list and len(event) > 0, 'gate shape')
    kind = event[0]
    require(kind in ('add', 'scale'), 'unknown gate')
    require(len(event) == (6 if kind == 'add' else 5), 'gate arity')
    target = integer(event[1], 'target')
    require(0 <= target < n, 'target range')
    j = 3 if kind == 'add' else 2
    num, den = integer(event[j], 'numerator'), integer(event[j+1], 'denominator')
    require(den != 0, 'zero denominator')
    require(kind != 'scale' or num != 0, 'zero scale')
    q = Fraction(num, den)
    out = dict(kind=kind, target=target, num=q.numerator, den=q.denominator)
    if kind == 'add':
        source = integer(event[2], 'source')
        require(0 <= source < n, 'source range')
        out['source'] = source  # self-adds are valid scalar operations
    require(type(event[-1]) is list and all(type(x) is int and 0 <= x < 512 for x in event[-1]), 'frame encoding')
    return out


def touched(g):
    return {g['target']} | ({g['source']} if g['kind'] == 'add' else set())


def syntactic_commute(a, b):
    """Independent transcription of the claimed rule, not the semantic oracle."""
    if a['target'] == b['target']:
        return a['kind'] == b['kind'] == 'add' and a['source'] != a['target'] and b['source'] != b['target']
    return a['target'] not in touched(b) and b['target'] not in touched(a)


def execute(gates, state):
    out = dict(state)
    for g in gates:
        q = Fraction(g['num'], g['den'])
        t = g['target']
        old = out.get(t, Fraction(0))
        out[t] = old + q * out.get(g['source'], Fraction(0)) if g['kind'] == 'add' else q * old
    return out


def counterexample(a, b):
    """Exact matrix-column oracle, on at most four touched coordinates."""
    support = sorted(touched(a) | touched(b))
    for column in support:
        left, right = execute([a, b], {column: Fraction(1)}), execute([b, a], {column: Fraction(1)})
        for row in support:
            x, y = left.get(row, 0), right.get(row, 0)
            if x != y:
                return dict(input_column=column, output_row=row, original=str(x), reversed=str(y))
    return None


def audit(cleanup, indices, helpers=None):
    require(all(type(i) is int and 0 <= i < len(cleanup) for i in indices), 'selected index range')
    require(len(set(indices)) == len(indices), 'duplicate selected index')
    occupied, pairs, overlap = set(), 0, []
    for k, i in enumerate(indices):
        g = cleanup[i]
        require(not occupied & touched(g), 'selected registers overlap')
        occupied |= touched(g)
        if helpers is not None:
            h = helpers[k]
            require(g['target'] == h and g['kind'] == 'add', 'helper target')
            occurrences = sum((x['target'] == h) + (x['kind'] == 'add' and x['source'] == h) for x in cleanup)
            require(occurrences == 1, 'helper not single-touch')
        # Every ORIGINAL prefix position, including all earlier selected gates.
        # No producer on-register index, prefix sampling, or sorted recipe order.
        for j in range(i):
            a = cleanup[j]
            require(syntactic_commute(a, g), f'prefix syntactic conflict {j},{i}')
            require(counterexample(a, g) is None, f'prefix semantic conflict {j},{i}')
            pairs += 1
            if touched(a) & touched(g):
                overlap.append([j, i])
    return dict(cleanup_gates=len(cleanup), selected_gates=len(indices), full_prefix_pairs=pairs,
                shared_register_pairs=overlap, selected_registers=len(occupied),
                selected_indices=indices, recipe_order_is_sorted=indices == sorted(indices))


def controls(cleanup, indices):
    def add(t, s, q=1):
        return dict(kind='add', target=t, source=s, num=q, den=1)
    def scale(t, q=2):
        return dict(kind='scale', target=t, num=q, den=1)
    positives = [('same_target_additions', add(0, 1, 2), add(0, 2, -3)),
                 ('shared_read', add(0, 2), add(1, 2)),
                 ('disjoint_self_add', add(0, 0), scale(1)),
                 ('disjoint_scale_add', scale(0), add(1, 2))]
    for name, a, b in positives:
        require(syntactic_commute(a, b) and counterexample(a, b) is None, 'positive: '+name)
    negatives = [('write_source', add(1, 2), add(0, 1)),
                 ('scale_source', scale(1), add(0, 1)),
                 ('scale_target', scale(0), add(0, 1)),
                 ('self_add_dependency', add(0, 0), add(1, 0))]
    evidence = {}
    for name, a, b in negatives:
        witness = counterexample(a, b)
        require(not syntactic_commute(a, b) and witness is not None, 'negative: '+name)
        evidence[name] = dict(first=a, second=b, witness=witness)
    # An actual selected gate gets a source-writing predecessor: this tests the
    # whole-prefix traversal, not merely a hand-picked pair function.
    damaged = copy.deepcopy(cleanup)
    g = cleanup[indices[0]]
    damaged[0] = scale(g['source'])
    bad_cases = [('actual_prefix_source_scale', damaged, indices),
                 ('duplicate_selection', cleanup, indices + indices[:1]),
                 ('out_of_range', cleanup, indices + [len(cleanup)]),
                 ('boolean_index', cleanup, [True] + indices)]
    for name, word, selected in bad_cases:
        try:
            audit(word, selected)
        except ValueError as e:
            evidence[name] = str(e)
        else:
            raise ValueError('negative accepted: '+name)
    shape_cases = [('unknown_kind', ['copy', 0, 1, 1, 1, []]),
                   ('zero_denominator', ['add', 0, 1, 1, 0, []]),
                   ('boolean_coefficient', ['add', 0, 1, True, 1, []]),
                   ('zero_scale', ['scale', 0, 0, 1, []]),
                   ('negative_register', ['add', -1, 1, 1, 1, []])]
    for name, event in shape_cases:
        try:
            normalize(event, 716)
        except ValueError as e:
            evidence[name] = str(e)
        else:
            raise ValueError('malformed gate accepted: '+name)
    # Opposite recipe order also works; never silently canonicalize the real one.
    audit(cleanup, list(reversed(indices)))
    return dict(positive_names=[x[0] for x in positives] + ['reversed_recipe_order'], rejected=evidence)


def load_fixture():
    """Recompute and return fixture only after checking every immutable binding."""
    pins = json.loads((HERE / 'SOURCES.json').read_bytes())
    for path, expected in pins['files_sha256'].items():
        require(digest((ROOT/path).read_bytes()) == expected, 'source hash: '+path)
    # Selection metadata floats on main. Audit the selection at our research
    # base, whose exact original certificate bytes are retained and hash-pinned.
    selected = json.loads((HERE/'BASE-SELECTED-RESULT.json').read_bytes())
    require(selected['audited_source_head'] == pins['selected_source_head'], 'selected head')
    inventory = json.loads((ROOT/selected['source_manifest']).read_bytes())['files']
    for relative in ['code/build_hpe.py', 'data/SPEC.json', 'data/recipes/k492-ck-hyperplane_end.json']:
        path = PACKAGE+relative
        require(inventory[path] == pins['files_sha256'][path], 'selected inventory: '+path)
    spec = json.loads((ROOT/(PACKAGE+'data/SPEC.json')).read_bytes())
    chain = spec['build']['providers']['ck']
    previous = chain['base']['content_sha256']
    hpe = None
    for step in chain['steps']:
        require(step['input_content_sha256'] == previous, 'broken construction chain')
        previous = step['output_content_sha256']
        if step['type'] == 'hyperplane_end':
            require(hpe is None, 'multiple HPE steps')
            hpe = step
    require(previous == chain['word_content_sha256'] and hpe is not None, 'chain endpoint')
    payload = gzip.decompress((HERE/'CK-PRE-HPE.json.gz').read_bytes())
    require(digest(payload) == hpe['input_content_sha256'] == pins['pre_hpe_payload_sha256'], 'pre-HPE payload hash')
    word = json.loads(payload)
    recipe_path = ROOT/(PACKAGE+hpe['recipe'].removeprefix('pkg:'))
    raw_recipe = recipe_path.read_bytes()
    require(digest(raw_recipe) == hpe['recipe_sha256'], 'recipe chain hash')
    recipe = json.loads(raw_recipe)
    require(recipe['output_content_sha256'] == hpe['output_content_sha256'], 'HPE output pin')
    require('early_cleanup' not in word and 'helper_final' not in word, 'not pre-HPE')
    n = 2*word['report']['v'] + word['report']['R']
    require(n == 716, 'CK register count')
    gates = [normalize(g, n) for g in word['cleanup']]
    indices = [integer(x['cleanup_index'], 'recipe index') for x in recipe['changes']]
    helpers = [integer(x['helper'], 'helper') for x in recipe['changes']]
    require(all(224 <= h < n and str(h) in word['start_extra'] for h in helpers), 'entering helper')
    counts = audit(gates, indices, helpers)
    fixture = dict(schema='cleanup-prefix-ck-v1', register_count=n, cleanup=gates,
                   selected_indices=indices, helpers=helpers,
                   pre_hpe_payload_sha256=digest(payload), counts=counts)
    require(canonical(fixture) == canonical(json.loads((HERE/'CK-FIXTURE.json').read_bytes())), 'fixture mismatch')
    return fixture


def portability_controls():
    """Exercise independence from live selection and rejection of snapshot drift.

    Reads are intercepted in memory; no repository input is changed.
    """
    from unittest.mock import patch
    read_bytes = Path.read_bytes
    floating = ROOT/'certificates/selected-result.json'
    snapshot = HERE/'BASE-SELECTED-RESULT.json'
    expected = canonical(load_fixture())
    for mode in ('later_selection', 'absent_selection', 'corrupt_snapshot'):
        def intercepted(path):
            if path == floating:
                if mode == 'absent_selection':
                    raise FileNotFoundError('portability control: live selection absent')
                return b'{"source_prs":[942],"status":"later unrelated selection"}'
            data = read_bytes(path)
            return data+b' ' if mode == 'corrupt_snapshot' and path == snapshot else data
        with patch.object(Path, 'read_bytes', intercepted):
            if mode == 'corrupt_snapshot':
                try:
                    load_fixture()
                except ValueError as e:
                    require(str(e) == 'source hash: research/cleanup-prefix-lean/BASE-SELECTED-RESULT.json',
                            'wrong snapshot corruption rejection')
                else:
                    raise ValueError('corrupt baseline snapshot accepted')
            else:
                require(canonical(load_fixture()) == expected, 'live selection affected baseline fixture')
    print('PASS_BASELINE_SELECTION_PORTABILITY later=unchanged absent=unchanged corrupt_snapshot=rejected')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-fixture', type=Path, help='write validated fixture to a new path')
    parser.add_argument('--portability-controls', action='store_true',
                        help='test live-selection independence and snapshot corruption in memory')
    args = parser.parse_args()
    fixture = load_fixture()
    report = dict(counts=fixture['counts'], controls=controls(fixture['cleanup'], fixture['selected_indices']))
    expected = json.loads((HERE/'SOURCE-RESULT.json').read_bytes())
    require(canonical(report) == canonical(expected), 'result receipt mismatch')
    if args.portability_controls:
        portability_controls()
    if args.emit_fixture:
        with args.emit_fixture.open('x', encoding='utf-8') as f:
            f.write(json.dumps(fixture, indent=2)+'\n')
    c = fixture['counts']
    print(f"PASS_CK_CLEANUP_SOURCE gates={c['cleanup_gates']} selected={c['selected_gates']} full_prefix_pairs={c['full_prefix_pairs']}")


if __name__ == '__main__':
    main()
