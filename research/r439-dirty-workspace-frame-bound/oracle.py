#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ross Richardson, with substantial OpenAI Codex assistance.
"""Separate truth-table / integer-geometry checker; imports no primary code."""
import argparse
from collections import Counter
import gzip
import hashlib
from itertools import permutations, product
from math import gcd
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank_integer(vectors):
    """Integer row operations, with primitive normalization after elimination."""
    rows = [list(row) for row in vectors]
    if not rows:
        return 0
    at = 0
    for c in range(len(rows[0])):
        p = next((j for j in range(at, len(rows)) if rows[j][c]), None)
        if p is None:
            continue
        rows[p], rows[at] = rows[at], rows[p]
        for j in range(at + 1, len(rows)):
            if not rows[j][c]:
                continue
            a, b = rows[at][c], rows[j][c]
            rows[j] = [a * x - b * y for x, y in zip(rows[j], rows[at])]
            divisor = 0
            for x in rows[j]:
                divisor = gcd(divisor, x)
            if divisor:
                rows[j] = [x // divisor for x in rows[j]]
        at += 1
    return at


def determinant(matrix):
    a = [list(row) for row in matrix]
    previous, sign = 1, 1
    for k in range(len(a) - 1):
        p = next((j for j in range(k, len(a)) if a[j][k]), None)
        if p is None:
            return 0
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                require(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1] if a else 1


def inverse_table(table):
    require(sorted(table) == list(range(len(table))), 'not a permutation')
    result = [0] * len(table)
    for x, y in enumerate(table):
        result[y] = x
    return tuple(result)


def columns(table, n):
    result = []
    for j in range(n):
        mask = 0
        for x in range(len(table)):
            if not (x >> j) & 1:
                mask |= table[x] ^ table[x ^ (1 << j)]
        result.append(mask)
    return result


def dependency_data(table, n):
    forward_columns = columns(table, n)
    forward_rows = [sum(((forward_columns[j] >> i) & 1) << j for j in range(n))
                    for i in range(n)]
    return forward_rows, columns(inverse_table(table), n)


def original_contract(table, original_table):
    """Reject clean-only success; check every original/workspace assignment."""
    inverse_table(table)
    size = len(original_table)
    require(size > 0 and size & (size - 1) == 0, 'original size')
    require(len(table) % size == 0, 'workspace size')
    for x, y in enumerate(table):
        require(y % size == original_table[x % size], 'dirty original endpoint')


def frame_obligations(table, initial, current):
    """Finite coordinate-subspace fixture for the semantic dual invariant."""
    n = len(initial)
    require(len(table) == 1 << n and len(current) == n, 'frame fixture shape')
    forward, dual = dependency_data(table, n)
    for i in range(n):
        required = initial[i]
        for j in range(n):
            if ((forward[i] | dual[i]) >> j) & 1:
                required |= initial[j]
        require(required & ~current[i] == 0, 'semantic frame obligation')


def source_words(root=ROOT):
    result = {}
    for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if pin['usage'] != 'input':
            continue
        raw = (root / pin['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source Git blob')
        if pin['path'].endswith('.gz'):
            result[pin['path']] = json.loads(gzip.decompress(raw))
    require(len(result) == 2, 'two source words')
    return result


def literal_table(ops, regs):
    index = {r: i for i, r in enumerate(regs)}
    table = []
    for x in range(1 << len(regs)):
        y = x
        for _, d, sources in ops:
            for s in sources:
                y ^= ((y >> index[s]) & 1) << index[d]
        table.append(y)
    return tuple(table)


def check_blocks(cert, words):
    total, assignments, workspace_assignments, determinants = Counter(), 0, 0, []
    require(cert['original_wire_count'] == 114, 'original wire count')
    require(len(cert['blocks']) == 10, 'ten blocks')
    for word_index, word in enumerate(words.values()):
        for b in cert['blocks']:
            f, regs = b['frame'], b['registers']
            where = [i for i, g in enumerate(word['B']) if g[0] == f]
            require(where == list(range(where[0], where[-1] + 1)), 'block continuity')
            ops = word['B'][where[0]:where[-1] + 1]
            actual_regs = sorted({r for _, d, ss in ops for r in [d, *ss]})
            require(regs == actual_regs, 'wire inventory')
            # Separate reverse-last-use lookup of each actual entry frame.
            prefix = word['D'] + word['A'] + word['B'][:where[0]]
            entry = []
            for r in regs:
                label = word['start'][r]
                for frame, dest, sources in reversed(prefix):
                    if r == dest or r in sources:
                        label = frame
                        break
                entry.append(label)
            require(entry == b['entry_frames'], 'entry frames')
            n = len(regs)
            table = literal_table(ops, regs)
            inverse = inverse_table(table)
            rows, dual = dependency_data(table, n)
            require(rows == b['matrix_rows'], 'matrix truth table')
            # Verify linear formulas on EVERY input, not only basis inputs.
            for x in range(1 << n):
                predicted = sum(((x & r).bit_count() & 1) << i for i, r in enumerate(b['matrix_rows']))
                recovered = sum(((x & r).bit_count() & 1) << i for i, r in enumerate(b['inverse_rows']))
                require(table[x] == predicted and inverse[x] == recovered, 'full forward/inverse table')
            assignments += 1 << n
            vectors = word['lines']
            labels = [word['frames'][e] for e in entry]
            entry_ranks = [rank_integer([vectors[r] for r in roots]) for roots in labels]
            require(entry_ranks == b['entry_ranks'], 'entry ranks')
            require(rank_integer([vectors[r] for r in word['frames'][f]]) == 4, 'F rank')
            for i, obligation in enumerate(b['obligations']):
                require(obligation['register'] == regs[i], 'obligation order')
                fw = [j for j in range(n) if (rows[i] >> j) & 1]
                bw = [j for j in range(n) if (dual[i] >> j) & 1]
                require(obligation['forward_inputs'] == [regs[j] for j in fw], 'forward support')
                require(obligation['inverse_outputs'] == [regs[j] for j in bw], 'inverse support')
                origins = {i, *fw, *bw}
                roots = {r for j in origins for r in labels[j]}
                require(roots <= set(word['frames'][f]), 'outside F')
                forward_roots = {r for j in {i, *fw} for r in labels[j]}
                require(obligation['forward_rank'] == rank_integer([vectors[r] for r in forward_roots]),
                        'forward rank')
                require(obligation['forced_rank'] == rank_integer([vectors[r] for r in roots]) == 4,
                        'combined rank')
                witness = []
                for origin, root in obligation['witness']:
                    require(origin in [regs[j] for j in origins], 'witness origin')
                    require(root in labels[regs.index(origin)], 'witness root membership')
                    witness.append(vectors[root])
                require(len(witness) == 4, 'four witness vectors')
                gram = [[sum(x * y for x, y in zip(u, v)) for v in witness] for u in witness]
                det = determinant(gram)
                require(det > 0, 'dependent witness')
                determinants.append(det)
            climbs = Counter(4 - d for d in entry_ranks)
            climbs.pop(0, None)
            require({str(k): v for k, v in sorted(climbs.items())} == b['minimum_climbs'], 'block bill')
            if word_index == 0:
                total.update(climbs)
                # Dirty auxiliary echo: prepare z ^= x0*x1, execute M, then
                # restore using x=M^-1*y. All operands operate at F; the extra
                # zero-dimensional entry wire pays one rank-four climb.
                garbage, restored = [], []
                for state in range(1 << (n + 1)):
                    x, z = state & ((1 << n) - 1), state >> n
                    z1 = z ^ ((x & 1) & ((x >> 1) & 1))
                    y = table[x]
                    garbage.append(y | (z1 << n))
                    recover = inverse[y]
                    z2 = z1 ^ ((recover & 1) & ((recover >> 1) & 1))
                    restored.append(y | (z2 << n))
                    require(restored[-1] == y | (z << n), 'dirty echo endpoint')
                inv_garbage = inverse_table(garbage)
                original_contract(garbage, table)
                original_contract(restored, table)
                for output, initial in enumerate(inv_garbage):
                    require((initial & ((1 << n) - 1)) == inverse[output & ((1 << n) - 1)],
                            'garbage changed inverse original coordinates')
                workspace_assignments += 2 * (1 << (n + 1))
    require(dict(total) == {2: 93, 3: 10}, 'total frame bill')
    require(cert['minimum_original_climbs'] == {'2': 93, '3': 10}, 'certificate total')
    require(cert['minimum_original_rank_mass'] == 216, 'certificate rank mass')
    require(cert['forward_forced_wire_count'] == sum(o['forward_rank'] == 4
            for b in cert['blocks'] for o in b['obligations']) == 112, 'forward-only coverage')
    return {'block_truth_inputs': assignments, 'dirty_workspace_truth_inputs': workspace_assignments,
            'gram_witnesses': len(determinants), 'gram_determinants': sorted(set(determinants)),
            'dirty_echo_extra_climbs_per_block': {'4': 1}}


def nonlinear_steps():
    """All 8! three-bit permutations, each followed by 6 CNOTs / 3 Toffolis."""
    data = {t: dependency_data(t, 3) for t in permutations(range(8))}
    gates = []
    for dest in range(3):
        for source in range(3):
            if dest != source:
                gates.append(((dest, source), tuple(x ^ (((x >> source) & 1) << dest) for x in range(8))))
        a, b = [j for j in range(3) if j != dest]
        gates.append(((0, 1, 2), tuple(x ^ ((((x >> a) & 1) & ((x >> b) & 1)) << dest) for x in range(8))))
    count = 0
    for table, old in data.items():
        for support, gate in gates:
            new = data[tuple(gate[x] for x in table)]
            for side in range(2):
                allowed = 0
                for k in support:
                    allowed |= old[side][k]
                for i in range(3):
                    if i in support:
                        require(new[side][i] & ~allowed == 0, 'dependency induction')
                    else:
                        require(new[side][i] == old[side][i], 'outside dependency changed')
            count += 1
    return count


def garbage_fibers():
    """All 3-bit permutations with a fixed invertible original output map."""
    count = 0
    for n in (1, 2):
        k = 3 - n
        for phi in permutations(range(1 << n)):
            pinv = inverse_table(phi)
            for fibers in product(tuple(permutations(range(1 << k))), repeat=1 << n):
                table = tuple(phi[x & ((1 << n) - 1)] |
                              (fibers[x & ((1 << n) - 1)][x >> n] << n) for x in range(8))
                inv = inverse_table(table)
                for y in range(8):
                    require((inv[y] & ((1 << n) - 1)) == pinv[y & ((1 << n) - 1)],
                            'dirty fiber closure')
                count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    args = ap.parse_args()
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    report = check_blocks(cert, source_words(args.root))
    report.update(nonlinear_prefix_gate_pairs=nonlinear_steps(), dirty_garbage_fibers=garbage_fibers())
    require(report['nonlinear_prefix_gate_pairs'] == 362880, 'step coverage')
    require(report['dirty_garbage_fibers'] == 1536, 'fiber coverage')
    print(json.dumps(report, sort_keys=True))
    print('PASS_R439_DIRTY_WORKSPACE_ORACLE no_new_kappa')


if __name__ == '__main__':
    main()
