"""Independent scoped CRT review. No heavy numerical/ROM suite is rerun."""
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType
import argparse
import json
import random

OUT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package-root', type=Path, default=OUT.parent,
                    help='reviewed package directory; default parent of this review folder')
parser.add_argument('--write-result', action='store_true',
                    help='explicitly regenerate the review receipt after reviewing changed inputs')
args = parser.parse_args()
P = args.package_root.resolve()
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    module = ModuleType(path.stem)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


tree = load(P / 'tree.py')
w = load(ROOT / 'research/r437-preparation-composition/predecessor4025/source/words.py')
entry = load(ROOT / 'research/encoded-crt-entry-lifecycle/entry.py')
pins = [pin for pin in json.loads((P / 'SOURCES.json').read_text())['files']
        if pin['usage'] == 'input']
for pin in pins:
    raw = (ROOT / pin['path']).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'SHA256 ' + pin['path'])
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
         == pin['git_blob'], 'Git blob ' + pin['path'])
seam = json.loads((P / 'SEAMS.json').read_text())
actual = (ROOT / seam['source']).read_text()
for old, new in seam['replacements'].items():
    need(actual.count(old) == 1, 'unique seam')
    actual = actual.replace(old, new)
need(actual == (P / 'workspace.py').read_text(), 'exact declared seam')


def independent_schedule(widths, ell):
    nodes = []
    size = 2
    while size <= len(widths):
        level = size.bit_length() - 1
        for row in range(2 * ell - 1):
            nodes.extend((level, start, row)
                         for start in range(0, len(widths), size))
        size *= 2
    return tuple(nodes)


