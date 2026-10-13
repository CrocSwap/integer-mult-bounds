#!/usr/bin/env python3
"""Exact X4 restored-pair cost exclusion. ToikY / OpenAI Codex, Apache-2.0.

No predecessor implementation is imported. See PROOF.md for the all-exponent
argument; this program checks the finite data and proof's arithmetic premises.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier799-audit/integrated799-replay.tar.gz'
CANONICAL = 'native/local/CANONICAL-WORD.json.gz'
PROGRAMS = 'native/local/LOCAL-PROGRAMS.json.gz'
CHECKS = 'native/local/LOCAL-CHECKS.json'
PINS = 'research/gauge44-frames-x/construction/jx/LOCAL-PINS-jx-X4.json'
SOURCE_FILES = {
    'certificates/selected-result.json', ARCHIVE, PINS,
    'research/community-frontier799-audit/ASSEMBLY.json',
    'research/community-frontier799-audit/SELECTED-SOURCE.json',
    'docs/research/community-frontier799-review.md',
    'research/complex-sw4-frame8/local/hpe_emit_local.py',
    'research/gauge44-frames-x/PROOF-NOTE-FRAMES-X4.md',
}
BASE = 'f567884aeb8851b6e794af1184119a3bfbe1e631'
SEED = 29
RADIUS = 1 + SEED % 2


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def same_json(a, b):
    # Python considers True == 1 == 1.0. Receipts must not.
    return encoded(a) == encoded(b)


def horner(a, b=4):
    """Inherited per-real-component invoice for add by a/b; zero is omitted."""
    require(type(a) is int and type(b) is int and b > 0, 'invalid coefficient')
    require(b & (b - 1) == 0, 'non-dyadic coefficient')
    if not a:
        return 0
    a = abs(a)
    g = math.gcd(a, b)
    a //= g
    b //= g
    return 3 + a.bit_length() - 1 + bin(a).count('1') + b.bit_length() - 1


def macro_cost(op):
    if op[0] in ('copy', 'clear'):
        return 1
    if op[0] == 'add':
        return horner(op[3], op[4])
    require(op[0] == 'scale', 'unknown scalar macro')
    a, b = abs(op[2]), abs(op[3])
    require(a > 0 and b > 0 and a & (a - 1) == 0 and b & (b - 1) == 0,
            'non-power-of-two scale')
    return abs(a.bit_length() - b.bit_length()) + int(op[2] * op[3] < 0)


def load_inputs(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    require(manifest['base_commit'] == BASE, 'wrong source base')
    require(set(manifest['files']) == SOURCE_FILES, 'incomplete source file pins')
    require(set(manifest['archive_members']) == {CANONICAL, PROGRAMS, CHECKS},
            'incomplete archive member pins')
    for name, pin in manifest['files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,
                'unsafe source path')
        data = (root / name).read_bytes()
        require(digest(data) == pin['sha256'], 'source hash mismatch: ' + name)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == pin['git_blob'], 'source Git blob mismatch: ' + name)
    with tarfile.open(root / ARCHIVE, 'r:gz') as archive:
        members = {}
        for name, pin in manifest['archive_members'].items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), 'ambiguous archive member')
            data = archive.extractfile(matches[0]).read()
            if name.endswith('.gz'):
                data = gzip.decompress(data)
            require(digest(data) == pin, 'member payload mismatch: ' + name)
            members[name] = json.loads(data)
    c, programs, checks = (members[CANONICAL], members[PROGRAMS], members[CHECKS])
    pins = json.loads((root / PINS).read_text())
    require(digest(encoded(c)) == pins['canonical_sha256'], 'wrong X4 canonical word')
    selected = json.loads((root / 'certificates/selected-result.json').read_text())
    require(selected['kappa'] == '1661634653669567/1000000000000000000', 'wrong checkpoint')
    require(selected['audited_source_head'] == '80e6463157cfc80b85af09e7e2f14748fe2dac60',
            'wrong selected source head')
    require(digest((root / selected['certificate']).read_bytes()) == selected['certificate_sha256'],
            'selected assembly binding')
    require(c['v'] == 112 and c['R'] == 504 and c['h'] == 9, 'wrong X4 dimensions')
    require(c['local_profile'] == {'1': 2548, '2': 338, '3': 430, '4': 194, '5': 56, '8': 8},
            'wrong X4 paid profile')
    rows = {i: {} for i in range(c['v'], 2 * c['v'])}
    require(len(c['compensation']) == 6320, 'wrong compensation length')
    for op in c['compensation']:
        require(len(op) == 6 and op[0] == 'add', 'unexpected compensation operation')
        _, target, source, a, b, frame = op
        require(all(type(x) is int for x in op[1:]), 'untyped compensation integer')
        require(target in rows and 224 <= source < 728 and frame == 0,
                'compensation support or frame')
        require(c['start'][target] == c['start'][source] == 0, 'nonzero input frame')
        require(source not in rows[target], 'duplicate matrix entry')
        require(b > 0 and b & (b - 1) == 0 and (4 * a) % b == 0, 'not quarter-grid')
        value = 4 * a // b
        require(0 < abs(value) <= 4, 'tail coefficient premise')
        rows[target][source] = value
    receipts = {}
    for orientation, events in programs.items():
        require(orientation in ('forward', 'backward'), 'unknown orientation')
        require(digest(encoded(events)) == pins['program_sha256'][orientation], 'program pin')
        require(checks[orientation]['sha256'] == pins['program_sha256'][orientation], 'receipt pin')
        begin = 1 + len(c['precondition'])
        panel = events[begin:begin + len(c['compensation'])]
        expected = []
        for _, target, source, a, b, _ in c['compensation']:
            if orientation == 'backward':
                target, source, a = source, target, -a
            expected.append(['scalar', ['add', ['L', target], ['L', source], a, b], 0])
        require(panel == expected, 'emitted compensation differs from canonical panel')
        cost = 2 * sum(macro_cost(e[1]) for e in events if e[0] == 'scalar')
        require(cost == checks[orientation]['real_component_primitive_bound'], 'native invoice mismatch')
        receipts[orientation] = {'real_primitives': cost, 'program_sha256': digest(encoded(events))}
    require(set(receipts) == {'forward', 'backward'}, 'missing orientation')
    return rows, receipts


def pair_histogram(left, right):
    return Counter((left.get(s, 0), right.get(s, 0)) for s in left.keys() | right.keys())


def pair_saving(histogram, numerator, denominator):
    old = sum(count * horner(a) for (a, _), count in histogram.items())
    new = sum(count * horner(denominator * a + numerator * b, 4 * denominator)
              for (a, b), count in histogram.items())
    return old - new - 2 * horner(numerator, denominator)


def census(rows):
    records = []
    by_exponent = {}
    # ±3 anchors the two tails; ±2 was the prespecified initial finite screen.
    for i in sorted(rows):
        for j in sorted(rows):
            if i == j:
                continue
            hist = pair_histogram(rows[i], rows[j])
            for exponent in range(-RADIUS - 1, RADIUS + 2):
                for sign in (-1, 1):
                    a = sign * 2 ** max(exponent, 0)
                    b = 2 ** max(-exponent, 0)
                    saving = pair_saving(hist, a, b)
                    records.append([saving, i, j, a, b])
                    by_exponent.setdefault(exponent, []).append([saving, i, j, a, b])
    summary = {}
    for exponent, cases in sorted(by_exponent.items()):
        maximum = max(r[0] for r in cases)
        summary[str(exponent)] = {
            'cases': len(cases), 'profitable': sum(r[0] > 0 for r in cases),
            'ties': sum(r[0] == 0 for r in cases),
            'max_saving_per_component': maximum,
            'min_saving_per_component': min(r[0] for r in cases),
            'first_maximizer': next(r for r in cases if r[0] == maximum),
        }
        if exponent:
            require(maximum < 0, 'nonunit improvement or tie found')
    return {'cases': len(records), 'records_sha256': digest(encoded(records)),
            'by_exponent': summary}


def tail_slope(a, b, negative):
    """Slope for (a*2^k+b)/2^(2+k*negative), k>=3, |a|,|b|<=4."""
    if a == 0 and b == 0:
        return 0
    if a == 0:
        return int(negative)
    if b == 0:
        return int(not negative)
    return 1 + int(a * b < 0) + int(negative)


def tail_checks():
    records = []
    for negative in (False, True):
        for a in range(-4, 5):
            for b in range(-4, 5):
                slope = tail_slope(a, b, negative)
                anchor = horner(8 * a + b, 2 ** (2 + 3 * negative))
                # Finite corroboration, not the universal proof in PROOF.md.
                for k in (3, 4, 5, 8, 29, 64, 127):
                    require(horner(a * 2 ** k + b, 2 ** (2 + k * negative)) ==
                            anchor + slope * (k - 3), 'tail affine identity')
                records.append([negative, a, b, anchor, slope])
    require(all(r[-1] >= 0 for r in records), 'negative tail slope')
    return {'families': len(records), 'tested_exponents': [3, 4, 5, 8, 29, 64, 127],
            'records_sha256': digest(encoded(records)),
            'minimum_boundary_slope_per_component': 2}


def controls():
    # Nonunit moves can be useful on another quarter-grid panel: exclude a
    # source-independent no-go claim. Ten common helpers give C_i=2*C_j.
    synthetic = Counter({(2, 1): 10})
    require(pair_saving(synthetic, -2, 1) == 40, 'synthetic positive control')
    require(horner(3, 4) == 8 and horner(2, 1) == 5 and horner(1, 2) == 5,
            'nonunit full primitive price')
    require(not same_json({'cost': 1}, {'cost': True}) and
            not same_json({'cost': 1}, {'cost': 1.0}), 'typed receipt control')
    return {'synthetic_nonunit_saving_per_component': 40, 'typed_receipts': True}


def run(root=ROOT):
    rows, programs = load_inputs(root)
    result = census(rows)
    return {'status': 'scoped negative result; no new kappa', 'base_commit': BASE,
            'assignment_seed': SEED,
            'source_manifest_sha256': digest((HERE / 'SOURCES.json').read_bytes()),
            'targets': len(rows),
            'helper_sources': len(set().union(*(set(r) for r in rows.values()))),
            'compensation_additions': sum(len(r) for r in rows.values()),
            'quarter_coefficient_counts': dict(sorted(Counter(str(a) for row in rows.values()
                                                             for a in row.values()).items())),
            'programs': programs, 'census': result, 'tails': tail_checks(),
            'controls': controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='print checked deterministic receipt')
    args = parser.parse_args()
    receipt = run()
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    require(same_json(receipt, expected), 'expected receipt mismatch')
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    print('PASS_X4_NONUNIT_PAIR_EXCLUSION cases=174048 nonunit=149184 '
          'tails=all_integer_exponents min_extra_real=20 no_new_kappa')


if __name__ == '__main__':
    main()
