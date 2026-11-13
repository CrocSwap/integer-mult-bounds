"""Independent exact construction and source-equivalence certificate.

This file does not import build.py. It reconstructs the splice, proves its
all-row local identity over Fraction, and checks the full emitted coframes.
The supplied #7480 source is the only construction input.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = Fraction
SOURCE_HASH = '5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
CANDIDATE_HASH = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

source = json.load(gzip.open(ROOT / 'inputs/pr7480/WORD.json.gz', 'rt'))
assert hashlib.sha256(canonical(source)).hexdigest() == SOURCE_HASH
old = source['program']
anchor = 33163
removed = [33163, 33164, 33165, 33172, 33186, 33191, 33200, 33201, 33203, 33205]
expected_removed = [
    ['MOVE', 485, 3, 721, False],
    ['ADD', 485, 54, '1', 721],
    ['ADD', 824, 485, '-1', 721],
    ['MOVE', 485, 721, 724, False],
    ['ADD', 212, 1455, '1', 3],
    ['ADD', 1455, 976, '1', 3],
    ['MOVE', 1455, 3, 721, False],
    ['ADD', 824, 1455, '1/2', 721],
    ['ADD', 1455, 54, '1/2', 721],
    ['MOVE', 1455, 721, 904, False],
]
assert [old[i] for i in removed] == expected_removed
# Four fixed stages derived directly from the two-shear calculation.
stages = [
    ('retain the original212 read and encode at3', [
        ['ADD', 212, 1455, '1', 3],
        ['ADD', 1455, 976, '1', 3],
        ['ADD', 485, 1455, '-2', 3],
        ['ADD', 1455, 485, '2/3', 3],
    ]),
    ('pay824 and the54 contribution at721', [
        ['MOVE', 1455, 3, 721, False],
        ['ADD', 824, 1455, '-3/2', 721],
        ['ADD', 824, 54, '-1', 721],
        ['ADD', 1455, 54, '1/2', 721],
    ]),
    ('decode both independent streams at724', [
        ['MOVE', 1455, 721, 724, False],
        ['MOVE', 485, 3, 724, False],
        ['ADD', 1455, 485, '-2/3', 724],
        ['ADD', 485, 1455, '2', 724],
    ]),
    ('continue1455 on its original high frame', [
        ['MOVE', 1455, 724, 904, False],
    ]),
]
splice = [event for _, block in stages for event in block]
emitted = []
mapping = {}
for i, event in enumerate(old):
    if i == anchor:
        emitted.extend(splice)
    if i not in removed:
        mapping[i] = len(emitted)
        emitted.append(event)
candidate = dict(source, program=emitted)
assert hashlib.sha256(canonical(candidate)).hexdigest() == CANDIDATE_HASH
assert candidate == json.load(gzip.open(HERE / 'WORD.json.gz', 'rt'))

# Every formal current row is independent for this local identity. The proof
# therefore applies to any rows supplied by the entire preceding source word.
count = source['public'] + source['owned_fields']
def plus(a, b, coefficient):
    result = a.copy()
    for column, value in b.items():
        result[column] = result.get(column, Q(0)) + coefficient * value
        if not result[column]:
            del result[column]
    return result

def local_replay(tagged):
    rows = [{r: Q(1)} for r in range(count)]
    protected = {}
    for label, event in tagged:
        opcode, dst = event[:2]
        if opcode in ('INIT', 'CLEAR', 'COPY'):
            protected[label] = dict(rows[dst])
        if opcode in ('INIT', 'CLEAR'):
            rows[dst] = {}
        elif opcode == 'SCALE':
            rows[dst] = {c: Q(event[2]) * v for c, v in rows[dst].items()}
        elif opcode == 'ADD':
            rows[dst] = plus(rows[dst], rows[event[2]], Q(event[3]))
        elif opcode == 'COPY':
            assert not rows[dst]
            rows[dst] = {c: Q(event[3]) * v for c, v in rows[event[2]].items()}
    return rows, protected

lo, hi = 33163, 33219
left, left_guards = local_replay(list(enumerate(old[lo:hi], lo)))
right, right_guards = local_replay(
    [('new_' + str(i), e) for i, e in enumerate(splice)] +
    [(i, old[i]) for i in range(lo, hi) if i not in removed]
)
assert left == right
assert left_guards == right_guards
assert not any(e[0] == 'COPY' for e in old[lo:hi])

# Audit the retiming assumptions by inspecting all literal contacts.
def touches(event, role):
    return role in (event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2])
contacts = {}
for role, moved_from in [(212, 33186), (976, 33191), (1455, 33186)]:
    intervening = [(i, old[i]) for i in range(anchor, moved_from)
                   if touches(old[i], role)]
    assert not intervening
    contacts[str(role)] = {'anchor': anchor, 'moved_from': moved_from,
                           'intervening_contacts': intervening}
# 54 has no writes between its two original source uses.
assert not any(e[0] in ('ADD', 'COPY', 'SCALE') and e[1] == 54
               for e in old[33163:33204])
# Every other old event is retained literally and in the original relative order.
assert [event for i, event in enumerate(emitted)
        if not anchor <= i < anchor + len(splice)] == [
            event for i, event in enumerate(old) if i not in removed]


def span(basis):
    result = {0}
    for vector in basis:
        result |= {vector ^ x for x in tuple(result)}
    return result
spaces = [span(basis) for basis in source['frames']]
assert spaces[3] < spaces[721] < spaces[724] < spaces[904]

def inventory(program):
    active = source['initial'] + [None] * source['owned_fields']
    paid, operations = Counter(), Counter()
    live, peak, lifetimes = 0, 0, 0
    for clock, event in enumerate(program):
        opcode, role = event[:2]
        operations[opcode] += 1
        if opcode == 'MOVE':
            lower, upper, owned = event[2:]
            assert active[role] == lower
            assert owned == (role >= source['public'])
            assert spaces[lower] < spaces[upper] or owned and spaces[upper] < spaces[lower]
            paid[abs(len(source['frames'][upper]) - len(source['frames'][lower]))] += 1
            active[role] = upper
        elif opcode == 'INIT':
            assert role >= source['public'] and active[role] is None
            active[role] = event[2]
            live += 1
            lifetimes += 1
            peak = max(peak, live)
        elif opcode == 'CLEAR':
            assert role >= source['public'] and active[role] == event[2]
            active[role] = None
            live -= 1
        else:
            for operand in event[1:3] if opcode in ('ADD', 'COPY') else event[1:2]:
                assert active[operand] == event[-1], (clock, event, operand, active[operand])
    assert active == source['final'] + [None] * source['owned_fields']
    return paid, operations, lifetimes, peak

before = inventory(old)
after = inventory(emitted)
def difference(a, b):
    return {str(k): b[k] - a[k] for k in sorted(set(a) | set(b), key=str) if a[k] != b[k]}
paid_delta = difference(before[0], after[0])
assert paid_delta == {'1': 1, '3': -1, '4': -1, '6': 1}
assert difference(before[1], after[1]) == {'ADD': 3}
assert before[2:] == after[2:] == (74, 50)
assert {k: v for k, v in candidate.items() if k != 'program'} == {
    k: v for k, v in source.items() if k != 'program'}

result = {
    'status': 'PASS_INDEPENDENT_EMISSION_ALL_ROW_IDENTITY_AND_COMPLETE_COFRAMES',
    'source_canonical_sha256': SOURCE_HASH,
    'candidate_canonical_sha256': CANDIDATE_HASH,
    'independent_emission_matches_root_word': True,
    'formal_rows_checked': count,
    'old_interval': [lo, hi],
    'new_interval': [lo, hi + 3],
    'all_local_rows_equal': True,
    'protected_owned_events_equal': {str(k): old[k] for k in left_guards},
    'interior_copy_count': 0,
    'retiming_contact_checks': contacts,
    'frame_chain': [{'id': f, 'rank': len(source['frames'][f]),
                     'basis': source['frames'][f]} for f in (3, 721, 724, 904)],
    'paid_delta': paid_delta,
    'productive_endpoint_delta': {},
    'operation_delta': {'ADD': 3},
    'events': len(emitted),
    'owned_lifetimes': after[2],
    'owned_peak': after[3],
    'scope': 'Exact normalized arbitrary-input construction and full coframes. Physical compiler, common-grid, complete signed prices, and outer gates are separate validations.'
}
(HERE / 'INDEPENDENT-RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
