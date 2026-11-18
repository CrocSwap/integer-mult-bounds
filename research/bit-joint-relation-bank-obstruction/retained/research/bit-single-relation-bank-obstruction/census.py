"""Compute exact receiver spaces for one binary helper relation."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
CALLER = 'research/paired-query-only-bit/EFREE-CALLER.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def source():
    for pin in read(HERE / 'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'input bytes')
    return read(ROOT / NATIVE), read(ROOT / CALLER)


def walk(word, reverse):
    n = word['public']
    initial, final = (word['final'], word['start']) if reverse else (word['start'], word['final'])
    at = initial[:] + [None] * word['owned_fields']
    rows = [1 << i for i in range(n)] + [0] * word['owned_fields']
    banks = defaultdict(dict)
    for r, chart in enumerate(initial):
        banks[chart][~r] = rows[r]
    moves = {}
    program = list(reversed(word['program'])) if reverse else word['program']
    for clock, event in enumerate(program):
        op, a, *args = event
        if reverse and op in ('INIT', 'CLEAR'):
            op = 'CLEAR' if op == 'INIT' else 'INIT'
        if op == 'INIT':
            need(a >= n and at[a] is None, 'new owned lifetime')
            at[a], rows[a] = args[0], 0
        elif op == 'CLEAR':
            need(a >= n and at[a] == args[0], 'owned retirement')
            at[a], rows[a] = None, 0
        elif op == 'SWAP':
            b, = args
            at[a], at[b] = at[b], at[a]
            rows[a], rows[b] = rows[b], rows[a]
        elif op == 'ADD':
            b, chart = args
            need(a != b and at[a] == at[b] == chart, 'cocharted ADD')
            if reverse:
                rows[b] ^= rows[a]
            else:
                rows[a] ^= rows[b]
        else:
            need(op == 'MOVE', 'native operation')
            start, end = args[::-1] if reverse else args
            need(at[a] == start, 'MOVE entrance')
            at[a] = end
            moves[clock] = (start, end)
            banks[end][clock] = rows[a]
    need(at == final + [None] * word['owned_fields'], 'complete final chart inventory')
    for r in range(n):
        other = r + 111 if reverse and r < 111 else r - 111 if not reverse and 111 <= r < 222 else None
        need(rows[r] == (1 << r) ^ (0 if other is None else 1 << other), 'full public endpoint')
    return initial, final, banks, moves


def echelon(rows):
    pivots = {}
    for value, tags in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value, tags
                break
            donor, indices = pivots[pivot]
            value ^= donor
            tags ^= indices
    return pivots


def solve(value, pivots):
    tags = set()
    while value:
        pivot = value.bit_length() - 1
        if pivot not in pivots:
            return None
        donor, indices = pivots[pivot]
        value ^= donor
        tags ^= indices
    return tags


def clean_space(bank, mask):
    outside, inside = {}, []
    for key, value in bank.items():
        tags = {key}
        while value & ~mask:
            pivot = (value & ~mask).bit_length() - 1
            if pivot not in outside:
                outside[pivot] = value, tags
                break
            donor, indices = outside[pivot]
            value ^= donor
            tags ^= indices
        else:
            if value:
                inside.append((value, tags))
    return echelon(inside)


def coordinates(value):
    return [i for i in range(value.bit_length()) if value >> i & 1]


def enumerate_space(space):
    values = {0}
    for row, _ in space.values():
        values |= {value ^ row for value in values}
    return values - {0}


def one_orientation(word, reverse):
    initial, final, banks, moves = walk(word, reverse)
    rank = lambda key: abs(word['frames'][str(moves[key][0])]['dim'] - word['frames'][str(moves[key][1])]['dim'])
    for bank in banks.values():
        need(len(echelon((v, set()) for v in bank.values())) == len(bank), 'independent receiver bank')
    groups = defaultdict(list)
    for r in range(222, word['public']):
        groups[initial[r], final[r]].append(r)
    records = []
    for (a, d), roles in groups.items():
        mask = sum(1 << r for r in roles)
        lost = abs(word['frames'][str(a)]['dim'] - word['frames'][str(d)]['dim'])
        spaces = {c: clean_space(bank, mask) for c, bank in banks.items() if c != a}
        nonzero = {c: space for c, space in spaces.items() if space}
        need(len(nonzero[d]) == len(roles), 'complete terminal space')
        exceptional = set()
        for c, space in nonzero.items():
            if c != d:
                need(len(space) <= 4, 'bounded exceptional enumeration')
                exceptional |= enumerate_space(space)
        keys = list(banks[d])
        positions = {key: i for i, key in enumerate(keys)}
        image = echelon((sum(1 << positions[k] for k in tags), set()) for _, tags in nonzero[d].values())
        terminal_pivots = sorted(keys[p] for p in image)
        need(all(k >= 0 and rank(k) <= lost for k in terminal_pivots), 'terminal-only rank bound')
        cases = []
        for value in sorted(exceptional):
            hits = []
            for c, space in nonzero.items():
                tags = solve(value, space)
                if tags is not None:
                    key = max(tags)
                    need(key >= 0, 'paid causal pivot')
                    hits.append(dict(chart=c, pivot=key, rank=rank(key), relation=sorted(tags)))
            need(sum(h['rank'] for h in hits) < lost, 'strict exceptional rank deficit')
            cases.append(dict(signal=coordinates(value), hits=hits))
        need(lost ** 99 > (lost - 1) ** 100, 'uniform power interval')
        records.append(dict(entrance=a, exit=d, roles=roles, lost_rank=lost,
            checked_receivers=len(spaces),
            spaces=[dict(chart=c, basis=[dict(signal=coordinates(v), relation=sorted(tags)) for v, tags in space.values()])
                    for c, space in sorted(nonzero.items())],
            terminal_pivots=terminal_pivots, terminal_rank_max=max(map(rank, terminal_pivots)),
            exceptional_cases=cases))
    return dict(direction='transpose' if reverse else 'forward', paid=len(moves),
        receiver_charts=len(banks), retained_rows=sum(map(len, banks.values())), groups=records,
        exceptional_directions=sum(len(g['exceptional_cases']) for g in records),
        bank_rows_sha256=sha256(json.dumps([[c, [[k, str(v)] for k, v in row.items()]]
                                          for c, row in sorted(banks.items())], separators=(',', ':')).encode()).hexdigest())


def invoice(word, caller):
    _, _, _, moves = walk(word, False)
    dim = lambda chart: word['frames'][str(chart)]['dim']
    native = Counter(abs(dim(a) - dim(b)) for a, b in moves.values())
    helpers = Counter(abs(dim(word['start'][r]) - dim(word['final'][r])) for r in range(222, word['public']))
    calls = [e for e in caller['events'] if e[0] == 'LOCAL']
    need(caller['ports'] == 111 and caller['stages'] == 18 and len(calls) == 36, 'complete paired caller')
    need(Counter(e[1] for e in calls) == Counter({s: 2 for s in range(1, 19)}), 'two native calls per stage')
    paid, targets = Counter({r: 36 * n for r, n in native.items()}), Counter({r: 36 * n for r, n in helpers.items()})
    for event in caller['events']:
        if event[0] == 'QUERY':
            paid[1] += 111
        elif event[0] == 'IDLE_ONE':
            paid[7 * len(event[2])] += 111
    for target in caller['diagonal']:
        need(target['q'] == 1 and target['stages'] and len(set(target['stages'])) == len(target['stages']), 'positive root target')
        targets[1 + 7 * len(target['stages'])] += 111
    need((sum(paid.values()), sum(targets.values())) == (107352, 19950), 'complete source invoice')
    return dict(paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())),
                calls=36, paid_count=sum(paid.values()), target_count=sum(targets.values()),
                rank_surplus=sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items()))


def run():
    word, caller = source()
    return dict(status='PASS_SINGLE_BIT_RELATION_OBSTRUCTION', public=word['public'],
                helper_groups=9, source_invoice=invoice(word, caller),
                orientations=[one_orientation(word, False), one_orientation(word, True)],
                kappa_interval=['0', '1/100'])


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
