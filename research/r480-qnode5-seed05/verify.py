"""Independent finite verifier; no search imports. Apache-2.0; Codex assistance."""
import argparse
import collections
import copy
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
REGS = [19, 24, 35, 40, 54, 56, 65, 74, 84, 95, 100, 111]
FRAME, START, STOP = 487, 2409, 2460


class Reject(ValueError):
    pass


def need(condition, label):
    if not condition:
        raise Reject(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rank(vectors):
    pivots = {}
    for vector in vectors:
        row = list(map(Fraction, vector))
        for k in sorted(pivots):
            scale = row[k]
            row = [a - scale * b for a, b in zip(row, pivots[k])]
        k = next((i for i, x in enumerate(row) if x), None)
        if k is not None:
            pivots[k] = [x / row[k] for x in row]
    return len(pivots)


def block_map(gates, value):
    values = {r: (value >> i) & 1 for i, r in enumerate(REGS)}
    for f, d, sources in gates:
        need(f == FRAME and d in values and len(sources) == 1,
             'block gate shape/frame')
        s = sources[0]
        need(s in values and d != s, 'block source/destination')
        values[d] ^= values[s]
    return sum(values[r] << i for i, r in enumerate(REGS))


def make_word(base, gates):
    w = copy.deepcopy(base)
    w['A'][START:STOP] = copy.deepcopy(gates)
    w['C'] = [[1, d, list(ss)] for _, d, ss in reversed(w['A'] + w['B'])
              if d < w['v'] or d >= 2 * w['v']]
    return w


def records(w, dimensions, check_cleanup=True):
    """Reconstruct the exact raw six-int contract, including every MOVE."""
    v, n = w['v'], 2 * w['v'] + w['R']
    need(len(w['start']) == len(w['final']) == n, 'boundary frame count')
    if check_cleanup:
        literal = [[1, d, list(ss)] for _, d, ss in reversed(w['A'] + w['B'])
                   if d < v or d >= 2 * v]
        need(w['C'] == literal, 'literal cleanup contract')
    current = w['start'][:]
    masks = [set(f) for f in w['frames']]
    trails = [[f] for f in current]
    result = []
    paid = collections.Counter()
    copies = []

    def move(r, frame):
        need(0 <= r < n and 0 <= frame < len(masks), 'register/frame range')
        old = current[r]
        if old != frame:
            need(masks[old] < masks[frame] and dimensions[old] < dimensions[frame],
                 'strict nested frame climb')
            charge = dimensions[frame] - dimensions[old]
            result.append((0, r, old, frame, charge, 0))
            paid[charge] += 1
            current[r] = frame
            trails[r].append(frame)

    def phase(name, number):
        for frame, d, sources in w[name]:
            need(len({d, *sources}) == 1 + len(sources), 'distinct operands')
            for r in [d, *sources]:
                move(r, frame)
            result.extend((1, d, s, 1, frame, number) for s in sources)

    phase('D', 1)
    phase('A', 2)
    need(all(current[v + t] == 0 for t in range(v)), 'targets before scatter')
    for k, q in enumerate(w['ret']):
        need(2 * v <= q < n, 'retained total register')
        frame = current[q]
        charge = dimensions[frame]
        result.append((2, q, n, frame, 0, charge))
        copies.append(charge)
        paid[charge] += 1
        for t, row in enumerate(w['scatter']):
            need(len(row) == len(set(row)) and all(0 <= i < len(w['ret']) for i in row),
                 'scatter indices')
            if k in row:
                result.append((1, v + t, n, 1, 0, 3))
        result.append((3, q, n, frame, 0, 0))
    phase('B', 4)
    phase('C', 5)
    for r, frame in enumerate(w['final']):
        move(r, frame)
    return result, trails, dict(sorted(paid.items())), copies


def events(raw):
    return [(op, a, b, c) for op, a, b, c, _, _ in raw if op != 0]


def positive_bounds(raw, n):
    """Exact cancellation-free row-l1 recurrence of columns_h/k.cpp."""
    peaks = []
    for reverse in (False, True):
        norms, peak, center = [1] * (n + 1), 1, None
        seq = raw[::-1] if reverse else raw
        for op, a, b, coefficient, _, _ in seq:
            if not op:
                continue
            if op == 1:
                need(a != n and a != b and (b != n or center is not None), 'ADD shape/temp')
                need(a != center, 'copied center must stay immutable')
                norms[a] += abs(coefficient) * norms[b]
                peak = max(peak, norms[a])
            elif (op == 2) != reverse:
                need(center is None and b == n, 'COPY opening')
                center = a
                norms[n] = norms[a]
            else:
                need(center == a and b == n, 'ERASE source binding')
                center = None
                norms[n] = 0
        need(center is None, 'COPY closure')
        peaks.append(peak)
    f, b = peaks
    payload = 64 * f ** 3 * b ** 2
    need(payload < 1 << 104, 'strict 104-bit precision')
    return dict(forward=f, reverse=b, payload=str(payload), payload_bits=payload.bit_length())


def formal_endpoint(raw, n):
    """Set-valued symbolic replay, separate from search's integer matrices."""
    values = [{i} for i in range(n)] + [set()]
    for op, a, b, coefficient in events(raw):
        if op == 1:
            if coefficient & 1:
                values[a].symmetric_difference_update(values[b])
        elif op == 2:
            values[n] = values[a].copy()
        else:
            values[n].clear()
    want = [{r, r - 120} if 120 <= r < 240 else {r} for r in range(n)] + [set()]
    need(values == want, 'complete arbitrary-dirt Boolean endpoint')
    return sha(canonical([sorted(s) for s in values]))


def stage_replay(raw, pairs, skip=None):
    """Literal bridged scalar schedule from DaysSky's PR363 rule, over F2."""
    v, helpers, local = 120, 480, 720
    total = 2 * pairs * v + helpers
    values = [1 << i for i in range(total)] + [0]
    schedule, after = [], [[] for _ in range(2 * pairs + 1)]
    for stage in range(2 * pairs + 1):
        pair = 1 if stage < 3 else (stage + 1) // 2
        reverse = stage % 2 == 1
        x, y = 2 * (pair - 1), 2 * (pair - 1) + 1
        schedule.append((y, x, reverse) if reverse else (x, y, reverse))
    for q in range(2, pairs + 1):
        x0, y0, x1, y1 = 2 * (q - 2), 2 * (q - 2) + 1, 2 * (q - 1), 2 * (q - 1) + 1
        after[2 * q - 3].extend([(x0, x1), (y1, y0)])
        after[2 * q - 2].extend([(y1, y0), (x0, x1)])
    for q in range(pairs, 1, -1):
        after[-1].extend([(2 * (q - 2) + 1, 2 * (q - 1) + 1),
                          (2 * (q - 1), 2 * (q - 2))])
    seq = events(raw)
    bridge = 0
    for stage, (xb, yb, reverse) in enumerate(schedule):
        def mapped(r):
            if r < v:
                return xb * v + r
            if r < 2 * v:
                return yb * v + r - v
            return 2 * pairs * v + r - 2 * v if r < local else total
        for op, a, b, coefficient in (reversed(seq) if reverse else seq):
            if op == 1:
                if coefficient & 1:
                    values[mapped(a)] ^= values[mapped(b)]
            elif (op == 2) != reverse:
                values[total] = values[mapped(a)]
            else:
                values[total] = 0
        if stage == 0:
            expected = [(1 << i) ^ (1 << (i - v)) if v <= i < 2 * v else 1 << i
                        for i in range(total)] + [0]
            need(values == expected, 'stage-zero full boundary')
        for d, s in after[stage]:
            if bridge != skip:
                for i in range(v):
                    values[d * v + i] ^= values[s * v + i]
            bridge += 1
    for bank in range(0, 2 * pairs, 2):
        for i in range(v):
            a, b = bank * v + i, (bank + 1) * v + i
            values[a], values[b] = values[b], values[a]
    need(values == [1 << i for i in range(total)] + [0], 'bridged full-column endpoint')
    return dict(stages=2 * pairs + 1, columns=total, bridges=bridge)


def integer_inverse(gates):
    values = [[int(i == j) for j in range(12)] for i in range(12)]
    index = {r: i for i, r in enumerate(REGS)}
    for reverse in (False, True):
        for _, d, sources in (reversed(gates) if reverse else gates):
            for s in sources:
                sign = -1 if reverse else 1
                values[index[d]] = [a + sign * b for a, b in zip(values[index[d]], values[index[s]])]
    need(values == [[int(i == j) for j in range(12)] for i in range(12)], 'signed integer inverse')


def reject(action, label):
    try:
        action()
    except (Reject, IndexError, KeyError):
        return label
    raise Reject('negative control unexpectedly passed: ' + label)


def verify_pins():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for relative, digest in pins['files'].items():
        need(sha((ROOT / relative).read_bytes()) == digest, 'source pin: ' + relative)
    return pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--replay-search', action='store_true')
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    pins = verify_pins()
    base = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    candidate_bytes = (HERE / 'CANDIDATE.json').read_bytes()
    need(sha(candidate_bytes) == pins['candidate_sha256'], 'candidate digest')
    candidate = json.loads(candidate_bytes)
    gates = candidate['best']['gates']
    need(candidate['frame'] == FRAME and candidate['start'] == START and candidate['stop'] == STOP
         and candidate['registers'] == REGS and candidate['trials'] == 2000, 'search domain')
    need(sum(candidate['histogram'].values()) == 2000, 'search coverage count')
    original = base['A'][START:STOP]
    need(len(original) == 51 and len(gates) == 41, 'expected saving')
    for value in range(1 << 12):
        need(block_map(original, value) == block_map(gates, value), 'exhaustive fixed-output Boolean transfer')
        need(block_map(list(reversed(gates)), block_map(gates, value)) == value, 'Boolean block inverse')
    integer_inverse(gates)
    w = make_word(base, gates)
    dimensions = [rank(w['lines'][i] for i in frame) for frame in w['frames']]
    need(dimensions[FRAME] == 4 and dimensions[0] == 0 and dimensions[1] == 8, 'frame ranks')
    base_raw, base_trails, base_paid, base_copies = records(base, dimensions)
    raw, trails, paid, copies = records(w, dimensions)
    need(base_trails == trails and base_paid == paid and base_copies == copies, 'all paid paths preserved')
    need(paid == {1:1200, 2:1440, 4:180, 6:120, 8:9}, 'historical paid profile')
    need(base['D'] == w['D'] and base['B'] == w['B'], 'D and B unchanged')
    endpoints = [formal_endpoint(data, 720) for data in (base_raw, raw)]
    need(endpoints[0] == endpoints[1], 'baseline/candidate boundary')
    precision = [positive_bounds(data, 720) for data in (base_raw, raw)]
    need((precision[1]['forward'], precision[1]['reverse'], int(precision[1]['payload'])) ==
         (candidate['best']['forward'], candidate['best']['reverse'], candidate['best']['payload']),
         'independent positive invoice vs search')
    counts = [sum(r[0] == 1 for r in data) for data in (base_raw, raw)]
    need(counts == [33958, 33938], 'full ADD invoice including literal cleanup')
    stages = [[stage_replay(data, k) for k in (2, 4, 5)] for data in (base_raw, raw)]
    controls = []
    for j in range(len(gates)):
        omitted = gates[:j] + gates[j+1:]
        controls.append(reject(lambda g=omitted: need(all(block_map(g, 1 << i) ==
                              block_map(original, 1 << i) for i in range(12)), 'omitted gate transfer'),
                               'omit gate %s' % j))
    wrong_frame = copy.deepcopy(w)
    wrong_frame['A'][START][0] = 0
    controls.append(reject(lambda: records(wrong_frame, dimensions), 'bad frame'))
    no_cleanup = copy.deepcopy(w)
    no_cleanup['C'] = base['C']
    formal_endpoint(records(no_cleanup, dimensions, check_cleanup=False)[0], 720)
    controls.append(reject(lambda: records(no_cleanup, dimensions), 'endpoint-valid stale cleanup contract'))
    bad_dirt = copy.deepcopy(w)
    bad_dirt['D'][0][2].pop()
    controls.append(reject(lambda: formal_endpoint(records(bad_dirt, dimensions)[0], 720), 'missing dirt compensation'))
    # Endpoint-valid neutral insertion still fails precision: pairs cancel only over F2.
    inflated = copy.deepcopy(w)
    neutral = [[FRAME, REGS[0], [REGS[1]]]] * 1000
    inflated['A'][START:START] = neutral
    inflated['C'] = [[1, d, list(ss)] for _, d, ss in reversed(inflated['A'] + inflated['B'])
                     if d < 120 or d >= 240]
    inflated_raw = records(inflated, dimensions)[0]
    formal_endpoint(inflated_raw, 720)
    controls.append(reject(lambda: positive_bounds(inflated_raw, 720), 'endpoint-valid precision overflow'))
    for pairs in (2, 4, 5):
        for skip in range(6 * (pairs - 1)):
            controls.append(reject(lambda k=pairs, s=skip: stage_replay(raw, k, s),
                                   'omit bridge %s/%s' % (pairs, skip)))
    out = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='qnode5-'))
    need(out != HERE and HERE not in out.parents, 'output must be outside package')
    out.mkdir(parents=True, exist_ok=True)
    word_path = out / 'candidate-word.json.gz'
    word_path.write_bytes(gzip.compress(canonical(w), mtime=0))
    # Pinned inherited checkers execute unchanged. Finite checks, not a full theorem proof.
    commands = [
        [ROOT / 'research/e8-bit-p111-tuned/code/xcheck_p.py', word_path, '--json', out / 'interface.json'],
        [ROOT / 'research/e8-bit-carrier-skeleton/code/bit/independent/interface.py', word_path],
        [ROOT / 'research/e8-bit-carrier-skeleton/code/bit/export_records.py', word_path, out / 'export'],
    ]
    for j, command in enumerate(commands):
        process = subprocess.run([sys.executable, '-I', '-B', *map(str, command)], capture_output=True, text=True)
        (out / ('inherited-check-%s.log' % j)).write_text(process.stdout + process.stderr, encoding='utf-8')
        need(process.returncode == 0, 'inherited checker %s: %s' % (j, process.stderr[-1000:]))
    expected_binary = b''.join(struct.pack('<6i', *row) for row in raw)
    need((out / 'export/249-records.bin').read_bytes() == expected_binary, 'unchanged exporter exact records')
    iface = json.loads((out / 'interface.json').read_text())
    need(iface['status'] == 'PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE' and
         all(iface['hypotheses'].values()) and all(iface['conclusion'].values()), 'inherited H1-H5')
    if args.replay_search:
        # A subprocess isolates the generator from this independent implementation.
        with tempfile.TemporaryDirectory(prefix='qnode5-search-') as scratch:
            search_result = Path(scratch) / 'CANDIDATE.json'
            process = subprocess.run([sys.executable, '-I', '-B', HERE / 'search.py', '--output', search_result],
                                     capture_output=True, text=True)
            need(process.returncode == 0, 'bounded search replay')
            need(search_result.read_bytes() == candidate_bytes, 'deterministic search replay')
    report = dict(format='r480-qnode5-finite-certificate-v1', base=pins['base'],
                  assignment_seed=5, block_gates=[51, 41], complete_adds=counts,
                  word_content_sha256=sha(canonical(w)), endpoint_sha256=endpoints[1],
                  raw_records_sha256=sha(expected_binary), paid_profile={str(k): v for k, v in paid.items()},
                  rank_mass=sum(k * v for k, v in paid.items()), copy_ranks=copies,
                  all_register_frame_paths_preserved=len(trails), Boolean_inputs=4096,
                  full_dirty_columns=720, precision=precision, stage_replays=stages,
                  rejected_controls=controls, no_new_kappa=True)
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.write_certificate:
        (HERE / 'CERTIFICATE.json').write_text(encoded, encoding='utf-8', newline='\n')
    else:
        need(json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8')) == report, 'certificate drift')
    (out / 'REPORT.json').write_text(encoded, encoding='utf-8', newline='\n')
    print('PASS_R480_QNODE5_SEED05 gates=51->41 ADDs=33958->33938 columns=720 '
          'payload_bits=102 controls=%s rank_mass=5592 no_new_kappa' % len(controls))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        print('REJECT', error, file=sys.stderr)
        raise SystemExit(1)
