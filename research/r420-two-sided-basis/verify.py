#!/usr/bin/env python3
"""Two-sided R420 D factorization, exact finite evidence; Apache-2.0.

Scott Woolsey Biggart, with substantial OpenAI Codex assistance.
Builds on Greer Guthrie's PR694 and the author's PR713; see README.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
CHECK = 'research/e8-bit-r420/code/xcheck.py'
EXPORT = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Reject(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise Reject(reason)


def read_sources():
    for path, pin in json.loads((HERE / 'SOURCES.json').read_text())['files'].items():
        data = (ROOT / path).read_bytes()
        if pin['representation'] == 'gzip-payload':
            data = gzip.decompress(data)
        need(sha(data) == pin['sha256'], 'source pin: ' + path)
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def original_rows(word):
    matrix = {}
    for frame, dst, sources in word['D']:
        need(frame == 0 and 120 <= dst < 240 and dst not in matrix and
             len(sources) == len(set(sources)) and all(240 <= s < 660 for s in sources), 'original D shape')
        matrix[dst] = set(sources)
    need(set(matrix) == set(range(120, 240)), 'complete original rows')
    return matrix


def helper_transform(word):
    """Recover KQ by changing rows directly, independently of PR694's columns."""
    recipe = json.loads((HERE / 'vendor/pr694-RECIPE.json').read_text())
    matrix = original_rows(word)
    used, gates, savings = set(), [], 0
    for pair in recipe['pairs']:
        a, b = pair['dst'], pair['src']
        need(240 <= a < 660 and 240 <= b < 660 and a != b and not ({a, b} & used),
             'helper pairs must be disjoint')
        before = sum(len(row) for row in matrix.values())
        for row in matrix.values():
            if a in row:
                row.symmetric_difference_update({b})
        gain = before - sum(len(row) for row in matrix.values()) - 2
        need(gain == pair['net_saved_additions'] and gain > 0, 'PR694 helper gain')
        savings += gain
        used.update((a, b))
        gates.append([0, a, [b]])
    need(len(gates) == 201 and savings == 6934, 'PR694 recipe totals')
    return matrix, gates


def nominate(word):
    matrix, _ = helper_transform(word)
    rng = random.Random(2)
    candidates = []
    for a in sorted(matrix):
        for b in sorted(matrix):
            if a != b:
                gain = len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2
                candidates.append((gain, rng.random(), a, b))
    used, pairs = set(), []
    for gain, _, a, b in sorted(candidates, reverse=True):
        if gain > 0 and not ({a, b} & used):
            pairs.append([a, b, gain])
            used.update((a, b))
    return {'assignment_seed': 2, 'fixed_helper_recipe_sha256': sha((HERE / 'vendor/pr694-RECIPE.json').read_bytes()),
            'matrix_scored': 'KQ', 'ordered_target_pairs_scored': len(candidates), 'target_pairs': pairs}


def build(word, recipe, helper_only=False):
    matrix, q_gates = helper_transform(word)
    used, p_gates = set(), []
    for a, b, gain in ([] if helper_only else recipe['target_pairs']):
        need(a in matrix and b in matrix and a != b and not ({a, b} & used), 'target matching overlap')
        need(gain == len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2 and gain > 0,
             'target gain must be priced on KQ')
        matrix[b] ^= matrix[a]
        used.update((a, b))
        p_gates.append([0, b, [a]])
    changed = copy.deepcopy(word)
    changed['D'] = q_gates + p_gates + [[0, t, sorted(row)] for t, row in sorted(matrix.items()) if row]
    changed['D'] += copy.deepcopy(list(reversed(p_gates)) + list(reversed(q_gates)))
    return changed


def prefix(word):
    values = [{r} for r in range(660)]
    for frame, dst, srcs in word['D']:
        need(frame == 0 and 120 <= dst < 660 and srcs and
             len(set(srcs + [dst])) == len(srcs) + 1 and all(120 <= s < 660 for s in srcs), 'D frame/operands')
        need(dst < 240 or all(s >= 240 for s in srcs), 'target feeds a helper')
        for src in srcs:
            values[dst].symmetric_difference_update(values[src])
    return values


def contract(word, changed):
    need({k: v for k, v in word.items() if k != 'D'} == {k: v for k, v in changed.items() if k != 'D'},
         'outside D changed')
    need(prefix(word) == prefix(changed), 'arbitrary-input D operator changed')


