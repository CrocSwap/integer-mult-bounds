"""Independently enumerate and replay the full #7481 fixed-bank terminal family."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
COMPRESSED = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
GRID = 1125 * 2**25
CASE_CAP, SECONDS = 19, 30


def terminal_lifetimes(word):
    n = word['public']
    pending = {}
    terminal = []
    frames = word['frames']
    for clock, (op, role, *args) in enumerate(word['program']):
        if op == 'INIT':
            assert role >= n and role not in pending
            pending[role] = None
        elif op == 'MOVE' and role >= n:
            assert args[2] and role in pending
            rank = abs(len(frames[args[0]]) - len(frames[args[1]]))
            pending[role] = (rank, clock, [], args[1])
        elif op == 'CLEAR':
            old = pending.pop(role)
            if old is None:
                continue
            rank, move, contacts, chart = old
            assert args[0] == chart
            if contacts and contacts[0][0] == 'SCALE':
                contacts = contacts[1:]
            if len(contacts) == 1 and contacts[0][0] == 'OUTWARD_ADD':
                _, read = contacts[0]
                terminal.append((rank, move, role, read, clock))
        else:
            used = [(role, op)]
            if op in ('ADD', 'COPY'):
                used.append((args[0], 'OUTWARD_ADD' if op == 'ADD' else 'COPY_SOURCE'))
            for key, kind in used:
                if key >= n:
                    assert key in pending
                    if pending[key] is not None:
                        pending[key][2].append((kind, clock))
    assert not pending
    return sorted(terminal, key=lambda row: (-row[0], row[1]))


def scaled(row, factor):
    num, den = factor.as_integer_ratio()
    products = [num * x for x in row]
    if den == 1:
        return products
    return [x // den if x % den == 0 else Q(x, den) for x in products]


def sparse(row):
    return {j: Q(value) / GRID for j, value in enumerate(row) if value}


def reduced(row, pivots):
    residual = row.copy()
    for key, vector in sorted(pivots.items()):
        if key not in residual:
            continue
        scale = residual[key]
        for j, weight in vector.items():
            value = residual.get(j, Q(0)) - scale * weight
            if value:
                residual[j] = value
            else:
                residual.pop(j, None)
    return residual


def basis(rows):
    pivots = {}
    for row in rows:
        remainder = reduced(row, pivots)
        if remainder:
            key = min(remainder)
            scale = remainder[key]
            pivots[key] = {j: weight / scale for j, weight in remainder.items()}
    return pivots


def dot(row, probe):
    return sum((weight * probe.get(i, Q(0)) for i, weight in row.items()), Q(0))


def separate(pivots, remainder):
    free = min(remainder)
    assert free not in pivots
    probe = {free: 1 / remainder[free]}
    for key, vector in sorted(pivots.items(), reverse=True):
        value = -dot(vector, probe)
        if value:
            probe[key] = value
    return probe


def inspect(case, event, rows, charts):
    rank, move, role, read, clear = case
    op, target, source, coefficient, chart = event
    assert op == 'ADD' and source == role and charts[target] == charts[source] == chart
    bank_ids = [i for i, chart_id in enumerate(charts) if chart_id == chart and i != role]
    bank = [sparse(rows[i]) for i in bank_ids]
    owned = sparse(rows[role])
    pivots = basis(bank)
    remainder = reduced(owned, pivots)
    probe = separate(pivots, remainder) if remainder else {}
    values = [dot(row, probe) for row in bank]
    old = dot(owned, probe)
    assert not any(values) and old == bool(remainder)
    return {'case':case, 'bank':bank_ids, 'bank_rank':len(pivots),
            'augmented_rank':len(pivots) + bool(remainder), 'chart':chart,
            'recipient':target, 'scope_status':'excluded' if remainder else 'span_survives',
            'separating_original_inputs':probe, 'owned_value_on_probe':old,
            'required_add_on_probe':Q(coefficient) * old, 'bank_values_on_probe':values}


def replay(word, population, outcomes):
    public = word['public']
    zero = [0] * public
    rows = [zero] * (public + word['owned_fields'])
    for index in range(public):
        row = zero.copy()
        row[index] = GRID
        rows[index] = row
    charts = word['initial'] + [None] * word['owned_fields']
    at = {case[3]:case for case in population}
    assert len(at) == len(population)
    for clock, event in enumerate(word['program'][:max(at) + 1]):
        if clock in at:
            outcomes[clock] = inspect(at[clock], event, rows, charts)
        op, dst, *args = event
        if op == 'INIT':
            assert charts[dst] is None and not any(rows[dst])
            charts[dst] = args[0]
        elif op == 'CLEAR':
            assert charts[dst] == args[0]
            charts[dst] = None
            rows[dst] = zero
        elif op == 'MOVE':
            assert charts[dst] == args[0] and args[2] == (dst >= public)
            charts[dst] = args[1]
        elif op == 'SCALE':
            assert charts[dst] == args[1]
            rows[dst] = scaled(rows[dst], Q(args[0]))
        else:
            source, coefficient, chart = args
            assert op in ('ADD', 'COPY') and charts[dst] == charts[source] == chart
            term = scaled(rows[source], Q(coefficient))
            if op == 'COPY':
                assert not any(rows[dst])
                rows[dst] = term
            else:
                rows[dst] = [a + b for a, b in zip(rows[dst], term)]


def main():
    assert __debug__
    outcomes = {}
    population = []
    def timeout(signum, frame):
        print(dumps({'status':'unresolved_timeout', 'case_cap':CASE_CAP, 'cap_seconds':SECONDS,
                     'population':population, 'cases_completed':len(outcomes),
                     'unresolved':[case for case in population if case[3] not in outcomes],
                     'records':[outcomes[case[3]] for case in population if case[3] in outcomes]},
                    default=str, sort_keys=True, indent=2))
        exit(124)
    signal(SIGALRM, timeout)
    alarm(SECONDS)
    source = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(source).hexdigest() == COMPRESSED
    raw = decompress(source)
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw)
    population = terminal_lifetimes(word)
    assert len(population) == CASE_CAP
    replay(word, population, outcomes)
    assert len(outcomes) == CASE_CAP
    records = [outcomes[case[3]] for case in population]
    alarm(0)
    print(dumps({'status':'PASS_INDEPENDENT_TERMINAL_DENSE', 'case_cap':CASE_CAP,
                 'cap_seconds':SECONDS, 'cases_completed':len(records), 'population':population,
                 'unresolved':[], 'survivors':[x['case'] for x in records if x['scope_status']=='span_survives'],
                 'records':records, 'compressed_sha256':COMPRESSED,'payload_sha256':PAYLOAD},
                default=str, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
