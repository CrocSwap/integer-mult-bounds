#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound two-slot raw6 audit; not physical COPY or supplier admission."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
PARTITION = ((0, 3), (1,), (2, 4), (5, 7), (6, 8))
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
RAW = struct.Struct('<6i')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin_inputs():
    for item in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if item['usage'] == 'input':
            data = (ROOT / item['path']).read_bytes()
            need(sha(data) == item['sha256'], 'source digest: ' + item['path'])
            need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                 == item['git_blob'], 'source blob: ' + item['path'])


def decode(raw):
    need(len(raw) % RAW.size == 0, 'raw6 stream alignment')
    return list(RAW.iter_unpack(raw))


def encode(records):
    return b''.join(RAW.pack(*e) for e in records)


def rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    r = 0
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(r, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        z = rows[r][col]
        rows[r] = [x / z for x in rows[r]]
        for i in range(r + 1, len(rows)):
            z = rows[i][col]
            if z:
                rows[i] = [x - z * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


class Geometry:
    def __init__(self, frames, h):
        self.frames = {int(k): v for k, v in frames.items()}
        self.h = h
        self.cache = {}
        for f in self.frames.values():
            b, a, d = f['B'], f['A'], f['dim']
            need(all(len(row) == h for row in b + a), 'frame ambient dimension')
            need(len(b) == rank(b) == d and len(a) == rank(a) == h - d,
                 'frame basis/annihilator rank')
            need(all(sum(x * y for x, y in zip(u, v)) == 0 for u in b for v in a),
                 'frame orthogonality')

    def dim(self, frame):
        need(frame in self.frames, 'unknown frame')
        return self.frames[frame]['dim']

    def subset(self, a, b):
        if (a, b) not in self.cache:
            self.dim(a)
            self.dim(b)
            self.cache[a, b] = all(sum(x * y for x, y in zip(u, v)) == 0
                                   for u in self.frames[a]['B'] for v in self.frames[b]['A'])
        return self.cache[a, b]


def splice(records, word):
    """Replace only the authenticated one-copy scatter, retaining every MOVE."""
    n, v = 2 * word['v'] + word['R'], word['v']
    indices = [i for i, e in enumerate(records) if e[0] in (2, 3) or (e[0] == 1 and e[5] == 3)]
    lo, hi = min(indices), max(indices) + 1
    need(indices == list(range(lo, hi)), 'contiguous scatter region')
    source_copies = [e for e in records[lo:hi] if e[0] == 2]
    need(len(source_copies) == len(word['ret']) == 9, 'nine retained copies')
    need([e[1] for e in source_copies] == word['ret'], 'COPY center ordering')
    zero = source_copies[0][4]
    targets = [{v + t for t, row in enumerate(word['scatter']) if i in row} for i in range(9)]
    replacement = []

    def add(d, s, coefficient=1):
        replacement.append((1, d, s, coefficient, zero, 3))

    def opening(i, slot):
        op, center, _, frame, target_frame, paid = source_copies[i]
        need(op == 2 and target_frame == zero and paid == 7, 'rank-seven snapshot')
        replacement.append((2, center, slot, frame, zero, paid))

    def closing(i, slot):
        replacement.append((3, source_copies[i][1], slot, source_copies[i][3], zero, 0))

    for group in PARTITION:
        a = group[0]
        opening(a, n)
        if len(group) == 1:
            for t in sorted(targets[a]):
                add(t, n)
            closing(a, n)
            continue
        b = group[1]
        opening(b, n + 1)
        for t in sorted(targets[a] - targets[b]):
            add(t, n)
        for t in sorted(targets[b] - targets[a]):
            add(t, n + 1)
        add(n, n + 1)
        for t in sorted(targets[a] & targets[b]):
            add(t, n)
        add(n, n + 1, -1)
        closing(a, n)
        closing(b, n + 1)
    return records[:lo] + replacement + records[hi:], (lo, hi), replacement


def add_row(dest, source, coefficient):
    for k, value in source.items():
        value = dest.get(k, 0) + coefficient * value
        if value:
            dest[k] = value
        else:
            dest.pop(k, None)


def audit(records, word, geo, reverse=False, require_endpoint=True):
    """Exact integer rows; frames reverse by rational annihilator complement."""
    n = 2 * word['v'] + word['R']
    v = word['v']
    state = list(word['final'] if reverse else word['start']) + [None, None]
    rows = [{i: 1} for i in range(n)] + [{}, {}]
    norm = [1] * n + [0, 0]
    peak = 1
    active = {}
    hist = Counter()
    counts = Counter()
    snapshots = []
    peak_slots = peak_rank = 0
    for number, rec in enumerate(reversed(records) if reverse else records):
        op, a, b, c, f, z = rec
        need(op in (0, 1, 2, 3), 'unknown opcode')
        need(0 <= a < n + 2, 'destination role')
        if op == 0:
            need(a < n, 'temporary MOVE forbidden')
            old, new = (c, b) if reverse else (b, c)
            need(state[a] == old, 'MOVE source frame')
            need(geo.subset(b, c) and geo.dim(c) - geo.dim(b) == f and f > 0,
                 'MOVE containment or charge')
            need(z == 0, 'MOVE reserved field')
            state[a] = new
            hist[f] += 1
            counts['MOVEs'] += 1
        elif op == 1:
            need(0 <= b < n + 2 and a != b, 'ADD operands')
            need(c in (-1, 1), 'ADD coefficient alphabet')
            need((a < n or a in active) and (b < n or b in active), 'ADD inactive slot')
            need(state[a] == state[b] == f, 'ADD common frame')
            need(a not in [s[0] for s in active.values()], 'mutated COPY center')
            add_row(rows[a], rows[b], -c if reverse else c)
            norm[a] += abs(c) * norm[b]
            peak = max(peak, norm[a])
            counts['ADDs'] += 1
        else:
            need(0 <= a < n and n <= b < n + 2, 'COPY/ERASE role')
            need(state[a] == c, 'COPY/ERASE center frame')
            need(geo.dim(f) == 0, 'snapshot zero-frame marker')
            opening = op == (3 if reverse else 2)
            paid = geo.dim(c) - geo.dim(f)
            need(paid > 0 and z == (paid if op == 2 else 0), 'COPY/ERASE rank charge')
            if opening:
                need(b not in active and not rows[b], 'occupied snapshot slot')
                active[b] = (a, dict(rows[a]), paid)
                rows[b] = dict(rows[a])
                norm[b] = norm[a]
                state[b] = f
                peak = max(peak, norm[b])
                hist[paid] += 1
                counts['COPYs'] += 1
                peak_slots = max(peak_slots, len(active))
                peak_rank = max(peak_rank, sum(item[2] for item in active.values()))
            else:
                need(b in active and active[b][0] == a and state[b] == f, 'ERASE source binding')
                need(rows[b] == active[b][1] == rows[a], 'ERASE exact signed snapshot')
                snapshots.append([number, b, sha(canonical(sorted(rows[b].items())))])
                del active[b]
                rows[b] = {}
                norm[b] = 0
                state[b] = None
                counts['ERASEs'] += 1
    need(not active and rows[n:] == [{}, {}], 'unclosed snapshot')
    need(state[:n] == list(word['start'] if reverse else word['final']), 'final frames')
    if require_endpoint:
        for i, row in enumerate(rows[:n]):
            parity = sum(1 << j for j, value in row.items() if value & 1)
            want = (1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0)
            need(parity == want, 'complete local F2 dirty endpoint')
    return rows[:n], {'reverse': reverse, 'counts': dict(counts),
                     'profile': dict(sorted(hist.items())), 'rank_mass': sum(r * k for r, k in hist.items()),
                     'peak_snapshot_slots': peak_slots, 'peak_live_copy_rank': peak_rank,
                     'positive_prefix': peak, 'checked_signed_ERASEs': len(snapshots),
                     'snapshot_rows_sha256': sha(canonical(snapshots))}


def run(argv, timeout=120):
    return subprocess.run(list(map(str, argv)), check=True, text=True, capture_output=True, timeout=timeout)


def expect_failure(fn, reason):
    try:
        fn()
    except ValueError as exc:
        need(reason in str(exc), 'wrong rejection: ' + str(exc))
        return str(exc)
    raise ValueError('accepted negative control: ' + reason)


def controls(records, word, geo, binary, folder):
    n = 2 * word['v'] + word['R']
    first_add = next(i for i, e in enumerate(records) if e[0] == 1 and e[1] == n)
    restore = next(i for i, e in enumerate(records) if e[0] == 1 and e[1] == n and e[3] == -1)
    erase = restore + 1
    need(records[erase][0] == 3, 'restoration immediately precedes ERASE')
    first_copy = next(i for i, e in enumerate(records) if e[0] == 2)
    result = []

    def test(name, changed, reason, native_reason=None):
        failure = expect_failure(lambda: audit(changed, word, geo), reason)
        row = {'name': name, 'python_rejection': failure}
        if native_reason:
            path = folder / (name + '.bin')
            path.write_bytes(encode(changed))
            proc = subprocess.run([str(binary), str(path), '2'], text=True, capture_output=True)
            need(proc.returncode != 0 and native_reason in proc.stderr,
                 'native negative control: ' + name + ': ' + proc.stdout + proc.stderr)
            row['native_rejection'] = native_reason
        result.append(row)

    test('omit_restore', records[:restore] + records[restore + 1:], 'ERASE exact signed snapshot', 'ERASE snapshot mismatch')
    changed = records.copy()
    e = list(changed[restore]); e[3] = 1; changed[restore] = tuple(e)
    test('wrong_restore_sign', changed, 'ERASE exact signed snapshot')
    # This is the important genuinely endpoint-neutral defect: an unrestored
    # snapshot is never read again, so blind deallocation would hide the error.
    changed = records[:restore] + records[restore + 1:]
    need(blind_endpoint(changed, word) == blind_endpoint(records, word), 'endpoint-neutral control')
    result[-2]['persistent_endpoint_unchanged_under_blind_discard'] = True
    changed = records.copy()
    e = list(changed[first_copy + 1]); need(e[0] == 2, 'two opening copies'); e[2] = n; changed[first_copy + 1] = tuple(e)
    test('aliased_slots', changed, 'occupied snapshot slot', 'occupied slot')
    changed = records.copy()
    e = list(changed[erase]); e[1] = word['ret'][3]; e[3] = records[first_copy + 1][3]; changed[erase] = tuple(e)
    test('wrong_erase_center', changed, 'ERASE source binding', 'ERASE source binding')
    changed = records.copy()
    e = list(changed[first_add]); e[4] = 1; changed[first_add] = tuple(e)
    test('nonzero_mix_frame', changed, 'ADD common frame')
    changed = records.copy()
    e = list(changed[first_copy]); e[5] -= 1; changed[first_copy] = tuple(e)
    test('underpriced_copy', changed, 'COPY/ERASE rank charge')
    changed = records.copy()
    e = list(changed[first_add]); e[1] = word['ret'][0]; e[2] = word['ret'][0]; changed[first_add] = tuple(e)
    test('self_add', changed, 'ADD operands', 'ADD operands')
    changed = records.copy()
    e = list(changed[first_add]); e[2] = n + 2; changed[first_add] = tuple(e)
    test('undeclared_slot', changed, 'ADD operands', 'role range')
    changed = records + [(1, n, 0, 1, 0, 3)]
    test('use_after_erase', changed, 'ADD inactive slot', 'inactive slot')
    malformed = folder / 'truncated.bin'
    malformed.write_bytes(encode(records) + b'x')
    expect_failure(lambda: decode(malformed.read_bytes()), 'raw6 stream alignment')
    proc = subprocess.run([str(binary), str(malformed), '2'], text=True, capture_output=True)
    need(proc.returncode != 0 and 'stream alignment' in proc.stderr, 'native truncated-stream rejection')
    result.append({'name': 'truncated_record', 'python_rejection': 'raw6 stream alignment', 'native_rejection': 'stream alignment'})
    return result


def blind_endpoint(records, word):
    n = 2 * word['v'] + word['R']
    rows = [1 << i for i in range(n)] + [0, 0]
    for op, a, b, c, f, z in records:
        if op == 1 and c & 1:
            rows[a] ^= rows[b]
        elif op == 2:
            rows[b] = rows[a]
        elif op == 3:
            rows[b] = 0
    return rows[:n]


def perform(folder, compare_receipt=True):
    pin_inputs()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    need((word['v'], word['R'], word['h']) == (111, 439, 8), 'pinned word shape')
    exported = folder / 'baseline'
    run([sys.executable, '-I', '-B', ROOT / EXPORTER, ROOT / WORD, exported])
    baseline = decode((exported / '249-records.bin').read_bytes())
    geo = Geometry(json.loads((exported / 'frames.json').read_text())['frames'], 8)
    candidate, cut, scatter = splice(baseline, word)
    need([e for e in baseline if e[0] == 0] == [e for e in candidate if e[0] == 0], 'unchanged MOVE stream')
    need(len([e for e in scatter if e[0] == 1]) == 407, 'predecessor scatter bill')
    orientations = {}
    for reverse in (False, True):
        before, before_bill = audit(baseline, word, geo, reverse)
        after, after_bill = audit(candidate, word, geo, reverse)
        need(before == after, 'full signed integer endpoint differs from predecessor')
        need(before_bill['profile'] == after_bill['profile'] == PROFILE, 'unchanged paid profile')
        need(before_bill['counts'] == {'ADDs': 11500, 'MOVEs': 2911, 'COPYs': 9, 'ERASEs': 9}, 'baseline count')
        need(after_bill['counts'] == {'ADDs': 11380, 'MOVEs': 2911, 'COPYs': 9, 'ERASEs': 9}, 'candidate count')
        need(after_bill['peak_snapshot_slots'] == 2 and after_bill['peak_live_copy_rank'] == 14, 'workspace bill')
        orientations['reverse' if reverse else 'forward'] = {'baseline': before_bill, 'candidate': after_bill}
    candidate_path = folder / 'two-slot-records.bin'
    candidate_path.write_bytes(encode(candidate))
    binary = folder / 'bank-columns'
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    need(bool(compiler), 'empty CXX')
    run(compiler + ['-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror', HERE / 'bank_columns.cpp', '-o', binary])
    compiler_version = run(compiler + ['--version']).stdout.splitlines()[0]
    bank = {}
    forward = orientations['forward']['candidate']['positive_prefix']
    backward = orientations['reverse']['candidate']['positive_prefix']
    for pairs in (2, 4, 5):
        native = json.loads(run([binary, candidate_path, pairs]).stdout)
        stages = 2 * pairs + 1
        need(native['columns'] == 2 * pairs * 111 + stages * 439, 'independent stage helper columns')
        need(native['stage_ADDs'] == stages * 11380 and native['COPYs'] == stages * 9, 'native full event bill')
        need(native['bridge_ADDs'] == 6 * (pairs - 1) * 111, 'native bridge bill')
        need(native['terminal_exchange_ADDs'] == 3 * pairs * 111, 'terminal exchange bill')
        need(native['checked_ERASEs'] == stages * 9 and native['peak_slots'] == 2, 'native chronological coverage')
        # Each bank bridge has norm at most2. The explicitly priced terminal
        # three-ADD signed exchange has cancellation-free intermediate norm5.
        prefix = 5 * (1 << (6 * (pairs - 1))) * forward ** (pairs + 1) * backward ** pairs
        if pairs == 2:
            need(prefix < 1 << 104, 'five-stage algebraic precision guard')
        if pairs == 4:
            need(prefix < 1 << 192, 'nine-stage algebraic precision guard')
        native['algebraic_prefix_upper'] = str(prefix)
        native['algebraic_prefix_bits'] = prefix.bit_length()
        native['total_scalar_ADDs'] = (native['stage_ADDs'] + native['bridge_ADDs']
                                      + native['terminal_exchange_ADDs'])
        native['physical_precision_admitted'] = False
        bank[str(stages)] = native
    negatives = controls(candidate, word, geo, binary, folder)
    # The baseline remains admitted by the new lifecycle without requiring the
    # second slot; the old immutable implementation is not weakened in place.
    baseline_native = json.loads(run([binary, exported / '249-records.bin', 2]).stdout)
    need(baseline_native['peak_slots'] == 1 and baseline_native['stage_ADDs'] == 5 * 11500, 'single-slot positive control')
    result = {'status': 'PASS_TWO_COPY_BANK_BOUNDARY', 'raw6_sha256': sha(encode(candidate)),
              'raw6_records': len(candidate), 'replaced_baseline_scatter_range': list(cut),
              'partition': PARTITION, 'local': orientations, 'banks': bank,
              'negative_controls': negatives, 'single_slot_positive': baseline_native,
              'finite_geometry_frames': len(geo.frames), 'finite_geometry_containments': len(geo.cache),
              'claims': {'physical_address_replay': False, 'native_record_formal_columns': True,
                         'hosted_supplier_admission': False, 'new_kappa': False}}
    (folder / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    environment = {'python': sys.version, 'compiler': compiler_version, 'platform': sys.platform}
    (folder / 'ENVIRONMENT.json').write_text(json.dumps(environment, indent=2) + '\n')
    receipt = HERE / 'RESULT.json'
    if compare_receipt:
        need(receipt.is_file(), 'missing recorded result')
        need(canonical(result) == canonical(json.loads(receipt.read_text())), 'recorded result mismatch')
    print('PASS_TWO_COPY_BANK_BOUNDARY records=%d banks=5,9,11 columns=2639,4839,5939 controls=%d no_physical_admission no_new_kappa'
          % (len(candidate), len(negatives)))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, help='new directory retaining emitted records, binary and receipt')
    ap.add_argument('--generate-receipt', action='store_true',
                    help='generate a fresh work-directory receipt instead of comparing the committed one')
    args = ap.parse_args()
    need(not args.generate_receipt or args.work is not None, 'receipt generation requires --work')
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        perform(args.work, compare_receipt=not args.generate_receipt)
    else:
        with tempfile.TemporaryDirectory(prefix='two-copy-bank-') as name:
            perform(Path(name))


if __name__ == '__main__':
    main()
