"""Check one exact same-frame input functional for the role-1451 split."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

INPUTS = Path(__file__).resolve().parent
CUT = 39826
BANK = [1451, 1495, 1501]
INITIAL = [1451, 1495]


def timeout(_signal, _frame):
    print('{"status":"UNRESOLVED_TIMEOUT","case_cap":1,"runner_cap_seconds":30}')
    raise SystemExit(124)


def solve(constraints, pivot_value):
    pivots = {}
    for key, (left, right, value) in constraints.items():
        row = [left, right, value]
        provenance = {key: Q(1)}
        for column, (prior, sources) in sorted(pivots.items()):
            scale = row[column]
            row = [a - scale * b for a, b in zip(row, prior)]
            for source, coefficient in sources.items():
                provenance[source] = provenance.get(source, Q(0)) - scale * coefficient
        column = next((i for i in range(2) if row[i]), None)
        if column is None:
            if row[2]:
                witness = {k: v for k, v in provenance.items() if v}
                assert [sum(w * constraints[k][i] for k, w in witness.items())
                        for i in range(3)] == row
                return None, {'constraints': witness, 'contradiction': row[2]}
            continue
        divisor = row[column]
        pivots[column] = ([x / divisor for x in row],
                          {k: v / divisor for k, v in provenance.items() if v})
    free = [column for column in range(2) if column not in pivots]
    trials = [[Q(0), Q(0)]] + [[Q(i == j) for i in range(2)] for j in free]
    for values in trials:
        for column, (row, _) in sorted(pivots.items(), reverse=True):
            values[column] = row[2] - sum(row[i] * values[i] for i in range(column + 1, 2))
        assert all(a * values[0] + b * values[1] == rhs for a, b, rhs in constraints.values())
        constant, left, right = pivot_value
        coefficient = constant + left * values[0] + right * values[1]
        if coefficient:
            return values, {'coefficient_1451': coefficient, 'normalizer': 1 / coefficient}
    return None, {'all_affine_basis_solutions_have_zero_1451': trials}


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    gate = INPUTS / 'gate.py'
    assert sha256(gate.read_bytes()).hexdigest() == 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'
    helpers = run_path(str(gate))
    raw = (INPUTS / '7481-WORD.json.gz').read_bytes()
    assert sha256(raw).hexdigest() == helpers['PINS']['7481-WORD.json.gz']
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(payload)
    tape = word['program']
    assert tape[CUT - 1:CUT + 1] == [['ADD', 1451, 1495, '-1', 737], ['MOVE', 1495, 737, 738, False]]
    assert tape[37945] == ['MOVE', 1451, 595, 737, False]
    assert tape[39877] == ['MOVE', 1451, 737, 529, False]
    assert [role for role, chart in enumerate(word['initial']) if chart == 595] == INITIAL
    _, active, _ = helpers['census'](word, CUT)
    assert sorted(role for role, chart in active.items() if chart == 737) == BANK
    a, b, c = helpers['exact_cut_rows'](tape[:CUT], BANK, word['public'])
    keys = sorted((set(a) | set(b) | set(c)) - set(INITIAL))
    constraints = {key: (Q(b.get(key, 0)), Q(c.get(key, 0)), -Q(a.get(key, 0))) for key in keys}
    solution, witness = solve(constraints, tuple(Q(row.get(1451, 0)) for row in (a, b, c)))
    output = {'status': 'INPUT_GATE_SURVIVES' if solution is not None else 'FIXED_INPUT_GATE_EXCLUDED',
              'cut': CUT, 'bank': BANK, 'allowed_initial': INITIAL, 'case_cap': 1,
              'runner_cap_seconds': 30, 'solution_uv': solution, 'evidence': witness}
    print(dumps(output, indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == '__main__':
    main()
