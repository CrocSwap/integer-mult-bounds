"""Standalone exact replay of weighted-path obstructions; standard library only."""
if not __debug__:
    raise SystemExit('Run without -O: inherited Clifford checks require assertions.')

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import model
import screen
from valuation import (require, direct_records, symbolic_records, canonical,
                       targets, check, structural_obstruction)


def add(a, b):
    out = dict(a)
    for e, c in b.items():
        out[e] = out.get(e, 0)+c
    return {e: c for e, c in out.items() if c}


def mul(a, b):
    out = {}
    for e, c in a.items():
        for f, d in b.items():
            out[e+f] = out.get(e+f, 0)+c*d
    return {e: c for e, c in out.items() if c}


def determinant(matrix):
    out = {}
    for p in permutations(range(3)):
        sign = (-1)**sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3))
        term = {0: sign}
        for r, c in enumerate(p):
            term = mul(term, matrix[r][c])
        out = add(out, term)
    return out


def determinant_control(vector):
    """Test the Laurent determinant identity with nontrivial invertible B's."""
    weights = vector[:-6]
    require(len(weights) % 3 == 0, 'Bad weight dimension')
    blocks = len(weights)//3+1
    current = [[{0: int(r == c)} if r == c else {} for c in range(3)] for r in range(3)]
    coefficient = 1
    for k in range(blocks):
        if k:
            current = [[{e+weights[3*(k-1)+r]: c for e, c in p.items()} for p in row]
                       for r, row in enumerate(current)]
        b = [[1, k+1, 0], [0, 1, 1], [1, 0, 1]]
        require(determinant([[{0: c} if c else {} for c in row] for row in b]) == {0: k+2},
                'Bad determinant control matrix')
        coefficient *= k+2
        out = [[{} for _ in range(3)] for _ in range(3)]
        for r, c, j in product(range(3), repeat=3):
            out[r][c] = add(out[r][c], mul({0: b[r][j]}, current[j][c]))
        current = out
    require(determinant(current) == {sum(weights): coefficient},
            'Laurent determinant identity failed')


def rejection(action, contains=None):
    try:
        action()
    except ValueError as exc:
        require(contains is None or contains in str(exc), 'Unexpected rejection: '+str(exc))
    else:
        raise ValueError('Invalid certificate was accepted')


def coverage(case, records, blocks, vectors):
    ts = targets(records)
    require(case['targets'] == ts, 'Target frame inventory mismatch')
    choices = list(product(*ts))
    global_id = case['global_certificate']
    frame_ids = case['frame_certificates']
    def get(index):
        require(type(index) is int and 0 <= index < len(vectors), 'Invalid vector index')
        return vectors[index]
    structural = sum(structural_obstruction(records, f) for f in choices)
    if global_id is not None:
        require(frame_ids == [], 'Global certificate must stand alone')
        check(records, blocks, get(global_id))
        return {'choices': len(choices), 'excluded': len(choices), 'unclassified': 0,
                'certificates': 1, 'structural': structural, 'whole_word_excluded': True}
    require(len(frame_ids) == len(choices), 'Incomplete frame coverage')
    excluded = 0
    for frames, index in zip(choices, frame_ids):
        if index is not None:
            check(records, blocks, get(index), frames)
            excluded += 1
        else:
            require(not structural_obstruction(records, frames),
                    'Unclassified entry has a trivial structural obstruction')
    return {'choices': len(choices), 'excluded': excluded,
            'unclassified': len(choices)-excluded, 'certificates': excluded,
            'structural': structural, 'whole_word_excluded': excluded == len(choices)}


