"""An exact carrier-copy elision, produced by Nick Petalas. Apache-2.0.

The input word and scalar tariff belong to PR6621 and its credited lineage.
This compares a new construction with that input; it does not audit its result.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from io import BytesIO
from pathlib import Path
import argparse
import gzip
import json
import platform
import tarfile

HERE = Path(__file__).resolve().parent
WORD_HASH = '25b350a56ce11436fccf4c987da466cb002fa28dfc9b7e9d88e8b1b748b79df3'
ARCHIVE_HASH = 'd04afb7cc96d0104dbf3a8142e1347ebfe240eba581210eca7ad877227078bd0'
N = 799
STATUS = 'PASS_OWNED_CARRIER_COPY_ELISION'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_word():
    path = HERE / 'WORD.json.gz'
    need(path.stat().st_size == 91086, 'Bounded retained source size')
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == WORD_HASH, 'Exact retained source word')
    with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
        decoded = stream.read(3 * 1024 * 1024 + 1)
    need(len(decoded) <= 3 * 1024 * 1024, 'Bounded decoded word')
    word = json.loads(decoded)
    need(word['public'] == 770 and word['owned_fields'] == 29, 'Fixed role domain')
    need(len(word['program']) == 18561, 'Fixed event domain')
    return word


def authenticate_archive(path):
    """Optional original-byte comparison; no extraction or predecessor execution."""
    need(path.stat().st_size == 5928960, 'Original archive size')
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == ARCHIVE_HASH, 'Original archive SHA256')
    source = json.loads((HERE / 'SOURCE.json').read_text())
    blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == source['archive_git_blob'], 'Original archive Git blob')
    need(len(source['chain']) == 2, 'Two source archive levels')
    for item in source['chain']:
        with tarfile.open(fileobj=BytesIO(raw), mode='r:') as archive:
            members = archive.getmembers()
            need(len(members) <= 100, 'Bounded archive inventory')
            matches = [m for m in members if m.name == item['member']]
            need(len(matches) == 1 and matches[0].isfile(), 'Unique source member')
            stream = archive.extractfile(matches[0])
            need(stream is not None, 'Readable source member')
            with stream:
                raw = stream.read(6 * 1024 * 1024 + 1)
        need(len(raw) == item['bytes'], 'Exact member size')
        need(sha256(raw).hexdigest() == item['sha256'], 'Exact member hash')
    need(raw == (HERE / 'WORD.json.gz').read_bytes(), 'Original retained bytes')


def transform(word):
    expected = {
        9045: ['INIT', 774, 394],
        9053: ['ADD', 774, 785, '1', 394],
        9054: ['SCALE', 774, '1/4', 394],
        9056: ['ADD', 786, 774, '1', 394],
        9058: ['ADD', 713, 774, '1', 394],
        9067: ['CLEAR', 774, 394],
    }
    uses = []
    for index in range(9045, 9068):
        event = word['program'][index]
        if event[1] == 774 or (event[0] in ('ADD', 'COPY') and event[2] == 774):
            uses.append(index)
        if index > 9052 and event[1] == 785:
            need(event[0] == 'MOVE', 'Retained carrier is not overwritten')
    need(uses == list(expected), 'Every use of the elided lifetime')
    need(all(word['program'][index] == event for index, event in expected.items()),
         'Exact source pattern')
    omitted = {9045, 9053, 9054, 9067}
    program = []
    for index, event in enumerate(word['program']):
        if index in omitted:
            continue
        if index in (9056, 9058):
            event = ['ADD', event[1], 785, '1/4', 394]
        program.append(event.copy())
    candidate = dict(word, program=program)
    need(len(program) == 18557, 'Exactly four events removed')
    return candidate


def add(row, source, coefficient):
    for column, value in tuple(source.items()):
        value = row.get(column, Q(0)) + coefficient * value
        if value:
            row[column] = value
        else:
            row.pop(column, None)


def scalar_cost(event):
    if event[0] in ('INIT', 'CLEAR'):
        return 2
    coefficient = Q(event[-2])
    n, d = abs(coefficient.numerator), coefficient.denominator
    need(n > 0 and d & (d - 1) == 0, 'Nonzero dyadic coefficient')
    if event[0] == 'SCALE':
        need(n & (n - 1) == 0, 'Dyadic unit scale')
        return 2 * (abs(n.bit_length() - d.bit_length()) + int(coefficient < 0))
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def scalar_step(rows, current, active, event):
    op, role = event[:2]
    if op in ('INIT', 'CLEAR'):
        need(role >= 770, 'Owned lifecycle role')
        if op == 'INIT':
            need(role not in active, 'Fresh owned initialization')
            active.add(role)
            current[role] = event[2]
        else:
            need(role in active and current[role] == event[2], 'Owned erasure frame')
            active.remove(role)
            current[role] = None
        rows[role] = {}
        return
    need(current[role] == event[-1], 'Scalar destination frame')
    coefficient = Q(event[-2])
    if op == 'SCALE':
        rows[role] = {k: coefficient * v for k, v in rows[role].items()}
        return
    need(op in ('ADD', 'COPY') and current[event[2]] == event[-1],
         'Scalar source frame')
    if op == 'COPY':
        need(role in active and not rows[role], 'COPY into cleared owned storage')
    add(rows[role], rows[event[2]], coefficient)


def sparse(word):
    rows = [{role: Q(1)} for role in range(N)]
    current = word['initial'] + [None] * 29
    active, paid = set(), Counter()
    scalar, lifetimes, peak = 0, 0, 0
    for event in word['program']:
        op, role = event[:2]
        if op == 'MOVE':
            need(current[role] == event[2] and (role in active) == event[4],
                 'Transport frame and ownership')
            rank = abs(len(word['frames'][event[2]]) - len(word['frames'][event[3]]))
            paid[rank] += 1
            current[role] = event[3]
        else:
            scalar_step(rows, current, active, event)
            scalar += scalar_cost(event)
            lifetimes += int(op == 'INIT')
            peak = max(peak, len(active))
    need(not active and current == word['final'] + [None] * 29, 'Complete exits')
    return rows, {'events': len(word['program']), 'scalar_allowance': scalar,
                  'owned_lifetimes': lifetimes, 'peak_owned': peak, 'paid': dict(paid)}


def modular(word):
    """Separate dense all-column interpreter over Z/65537Z."""
    modulus = 65537
    matrix = [[int(i == j) for j in range(N)] for i in range(N)]
    coefficients = {}
    for event in word['program']:
        op, destination = event[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            matrix[destination] = [0] * N
            continue
        literal = event[-2]
        if literal not in coefficients:
            parts = literal.split('/')
            numerator = int(parts[0])
            denominator = int(parts[1]) if len(parts) == 2 else 1
            coefficients[literal] = numerator * pow(denominator, -1, modulus) % modulus
        q = coefficients[literal]
        if op == 'SCALE':
            matrix[destination] = [q * x % modulus for x in matrix[destination]]
        elif op == 'COPY':
            matrix[destination] = [q * x % modulus for x in matrix[event[2]]]
        else:
            need(op == 'ADD', 'Independent modular opcode')
            matrix[destination] = [(x + q * y) % modulus
                                   for x, y in zip(matrix[destination], matrix[event[2]])]
    return matrix


def equal_coefficients(first, second):
    checked = 0
    for left, right in zip(first, second):
        for column in range(N):
            need(left.get(column, 0) == right.get(column, 0), 'Exact rational equivalence')
            checked += 1
    need(checked == N * N, 'Complete rational coefficient domain')
    return checked


def controls(source_rows, candidate):
    rejected = []
    for receiver in (713, 786):
        program = [event.copy() for event in candidate['program']]
        positions = [i for i, event in enumerate(program)
                     if event == ['ADD', receiver, 785, '1/4', 394]]
        need(len(positions) == 1, 'Unique changed consumer')
        for kind in ('wrong_scale', 'wrong_frame', 'missing_read'):
            bad = [event.copy() for event in program]
            if kind == 'wrong_scale':
                bad[positions[0]][3] = '1'
            elif kind == 'wrong_frame':
                bad[positions[0]][-1] = 240
            else:
                del bad[positions[0]]
            try:
                rows, _ = sparse(dict(candidate, program=bad))
                equal_coefficients(source_rows, rows)
            except ValueError:
                rejected.append(str(receiver) + '_' + kind)
            else:
                raise ValueError('Invalid construction accepted')
    need(len(rejected) == 6, 'Every semantic control rejected')
    return rejected


def run():
    source = read_word()
    candidate = transform(source)
    need({k: v for k, v in source.items() if k != 'program'} ==
         {k: v for k, v in candidate.items() if k != 'program'}, 'Identical boundary data')
    old_moves = [event for event in source['program'] if event[0] == 'MOVE']
    new_moves = [event for event in candidate['program'] if event[0] == 'MOVE']
    need(old_moves == new_moves, 'Identical ordered native jobs, frames and ownership')
    old_rows, before = sparse(source)
    new_rows, after = sparse(candidate)
    positions = equal_coefficients(old_rows, new_rows)
    need(before['scalar_allowance'] == 137866 and after['scalar_allowance'] == 137858,
         'Exact scalar allowance improvement')
    need(before['owned_lifetimes'] == 46 and after['owned_lifetimes'] == 45,
         'One owned lifetime removed')
    need(before['paid'] == after['paid'] and before['peak_owned'] == after['peak_owned'],
         'Unchanged paid histogram and peak allocation')
    first, second = modular(source), modular(candidate)
    count = 0
    for left, right in zip(first, second):
        for x, y in zip(left, right):
            need(x == y, 'Independent modular coefficient agreement')
            count += 1
    need(count == N * N, 'Complete modular column domain')
    rejections = controls(old_rows, candidate)
    files = ('verify.py', 'WORD.json.gz', 'SOURCE.json', 'SOURCES.json',
             'TASK.json', 'VERIFY.json', 'README.md', 'PROOF.md', 'NOTICE', 'SOURCE-NOTICE')
    return {'status': STATUS, 'python': platform.python_version(),
            'before': before, 'after': after, 'scalar_units_saved': 8,
            'rational_coefficient_comparisons': positions,
            'modular_coefficient_comparisons': count, 'semantic_rejections': rejections,
            'candidate_program_sha256': sha256(json.dumps(candidate['program'],
                separators=(',', ':')).encode()).hexdigest(),
            'file_sha256': {name: sha256((HERE / name).read_bytes()).hexdigest()
                            for name in files},
            'claim_type': 'scoped scalar-program construction with finite exact equivalence',
            'selected_frontier_changed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-archive', type=Path)
    args = parser.parse_args()
    if args.source_archive is not None:
        authenticate_archive(args.source_archive)
    print(json.dumps(run(), indent=2, sort_keys=True))
