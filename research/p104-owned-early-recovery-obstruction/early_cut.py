"""Exact favorable relaxation for a single coframed correction before MOVE42500."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm
from time import monotonic


ROOT = Path(__file__).resolve().parent
ROLE, INIT, CUT = 1533, 38139, 42500
CHART = 1031
WORD_PAYLOAD = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
GATE_HASH = 'aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9'


def value(row, assignment):
    return sum((coefficient * assignment.get(index, 0) for index, coefficient in row.items()), Fraction(0))


def separate(pivots, remainder):
    # Echelon rows use their smallest nonzero column as a unit pivot.
    # Activate one free column of the nonzero target remainder, then solve
    # the homogeneous bank equations for the pivot coordinates.
    free = min(remainder)
    assert free not in pivots
    assignment = {free: 1 / remainder[free]}
    for pivot, (row, _) in sorted(pivots.items(), reverse=True):
        coordinate = -value(row, assignment)
        if coordinate:
            assignment[pivot] = coordinate
    return assignment


def main():
    assert __debug__
    started = monotonic()
    alarm(30)
    assert sha256((ROOT / "gate.py").read_bytes()).hexdigest() == GATE_HASH
    helpers = run_path(str(ROOT / "gate.py"))
    pins = helpers["PINS"]
    add, basis, census, column, exact_cut_rows, representation = (helpers[name] for name in (
        "add", "basis", "census", "column", "exact_cut_rows", "representation",
    ))
    inputs = {name: (ROOT / name).read_bytes() for name in pins}
    assert {name: sha256(blob).hexdigest() for name, blob in inputs.items()} == pins
    payload = decompress(inputs['7481-WORD.json.gz'])
    assert sha256(payload).hexdigest() == WORD_PAYLOAD
    word = loads(payload)
    program = word['program']
    z = word['public']
    assert program[INIT] == ['INIT', ROLE, 597]
    assert program[CUT:CUT+4] == [
        ['MOVE', ROLE, CHART, 591, True], ['SCALE', ROLE, '-1/2', 591],
        ['ADD', 901, ROLE, '1', 591], ['CLEAR', ROLE, 591],
    ]
    assert loads(inputs['7113-CALLER.json'])['stages'] == 17
    _, active, _ = census(word, CUT)
    peers = sorted(role for role, chart in active.items() if chart == CHART)
    old = exact_cut_rows(program[:CUT], peers, z)
    dirty, guards = column(program, INIT, CUT, ROLE)
    assert ROLE in peers and 901 in active and active[901] == 591
    assert set(dirty) <= set(peers)
    bank = [row.copy() for row in old]
    for role, row in zip(peers, bank):
        add(row, z, dirty.get(role, Fraction(0)))
    basis_rows = basis(bank)
    outward = {index: -coefficient / 2 for index, coefficient in old[peers.index(ROLE)].items()}
    targets = [('recover', {z: Fraction(1)}), ('outward_ADD42502', outward)]
    targets.extend((str(role), row) for role, row in zip(peers, old))
    solutions = {}
    obstructions = {}
    for label, target in targets:
        remainder, coefficients = representation(basis_rows, target)
        if not remainder:
            assert all(value(target, {j: 1}) == sum(c * bank[i].get(j, 0) for i, c in coefficients.items())
                       for j in set(target).union(*(bank[i] for i in coefficients)))
            solutions[label] = coefficients
            continue
        assignment = separate(basis_rows, remainder)
        assert all(value(row, assignment) == 0 for row in bank)
        assert value(target, assignment) == 1
        obstructions[label] = assignment
    control = separate(basis([{0: Fraction(1), 1: Fraction(1)}]), {1: Fraction(1)})
    assert control == {0: Fraction(-1), 1: Fraction(1)}
    output = {
        'case': [ROLE, INIT, CUT, CHART], 'case_cap': 1, 'runner_cap_seconds': 30,
        'extra_coordinate': z, 'coframe': peers, 'dirty_column': dirty,
        'changed_INIT_COPY_guards': guards, 'bank_rank': len(basis_rows),
        'old_rank': len(basis(old)), 'rank_with_recovery': len(basis(bank + [targets[0][1]])),
        'source_rows': bank, 'target_rows': dict(targets),
        'representations': solutions, 'separating_inputs': obstructions,
        'status': 'EXACT_EARLY_CUT_EXCLUSION' if obstructions or guards else 'RATIONAL_GATE_SURVIVES',
    }
    print(dumps(output, indent=2, sort_keys=True, default=str))
    assert monotonic() - started < 30
    alarm(0)


if __name__ == '__main__':
    main()
