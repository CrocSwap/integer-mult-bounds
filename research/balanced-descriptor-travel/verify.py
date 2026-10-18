"""Independent word summaries and literal tape walks audit the pinned dispatcher."""
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent

def require(value, message):
    if not value:
        raise ValueError(message)

@dataclass(frozen=True)
class Summary:
    first: int
    last: int
    count: int
    variation: int

    def reverse(self):
        return Summary(self.last, self.first, self.count, self.variation)

    def shift(self, offset):
        return Summary(self.first + offset, self.last + offset, self.count, self.variation)


def join(*parts):
    return Summary(parts[0].first, parts[-1].last,
                   sum(p.count for p in parts),
                   sum(p.variation for p in parts) +
                   sum(abs(a.last-b.first) for a, b in zip(parts, parts[1:])))

@cache
def model(n):
    """Compressed word algebra: no dispatch, array roles, or leaf execution."""
    require(type(n) is int and n >= 1, 'positive factor count')
    if n == 1:
        return Summary(0, 0, 1, 0)
    left = model(n//2)
    right = model(n-n//2).shift(n//2)
    return join(left, right, left.reverse(), right.reverse())


def leaf_formula(n):
    q = 1 << (n.bit_length()-1)
    return 3*q*n - 2*q*q


def measured(indices):
    return Summary(indices[0], indices[-1], len(indices),
                   sum(abs(a-b) for a, b in zip(indices, indices[1:])))


def check_summary(n, actual, direction=1):
    want = model(n)
    if direction == -1:
        want = want.reverse()
    require(actual == want, f'trace mismatch for n={n}, sign={direction}')
    require(actual.count == leaf_formula(n), 'closed leaf count')
    require(actual.variation <= 2*(actual.count-n), 'universal variation bound')
    closed = actual.first + actual.variation + actual.last
    require(closed < 2*actual.count, 'closed seek bound')


def load_dispatcher():
    manifest = json.loads((ROOT/'SOURCES.json').read_text())
    expected = {'dirty_stride.py', 'LICENSE', 'NOTICE.md', 'PR985-PROOF.md', 'PR628-DIRTY-PROOF.md'}
    require(set(manifest['vendor_sha256']) == expected, 'complete vendor inventory')
    require({p.name for p in (ROOT/'vendor').iterdir()} == expected, 'exact vendor file set')
    require(manifest['source_head'] == 'da1cdf8ed4ac9b1b8378dfec73f77ff4e81a4f70', 'audited source head')
    for name, digest in manifest['vendor_sha256'].items():
        require(sha256((ROOT/'vendor'/name).read_bytes()).hexdigest() == digest,
                f'vendor source drift: {name}')
    spec = importlib.util.spec_from_file_location('pinned_dirty_stride', ROOT/'vendor/dirty_stride.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LoggedFactors(list):
    def __init__(self, values):
        super().__init__(values)
        self.indices = []

    def __getitem__(self, index):
        self.indices.append(index)
        return super().__getitem__(index)


def trace_dispatcher(module, n, direction, length=1):
    # Preflight uses list iteration; only actual leaf descriptor lookups index this list.
    factors = LoggedFactors([(True, module.ZERO, 1)] * n)
    x = [module.ONE] * length
    y = [(module.F(-3), module.F(2))] * length
    scratch = [[(module.F(j+2), module.F(1))] * length
               for j in range((n-1).bit_length())]
    original = [a[:] for a in [x] + scratch]
    meter = module.compose(x, y, factors, scratch, module.ONE, module.F(1, 2),
                           64, 1, sign=direction)
    require([x] + scratch == original, 'actual source and scratch restoration')
    require(meter.leaves == len(factors.indices), 'every executed leaf logs once')
    check_summary(n, measured(factors.indices), direction)
    return factors.indices


def literal_tape(indices, n, width):
    """Move a bit head one cell at a time; read every record and rewind it."""
    require(type(width) is int and width > 0, 'positive fixed record width')
    require(all(type(i) is int and 0 <= i < n for i in indices), 'record index')
    records = [[(i + 3*j) % 2 for j in range(width)] for i in range(n)]
    tape = [bit for record in records for bit in record]
    head = 0
    moves = 0
    reads = 0
    def move(target):
        nonlocal head, moves
        while head != target:
            head += 1 if target > head else -1
            moves += 1
    for index in indices:
        start = index*width
        move(start)
        found = []
        for _ in range(width):
            found.append(tape[head])
            reads += 1
            move(head+1)
        require(found == records[index], 'literal record contents')
        move(start)
    move(0)
    require(head == 0, 'final head return')
    return moves, reads


def literal_countdown(start):
    """Finite-alphabet counter, including zero detection and all head returns."""
    require(type(start) is int and start >= 0, 'nonnegative countdown')
    cells = ([int(c) for c in bin(start)[2:][::-1]] if start else []) + [None]
    head = steps = decrements = 0
    def read():
        nonlocal steps
        steps += 1
        return cells[head]
    def write(value):
        nonlocal steps
        steps += 1
        cells[head] = value
    def move(delta):
        nonlocal head, steps
        head += delta
        steps += 1
    while read() is not None:
        while read() == 0:
            write(1)
            move(1)
        require(read() == 1, 'borrow reaches a one')
        write(0)
        move(1)
        leading = read() is None
        move(-1)
        if leading:
            write(None)
        while head:
            move(-1)
        decrements += 1
    require(decrements == start and head == 0 and cells[0] is None, 'counter completion')
    require(steps <= 20*(start+start.bit_length()+1), 'amortized counter bill')
    return steps


def rejected(thunk):
    try:
        thunk()
    except ValueError:
        return
    raise ValueError('negative control unexpectedly passes')


def main():
    module = load_dispatcher()
    counter_steps = sum(literal_countdown(d) for d in range(1025))
    # All counts in this domain, with no sampled early stop.
    counts = list(range(1, 34)) + [63, 64, 65, 127, 128, 129]
    traces = {}
    leaves = 0
    for n in counts:
        for direction in (1, -1):
            indices = trace_dispatcher(module, n, direction)
            traces[n, direction] = indices
            leaves += len(indices)
    # Additional nontrivial array geometry; the audited property concerns dispatch only.
    for direction in (1, -1):
        require(trace_dispatcher(module, 7, direction, length=5) == traces[7, direction],
                'trace independent of array length in tested geometry')
    huge = {2**h + d for h in range(1, 61) for d in (-1, 0, 1)}
    summary_counts = set(range(1, 4097)) | huge
    for n in sorted(summary_counts):
        actual = model(n)
        check_summary(n, actual)
        require(actual.first == 0 and actual.last == n//2, 'positive endpoints')
        if n & (n-1) == 0:
            require(actual.variation == 3*n*(n-1)//2, 'power-of-two exact variation')
    tape_cases = 0
    for n in range(1, 18):
        for direction in (1, -1):
            for width in (1, 3, 17):
                indices = traces[n, direction]
                moves, reads = literal_tape(indices, n, width)
                summary = measured(indices)
                closed = summary.first + summary.variation + summary.last
                require(moves == width*(closed+2*len(indices)), 'literal tape invoice')
                require(reads == width*len(indices), 'literal tape reads')
                require(moves < 4*width*len(indices), 'tape movement bound')
                tape_cases += 1
    # Every control is forced to disagree with an independently specified property.
    rejected(lambda: check_summary(7, measured(traces[7, 1][:-1])))
    rejected(lambda: check_summary(7, measured(traces[7, 1]), -1))
    wrong = traces[7, 1][:]
    wrong[len(wrong)//2] = 0 if wrong[len(wrong)//2] else 6
    rejected(lambda: check_summary(7, measured(wrong)))
    rejected(lambda: require(model(7).last == 4, 'wrong odd split endpoint'))
    rejected(lambda: require(model(8).variation == 2*(64-8), 'upper bound is not exact'))
    rejected(lambda: literal_tape([0], 1, 0))
    rejected(lambda: literal_tape([3], 3, 1))
    s = measured(traces[7, 1])
    moves, reads = literal_tape(traces[7, 1], 7, 3)
    rejected(lambda: require(moves == 3*(s.variation+2*s.count), 'omitted final return'))
    s = measured(traces[8, 1])
    reset_cost = 2*sum(traces[8, 1])
    rejected(lambda: require(reset_cost == s.variation+s.last, 'per-lookup reset differs'))
    result = {
        'status': 'PASS_BALANCED_DESCRIPTOR_TRAVEL',
        'dispatcher_counts': counts,
        'dispatcher_signs': [1, -1],
        'dispatcher_cases': 2*len(counts),
        'dispatcher_leaf_lookups': leaves,
        'extra_geometry_cases': 2,
        'summary_cases': len(summary_counts),
        'literal_tape_cases': tape_cases,
        'negative_controls': 9,
        'countdown_cases': 1025,
        'countdown_primitive_steps': counter_steps,
        'scope': 'factor descriptor trace and fixed-width tape access only',
        'python': sys.version,
        'executable': sys.executable,
    }
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