def controls(data, cache):
    counts = Counter()
    identity = ('mix3', 1, 0, 0, 0, 1, 0, 0, 0, 1)
    words = [tuple(('paid', r, a) for r in range(3) for a in (1, 2, 4))+(identity,)]
    for extra in (0, 2):
        word = [identity]
        for axis in (1, 2, 4):
            word.extend(('paid', r, axis) for r in range(3))
            word.append(identity)
        words.append(tuple(word+[identity]*extra))
    for word in words:
        a, blocks = symbolic_records(word)
        b, n = direct_records(word)
        require(blocks == n and canonical(a) == canonical(b), 'Positive-control engine mismatch')
        ring = model.Engine()
        frames = model.endpoint_frames(ring, model.execute(ring, word))
        require(frames is not None, 'Known nine-call construction failed')
        forged = [0]*(3*(blocks-1))+[1, 1, 1, 0, 0, 0]
        rejection(lambda: check(b, blocks, forged, frames), 'Allowed path')
        determinant_control(forged)
        counts['positive_nine_call_controls'] += 1
    global_case = next(c for c in data['cases'] if c['global_certificate'] is not None)
    records, blocks = cache[global_case['id']]
    vector = data['vectors'][global_case['global_certificate']]
    rejection(lambda: check(records, blocks, [0]*len(vector)), 'Nonpositive')
    counts['nonpositive_gap_rejected'] += 1
    rejection(lambda: check(records, blocks, vector[:-1]), 'dimension')
    counts['wrong_dimension_rejected'] += 1
    rejection(lambda: check(records, blocks, list(map(float, vector))), 'exact integers')
    counts['floating_certificate_rejected'] += 1
    found = set()
    for i, delta in product(range(len(vector)), (-2, -1, 1, 2)):
        changed = vector[:]
        changed[i] += delta
        try:
            check(records, blocks, changed)
        except ValueError as exc:
            if 'heterogeneous' in str(exc):
                found.add('forbidden_homogeneity_mutation_rejected')
            if 'Allowed path' in str(exc):
                found.add('allowed_valuation_mutation_rejected')
    require(len(found) == 2, 'Missing theorem-hypothesis mutation control')
    counts.update(found)
    case = next(c for c in data['cases'] if c['global_certificate'] is None)
    recs, n = cache[case['id']]
    forged = deepcopy(case)
    forged['frame_certificates'].pop()
    rejection(lambda: coverage(forged, recs, n, data['vectors']), 'Incomplete frame')
    counts['missing_frame_choice_rejected'] += 1
    forged = deepcopy(case)
    forged['targets'][0][0] ^= 1
    rejection(lambda: coverage(forged, recs, n, data['vectors']), 'inventory')
    counts['wrong_frame_inventory_rejected'] += 1
    for v in data['vectors']:
        determinant_control(v)
        counts['laurent_determinant_controls'] += 1
    return dict(counts)


def replay():
    payload = gzip.decompress((ROOT/'words.json.gz').read_bytes())
    source = json.loads(payload)
    data = json.loads((ROOT/'CERTIFICATES.json').read_text())
    require(data['schema'] == 1, 'Unknown certificate schema')
    old_unknown = {}
    old_excluded = 0
    require(len({c['id'] for c in source['cases']}) == len(source['cases']), 'Duplicate source case')
    for case in source['cases']:
        word = model.decode(case['program'])
        prior = screen.certificate(word)
        require(prior['paid_calls'] == 8, 'Wrong paid-call count')
        if prior['status'] == 'excluded':
            old_excluded += 1
        else:
            old_unknown[case['id']] = word
    require(len({c['id'] for c in data['cases']}) == len(data['cases']), 'Duplicate submitted case')
    require({c['id'] for c in data['cases']} == set(old_unknown), 'Unresolved source corpus mismatch')
    require(len({tuple(v) for v in data['vectors']}) == len(data['vectors']), 'Duplicate vector')
    cache, result, totals = {}, {}, Counter()
    for case in data['cases']:
        word = old_unknown[case['id']]
        symbolic, blocks = symbolic_records(word)
        independent, n = direct_records(word)
        require(n == blocks and canonical(symbolic) == canonical(independent),
                'Independent dense/symbolic path disagreement: '+case['id'])
        cache[case['id']] = independent, blocks
        report = coverage(case, independent, blocks, data['vectors'])
        result[case['id']] = report
        totals.update({k: int(v) for k, v in report.items()})
        totals['dense_full_paths'] += sum(len(r['paths']) for r in independent)
    return {'status': 'PASS_WEIGHTED_PATH_VALUATIONS',
            'source_cases': len(source['cases']), 'source_rank_homogeneous_excluded': old_excluded,
            'source_unclassified': len(old_unknown), 'unique_vectors': len(data['vectors']),
            'totals': dict(totals), 'cases': result, 'controls': controls(data, cache),
            'words_payload_sha256': sha256(payload).hexdigest(),
            'certificate_canonical_sha256': sha256(json.dumps(data, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest()}


def check_manifest():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    actual = {p.name for p in ROOT.iterdir() if p.is_file() and p.name != 'MANIFEST.json'}
    require(actual == set(manifest['files']) | {'words.json.gz'}, 'Source inventory mismatch')
    for name, expected in manifest['files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == expected,
                'Source integrity mismatch: '+name)
    payload = gzip.decompress((ROOT/'words.json.gz').read_bytes())
    require(sha256(payload).hexdigest() == manifest['words_payload_sha256'], 'Word payload mismatch')
    origins = json.loads((ROOT/'ORIGINS.json').read_text())
    require(origins['words_payload_sha256'] == manifest['words_payload_sha256'], 'Word source pin mismatch')
    for name, expected in origins['vendored_files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'Vendored source mismatch: '+name)


if __name__ == '__main__':
    check_manifest()
    report = replay()
    require(report == json.loads((ROOT/'EXPECTED.json').read_text()), 'Expected result mismatch')
    print(json.dumps(report, sort_keys=True))
