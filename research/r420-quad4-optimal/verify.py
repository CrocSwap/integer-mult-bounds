#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Chris Barber (@cbarber1) with OpenAI Codex assistance.
"""Source-bound quad-4 optimality and complete R420 native-word verification.

Usage: python3 -B research/r420-quad4-optimal/verify.py
No third-party packages, network, external solver or cached result is used.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from optimal import minimum_additions

WORD = 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
CHECKER = 'research/e8-bit-r420/code/xcheck.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


class Reject(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_check():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for path, record in pins['files'].items():
        data = (ROOT/path).read_bytes()
        need(sha(data) == record['sha256'], 'source hash: ' + path)
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == record['git_blob'], 'source blob: ' + path)
    return pins


def matrix(operations, n=6, xor=False):
    m = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in operations:
        need(type(d) is int and type(s) is int and 0 <= d < n and 0 <= s < n and d != s, 'invalid addition')
        m[d] = [a ^ b if xor else a + b for a, b in zip(m[d], m[s])]
    return m


def dominated(a, b):
    return all(x <= y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def admit_local(old, new):
    need(matrix(old) == matrix(new), 'integer forward endpoint')
    need(dominated(matrix(new[::-1]), matrix(old[::-1])), 'reverse positive transfer')


def rebuild(word, spec):
    new = deepcopy(word)
    regs = spec['registers']
    frame = spec['frame']
    old = [[frame, regs[d], [regs[s]]] for d, s in spec['old_operations']]
    a, b = spec['start_inclusive'], spec['stop_exclusive']
    need((a, b, frame, regs) == (690, 709, 306, [259,270,284,290,294,296]), 'wrong selected quad')
    need(new['A'][a:b] == old, 'source slice')
    new['A'][a:b] = [[frame, regs[d], [regs[s]]] for d, s in spec['operations']]
    v = new['v']
    new['C'] = [[1, d, list(src)] for _, d, src in reversed(new['A'] + new['B']) if not v <= d < 2*v]
    return new


def load_checker():
    spec = importlib.util.spec_from_file_location('pinned_r420_xcheck', ROOT/CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native(checker, word):
    obj, labels, full, hypotheses, conclusion, info = checker.check(word)
    need(all(hypotheses.values()) and all(conclusion.values()), 'native H1-H5 or decomposition')
    return obj, {'labels': labels, 'full': full, 'hypotheses': hypotheses, 'conclusion': conclusion}


def paths_and_histogram(word, dimensions):
    paths = [[f] for f in word['start']]
    histogram = Counter()

    def move(r, f):
        old = paths[r][-1]
        if old != f:
            diff = dimensions[f] - dimensions[old]
            need(diff > 0, 'nonpositive frame step')
            histogram[diff] += 1
            paths[r].append(f)

    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            for r in word['ret']:
                histogram[dimensions[paths[r][-1]]] += 1
        else:
            for f, d, sources in word[section]:
                for r in [d] + sources:
                    move(r, f)
    for r, f in enumerate(word['final']):
        move(r, f)
    return paths, {str(k): v for k, v in sorted(histogram.items())}


def export(word, directory):
    path = directory/'word.json.gz'
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    records = directory/'records'
    result = subprocess.run([sys.executable, '-I', '-B', str(ROOT/EXPORTER), str(path), str(records)], capture_output=True, text=True)
    need(result.returncode == 0, 'record exporter: ' + result.stderr)
    data = (records/'249-records.bin').read_bytes()
    need(len(data) % 24 == 0, 'record alignment')
    return list(struct.iter_unpack('<6i', data))


def records_check(records, n=660, v=120):
    """Set-valued columns and integer bounds, independent of native xcheck."""
    reports = []
    for reverse in (False, True):
        values = [{r} for r in range(n)] + [set()]
        bounds = [1]*(n+1)
        peak = 1
        opened = None
        adds = copies = erasures = 0
        for op, a, b, coefficient, frame, phase in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5-op
            if op == 1:
                need(0 <= a < n and 0 <= b <= n and a != b, 'record operands')
                need(b != n or opened is not None, 'read closed copy')
                need(a != opened, 'copy source mutated')
                if coefficient % 2:
                    values[a].symmetric_difference_update(values[b])
                bounds[a] += abs(coefficient)*bounds[b]
                peak = max(peak, bounds[a])
                adds += 1
            elif op == 2:
                need(opened is None and b == n and 0 <= a < n, 'copy open')
                opened = a
                values[n] = set(values[a])
                bounds[n] = bounds[a]
                copies += 1
            elif op == 3:
                need(opened == a and b == n, 'copy close')
                values[n] = set()
                bounds[n] = 0
                opened = None
                erasures += 1
            else:
                raise Reject('record opcode')
        need(opened is None and copies == erasures == 9, 'copy lifecycle')
        for r in range(n):
            expected = {r, r-v} if v <= r < 2*v else {r}
            need(values[r] == expected, 'record dirty endpoint')
        need(not values[n], 'copy work not clear')
        reports.append({'reverse': reverse, 'adds': adds, 'copies': copies, 'erasures': erasures, 'columns': n, 'positive_prefix': peak})
    f, b = [r['positive_prefix'] for r in reports]
    payload = 64*f**3*b**2
    need(payload < 2**104, 'payload threshold')
    return {'records': len(records), 'directions': reports, 'payload_upper': payload, 'payload_bits': payload.bit_length()}


def negative_controls(checker, original, candidate, spec, records):
    rejected = []

    def fails(name, action):
        try:
            action()
        except (Reject, checker.Reject, ValueError):
            rejected.append(name)
        else:
            raise Reject('vacuous negative control: ' + name)

    old, new = spec['old_operations'], spec['operations']
    fails('dropped local gate', lambda: admit_local(old, new[:-1]))
    fails('wrong local source', lambda: admit_local(old, [[1,2]] + new[1:]))
    # A cancelling XOR pair must not sneak through the stronger integer contract.
    neutral = new + [[0,1],[0,1]]
    need(matrix(neutral, xor=True) == matrix(new, xor=True), 'control must be F2 neutral')
    fails('F2-neutral integer inflation', lambda: admit_local(old, neutral))
    same_map = [[1,3],[3,4],[2,5],[4,5],[5,3],[4,3],[4,2],[5,0],[5,2],
                [3,2],[2,3],[0,3],[2,1],[4,1],[5,1],[1,0],[4,0],[2,0]]
    need(matrix(same_map) == matrix(old), 'reverse control must preserve integer map')
    fails('integer-correct 18-gate word inflates reverse bound', lambda: admit_local(old, same_map))
    bad = deepcopy(candidate)
    bad['C'] = original['C']
    fails('stale cleanup', lambda: native(checker, bad))
    bad = deepcopy(candidate)
    bad['A'][690][0] = 0
    fails('illegal low frame', lambda: native(checker, bad))
    bad = deepcopy(candidate)
    bad['D'][0][2] = bad['D'][0][2][1:]
    fails('missing dirt compensation', lambda: native(checker, bad))
    bad = deepcopy(candidate)
    # Same F2 word but violates the literal cleanup hypothesis.
    bad['C'] += [[1,259,[270]], [1,259,[270]]]
    fails('nonliteral F2-neutral cleanup', lambda: native(checker, bad))
    ri = next(i for i, r in enumerate(records) if r[0] == 1 and r[5] == 2)
    bad_records = records[:ri]+records[ri+1:]
    fails('missing exported ADD', lambda: records_check(bad_records))
    # All F2 endpoints survive changing an odd coefficient by a large even value.
    bad_records = list(records)
    r = list(bad_records[ri]); r[3] = 1 + 2**104; bad_records[ri] = tuple(r)
    fails('F2-correct record exceeds prefix budget', lambda: records_check(bad_records))
    return rejected


def run():
    pins = source_check()
    spec = json.loads((HERE/'CIRCUIT.json').read_text())
    original = json.loads(gzip.decompress((ROOT/WORD).read_bytes()))
    old, new = spec['old_operations'], spec['operations']
    admit_local(old, new)
    need(len(new) == 11 and len(old) == 19, 'gate counts')
    target = matrix(old)
    optimum = minimum_additions(target)
    need(optimum['minimum_additions'] == len(new), 'circuit not optimal in monotone class')
    candidate = rebuild(original, spec)
    checker = load_checker()
    before_obj, before_native = native(checker, original)
    after_obj, after_native = native(checker, candidate)
    before_paths, before_histogram = paths_and_histogram(original, before_obj.fdim)
    after_paths, after_histogram = paths_and_histogram(candidate, after_obj.fdim)
    need(before_paths == after_paths, 'register frame paths changed')
    need(before_histogram == after_histogram == {'1':1320,'2':1440,'4':60,'5':120,'8':9}, 'paid histogram')
    with tempfile.TemporaryDirectory(prefix='r420-quad4-') as tmp:
        directory = Path(tmp)
        (directory/'before').mkdir(); (directory/'after').mkdir()
        before_records = export(original, directory/'before')
        after_records = export(candidate, directory/'after')
        before = records_check(before_records)
        after = records_check(after_records)
        need(before['directions'][0]['adds'] - after['directions'][0]['adds'] == 16, 'whole-word saving')
        for b, a in zip(before['directions'], after['directions']):
            need(a['positive_prefix'] <= b['positive_prefix'], 'native prefix increased')
        controls = negative_controls(checker, original, candidate, spec, after_records)
    return {
        'status': 'PASS_R420_QUAD4_OPTIMAL',
        'base_commit': pins['base_commit'],
        'source_pr543': pins['source_head'],
        'scope': 'Finite phase-A quad circuit improvement, monotone integer minimum, native bit-word verification; no new kappa.',
        'local': {'before_gates':len(old), 'after_gates':len(new), 'forward_integer_matrix':target,
                  'before_reverse_positive_matrix':matrix(old[::-1]), 'after_reverse_positive_matrix':matrix(new[::-1]),
                  'optimality':optimum},
        'candidate_content_sha256':sha(canonical(candidate)),
        'native': {'before':before_native, 'after':after_native},
        'frame_paths_sha256':sha(canonical(before_paths)),
        'paid_histogram':after_histogram,
        'rank_mass':sum(int(k)*v for k,v in after_histogram.items()),
        'records':{'before':before,'after':after},
        'negative_controls':controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', type=Path, help='write to a new path instead of comparing EXPECTED.json')
    args = parser.parse_args()
    if args.write_receipt:
        need(not args.write_receipt.exists(), 'refuse to overwrite output')
    report = run()
    if args.write_receipt:
        with args.write_receipt.open('x') as f:
            json.dump(report, f, indent=2, sort_keys=True); f.write('\n')
    else:
        expected = json.loads((HERE/'EXPECTED.json').read_text())
        need(report == expected, 'exact receipt mismatch')
    print('PASS_R420_QUAD4_OPTIMAL gates=19->11 minimum=11 states=165828 native_adds=26916->26900 columns=660 controls=10 kappa=unchanged')


if __name__ == '__main__':
    try:
        main()
    except (Reject, ValueError) as error:
        print('REJECT:', error, file=sys.stderr)
        sys.exit(1)