def independent_bill(widths, ell):
    d, address = len(widths), sum(widths)
    length = 2 + 3 * address + 4 * d
    total, sums = 8, [0, 0, 0, 0]
    size = 2
    while size <= d:
        for start in range(0, d, size):
            precision = 1 + sum(widths[start:start + size])
            right = widths[start + size // 2:start + size]
            stream = 2 + sum(right) + len(right)
            sums[0] += (precision + 2) ** 4
            sums[1] += (precision + 2) ** 2
            sums[2] += precision ** 2 * len(right)
            sums[3] += (size + 1) * (precision + 2)
            for row in range(2 * ell - 1):
                active = [h for h in right
                          if h == ell or row < ell - 1 or row > ell]
                if not active:
                    continue
                numerical = ((1 << 20) * (precision + 2) ** 4
                             + (1 << 16) * (precision + 2) ** 2
                             + 128 * (length + precision + size + 1))
                rom = sum(2000000 * precision ** 2 * (2 ** h + 1) ** 3
                          * (h + 1) ** 4 for h in active)
                front = length + (size + 1) * (precision + 2)
                front += sum(3 * h * 2 ** h + 3 * h + 5 for h in active)
                total += (numerical + rom + 4096 * front
                          + 4096 * (length + stream)
                          + 370 + 4096 * (precision + 2))
        size *= 2
    return total, sums


rng = random.Random(20261110)
case_count, largest_ratio = 0, Fraction(0)
for ell in range(2, 33):
    for d in (2, 4, 8, 16, 32, 64):
        families = [tuple([ell - 1] * d), tuple([ell] * d),
                    tuple(ell - 1 + (i & 1) for i in range(d)),
                    tuple(ell - 1 + rng.randrange(2) for _ in range(d))]
        for widths in families:
            expected, sums = independent_bill(widths, ell)
            need(expected == tree.whole_bound(widths, ell), 'independent invoice')
            schedule = independent_schedule(widths, ell)
            need(tree.commands(widths, ell) == schedule, 'independent topology order')
            need(tree.commands(widths, ell, True) == tuple(reversed(schedule)), 'inverse order')
            p = sum(widths)
            first = [Fraction(8, 7) * (ell + 3) ** 4 * d ** 4,
                     2 * (ell + 2) ** 2 * d ** 2,
                     Fraction(2, 3) * (ell + 1) ** 2 * d ** 3,
                     3 * (ell + 3) * d ** 2]
            final = [715 * p ** 4, 32 * p ** 2, 6 * p ** 3, 15 * p ** 2]
            for observed, intermediate, bound in zip(sums, first, final):
                need(observed < intermediate <= bound, 'corrected geometric bound')
            ample = (1 << 34) * 2 ** (3 * ell) * (p + 2) ** 8
            need(expected <= ample, 'full explicit majorant')
            if p >= 14:
                need(ample <= 2 ** (4 * ell) * (p + 2) ** 16, 'E-shape comparison')
            largest_ratio = max(largest_ratio, Fraction(expected, ample))
            case_count += 1

# The initial proof's quadratic inequality is false; this is an exact control.
_, counter_sums = independent_bill((20,) * 16, 20)
old_bound = Fraction(4, 3) * 23 ** 2 * 16 ** 2
need(counter_sums[1] == 199815 and counter_sums[1] > old_bound, 'original inequality counterexample')

guards = tree.ProtectedZeros(w, entry)
guard_cases, max_precision = [], 0
for index, precision in enumerate((4, 5, 64, 4, 127, 9, 5, 256, 4)):
    def traffic():
        return sum(p.meter.reads + p.meter.writes + p.meter.moves for p in guards.ports)
    before = traffic()
    guards.prepare(precision)
    for port in guards.ports:
        need(port.head == 1 and port.cells[0] == w.LEFT, 'prepared entry head')
        need(port.cells[1:precision + 1] == bytes([w.ZERO]) * precision, 'exact current zero word')
        need(port.cells[precision + 1] == w.RIGHT, 'current exact delimiter')
        need(all(c == w.BLANK for c in port.cells[precision + 2:]), 'old tail remains blank')
    guards.retire()
    measured = traffic() - before
    expected = 8 * (10 * precision + (23 if index == 0 else 24))
    need(measured == expected, 'independently derived guard lifecycle count')
    need(measured <= 4096 * (precision + 2), 'paid guard allowance')
    max_precision = max(max_precision, precision)
    for port in guards.ports:
        need(port.head == 1 and all(c == w.BLANK for c in port.cells), 'full retirement')
        need(len(port.cells) == max_precision + 2, 'retained historical extent')
    guard_cases.append({'precision': precision, 'actions': measured,
                        'per_role_capacity': max_precision + 2})

controls = []
guards.prepare(5)
try:
    guards.prepare(4)
except ValueError:
    controls.append('live_guard_resize_rejected')
else:
    raise ValueError('live guard resize survived')
guards.retire()
guards.ports[0].cells[-1] = w.ONE
try:
    need(all(c == w.BLANK for c in guards.ports[0].cells), 'historical blankness')
except ValueError:
    controls.append('stale_tail_detected')
else:
    raise ValueError('stale tail survived')
guards.ports[0].cells[-1] = w.BLANK
controls.append('false_quadratic_geometric_inequality_detected')

receipt = {
    'status': 'PASS_INDEPENDENT_SCOPED_REVIEW',
    'base_commit': 'e54523517d0f03e58352e647c403a5af3e525a57',
    'source_pins': len(pins), 'budget_cases': case_count,
    'largest_full_majorant_ratio': [largest_ratio.numerator, largest_ratio.denominator],
    'initial_proof_counterexample': {'ell': 20, 'd': 16, 'all_widths': 20,
                                    'actual': counter_sums[1],
                                    'claimed_upper': [old_bound.numerator, old_bound.denominator]},
    'guard_lifecycle_cases': guard_cases, 'negative_controls': controls,
    'reviewed_files': {name: sha256((P / name).read_bytes()).hexdigest()
                       for name in ('PROOF.md', 'tree.py', 'workspace.py', 'SEAMS.json', 'RESULT.json')},
    'heavy_rom_suite_rerun': False, 'universal_proof_in_review': True,
}
if args.write_result:
    (OUT / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
else:
    need(receipt == json.loads((OUT / 'RESULT.json').read_text()), 'frozen independent receipt')
print(receipt['status'], case_count, len(guard_cases), len(controls))
