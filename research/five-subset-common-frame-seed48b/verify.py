#!/usr/bin/env python3
"""Exact common-frame witness and dirty scalar macro. Apache-2.0.

Prepared for ToikY with substantial OpenAI Codex assistance. This checker
imports neither census implementation nor predecessor executable code.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return bin(a & b).count('1') % 2


def closure(rows):
    out = {0}
    for row in rows:
        out = out | {x ^ row for x in out}
    return out


def orthonormal(rows, ambient):
    need(len(rows) == (len(ambient).bit_length() - 1), 'basis cardinality')
    need(all(type(x) is int and 0 < x < 512 for x in rows), 'basis vector type/range')
    need(closure(rows) == ambient, 'basis span')
    need(all(dot(x, y) == (i == j) for i, x in enumerate(rows)
             for j, y in enumerate(rows)), 'identity Gram')


def find_basis(space):
    if space == {0}:
        return []
    for x in sorted(space):
        if dot(x, x):
            tail = find_basis({y for y in space if not dot(x, y)})
            if tail is not None:
                answer = [x] + tail
                orthonormal(answer, space)
                return answer
    return None


def K(s, t):
    return (1, 0, -1, 0)[bin(s & t).count('1') % 4]


def fixture():
    sources = [31, 55, 457, 458, 481, 482]
    targets = [47, 59, 87, 151, 279, 451]
    U = closure([31, 481, 3, 40])
    W = {x for x in range(512) if all(not dot(x, u) for u in U)}
    incoming = [find_basis({u for u in U if not dot(u, s)}) for s in sources]
    outgoing = [find_basis({w for w in W if not dot(w, t)}) for t in targets]
    alpha = [1, 1, -1, -1, -1, -1]
    beta = [1, 1, 1, 1, 1, -1]
    # Registers: six immutable inputs, six dirty accumulating outputs, one
    # dirty helper. Its old contribution is removed after literal ungather.
    word = ([[12, i, c] for i, c in enumerate(alpha)]
            + [[6 + j, 12, c] for j, c in enumerate(beta)]
            + [[12, i, -c] for i, c in reversed(list(enumerate(alpha)))]
            + [[6 + j, 12, -c] for j, c in enumerate(beta)])
    return {'h': 9, 'source_labels': sources, 'target_labels': targets,
            'U_basis': [31, 481, 3, 40], 'U_characteristic': 40,
            'W_characteristic': 471, 'incoming_residual_bases': incoming,
            'outgoing_residual_bases': outgoing, 'source_signs': alpha,
            'target_signs': beta, 'word': word}


def endpoint(word):
    matrix = [[int(i == j) for j in range(13)] for i in range(13)]
    for record in word:
        need(len(record) == 3 and all(type(v) is int for v in record), 'gate encoding')
        dst, src, coefficient = record
        need(0 <= dst < 13 and 0 <= src < 13 and dst != src and abs(coefficient) == 1,
             'signed ADD operands')
        matrix[dst] = [x + coefficient * y for x, y in zip(matrix[dst], matrix[src])]
    return matrix


def check(f):
    need(f['h'] == 9 and type(f['h']) is int, 'ambient dimension')
    S, T = f['source_labels'], f['target_labels']
    need(len(S) == len(T) == 6 and len(set(S)) == len(set(T)) == 6, 'endpoint coverage')
    need(all(type(x) is int and 0 < x < 512 and bin(x).count('1') == 5 for x in S + T),
         'constant weight-five labels')
    U = closure(f['U_basis'])
    W = {v for v in range(512) if all(not dot(v, u) for u in U)}
    need(len(U) == 16 and len(W) == 32 and U & W == {0}, 'common nondegenerate separator')
    need(set(S) <= U and set(T) <= W, 'common-frame containment')
    need(any(dot(x, y) for i, x in enumerate(S) for y in S[i + 1:])
         and any(dot(x, y) for i, x in enumerate(T) for y in T[i + 1:]),
         'degenerate pair on both sides')
    for name, space, labels in [('U_characteristic', U, S), ('W_characteristic', W, T)]:
        w = f[name]
        need(w in space and all(dot(w, x) == dot(x, x) for x in space), 'characteristic')
        need(w not in labels, 'nonalternating incident residuals')
    need(f['U_characteristic'] ^ f['W_characteristic'] == 511, 'characteristic splitting')
    for labels, space, key in [(S, U, 'incoming_residual_bases'), (T, W, 'outgoing_residual_bases')]:
        need(len(f[key]) == len(labels), 'all incident residuals covered')
        for label, rows in zip(labels, f[key]):
            orthonormal(rows, {x for x in space if not dot(x, label)})
    alpha, beta = f['source_signs'], f['target_signs']
    need(len(alpha) == len(S) and len(beta) == len(T) and all(type(v) is int and abs(v) == 1
                                                          for v in alpha + beta), 'sign coverage')
    kernel = [[K(s, t) for s in S] for t in T]
    need(all(kernel[j][i] == alpha[i] * beta[j] for j in range(6) for i in range(6)),
         'all 36 signed kernel entries')
    expected = [[int(i == j) for j in range(13)] for i in range(13)]
    for j in range(6):
        expected[6 + j][:6] = kernel[j]
    need(len(f['word']) == 24 and endpoint(f['word']) == expected, 'full dirty endpoint')
    inverse = [[d, s, -c] for d, s, c in reversed(f['word'])]
    identity = [[int(i == j) for j in range(13)] for i in range(13)]
    need(endpoint(f['word'] + inverse) == identity, 'literal inverse restores all columns')
    # These are conditional *incident* nested-edge ranks, not a supplier bill.
    ranks = [3 if dst == 12 else 4 for dst, src, c in f['word']]
    need(ranks.count(3) == ranks.count(4) == 12 and sum(ranks) == 84, 'incident ranks')
    return {'kernel_entries': 36, 'input_columns': 13, 'scalar_adds': 24,
            'direct_scalar_adds': 36, 'saved_scalar_adds': 12,
            'incident_rank_histogram': {'3': 12, '4': 12}, 'incident_rank_mass': 84,
            'direct_incident_rank_mass': 252, 'helpers': 1, 'copy_gates': 0,
            'erase_gates': 0, 'residual_bases': 12, 'residual_dimensions': [3] * 6 + [4] * 6,
            'full_endpoint_sha256': hashlib.sha256(json.dumps(expected, separators=(',', ':')).encode()).hexdigest(),
            'scope': 'Integer-normalized scalar kernel and conditional incident-frame ranks; no physical supplier or complete recursive invoice.'}


def controls(f):
    count = 0
    def rejects(g):
        nonlocal count
        try:
            check(g)
        except (ValueError, KeyError, IndexError, TypeError):
            count += 1
            return
        raise ValueError('negative control accepted')
    for index in (0, 6, 12, 18):
        g = deepcopy(f); del g['word'][index]; rejects(g)
    g = deepcopy(f); g['word'][0][2] *= -1; rejects(g)
    g = deepcopy(f); g['source_signs'][0] *= -1; rejects(g)
    g = deepcopy(f); g['incoming_residual_bases'][0].pop(); rejects(g)
    g = deepcopy(f); g['outgoing_residual_bases'].pop(); rejects(g)
    g = deepcopy(f); g['outgoing_residual_bases'][0][0] ^= 1; rejects(g)
    g = deepcopy(f); g['U_basis'].pop(); rejects(g)
    g = deepcopy(f); g['W_characteristic'] ^= 1; rejects(g)
    g = deepcopy(f); g['word'][0][0] = True; rejects(g)
    # All source columns can look correct if old helper cancellation is absent.
    missing = endpoint(f['word'][:18])
    correct = endpoint(f['word'])
    need(all(row[:6] == ref[:6] for row, ref in zip(missing, correct))
         and missing != correct, 'dirty-state omission is invisible to clean-source-only tests')
    return count


def pins():
    sources = load(HERE / 'SOURCES.json')
    for rec in sources['repository_inputs']:
        need(hashlib.sha256((ROOT / rec['path']).read_bytes()).hexdigest() == rec['sha256'], 'repository source pin')
    for rec in sources['retained_inputs']:
        need(hashlib.sha256((HERE / rec['path']).read_bytes()).hexdigest() == rec['sha256'], 'retained source pin')
    for rec in sources.get('package_sources', []):
        need(hashlib.sha256((HERE / rec['path']).read_bytes()).hexdigest() == rec['sha256'], 'package source pin')
    selected = load(ROOT / 'certificates/selected-result.json')
    need(selected['source_prs'][0] == 1094 and selected['certificate_sha256'] == sources['selected_certificate_sha256'], 'selected record guard')
    need(hashlib.sha256((ROOT / selected['certificate']).read_bytes()).hexdigest()
         == sources['selected_certificate_sha256'], 'selected certificate guard')
    return len(sources['repository_inputs']) + len(sources['retained_inputs']) + len(sources.get('package_sources', []))


def main():
    need(sys.argv[1:] in ([], ['--write']), 'usage: verify.py [--write]')
    f = fixture()
    result = {'base_commit': '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe', 'seed': 48,
              'witness': f, 'checks': check(f), 'negative_controls': controls(f),
              'source_pins': pins(), 'new_kappa': False}
    path = HERE / 'WITNESS.json'
    if sys.argv[1:] == ['--write']:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(canonical(load(path)) == canonical(result), 'witness certificate mismatch')
    print('PASS_COMMON_FRAME_WEIGHT5_WITNESS area=36 residuals=12 dirty_columns=13 adds=24 incident_rank_mass=84 controls=12 no_new_kappa')


if __name__ == '__main__':
    main()
