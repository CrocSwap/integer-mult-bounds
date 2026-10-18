#!/usr/bin/env python3
"""Finite circuit + independent lower-bound certificate replay; stdlib only.
Yuzhou Wang / yzhouwang, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True  # Do not add caches to immutable supplier inventories.

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 12
WORD = 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
XCHECK = 'research/e8-bit-r420/code/xcheck.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'


class Reject(Exception):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source_check():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected in pins['files'].items():
        need(digest((ROOT / path).read_bytes()) == expected, 'source hash: ' + path)
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    need(selected['reviewed_dependency_heads']['543'] == pins['pr543_head'], 'selected supplier binding')
    need(selected['audited_source_head'] == pins['pr626_head'], 'selected construction binding')
    return pins


def integer_columns(ops):
    """Column-vector implementation, independent of nomination's row updates."""
    columns = []
    for j in range(N):
        col = [int(i == j) for i in range(N)]
        for d, s in ops:
            need(0 <= d < N and 0 <= s < N and d != s, 'bad local gate')
            col[d] += col[s]
        columns.append(col)
    return columns


def factor_audit(original, cert):
    columns = integer_columns(original)
    m = list(map(list, zip(*columns)))
    need(all(x in (0, 1) for row in m for x in row), 'binary factor')
    need(all(m[i][i] == 1 for i in range(N)), 'diagonal factor')
    rows = [sum(x << j for j, x in enumerate(row)) for row in m]
    need(cert['rows'] == rows and cert['original_gates'] == len(original), 'factor binding')
    p = cert['potentials']
    need(len(p) == 1 << N and all(type(x) is int and x >= 0 for x in p) and p[0] == 0, 'potential admission')
    # A different oracle from nomination: enumerate donor subsets as base-16
    # integers, using ordinary addition. At most 11 binary vectors are summed,
    # so no digit carries can conceal repeated or missing coordinates.
    encode = lambda mask: sum(((mask >> j) & 1) << (4 * j) for j in range(N))
    packed = [encode(row) for row in rows]
    feasible = 0
    covers = 0
    transitions = 0
    for state in range(1 << N):
        for d in range(N):
            if state >> d & 1:
                continue
            transitions += 1
            wanted_mask = rows[d] ^ (1 << d)
            wanted = encode(wanted_mask)
            available = []
            for s in range(N):
                if s == d:
                    continue
                mask = rows[s] if state >> s & 1 else 1 << s
                if mask & ~wanted_mask == 0:
                    available.append(packed[s] if state >> s & 1 else 1 << (4 * s))
            sums = [0]
            counts = [0]
            for value in available:
                sums += [x + value for x in sums]
                counts += [x + 1 for x in counts]
            found = False
            for total, count in zip(sums, counts):
                if total == wanted:
                    covers += 1
                    found = True
                    need(p[state | (1 << d)] <= p[state] + count, 'Bellman lower bound')
            feasible += int(found)
    need(feasible == cert['feasible_state_destination_pairs'], 'transition coverage')
    need(len(cert['batches']) == N, 'batch count')
    state = 0
    witness = []
    for d, ss in cert['batches']:
        need(type(d) is int and 0 <= d < N and not (state >> d & 1), 'destination once')
        need(all(type(s) is int and 0 <= s < N and s != d for s in ss) and len(set(ss)) == len(ss), 'donor admission')
        total = 1 << (4 * d)
        for s in ss:
            total += packed[s] if state >> s & 1 else 1 << (4 * s)
        need(total == packed[d], 'batch exact integer sum')
        witness += [(d, s) for s in ss]
        state |= 1 << d
    need(len(witness) == p[-1] == cert['minimum'], 'optimal witness length')
    need(integer_columns(witness) == columns, 'factor integer map')
    return witness, {'states': 1 << N, 'state_destination_pairs': transitions,
                     'feasible_pairs': feasible, 'valid_donor_subsets': covers,
                     'old': len(original), 'new': len(witness)}


def local_check(original, replacement):
    need(integer_columns(original) == integer_columns(replacement), 'local integer map')
    old_rev = integer_columns(list(reversed(original)))
    new_rev = integer_columns(list(reversed(replacement)))
    need(all(b <= a for aa, bb in zip(old_rev, new_rev) for a, b in zip(aa, bb)), 'reverse positive envelope')
    for value in range(1 << N):
        a = [(value >> i) & 1 for i in range(N)]
        b = a[:]
        for d, s in original:
            a[d] ^= a[s]
        for d, s in replacement:
            b[d] ^= b[s]
        need(a == b, 'local truth table')
    return {'boolean_inputs': 1 << N, 'integer_columns_each_orientation': N,
            'reverse_strictly_smaller_entries': sum(b < a for aa, bb in zip(old_rev, new_rev) for a, b in zip(aa, bb))}


