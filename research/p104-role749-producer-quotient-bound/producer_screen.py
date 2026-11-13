"""Exact one-case fixed-bank owned transfer test on #7481."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent


def timeout(_signal, _frame):
    raise SystemExit(124)


def evaluate(row, probe):
    return sum(value * probe.get(index, 0) for index, value in row.items())


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    helper_path = ROOT / 'gate.py'
    assert sha256(helper_path.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    helper = run_path(str(helper_path))
    inputs = {name: (ROOT / name).read_bytes() for name in helper['PINS']}
    assert {name: sha256(raw).hexdigest() for name, raw in inputs.items()} == helper['PINS']
    raw = decompress(inputs['7481-WORD.json.gz'])
    assert sha256(raw).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(raw)
    app = loads(inputs['7481-APPLICATION.json'])
    caller = loads(inputs['7113-CALLER.json'])
    power = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    rows, basis, census = (helper[key] for key in ('exact_cut_rows', 'basis', 'census'))
    tape, public = word['program'], word['public']
    assert tape[32222] == ['MOVE', 749, 3, 260, False]
    assert tape[35152:35155] == [['MOVE', 1541, 599, 260, True], ['ADD', 749, 1541, '1', 260],
                                 ['ADD', 1540, 749, '1/4', 260]]
    assert tape[35155] == ['ADD', 1540, 1393, '-1/4', 260]
    assert len(word['frames'][260]) - len(word['frames'][3]) == 3
    assert len(word['frames'][599]) - len(word['frames'][3]) == 1
    assert len(word['frames'][260]) - len(word['frames'][599]) == 2
    _, active, _ = census(word, 35152)
    bank = [role for role, chart in active.items() if chart == 260 and role not in (749, 1540, 1541)]
    old = rows(tape[:35152], bank, public)
    targets = rows(tape[:35155], [749, 1540], public)
    rank, union = len(basis(old)), len(basis(old + targets))
    assert bank == [226, 988, 990, 1345, 1393, 1506, 1514] and (rank, union) == (6, 8)
    probes = [{749: Fraction(1)}, {270: Fraction(-3, 4), 317: Fraction(1)}]
    assert not any(evaluate(row, probe) for row in old for probe in probes)
    values = [[evaluate(row, probe) for row in targets] for probe in probes]
    assert values == [[1, 0], [0, Fraction(3, 4)]]
    lo, hi = map(Fraction, app['directed_crossing_bracket'])
    copies = caller['stages']
    assert copies == sum(event[0] == 'J' for event in caller['events']) == 17
    gross = [copies * (power(3, hi)[0] - 1), copies * (power(3, lo)[1] - 1)]
    assert 33 < gross[0] <= gross[1] < 34
    receipt = {'status': 'ONE_LATE_SCALAR_EXCLUDED', 'receiver': bank, 'rank': rank, 'union': union,
               'probes': probes, 'target_values': values, 'gross_before_repairs': gross, 'case_cap': 1}
    print(dumps(receipt, indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == '__main__':
    main()