def controls(word, changed, recipe):
    names = []
    def reject(name, action):
        try:
            action()
        except Reject:
            names.append(name)
        else:
            raise Reject('negative control accepted: ' + name)
    for name, index in [('missing helper preparation', 0), ('missing target preparation', 201),
                        ('missing target restoration', -202), ('missing helper restoration', -1)]:
        mutant = copy.deepcopy(changed); mutant['D'].pop(index)
        reject(name, lambda: contract(word, mutant))
    mutant = copy.deepcopy(changed); mutant['D'][258][2].pop()
    reject('wrong PKQ helper coefficient', lambda: contract(word, mutant))
    mutant = copy.deepcopy(changed); mutant['D'][0][0] = 1
    reject('basis operation above frame zero', lambda: contract(word, mutant))
    mutant = copy.deepcopy(changed); mutant['C'].pop()
    reject('cleanup omitted', lambda: contract(word, mutant))
    wrong = copy.deepcopy(recipe)
    a, b, _ = wrong['target_pairs'][0]
    original = original_rows(word)
    wrong['target_pairs'][0][2] = len(original[b]) - len(original[a] ^ original[b]) - 2
    need(wrong != recipe, 'stale-price control must differ')
    reject('target price incorrectly inherited from K', lambda: build(word, wrong))
    # The middle must be PKQ, not PK. Omitting Q from its coefficients is invalid.
    q = changed['D'][:201]
    p = changed['D'][201:258]
    matrix = original_rows(word)
    for a, b, _ in recipe['target_pairs']:
        matrix[b] ^= matrix[a]
    mutant = copy.deepcopy(word)
    mutant['D'] = q + p + [[0, t, sorted(row)] for t, row in sorted(matrix.items()) if row]
    mutant['D'] += copy.deepcopy(list(reversed(p)) + list(reversed(q)))
    reject('middle PK used instead of PKQ', lambda: contract(word, mutant))
    # Combining the separate changes also requires their bilinear cross term.
    original = original_rows(word)
    target_parent = {b: a for a, b, _ in recipe['target_pairs']}
    helper_parent = {gate[2][0]: gate[1] for gate in q}
    incomplete = {}
    for t in range(120, 240):
        incomplete[t] = {s for s in range(240, 660) if
                         ((s in original[t]) ^
                          (t in target_parent and s in original[target_parent[t]]) ^
                          (s in helper_parent and helper_parent[s] in original[t]))}
    mutant['D'] = q + p + [[0, t, sorted(row)] for t, row in sorted(incomplete.items()) if row]
    mutant['D'] += copy.deepcopy(list(reversed(p)) + list(reversed(q)))
    reject('missing (P-I)K(Q-I) cross term', lambda: contract(word, mutant))
    return names


def certificate():
    word = read_sources()
    # Import pinned predecessor tools only after verifying their bytes.
    old = load_module('pr713_utilities', HERE / 'vendor/pr713-verify.py')
    geometry = load_module('r420_geometry', ROOT / CHECK)
    recipe = nominate(word)
    need(recipe == json.loads((HERE / 'RECIPE.json').read_text()), 'matching differs')
    helper = build(word, recipe, helper_only=True)
    changed = build(word, recipe)
    contract(word, helper); contract(word, changed)
    baseline = geometry.Word(word)
    labels = baseline.labels(); baseline.full()
    h, c, _ = baseline.interface()
    need(all(h.values()) and all(c.values()), 'original interface')
    for candidate in (helper, changed):
        check = geometry.Word(candidate); check.full()
        h, c, _ = check.interface()
        need([k for k, ok in h.items() if not ok] == ['H2_D_frame0_targets_from_helpers'] and
             [k for k, ok in c.items() if not ok] == ['K_equals_D'], 'only literal H2/K may fail')
    streams = [old.records(w, baseline.fdim) for w in (word, helper, changed)]
    common = [r for r in streams[0] if r[0] != 1]
    need(all([r for r in stream if r[0] != 1] == common for stream in streams), 'frame/copy paths differ')
    bills = []
    with tempfile.TemporaryDirectory(prefix='r420-two-sided-') as tmp:
        for i, (w, stream) in enumerate(zip((word, helper, changed), streams)):
            folder = Path(tmp) / str(i); folder.mkdir()
            # Same retained exporter as PR713, supplied via this checkout.
            path = folder / 'word.json'; path.write_bytes(canonical(w))
            subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORT), str(path), str(folder / 'out')],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            actual = list(struct.iter_unpack('<6i', (folder / 'out/249-records.bin').read_bytes()))
            need(actual == stream, 'official exporter stream mismatch')
            bills.append(old.bill(stream))
    predecessor = json.loads((HERE / 'vendor/pr694-CERTIFICATE.json').read_text())['after']
    for key, original_key in [('ADDs', 'binary_additions'), ('record_sha256', 'record_sha256'),
                              ('forward_prefix', 'forward_prefix'), ('reverse_prefix', 'reverse_prefix'),
                              ('payload_prefix_upper', 'payload_prefix_upper')]:
        need(bills[1][key] == predecessor[original_key], 'PR694 reconstruction: ' + key)
    need(bills[0]['histogram'] == bills[1]['histogram'] == bills[2]['histogram'] ==
         {'1': 1320, '2': 1440, '4': 60, '5': 120, '8': 9}, 'paid profile')
    extra = sum(p[2] for p in recipe['target_pairs'])
    need(bills[1]['ADDs'] - bills[2]['ADDs'] == extra == 1434, 'fully charged incremental gain')
    return {'status': 'PASS_R420_TWO_SIDED_BASIS', 'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
            'assignment_seed': 2, 'scope': 'finite two-sided D construction; no new kappa',
            'labels': labels, 'helper_pairs': 201, 'target_pairs': len(recipe['target_pairs']),
            'target_orientations_scored': recipe['ordered_target_pairs_scored'],
            'before': bills[0], 'helper_only': bills[1], 'after': bills[2],
            'D_ADDs': [sum(len(g[2]) for g in w['D']) for w in (word, helper, changed)],
            'saved_over_original': bills[0]['ADDs'] - bills[2]['ADDs'], 'saved_over_PR694': extra,
            'naive_sum_of_predecessor_savings_is_not_the_result': {'naive': 6934 + 3150, 'actual': 8368},
            'columns_in_each_direction': 660, 'changed_word_canonical_sha256': sha(canonical(changed)),
            'controls': controls(word, changed, recipe), 'literal_H2_and_K_accept': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'run without -O: inherited exporter uses assertions')
    result = certificate()
    if args.write_certificate:
        with args.write_certificate.open('x') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate differs')
    print('PASS_R420_TWO_SIDED_BASIS native_ADDs=26916->18548 saved=8368 beyond_PR694=1434 payload_bits=103 kappa=unchanged')


if __name__ == '__main__':
    try:
        main()
    except (Reject, OSError, ValueError, KeyError) as error:
        print('REJECT:', error, file=sys.stderr)
        sys.exit(1)