def scalar(word):
    """Independent set-valued interpretation including arbitrary helper dirt."""
    n = 2 * word['v'] + word['R']
    values = [{r} for r in range(n)]
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            saved = [values[r].copy() for r in word['ret']]
            for t, row in enumerate(word['scatter']):
                for k in row:
                    values[word['v'] + t] ^= saved[k]
        else:
            for _, d, ss in word[section]:
                for s in ss:
                    values[d] ^= values[s]
    for r, value in enumerate(values):
        expected = {r}
        if word['v'] <= r < 2 * word['v']:
            expected.add(r - word['v'])
        need(value == expected, 'dirty-column endpoint')
    return n


def paths(word):
    current = list(word['start'])
    result = [[f] for f in current]
    frames = list(map(set, word['frames']))
    def move(r, f):
        if current[r] != f:
            need(frames[current[r]] < frames[f], 'frame descent')
            result[r].append(f)
            current[r] = f
    for section in ('D', 'A', 'B', 'C'):
        for f, d, ss in word[section]:
            for r in [d] + ss:
                move(r, f)
    for r, f in enumerate(word['final']):
        move(r, f)
    return result


def literal(word):
    need(word['C'] == [[1, d, ss] for sec in ('B', 'A') for _, d, ss in reversed(word[sec])
                       if not word['v'] <= d < 2 * word['v']], 'literal cleanup')


def prefix(records, reverse=False):
    norms = [1] * 661
    maximum = 1
    opened = False
    for op, a, b, c, f, ph in (reversed(records) if reverse else records):
        if op == 1:
            norms[a] += abs(c) * norms[b]
            maximum = max(maximum, norms[a])
        elif op in (2, 3):
            if (op == 2) != reverse:
                need(not opened, 'copy nesting')
                norms[b] = norms[a]
                opened = True
            else:
                need(opened, 'copy close')
                norms[b] = 0
                opened = False
    need(not opened, 'copy lifecycle')
    return maximum


def export(word, out):
    path = out / 'word.json'
    path.write_bytes(canonical(word))
    subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORTER), str(path), str(out / 'records')],
                   check=True, stdout=subprocess.DEVNULL)
    raw = (out / 'records/249-records.bin').read_bytes()
    records = list(struct.iter_unpack('<6i', raw))
    counts = Counter(r[0] for r in records)
    hist = Counter(r[4] for r in records if r[0] == 0)
    hist.update(r[5] for r in records if r[0] == 2)
    # Record MOVE/COPY ranks, not scalar gate fan-in, determine this bill.
    forward, backward = prefix(records), prefix(records, True)
    payload = 64 * forward**3 * backward**2
    return records, {'records': len(records), 'adds': counts[1], 'copies': counts[2], 'erasures': counts[3],
                     'paid_histogram': {str(k): v for k, v in sorted(hist.items())},
                     'rank_mass': sum(k * v for k, v in hist.items()),
                     'forward_prefix': forward, 'reverse_prefix': backward,
                     'payload_bits': payload.bit_length(), 'payload': str(payload)}


def rejected(label, fn, message):
    try:
        fn()
    except Reject as exc:
        need(message in str(exc), 'wrong rejection for ' + label + ': ' + str(exc))
        return label
    raise Reject('negative control accepted: ' + label)


