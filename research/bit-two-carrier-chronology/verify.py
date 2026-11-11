"""Exact source-row exclusion for BIT summary 770 and two public carriers."""
from bisect import bisect_left
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
PIN = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
SUMMARY = 770
INIT = 26857
READ = 32938


def basis(values):
    pivots = {}
    for value in values:
        while value:
            lead = value & -value
            if lead not in pivots:
                pivots[lead] = value
                break
            value ^= pivots[lead]
    ordered = sorted(pivots.items())

    def reduce(value):
        for lead, pivot in ordered:
            if value & lead:
                value ^= pivot
        return value

    return reduce, len(pivots)


def matches(signatures, target):
    return signatures[target], sum(n * signatures[s ^ target] for s, n in signatures.items())


def verify(path):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PIN
    word = json.loads(gzip.decompress(raw))
    n = word['public']
    assert n == 659
    dims = {int(key): f['dim'] for key, f in word['frames'].items()}
    frames = word['start'] + [None] * word['owned_fields']
    rows = [1 << i for i in range(n)] + [0] * word['owned_fields']
    touch = defaultdict(list)
    ascents = []
    zero_rows = set()
    target = None
    first_read = None
    erasures = 0
    for i, (op, a, *args) in enumerate(word['program']):
        touch[a].append(i)
        changed = [a]
        if op == 'ADD':
            b, f = args
            assert a != b and frames[a] == frames[b] == f
            touch[b].append(i)
            if b == SUMMARY and first_read is None:
                first_read = i
            rows[a] ^= rows[b]
        elif op == 'SWAP':
            b = args[0]
            assert a < n and b < n
            touch[b].append(i)
            changed.append(b)
            frames[a], frames[b] = frames[b], frames[a]
            rows[a], rows[b] = rows[b], rows[a]
        elif op == 'MOVE':
            f, g = args
            assert frames[a] == f
            frames[a] = g
            if a < n:
                assert dims[f] < dims[g]
                ascents.append((i, a, f, rows[a]))
            elif a == SUMMARY:
                assert target is None and dims[f] == 7 and g == 0
                target = rows[a]
        elif op == 'INIT':
            assert a >= n and frames[a] is None
            frames[a], rows[a] = args[0], 0
            if a == SUMMARY:
                assert i == INIT
        else:
            assert op == 'CLEAR' and a >= n and frames[a] == args[0]
            erasures += bool(rows[a])
            frames[a], rows[a] = None, 0
        if INIT <= i < READ:
            owners = range(len(frames)) if i == INIT else changed
            zero_rows.update(rows[j] for j in owners if j != SUMMARY and frames[j] == 0)

    assert first_read == READ and target is not None
    assert frames == word['final'] + [None] * word['owned_fields']
    assert all(rows[i] == (1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(n))
    assert len(ascents) == 2862 and erasures == 237

    pool = []
    zero_sources = []
    for i, role, frame, row in ascents:
        contacts = touch[role]
        j = bisect_left(contacts, i)
        assert contacts[j] == i
        previous = contacts[j-1] if j else -1
        following = contacts[j+1] if j+1 < len(contacts) else len(word['program'])
        if previous < READ and following > INIT:
            if dims[frame]:
                pool.append((role, row))
            else:
                zero_sources.append(row)

    reduce, rank = basis(sorted(zero_rows))
    goal = reduce(target)
    assert rank == 119 and goal
    assert len(zero_sources) == 2 and all(reduce(row) == 0 for row in zero_sources)
    assert basis([*sorted(zero_rows), target])[0](target) == 0
    assert matches(Counter({1: 1, 2: 1}), 3) == (0, 2)
    assert matches(Counter({1: 1, 2: 1}), 4) == (0, 0)
    assert matches(Counter({1: 1, 2: 1}), 1) == (1, 0)
    signatures = Counter(reduce(row) for _, row in pool)
    one, two = matches(signatures, goal)
    assert (one, two) == (0, 0)
    owners = Counter(role for role, _ in pool)
    ordered_pairs = len(pool)**2 - sum(v*v for v in owners.values())
    assert (len(pool), len(owners), ordered_pairs) == (907, 547, 821022)
    return dict(status='PASS_TWO_CARRIER_BIT_ROW_EXCLUSION', summary=SUMMARY,
                summary_init=INIT, first_read=READ, basis_rank=rank, public_endpoint_rows=n,
                source_events=len(pool), source_owners=len(owners), ordered_distinct_owner_pairs=ordered_pairs,
                rank_zero_sources_in_retained_basis=len(zero_sources),
                one_source_matches=one, two_source_matches_including_same_owner=two,
                dependencies={SOURCE: PIN})


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Use assertions')
    report = verify(HERE.parents[1] / SOURCE)
    assert json.dumps(report, indent=2, sort_keys=True) + '\n' == (HERE / 'RECEIPT.json').read_text()
    print(report['status'])
