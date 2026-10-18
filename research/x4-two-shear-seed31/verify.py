#!/usr/bin/env python3
"""Exact X4 two-shear census. @woklerx / OpenAI Codex, Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '8bddbee377e2f3ce1f1247196c4b290d55767d20'
ARCHIVE = 'research/community-frontier799-audit/integrated799-replay.tar.gz'
MEMBER = 'native/local/CANONICAL-WORD.json.gz'
COEFFICIENTS = (-4, -2, -1, 1, 2, 4)  # numerators over 2
SOURCE_PATHS = {ARCHIVE, 'research/community-frontier942-audit/ASSEMBLY.json',
    'docs/research/community-batch952-review.md',
    'research/complex-sw4-frame8/local/hpe_emit_local.py',
    'research/gauge44-frames-x/construction/jx/LOCAL-PINS-jx-X4.json',
    'research/complex-x4-scaled-pairs/PROOF.md',
    'research/complex-x4-scaled-pairs/README.md'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def horner(numerator, denominator=4):
    if not numerator:
        return 0
    value = Fraction(numerator, denominator)
    n, d = abs(value.numerator), value.denominator
    need(d & (d - 1) == 0, 'non-dyadic')
    return 2 + n.bit_length() + n.bit_count() + d.bit_length() - 1


def load_rows():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    need(pins['base_commit'] == BASE and set(pins['files']) == SOURCE_PATHS, 'source pin scope')
    selected_raw = (HERE/'BASE-SELECTED.json').read_bytes().replace(b'\r\n',b'\n')
    need(hashlib.sha256(selected_raw).hexdigest() == pins['base_selected_sha256'], 'selected snapshot digest')
    selected = json.loads(selected_raw)
    need(selected['kappa'] == '1661960547713947/1000000000000000000'
         and selected['audited_source_head'] == '1960cfa919a0945d0ca4cb14ea96237000037903', 'selected snapshot scope')
    for name, digest in pins['files'].items():
        raw = (ROOT/name).read_bytes()
        if not name.endswith('.gz'):
            raw = raw.replace(b'\r\n', b'\n')
        need(hashlib.sha256(raw).hexdigest() == digest, 'source hash mismatch: '+name)
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as packed:
        data = gzip.decompress(packed.extractfile(MEMBER).read())
    need(hashlib.sha256(data).hexdigest() == '1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa',
         'X4 canonical payload mismatch')
    word = json.loads(data)
    rows = {i: {} for i in range(112, 224)}
    need((word['v'], word['R'], word['h']) == (112, 504, 9), 'X4 dimensions')
    need(len(word['compensation']) == 6320, 'X4 panel size')
    for kind, dst, src, n, d, frame in word['compensation']:
        need(kind == 'add' and dst in rows and 224 <= src < 728 and frame == 0, 'panel support')
        need(word['start'][dst] == word['start'][src] == 0, 'panel entry frame')
        need(src not in rows[dst] and (4*n) % d == 0, 'duplicate or non-quarter entry')
        rows[dst][src] = 4*n//d
    return rows


def census(rows):
    h4 = {n: horner(n, 4) for n in range(-4, 5)}
    h8 = {n: horner(n, 8) for n in range(-24, 25)}
    h16 = {n: horner(n, 16) for n in range(-112, 113)}
    boundary = {p: 2 * horner(p, 2) for p in COEFFICIENTS}
    # Price each alphabet pair once; both operands have quarter coefficients.
    prices = {(p, q, x, y): h8[2*x+p*y] + h16[2*q*x+(4+p*q)*y]
              for p, q, x, y in itertools.product(COEFFICIENTS, COEFFICIENTS, range(-4, 5), range(-4, 5))}
    digest = hashlib.sha256()
    histogram = Counter()
    best_extra = None
    pair_records = []
    profitable = better = candidates = 0
    for i, j in itertools.combinations(sorted(rows), 2):
        hist = Counter((rows[i].get(s, 0), rows[j].get(s, 0)) for s in rows[i].keys() | rows[j].keys())
        old = sum(count * (h4[x] + h4[y]) for (x, y), count in hist.items())
        best_single = old
        single_witness = None
        for direction in (0, 1):
            ordered = hist if direction == 0 else Counter({(y, x): count for (x, y), count in hist.items()})
            for p in COEFFICIENTS:
                cost = boundary[p] + sum(count * (h8[2*x+p*y] + h4[y]) for (x, y), count in ordered.items())
                if cost < best_single:
                    best_single, single_witness = cost, [direction, p]
        best_double = None
        double_witness = None
        for direction in (0, 1):
            ordered = hist if direction == 0 else Counter({(y, x): count for (x, y), count in hist.items()})
            for p, q in itertools.product(COEFFICIENTS, repeat=2):
                cost = boundary[p] + boundary[q] + sum(count * prices[p, q, x, y] for (x, y), count in ordered.items())
                record = [i, j, direction, p, q, cost, old, best_single]
                digest.update(canonical(record) + b'\n')
                candidates += 1
                profitable += cost < old
                better += cost < best_single
                histogram[str(best_single-cost)] += 1
                if best_double is None or cost < best_double:
                    best_double, double_witness = cost, [direction, p, q]
                if best_extra is None or best_single-cost > best_extra[0]:
                    best_extra = [best_single-cost, record]
        pair_records.append({'targets': [i,j], 'baseline': old, 'best_single': best_single,
                             'single_witness': single_witness, 'best_double': best_double,
                             'double_witness': double_witness})
    return {'base_commit': BASE, 'assignment_seed': 31, 'pairs': len(pair_records), 'candidates': candidates, 'profitable_over_identity': profitable,
            'better_than_best_single': better, 'maximum_extra_saving_per_component': best_extra,
            'best_pair_improvement_count': sum(r['best_double'] < r['best_single'] for r in pair_records),
            'records_sha256': digest.hexdigest(), 'saving_histogram': dict(sorted(histogram.items(), key=lambda x:int(x[0]))),
            'pair_records_sha256': hashlib.sha256(canonical(pair_records)).hexdigest(),
            'cost_floor_sha256': hashlib.sha256(canonical([[r['targets'], r['best_single'], r['best_double']] for r in pair_records])).hexdigest(),
            'best_pair_records': sorted(pair_records, key=lambda r:(r['best_double']-r['best_single'],r['targets']))[:8]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = census(load_rows())
    if args.write:
        with args.write.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        need(canonical(result) == canonical(json.loads((HERE/'EXPECTED.json').read_text())), 'receipt mismatch')
    print(f"PASS_X4_TWO_SHEAR candidates={result['candidates']} improving={result['better_than_best_single']} "
          f"extra_real_saving={2*result['maximum_extra_saving_per_component'][0]} no_new_kappa")


if __name__ == '__main__':
    main()