def run(out):
    source_check()
    old = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    need({k: cert[k] for k in ('schema', 'seed', 'block', 'frame', 'slice', 'split')} ==
         dict(schema=1, seed=17, block=7, frame=549, slice=[471, 512], split=17), 'object binding')
    block = old['B'][471:512]
    regs = sorted({r for _, d, ss in block for r in [d] + ss})
    need(cert['registers'] == regs and len(regs) == N and all(f == 549 and len(ss) == 1 for f, _, ss in block), 'register binding')
    ix = {r: i for i, r in enumerate(regs)}
    original = [(ix[d], ix[ss[0]]) for _, d, ss in block]
    first, a = factor_audit(original[:17], cert['factors'][0])
    second, b = factor_audit(original[17:], cert['factors'][1])
    replacement = first + second
    local = local_check(original, replacement)
    new = copy.deepcopy(old)
    new['B'][471:512] = [[549, regs[d], [regs[s]]] for d, s in replacement]
    new['C'] = [[1, d, ss] for sec in ('B', 'A') for _, d, ss in reversed(new[sec]) if not 120 <= d < 240]
    need(all(new[k] == old[k] for k in old if k not in ('B', 'C')), 'unrelated word edit')
    for word in (old, new):
        literal(word)
        scalar(word)
    need(paths(old) == paths(new), 'per-register frame paths')
    spec = importlib.util.spec_from_file_location('pr543_xcheck', ROOT / XCHECK)
    xc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xc)
    audit = xc.Word(old)
    labels = audit.labels()
    for word in (old, new):
        audit.w = word  # Geometry unchanged and hash-pinned; retain exact rational geometry.
        audit.full()
        h, c, _ = audit.interface()
        need(all(h.values()) and all(c.values()), 'predecessor interface')
    receipts = []
    for name, word in (('original', old), ('replacement', new)):
        directory = out / name
        directory.mkdir()
        records, receipt = export(word, directory)
        receipts.append(receipt)
        need(receipt['rank_mass'] == 5112 and receipt['copies'] == receipt['erasures'] == 9, 'paid profile')
        need(int(receipt['payload']) < 2**104, 'payload cap')
    need(receipts[0]['adds'] - receipts[1]['adds'] == 2 * (len(original) - len(replacement)), 'complete scalar bill')
    need(receipts[0]['paid_histogram'] == receipts[1]['paid_histogram'], 'paid histogram changed')
    controls = []
    controls.append(rejected('omitted local XOR', lambda: local_check(original, replacement[:-1]), 'local integer map'))
    controls.append(rejected('F2-neutral positive inflation', lambda: local_check(original, replacement + [(0, 1), (0, 1)]), 'local integer map'))
    mutant = copy.deepcopy(new); mutant['C'].pop()
    controls.append(rejected('omitted cleanup', lambda: scalar(mutant), 'dirty-column endpoint'))
    mutant = copy.deepcopy(new); mutant['C'] = old['C']
    scalar(mutant)  # Same F2 inverse, but intentionally outside literal-H4 contract.
    controls.append(rejected('stale scalar-valid cleanup', lambda: literal(mutant), 'literal cleanup'))
    mutant = copy.deepcopy(new); mutant['D'].pop()
    controls.append(rejected('omitted dirty compensation', lambda: scalar(mutant), 'dirty-column endpoint'))
    mutant = copy.deepcopy(new); mutant['B'][471][0] = 0
    controls.append(rejected('illegal frame descent', lambda: paths(mutant), 'frame descent'))
    bad = copy.deepcopy(cert['factors'][0]); bad['potentials'][-1] += 1
    controls.append(rejected('inflated lower-bound certificate', lambda: factor_audit(original[:17], bad), 'Bellman lower bound'))
    bad = copy.deepcopy(cert['factors'][0]); bad['batches'][0][1] = []
    controls.append(rejected('unpaid witness gate', lambda: factor_audit(original[:17], bad), 'batch exact integer sum'))
    receipt = {'status': 'PASS_R420_BLOCK7_EXACT_SCHEDULE', 'factor_audits': [a, b], 'local': local,
               'native': receipts, 'columns': 660, 'labels': labels, 'controls': controls,
               'word_sha256': [digest(canonical(old)), digest(canonical(new))], 'kappa': 'unchanged'}
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    need(receipt == expected, 'expected receipt mismatch')
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print('PASS_R420_BLOCK7_EXACT_SCHEDULE factors=17+24->14+14 ADDs=26916->26890 states=8192 columns=660 controls=8 kappa=unchanged')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='new directory for both words, native records and receipt')
    args = parser.parse_args()
    try:
        if args.out:
            # Never overwrite an existing path or place artifacts inside this package.
            destination = args.out.resolve()
            need(destination != HERE and HERE not in destination.parents, 'output inside package')
            destination.mkdir(parents=True, exist_ok=False)
            run(destination)
        else:
            with tempfile.TemporaryDirectory(prefix='r420-block7-') as tmp:
                run(Path(tmp))
    except (Reject, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print('REJECT_R420_BLOCK7_EXACT_SCHEDULE:', exc, file=sys.stderr)
        sys.exit(1)
