"""Check the exact native lift and the finite local bill.

The checker does not import the emitter or the Clifford compiler. It uses
Pauli conjugation and a separate exact state interpreter. The scalar map is
owned by the independent transpose replay in the adjacent review lane.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import resource
import subprocess
import tarfile
import time

BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_HASH = '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'
PINS = {
    'CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
    'CLIFFORD-RECIPES.json': 'd0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731',
    'RESIDUAL-ADAPTERS.json': '383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c',
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def load(repo):
    args = ['git', 'show', BASE + ':' + ARCHIVE]
    proc = subprocess.Popen(args, cwd=repo, stdout=subprocess.PIPE)
    digest = sha256()
    while chunk := proc.stdout.read(65536):
        digest.update(chunk)
    require(proc.wait() == 0 and digest.hexdigest() == ARCHIVE_HASH, 'archive pin')
    proc = subprocess.Popen(args, cwd=repo, stdout=subprocess.PIPE)
    values = {}
    with tarfile.open(fileobj=proc.stdout, mode='r|gz') as archive:
        for entry in archive:
            name = entry.name.removeprefix('slots/local/')
            if entry.name.startswith('slots/local/') and name in PINS:
                raw = archive.extractfile(entry).read()
                require(sha256(raw).hexdigest() == PINS[name], name + ' pin')
                values[name] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    require(proc.wait() == 0 and set(values) == set(PINS), 'source extraction')
    return values


def parity(value):
    return value.bit_count() % 2


def mul(matrix, vector):
    return sum(parity(row & vector) << i for i, row in enumerate(matrix))


def transpose(matrix):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(matrix)) for j in range(len(matrix)))


def inverse(matrix):
    n = len(matrix)
    rows = [row | (1 << (n+i)) for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        require(pivot is not None, 'singular binary chart')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    require([row & ((1 << n)-1) for row in rows] == [1 << i for i in range(n)], 'binary inverse')
    return tuple(row >> n for row in rows)


def extend(vectors, n):
    columns, pivots = [], {}
    for value in tuple(vectors) + tuple(1 << i for i in range(n)):
        reduced = value
        while reduced:
            j = reduced.bit_length()-1
            if j not in pivots:
                pivots[j] = reduced
                columns.append(value)
                break
            reduced ^= pivots[j]
    require(len(columns) == n, 'frame basis extension')
    return tuple(columns)


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        if gate[0] == 'P':
            out.append(('P', inverse(gate[1])))
        elif gate[0] == 'D':
            out.append(('D', gate[1], tuple(-a % 4 for a in gate[2])))
        elif gate[0] == 'C':
            out.append(('C', gate[1], -gate[2]))
        elif gate[0] == 'phase':
            out.append(('phase', -gate[1] % 4))
        else:
            require(gate[0] == 'X', 'adjoint gate type')
            out.append(gate)
    return tuple(out)


def fourier(rank):
    return tuple(('C', 1 << i, 1) for i in range(rank))


def frame(vectors, n):
    rank = len(vectors)
    if rank == 0:
        return ()
    if rank == n:
        return fourier(n)
    matrix = transpose(extend(vectors, n))
    columns = transpose(inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(columns)) for i, a in enumerate(columns))
    diagonal = tuple((row >> i) & 1 for i, row in enumerate(quadratic))
    chart = (('P', matrix), ('D', quadratic, diagonal))
    return adjoint(chart) + fourier(rank) + chart


def monomial(record):
    matrix = tuple(record['matrix_rows'])
    quadratic = tuple(record['quadratic_rows'])
    linear = tuple(record['linear_Z4'])
    require(transpose(quadratic) == quadratic, 'quadratic symmetry')
    require(len(matrix) == len(quadratic) == len(linear) == 9, 'monomial dimension')
    require(all(a % 2 == (quadratic[i] >> i) & 1 for i, a in enumerate(linear)), 'diagonal parity')
    inverse(matrix)
    return (('D', quadratic, linear), ('P', matrix), ('X', record['offset']), ('phase', record['phase']))


def recipe(record):
    rank = record['rank']
    require(isinstance(rank, int) and 0 <= rank <= 9, 'child rank')
    if rank == 0:
        require(record['right'] is None, 'rank zero right factor')
        return monomial(record['left'])
    return monomial(record['right']) + fourier(rank) + monomial(record['left'])


def tableau(circuit, n=9):
    rows = [(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)]
    for gate in circuit:
        tag = gate[0]
        out = []
        inverse_transpose = transpose(inverse(gate[1])) if tag == 'P' else None
        for x, z, phase in rows:
            if tag == 'P':
                x, z = mul(gate[1], x), mul(inverse_transpose, z)
            elif tag == 'X':
                phase += 2 * parity(z & gate[1])
            elif tag == 'C':
                if parity(z & gate[1]):
                    x ^= gate[1]
                    phase += 3 * gate[2]
            elif tag == 'D':
                quadratic, linear = gate[1:]
                phase += sum(linear[i] for i in range(n) if x >> i & 1)
                phase += 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(n) if x >> i & 1)
                z ^= mul(quadratic, x)
            else:
                require(tag == 'phase', 'tableau gate type')
            out.append((x, z, phase % 4))
        rows = out
    return tuple(rows)


@lru_cache(maxsize=512)
def action(gate):
    if gate[0] == 'P':
        return tuple(mul(gate[1], x) for x in range(512))
    require(gate[0] == 'D', 'state action type')
    quadratic, linear = gate[1:]
    return tuple((sum(linear[i] for i in range(9) if x >> i & 1)
                  + 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(9) if x >> i & 1)) % 4 for x in range(512))


def rotate(pair, power):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def state(circuit, basis=0):
    value = [(0, 0)] * 512
    value[basis] = (1, 0)
    denominator = 0
    for gate in circuit:
        tag = gate[0]
        if tag == 'P':
            moved = [(0, 0)] * 512
            for source, target in enumerate(action(gate)):
                moved[target] = value[source]
            value = moved
        elif tag == 'X':
            value = [value[x ^ gate[1]] for x in range(512)]
        elif tag == 'D':
            value = [rotate(pair, p) for pair, p in zip(value, action(gate))]
        elif tag == 'phase':
            value = [rotate(pair, gate[1]) for pair in value]
        elif tag == 'C':
            direction, sign = gate[1:]
            moved = []
            for x, (a, b) in enumerate(value):
                c, d = value[x ^ direction]
                moved.append((a-sign*b+c+sign*d, b+sign*a+d-sign*c))
            value = moved
            denominator += 1
        else:
            raise ValueError('state gate type')
        while denominator and all((a | b) % 2 == 0 for a, b in value):
            value = [(a//2, b//2) for a, b in value]
            denominator -= 1
    return value, denominator


def equal(actual, expected, label):
    require(tableau(actual) == tableau(expected), label + ': Pauli action')
    require(state(actual) == state(expected), label + ': global phase')


def scalar_cost(gate):
    if gate[0] in ('copy', 'clear'):
        return 1
    value = Fraction(*gate[-2:])
    numerator, denominator = abs(value.numerator), value.denominator
    require(numerator > 0 and denominator & (denominator-1) == 0, 'nonzero dyadic scalar')
    if gate[0] == 'scale':
        require(numerator & (numerator-1) == 0, 'dyadic scale unit')
        return abs(numerator.bit_length()-denominator.bit_length()) + (value < 0)
    require(gate[0] == 'add', 'scalar type')
    return 3 + numerator.bit_length()-1 + numerator.bit_count() + denominator.bit_length()-1


def main(args):
    start = time.monotonic()
    data = load(args.repo)
    word = data['CANONICAL-WORD.json.gz']
    old = data['LOCAL-PROGRAMS.json.gz']
    phase = data['CLIFFORD-RECIPES.json']
    residual = data['RESIDUAL-ADAPTERS.json']['recipes']
    changed_raw = gzip.decompress(args.changed.read_bytes())
    require(sha256(changed_raw).hexdigest() == 'fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877', 'changed payload pin')
    changed = json.loads(changed_raw)
    require(set(changed) == {'forward', 'backward'}, 'orientation inventory')
    native = lambda events: [e for e in events if e[0] in ('climb', 'adapter', 'residual_adapter')]
    invoices = {}
    for name, events in changed.items():
        require(native(events) == native(old[name]), 'persistent native stream')
        require(all(e[0] in ('scalar', 'phase', 'climb', 'adapter', 'residual_adapter') for e in events), 'event grammar')
        first = events.index(['phase', 'centre_dirty_correction'])
        last = events.index(['phase', 'A'])
        prefix = [e[1] for e in events[first+1:last]]
        require(all(e[0] == 'scalar' and e[2] == 0 for e in events[first+1:last]), 'correction frame')
        scalars = [e[1] for e in events if e[0] == 'scalar']
        paid = Counter(e[5] for e in events if e[0] == 'climb')
        invoices[name] = {
            'events': len(events), 'scalar_macros': len(scalars),
            'real_component_primitive_bound': 2*sum(map(scalar_cost, scalars)),
            'prefix_macros': dict(Counter(e[0] for e in prefix)),
            'prefix_real_component_primitive_bound': 2*sum(map(scalar_cost, prefix)),
            'paid_profile': dict(sorted(paid.items())),
            'paid_rank_sum': sum(rank*count for rank, count in paid.items()),
            'persistent_native_events': len(native(events)),
        }
    used = {(e[3], e[4]) for e in changed['forward'] if e[0] == 'climb'}
    children = {(r['old'], r['new']): r for r in phase['children']}
    require(len(children) == len(phase['children']) and used <= set(children), 'child recipe binding')
    frames = [frame(tuple(vectors), 9) for vectors in word['frames']]
    for i, (a, b) in enumerate(sorted(used)):
        record = children[a, b]
        require(record['rank'] == len(word['frames'][b])-len(word['frames'][a]), 'paid frame difference')
        equal(recipe(record), adjoint(frames[a])+frames[b], 'child '+str((a, b)))
        if i % 500 == 0:
            print('phase edges', i, '/', len(used), flush=True)
    endpoints = {(r['role'], r['port']): r for r in phase['endpoint_adapters']}
    require(set(endpoints) == {(role, p) for role in ('source', 'target') for p in range(112)}, 'endpoint coverage')
    for (role, port), record in endpoints.items():
        q = word['ports'][port]
        conventional = (('C', q, 1),) if role == 'source' else (('C', q, -1),)+fourier(9)
        expected_frame = word['start'][port] if role == 'source' else word['final'][112+port]
        require(record['frame'] == expected_frame and record['rank'] == 0, 'endpoint frame binding')
        equal(recipe(record), adjoint(conventional)+frames[expected_frame], 'endpoint '+str((role, port)))
    used_residual = set()
    for event in changed['forward']:
        if event[0] == 'residual_adapter':
            _, position, register, entry, *tail = event
            terminal = tail[0] if tail else 1
            key = str(entry) if terminal == 1 else str(entry)+':'+str(terminal)
            require(key in residual and position in ('pre', 'post'), 'residual binding')
            require(entry == word['start'][register] and terminal == word['final'][register], 'residual boundary')
            used_residual.add(key)
    for key in sorted(used_residual):
        record = residual[key]
        entry = record['frame']
        terminal = record.get('terminal', 1)
        equal(recipe(record), adjoint(frames[entry])+frames[terminal], 'residual '+key)
    probe = next(r for r in children.values() if r['left']['phase'] != 0 or r['right'] and r['right']['phase'] != 0)
    correct = recipe(probe)
    corrupt = tuple(gate for gate in correct if gate[0] != 'phase')
    if state(corrupt) == state(correct):
        corrupt = correct+(('phase', 1),)
    require(tableau(corrupt) == tableau(correct) and state(corrupt) != state(correct), 'global phase negative control')
    require(state(corrupt, 1) != state(correct, 1), 'phase control second input')
    report = {
        'status': 'PASS_INDEPENDENT_NATIVE_FRAME_LIFT_AND_FINITE_LOCAL_BILL',
        'base': BASE, 'archive_sha256': ARCHIVE_HASH, 'member_sha256': PINS,
        'changed_payload_sha256': sha256(changed_raw).hexdigest(),
        'checked_unique_persistent_edges': len(used), 'checked_endpoint_adapters': len(endpoints),
        'checked_residual_recipes': len(used_residual), 'finite_local_invoice': invoices,
        'exact_operator_method': 'Pauli conjugation and exact Gaussian dyadic zero state; no compiler import',
        'negative_controls': ['wrong global phase with the same Pauli action, on basis inputs 0 and 1'],
        'all_tensor_powers': 'Base operators are exactly equal, so their tensor powers are equal for every positive integer. The common frame conjugation proof gives the full array map.',
        'not_claimed': ['global chart or owner admission', 'recursive supplier admission', 'new kappa', 'fresh all-size compiler proof'],
        'seconds': time.monotonic()-start, 'max_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--changed', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args())
