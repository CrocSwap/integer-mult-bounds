#!/usr/bin/env python3
"""Independent explicit-coordinate reconstruction; imports no package code."""
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, name):
    if not ok:
        raise ValueError(name)


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT / row['path']).read_bytes()
        check(hashlib.sha256(data).hexdigest() == row['sha256'], 'source bytes')
    with tarfile.open(ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        payload = archive.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read()
    check(hashlib.sha256(payload).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'payload bytes')
    rows = sorted(json.loads(payload)['recipes'], key=lambda row: row['port'])
    vectors = [[(row['q'] // (2 ** k)) % 2 for k in range(9)] for row in rows]
    pairs = json.loads((ROOT / 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json').read_text())['matching']
    witness = json.loads((HERE / 'CERTIFICATE.json').read_text())
    owner = {p: k for k, pair in enumerate(pairs) for p in pair}

    def orthogonal(first, second):
        return all(sum(x * y for x, y in zip(vectors[a], vectors[b])) % 2 == 0
                   for a in pairs[first] for b in pairs[second])

    ports = witness['port_clique']
    check(len(ports) == len(set(ports)) == 48, '48 unique ports')
    check(all(not orthogonal(owner[i], owner[j]) for i in ports for j in ports), 'forced I48')
    groups = witness['orthogonal_classes']
    check(len(groups) == 25 and sorted(v for group in groups for v in group) == list(range(56)), '25 classes')
    # Independent direct channel labels, rather than sums of outer products.
    channel = {}
    for color, group in enumerate(groups):
        for plane in group:
            for slot, port in enumerate(pairs[plane]):
                channel[port] = 2 * color + slot
    check(len(set(channel.values())) == 50, '50 nonempty channels')
    matrix = [[int(channel[i] == channel[j]) for j in range(112)] for i in range(112)]
    checked = 0
    for i in range(112):
        for j in range(112):
            if i == j or not orthogonal(owner[i], owner[j]):
                check(matrix[i][j] == int(i == j), 'required entry')
                checked += 1
    # Distinct representative channels form I50; this proves rank 50 in every
    # field without modular rank sampling or numerical tolerances.
    representatives = [next(i for i in range(112) if channel[i] == c) for c in range(50)]
    check(all(matrix[i][j] == int(i == j) for i in representatives for j in representatives), 'I50')
    for modulus in (2, 3, 5, 101):
        source = [(i * i + 3) % modulus for i in range(112)]
        dirty = [(7 * i + 2) % modulus for i in range(112)]
        sums = [sum(source[i] for i in range(112) if channel[i] == c) % modulus for c in range(50)]
        actual = [(dirty[i] + sums[channel[i]]) % modulus for i in range(112)]
        expected = [(dirty[i] + sum(matrix[i][j] * source[j] for j in range(112))) % modulus for i in range(112)]
        check(actual == expected, 'finite field dirty update')
    check(checked == 11672, 'required entries')
    receipt = json.loads((HERE / 'RESULTS.json').read_text())
    check(receipt['matrix_sha256'] == hashlib.sha256(bytes(x for row in matrix for x in row)).hexdigest(), 'independent matrix hash')
    print('PASS_PAIRED_PLANE_VECTOR_CHECK forced=48 constructed=50 entries=11672 fields=4')


if __name__ == '__main__':
    main()
