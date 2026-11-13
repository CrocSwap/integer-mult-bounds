"""Reconstruct the exact fixed-receiver terminal owned transfer receipts."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv

ROOT = Path(__file__).resolve().parent


def timeout(_signal, _frame):
    raise SystemExit(124)


def select_transfers(tape, frames):
    contacts = {}
    for clock, (op, role, *args) in enumerate(tape):
        contacts.setdefault(role, []).append(clock)
        if op in ('ADD', 'COPY'):
            contacts.setdefault(args[0], []).append(clock)
    candidates = []
    for clock, (op, role, *args) in enumerate(tape):
        if op != 'MOVE' or not args[2]:
            continue
        later = [index for index in contacts[role] if index > clock]
        stop = next((i for i, index in enumerate(later) if tape[index][0] in ('MOVE', 'CLEAR')), None)
        if stop is None or tape[later[stop]][0] != 'CLEAR':
            continue
        use = later[:stop]
        if use and tape[use[0]][0] == 'SCALE' and tape[use[0]][1] == role:
            use = use[1:]
        if len(use) == 1 and tape[use[0]][0] == 'ADD' and tape[use[0]][2] == role:
            rank = abs(len(frames[args[0]]) - len(frames[args[1]]))
            candidates.append((rank, clock, role, use[0], later[stop]))
    return sorted(candidates, key=lambda case: (-case[0], case[1]))


def main():
    assert __debug__
    assert argv[1:] in (['--first-eight'], ['--remaining-eleven'])
    start, cap = (0, 8) if argv[1] == '--first-eight' else (8, 11)
    signal(SIGALRM, timeout)
    alarm(30)
    helper_path = ROOT / 'gate.py'
    assert sha256(helper_path.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    helper = run_path(str(helper_path))
    inputs = {name: (ROOT / name).read_bytes() for name in helper['PINS']}
    assert {name: sha256(raw).hexdigest() for name, raw in inputs.items()} == helper['PINS']
    payload = decompress(inputs['7481-WORD.json.gz'])
    assert sha256(payload).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(payload)
    caller = loads(inputs['7113-CALLER.json'])
    copies = caller['stages']
    assert copies == sum(event[0] == 'J' for event in caller['events']) == 17
    application = loads(inputs['7481-APPLICATION.json'])
    lo, hi = map(Fraction, application['directed_crossing_bracket'])
    power = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    rows, basis, reduce, census = (helper[key] for key in ('exact_cut_rows', 'basis', 'representation', 'census'))
    tape, public = word['program'], word['public']
    population = select_transfers(tape, word['frames'])
    assert len(population) == 19
    records = []
    for rank, move, role, read, clear in population[start:start + cap]:
        _, active, _ = census(word, read)
        destination, chart = tape[read][1], tape[read][-1]
        bank = [item for item, frame in active.items() if frame == chart and item != role]
        original = rows(tape[:read], bank + [role], public)
        pivots = basis(original[:-1])
        residual, coefficients = reduce(pivots, original[-1])
        gross = [copies * power(rank, hi)[0], copies * power(rank, lo)[1]]
        assert 0 < gross[0] <= gross[1]
        assert residual and len(basis(original)) == len(pivots) + 1
        records.append({'move': move, 'read': read, 'clear': clear, 'role': role, 'rank': rank,
                        'receiver': destination, 'chart': chart, 'bank': bank, 'bank_rank': len(pivots),
                        'augmented_rank': len(basis(original)), 'gross_before_repairs': gross,
                        'residual': residual, 'representation': {bank[i]: q for i, q in coefficients.items()}})
    print(dumps({'status': 'FIXED_BANK_SCREEN', 'case_cap': cap, 'tested': records,
                 'population': population, 'unresolved': population[start + len(records):]},
                indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == '__main__':
    main()
