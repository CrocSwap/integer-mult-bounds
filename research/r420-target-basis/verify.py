#!/usr/bin/env python3
"""Exact finite target-row conjugation of PR543's D prefix; Apache-2.0.

Scott Woolsey Biggart, with substantial OpenAI Codex assistance.
Uses eumemic's pinned xcheck for E8 geometry and original interface checks.
The target matching, synthesis and record/set interpreters below are new.
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
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
CHECK = 'research/e8-bit-r420/code/xcheck.py'
EXPORT = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


class Reject(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, pin in pins['files'].items():
        data = (ROOT / path).read_bytes()
        if pin['representation'] == 'gzip-payload':
            data = gzip.decompress(data)
        need(sha(data) == pin['sha256'], 'source pin: ' + path)
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def rows(word):
    result = {}
    for frame, target, sources in word['D']:
        need(frame == 0 and 120 <= target < 240 and target not in result,
             'original D must have one zero-frame row per target')
        need(len(set(sources)) == len(sources) and all(240 <= s < 660 for s in sources),
             'original D helper operands')
        result[target] = set(sources)
    need(set(result) == set(range(120, 240)), 'complete original D rows')
    return result


def nominate(word):
    """Exactly 14,280 directed pairs, one seeded greedy matching, then stop."""
    matrix = rows(word)
    rng = random.Random(5)
    candidates = []
    for a in sorted(matrix):
        for b in sorted(matrix):
            if a != b:
                gain = len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2
                candidates.append((gain, rng.random(), a, b))
    used, selected = set(), []
    for gain, _, a, b in sorted(candidates, reverse=True):
        if gain > 0 and a not in used and b not in used:
            selected.append([a, b, gain])
            used.update((a, b))
    return {'seed': 5, 'oriented_pairs_scored': len(candidates), 'pairs': selected}


def build(word, recipe):
    matrix = rows(word)
    used, shears = set(), []
    for a, b, gain in recipe['pairs']:
        need(a in matrix and b in matrix and a != b and not ({a, b} & used),
             'target matching must be disjoint')
        need(gain == len(matrix[b]) - len(matrix[a] ^ matrix[b]) - 2 and gain > 0,
             'incorrect fully charged gain')
        matrix[b] ^= matrix[a]
        used.update((a, b))
        shears.append([0, b, [a]])
    changed = copy.deepcopy(word)
    changed['D'] = shears + [[0, t, sorted(matrix[t])] for t in sorted(matrix) if matrix[t]]
    changed['D'] += copy.deepcopy(list(reversed(shears)))
    return changed


def set_prefix(word):
    """Set-valued symbolic interpreter, independent of bit-packed xcheck."""
    values = [{r} for r in range(660)]
    for frame, target, sources in word['D']:
        need(frame == 0 and 120 <= target < 240 and sources and
             len(set(sources + [target])) == len(sources) + 1 and
             all(120 <= s < 660 for s in sources), 'illegal D gate')
        for source in sources:
            values[target].symmetric_difference_update(values[source])
    return values


def prefix_contract(original, changed):
    need({k: v for k, v in original.items() if k != 'D'} ==
         {k: v for k, v in changed.items() if k != 'D'}, 'field outside D changed')
    need(set_prefix(original) == set_prefix(changed), 'D operator changed on arbitrary inputs')


def records(word, dimensions):
    """Compile literal records separately from the retained official exporter."""
    state = list(word['start'])
    out = []
    def move(reg, frame):
        if state[reg] != frame:
            out.append((0, reg, state[reg], frame, dimensions[frame] - dimensions[state[reg]], 0))
            state[reg] = frame
    def gates(section, phase):
        for frame, dst, srcs in word[section]:
            for reg in [dst] + srcs:
                move(reg, frame)
            out.extend((1, dst, src, 1, frame, phase) for src in srcs)
    gates('D', 1)
    gates('A', 2)
    for k, center in enumerate(word['ret']):
        frame = state[center]
        out.append((2, center, 660, frame, 0, dimensions[frame]))
        out.extend((1, 120 + t, 660, 1, 0, 3) for t, row in enumerate(word['scatter']) if k in row)
        out.append((3, center, 660, frame, 0, 0))
    gates('B', 4)
    gates('C', 5)
    for reg, frame in enumerate(word['final']):
        move(reg, frame)
    return out


def replay(stream, reverse=False):
    """All 660 dirty-input columns using sets; integer positive prefix in parallel."""
    values = [{r} for r in range(660)] + [set()]
    norms = [1] * 660 + [0]
    largest = 1
    center = None
    copies = 0
    for op, a, b, c, f, z in (reversed(stream) if reverse else stream):
        if op == 0:
            continue
        if reverse and op in (2, 3):
            op = 5 - op
        if op == 1:
            need(c == 1 and 0 <= a < 660 and 0 <= b <= 660 and a != b and
                 a != center and (b != 660 or center is not None), 'invalid ADD/copy lifetime')
            values[a].symmetric_difference_update(values[b])
            norms[a] += norms[b]
            largest = max(largest, norms[a])
        elif op == 2:
            need(center is None and b == 660 and 0 <= a < 660, 'COPY lifetime')
            center = a
            copies += 1
            values[660] = values[a].copy()
            norms[660] = norms[a]
        elif op == 3:
            need(center == a and b == 660, 'ERASE lifetime')
            center = None
            values[660] = set()
            norms[660] = 0
        else:
            raise Reject('unknown record opcode')
    need(center is None and copies == 9 and not values[660], 'copy closure')
    expected = [{r, r - 120} if 120 <= r < 240 else {r} for r in range(660)]
    need(values[:660] == expected, 'full dirty-input endpoint')
    return largest


def bill(stream):
    forward, backward = replay(stream), replay(stream, True)
    payload = 64 * forward ** 3 * backward ** 2
    need(payload < 2 ** 104, '104-bit local prefix cap')
    paid = Counter()
    for op, a, b, c, f, z in stream:
        if op == 0:
            need(f > 0, 'nonpositive frame move')
            paid[f] += 1
        elif op == 2:
            paid[z] += 1
    return {'ADDs': sum(r[0] == 1 for r in stream), 'records': len(stream),
            'forward_prefix': forward, 'reverse_prefix': backward,
            'payload_prefix_upper': str(payload), 'payload_bits': payload.bit_length(),
            'histogram': {str(k): v for k, v in sorted(paid.items())},
            'rank_mass': sum(k * v for k, v in paid.items()),
            'record_sha256': sha(b''.join(struct.pack('<6i', *r) for r in stream))}


def export_compare(word, expected, directory):
    path = directory / 'word.json'
    path.write_bytes(canonical(word))
    subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORT), str(path), str(directory / 'export')],
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    got = list(struct.iter_unpack('<6i', (directory / 'export/249-records.bin').read_bytes()))
    need(got == expected, 'official exported records differ')


def controls(original, changed, stream):
    names = []
    def rejects(name, action):
        try:
            action()
        except Reject:
            names.append(name)
        else:
            raise Reject('negative control accepted: ' + name)
    x = copy.deepcopy(changed); x['D'].pop()
    rejects('missing final target restoration', lambda: prefix_contract(original, x))
    x = copy.deepcopy(changed); x['D'].pop(0)
    # This bug is invisible if tests initialize every target to zero.
    projected = lambda w: [s - set(range(120, 240)) for s in set_prefix(w)]
    need(projected(original) == projected(x), 'missing initial shear should evade zero-target tests')
    rejects('missing initial target shear', lambda: prefix_contract(original, x))
    x = copy.deepcopy(changed); x['D'][57][2].pop()
    rejects('wrong transformed helper row', lambda: prefix_contract(original, x))
    x = copy.deepcopy(changed); x['D'][0][0] = 1
    rejects('nonzero D frame', lambda: prefix_contract(original, x))
    x = copy.deepcopy(changed); x['D'][0][2] = [0]
    rejects('source accessed at frame zero', lambda: prefix_contract(original, x))
    x = copy.deepcopy(changed); x['C'].pop()
    rejects('unrelated cleanup modification', lambda: prefix_contract(original, x))
    damaged = list(stream); damaged.pop(next(i for i, r in enumerate(damaged) if r[0] == 3))
    rejects('omitted exported ERASE', lambda: replay(damaged))
    damaged = list(stream); damaged.pop(next(i for i, r in enumerate(damaged) if r[0] == 1))
    rejects('omitted exported target shear', lambda: replay(damaged))
    # F2-neutral overhead is accepted semantically and still pays two ADDs.
    neutral = copy.deepcopy(changed)
    neutral['D'] = [[0, 120, [121]], [0, 120, [121]]] + neutral['D']
    prefix_contract(original, neutral)
    need(sum(len(g[2]) for g in neutral['D']) == sum(len(g[2]) for g in changed['D']) + 2,
         'neutral pair must pay both gates')
    return names


def certificate():
    word = read_sources()
    recipe = nominate(word)
    need(recipe == json.loads((HERE / 'RECIPE.json').read_text()), 'frozen matching mismatch')
    changed = build(word, recipe)
    prefix_contract(word, changed)
    spec = importlib.util.spec_from_file_location('r420_pinned_xcheck', ROOT / CHECK)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    original = module.Word(word)
    labels = original.labels()
    original.full()
    hypotheses, conclusions, _ = original.interface()
    need(all(hypotheses.values()) and all(conclusions.values()), 'original interface')
    candidate = module.Word(changed)
    candidate.full()
    h, c, _ = candidate.interface()
    need([k for k, v in h.items() if not v] == ['H2_D_frame0_targets_from_helpers'],
         'only literal H2 should fail')
    need([k for k, v in c.items() if not v] == ['K_equals_D'], 'literal K extractor should fail')
    before, after = records(word, original.fdim), records(changed, original.fdim)
    need([r for r in before if r[0] != 1] == [r for r in after if r[0] != 1],
         'MOVE/COPY/ERASE subsequence changed')
    receipts = []
    with tempfile.TemporaryDirectory(prefix='r420-target-') as tmp:
        for i, (w, stream) in enumerate(((word, before), (changed, after))):
            directory = Path(tmp) / str(i); directory.mkdir()
            export_compare(w, stream, directory)
            receipts.append(bill(stream))
    need(receipts[0]['histogram'] == receipts[1]['histogram'] ==
         {'1': 1320, '2': 1440, '4': 60, '5': 120, '8': 9}, 'paid profile changed')
    saved = sum(p[2] for p in recipe['pairs'])
    need(receipts[0]['ADDs'] - receipts[1]['ADDs'] == saved, 'full charged saving')
    d_counts = [sum(len(g[2]) for g in w['D']) for w in (word, changed)]
    return {'status': 'PASS_R420_TARGET_BASIS', 'scope': 'finite native bit circuit; no new kappa',
            'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
            'source_pr543': '2065fe4f72a914d907f1046603f5a36f17018535',
            'assignment_seed': 5, 'pair_count': len(recipe['pairs']),
            'oriented_pairs_scored': recipe['oriented_pairs_scored'],
            'D_ADDs': d_counts, 'saved_ADDs': saved, 'columns_in_each_direction': 660,
            'labels': labels, 'before': receipts[0], 'after': receipts[1],
            'candidate_word_canonical_sha256': sha(canonical(changed)),
            'rejection_controls': controls(word, changed, after),
            'positive_control': 'F2-neutral target pair preserves operator and costs two ADDs',
            'legacy_H2_and_literal_K_accept': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    need(sys.flags.optimize == 0, 'run without -O: inherited exporter has assertions')
    result = certificate()
    if args.write_certificate:
        with args.write_certificate.open('x') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate differs')
    print('PASS_R420_TARGET_BASIS D=19922->16772 native_ADDs=26916->23766 saved=3150 columns=660 rank_mass=5112 kappa=unchanged')


if __name__ == '__main__':
    try:
        main()
    except (Reject, ValueError, KeyError, OSError) as error:
        print('REJECT:', error, file=sys.stderr)
        sys.exit(1)
