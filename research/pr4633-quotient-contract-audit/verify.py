#!/usr/bin/env python3
"""Exact counterexamples to PR4633, b2998bacd50. Apache-2.0.
Cinna Davis, with substantial OpenAI Codex assistance.
Vendored construction/verifier retain DaysSky's attribution.
"""
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated'
VENDOR = HERE/'sources/research/bit-ambient-quotient'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank_q(rows):
    rows = [list(map(Q, row)) for row in rows]
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        x = rows[rank][col]
        rows[rank] = [y/x for y in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                x = rows[i][col]
                rows[i] = [a-x*b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def nullspace_mod2(rows):
    masks = [sum((x % 2) << i for i, x in enumerate(row)) for row in rows]
    return frozenset(x for x in range(256)
                     if all((x & row).bit_count() % 2 == 0 for row in masks))


def phi(x):
    if x & 2:
        x ^= 150
    return (x & 1) | ((x >> 2) << 1)


def run_author(verifier, artifact):
    with tempfile.TemporaryDirectory() as folder:
        verifier.HERE = Path(folder)
        with gzip.open(verifier.HERE/'QUOTIENT-BIT-WORD.json.gz', 'wt') as f:
            json.dump(artifact, f)
        with redirect_stdout(io.StringIO()):
            verifier.main()
        return json.loads((verifier.HERE/'RESULT.json').read_text())


def main():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Live source pin: '+row['path'])
    frames = json.loads((SOURCE/'records/frames.json').read_text())['frames']
    word = json.loads(gzip.decompress((SOURCE/'WORD.json.gz').read_bytes()))
    records = list(struct.iter_unpack('<6i', (SOURCE/'records/249-records.bin').read_bytes()))
    artifact = json.loads(gzip.decompress((VENDOR/'QUOTIENT-BIT-WORD.json.gz').read_bytes()))
    binary = {int(k): nullspace_mod2(f['A']) for k, f in frames.items()}
    for k, f in frames.items():
        need(rank_q(f['A'])+f['dim'] == 8 and rank_q(f['B']) == f['dim'], 'Source rational rank')
        need(all(sum(a*b for a, b in zip(row, basis)) == 0
                 for row in f['A'] for basis in f['B']), 'Exact annihilator')
        need(len(binary[int(k)]) == 2**f['dim'], 'Binary dimension control')
    need(len(set(binary.values())) == 157, 'Reduction already identifies frames')
    table, image = {}, {}
    for k, vectors in binary.items():
        key = frozenset(phi(x) for x in vectors)
        if key not in table:
            table[key] = len(table)
        image[k] = table[key]
    full_image = image[1]
    table[frozenset(range(256))] = len(table)
    padded = table[frozenset(range(256))]
    image = {k: padded if f == full_image else f for k, f in image.items()}
    dims = {i: len(v).bit_length()-1 for v, i in table.items()}
    sets = {i: v for v, i in table.items()}
    need({str(k): v for k, v in dims.items()} == artifact['frame_dims'], 'Independent dimensions')
    for boundary in ('start', 'final'):
        need([image[x] for x in word[boundary]] == artifact[boundary], 'Independent '+boundary)
    rewritten = []
    for op, x, y, c, f, z in records:
        if op == 0:
            old, new = image[y], image[c]
            need(sets[old] <= sets[new], 'Binary quotient MOVE containment control')
            rewritten.append([op, x, old, new, dims[new]-dims[old], z])
        elif op == 1:
            rewritten.append([op, x, y, c, image[f], z])
        else:
            need(sets[image[c]] <= sets[image[f]] or sets[image[f]] <= sets[image[c]],
                 'Binary quotient COPY containment control')
            rewritten.append([op, x, y, image[c], image[f], z])
    need(rewritten == artifact['records'], 'Independent record reconstruction')
    lost = [i for i in range(111) if dims[artifact['start'][i]] == 0]
    need(lost == list(range(8, 14)), 'Six collapsed rational entrance lines')
    q8, q9 = word['lines'][8], word['lines'][9]
    need(q8 == [0, 1, 1, 0, 1, 0, 0, 1] and
         q9 == [0, 1, 1, 0, 1, 0, 0, -1], 'Explicit rational witness')
    need(rank_q([q8, q9]) == 2, 'Two independent vectors cannot fit a line kernel')
    need(Q(q8[1]*q8[7], 4) == Q(1, 4) and Q(q9[1]*q9[7], 4) == Q(-1, 4),
         'Distinct source rational projectors')
    pair_widths = Counter((dims[artifact['final'][i]]-dims[artifact['start'][i]],
                           dims[artifact['final'][111+i]]-dims[artifact['start'][111+i]])
                          for i in range(111))
    need(pair_widths == {(7, 6): 101, (7, 8): 4, (8, 6): 6}, 'Retained rank-seven pair invariant fails')
    spec = importlib.util.spec_from_file_location('pr4633_author_verify', VENDOR/'verify.py')
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    author.SOURCE = SOURCE
    positive = run_author(author, artifact)
    need(positive['quotient_paid_mass'] == 5023 and
         abs(positive['quotient_kappa']-0.012401086416) < 1e-12, 'Author positive control')
    mutant = deepcopy(artifact)
    count = 0
    for record in mutant['records']:
        if record[0] == 0 and record[4] > 0:
            record[4] = 0
            count += 1
    need(count == 2802, 'Complete MOVE mutation inventory')
    bad = run_author(author, mutant)
    need(bad['status'] == 'PASS_BIT_AMBIENT_QUOTIENT' and bad['quotient_kappa'] == .25,
         'Submitted verifier falsely accepts free MOVEs')
    mismatch = sum(r[4] != dims[r[3]]-dims[r[2]] for r in mutant['records'] if r[0] == 0)
    need(mismatch == 2802, 'Independent rank check rejects changed charges')
    broken = deepcopy(artifact)
    next(r for r in broken['records'] if r[0] == 0)[2] = -12345
    rejected = False
    try:
        run_author(author, broken)
    except ValueError:
        rejected = True
    need(rejected, 'Author replay rejects a broken frame entrance')
    result = {
        'status': 'PASS_PR4633_AUDIT_COUNTEREXAMPLES',
        'reviewed_head': 'b2998bacd50d57c301fe67c5392054440c42398c',
        'rational_source_frames': len(frames), 'binary_reductions_distinct': 157,
        'all_source_dimensions_preserved_mod2': True, 'quotient_reconstructed_exactly': True,
        'erased_rational_ports': lost,
        'erased_rational_span_rank': rank_q([word['lines'][i] for i in lost]),
        'independent_erased_vectors': [q8, q9],
        'port_transport_width_pairs': {str(k): v for k, v in pair_widths.items()},
        'positive_control': positive,
        'free_move_mutation': {'changed_records': count, 'author_accepts': True,
                               'reported_kappa': bad['quotient_kappa'],
                               'paid_profile': bad['quotient_paid'],
                               'independent_rank_mismatches': mismatch},
        'broken_frame_entrance_rejected': rejected,
        'scope': 'Exact source and verifier counterexamples; no new supplier or kappa.'}
    if (HERE/'EXPECTED.json').exists():
        need(result == json.loads((HERE/'EXPECTED.json').read_text()), 'Exact counterexample receipt')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
