#!/usr/bin/env python3
"""External finite binding of the exact PR2484 mask to the formal C5 interface.
This Python replay does not execute Lean; use check_lean.py for a fresh kernel run.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MATCHING = 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
PINS = {ARCHIVE: 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
        MATCHING: '4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1'}
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
CORE = [13, 23, 35, 16, 34]
CLIQUE = [0,4,8,17,18,19,20,21,24,26,28,29,32,36,38,39,41,42,43,45,46,52]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def pinned(path, raw=None):
    raw = (ROOT/path).read_bytes() if raw is None else raw
    need(sha256(raw).hexdigest() == PINS[path], 'source hash mismatch: '+path)
    return raw


def dot(x, y):
    return (x & y).bit_count() % 2


def load():
    archive, matching = pinned(ARCHIVE), pinned(MATCHING)
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
        handle = tar.extractfile(MEMBER)
        need(handle is not None, 'missing source member')
        raw = handle.read()
    need(sha256(raw).hexdigest() == MEMBER_SHA, 'source member hash')
    rows = sorted(json.loads(raw)['recipes'], key=lambda r: r['port'])
    need([r['port'] for r in rows] == list(range(112)), 'port indexing')
    labels = [r['q'] for r in rows]
    need(len(set(labels)) == 112 and all(0 < q < 512 and dot(q, q) for q in labels), 'binary labels')
    pairs = json.loads(matching)['matching']
    need(len(pairs) == 56 and sorted(v for pair in pairs for v in pair) == list(range(112)), 'matching partition')
    need(all(len(p) == 2 and dot(labels[p[0]], labels[p[1]]) == 0 for p in pairs), 'nondegenerate plane bases')
    planes = [{0, labels[a], labels[b], labels[a] ^ labels[b]} for a, b in pairs]
    # Whole four-element spans, instead of trusting the predecessor's four basis pairings.
    orth = [[i != j and all(dot(a, b) == 0 for a in planes[i] for b in planes[j])
             for j in range(56)] for i in range(56)]
    return labels, pairs, orth


def check_binding(orth, core, clique):
    need(len(core) == 5 and len(set(core)) == 5, 'core size')
    need(len(clique) == 22 and len(set(clique)) == 22 and not set(core) & set(clique), 'clique size/disjointness')
    need(all(orth[core[i]][core[j]] == ((i-j) % 5 in [1,4])
             for i in range(5) for j in range(5)), 'induced C5 in named cycle order')
    need(all(not orth[a][b] for a in clique for b in clique if a != b), 'identity clique')
    need(all(not orth[a][b] for a in clique for b in core), 'isolated core cross blocks')


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def rank_mod(a, p):
    rows = [[v % p for v in row] for row in a]
    pos = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(pos, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pos], rows[pivot] = rows[pivot], rows[pos]
        scale = pow(rows[pos][col], -1, p)
        rows[pos] = [(v*scale) % p for v in rows[pos]]
        for i in range(len(rows)):
            if i != pos:
                scale = rows[i][col]
                rows[i] = [(x-scale*y) % p for x, y in zip(rows[i], rows[pos])]
        pos += 1
    return pos


def reject(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control accepted: '+label)


def build():
    labels, pairs, orth = load()
    check_binding(orth, CORE, CLIQUE)
    # Match the formal definition exactly: two scalar entries per plane, identity diagonal blocks.
    far = [[(i+2) % 5 == j or (j+2) % 5 == i for j in range(5)] for i in range(5)]
    need(all(far[i][j] == (i != j and not orth[CORE[i]][CORE[j]])
             for i in range(5) for j in range(5)), 'formal Far predicate binding')
    core_ports = [p for i in CORE for p in pairs[i]]
    clique_ports = [p for i in CLIQUE for p in pairs[i]]
    need(len(set(core_ports+clique_ports)) == 54, '54 distinct source ports')
    # The relaxed witness is an integer Gram factorization with four columns.
    groups = [0,1,1,1,0]
    u = [[int(k == 2*groups[i]+j) for k in range(4)] for i in range(5) for j in range(2)]
    m = multiply(u, list(map(list, zip(*u))))
    s = [0,1,4,5]
    need([[m[i][j] for j in s] for i in s] == [[int(i == j) for j in range(4)] for i in range(4)], 'four pivot identity')
    need(m == multiply([[row[j] for j in s] for row in m], [m[i] for i in s]), 'literal Schur boundary')
    need(all(m[i][j] == int(i == j) for i in range(10) for j in range(10) if i//2 == j//2), 'boundary diagonal')
    violations = [(i,j) for i in range(5) for j in range(5) if far[i][j]
                  and any(m[2*i+a][2*j+b] for a in range(2) for b in range(2))]
    need(violations == [(1,3),(3,1)], 'exact missing edge')
    need([rank_mod(m, p) for p in [2,3,101]] == [4]*3, 'boundary rank crosscheck')
    controls = [reject(lambda: check_binding(orth, [CORE[1],CORE[0],*CORE[2:]], CLIQUE), 'wrong cycle order'),
                reject(lambda: check_binding(orth, CORE, [22 if i == 20 else i for i in CLIQUE]), 'clique still internal but core cross edge changed'),
                reject(lambda: need(not violations, 'strict mask fails'), 'relaxed factorization passed as strict'),
                reject(lambda: pinned(MATCHING, pinned(MATCHING)+b' '), 'matching drift')]
    # An ordinary full check may verify this local receipt but does not rerun Lean.
    lean = json.loads((HERE/'LEAN-CHECK.json').read_text())
    formal_hash = sha256((HERE/'Schur.lean').read_bytes()).hexdigest()
    need(lean['status'] == 'PASS_PAIRED_C5_LEAN' and lean['source_sha256'] == formal_hash, 'Lean receipt source binding')
    names = {'reverse_inverse','no_four_pivot','relaxed_diagonal','relaxed_remaining_zeros','relaxed_four_pivot','relaxed_missing_edge'}
    need(set(lean['theorem_axioms']) == names and all(set(v) <= {'propext','Classical.choice','Quot.sound'}
         for v in lean['theorem_axioms'].values()), 'recorded formal inventory')
    need('version 4.34.1,' in lean['version'] and lean['rejected_mutations'] ==
         ['wrong_reversed_inverse','zero_diagonal','drop_nontriviality','free_B_D'], 'recorded toolchain and controls')
    return {'scope': 'External source binding to PairedC5.no_four_pivot; formal rank bridge excluded',
            'source_hashes': PINS, 'member_sha256': MEMBER_SHA,
            'core': CORE, 'clique22': CLIQUE, 'core_ports': core_ports, 'clique_ports': clique_ports,
            'formal_far': far, 'forced_zero_core_scalar_entries': sum(map(sum, far))*4,
            'identity_block_scalar_dimension': 44, 'cross_forced_zero_entries': 2*44*10,
            'relaxed_matrix': m, 'relaxed_factor': u, 'relaxed_rank_mod_2_3_101': [4,4,4],
            'relaxed_only_violations': violations, 'controls': controls,
            'formal_source_sha256': formal_hash,
            'formal_status': 'Source-bound recorded kernel run; run check_lean.py for a fresh Lean check.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = build()
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    else:
        need(canon(result) == canon(json.loads((HERE/'RESULT.json').read_text())), 'complete receipt mismatch')
    print('PASS_PAIRED_C5_FINITE_BINDING planes=56 core_ports=10 isolated_identity=44 controls=4; not a fresh Lean run')


if __name__ == '__main__':
    main()
