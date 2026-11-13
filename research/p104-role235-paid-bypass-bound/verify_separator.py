"""Verify the exact role-235 chart-549 separation by literal signed forward action."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm
from sys import argv

ROOT = Path(__file__).resolve().parent
WORD_HASH = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
RAW_HASH = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
ROLE, CUT, CHART = 235, 39249, 549


def evaluate(word, assignment):
    public = word['public']
    values = [assignment.get(role, Fraction()) for role in range(public)] + [None] * word['owned_fields']
    charts = word['initial'] + [None] * word['owned_fields']
    for clock, (op, role, *args) in enumerate(word['program'][:CUT]):
        if op == 'INIT':
            assert charts[role] is None and values[role] is None
            values[role] = Fraction()
            charts[role] = args[0]
        elif op == 'CLEAR':
            assert charts[role] == args[0]
            values[role] = None
            charts[role] = None
        elif op == 'MOVE':
            assert charts[role] == args[0] and (role >= public) == args[2]
            charts[role] = args[1]
        elif op == 'SCALE':
            assert charts[role] == args[1]
            values[role] *= Fraction(args[0])
        elif op in ('ADD', 'COPY'):
            donor, weight, chart = args
            assert charts[role] == charts[donor] == chart
            if op == 'COPY':
                assert not values[role], (clock, role)
            values[role] += Fraction(weight) * values[donor]
        else:
            raise AssertionError(op)
    assert charts[ROLE] == CHART
    bank = {role: values[role] for role, chart in enumerate(charts) if chart == CHART and role != ROLE}
    return bank, -values[ROLE] / 2


def verify(word, assignment):
    bank, contribution = evaluate(word, assignment)
    assert set(bank) == {173, 881, 937, 999, 1549}
    assert not any(bank.values()) and contribution
    return bank, contribution


def main():
    assert __debug__
    alarm(30)
    payload = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(payload).hexdigest() == WORD_HASH
    raw = decompress(payload)
    assert sha256(raw).hexdigest() == RAW_HASH
    word = loads(raw)
    assert word['program'][CUT] == ['ADD', 173, ROLE, '-1/2', CHART]
    assignment = {int(role): Fraction(value) for role, value in loads(Path(argv[1]).read_bytes()).items()}
    assert all(0 <= role < word['public'] for role in assignment)
    bank, contribution = verify(word, assignment)
    assert verify(word, {role: -value for role, value in assignment.items()}) == (bank, -contribution)
    zero_bank, zero_contribution = evaluate(word, {})
    assert zero_bank == bank and zero_contribution == 0
    print(dumps({'status': 'EXACT_SIGNED_SEPARATOR', 'role': ROLE, 'cut': CUT, 'chart': CHART,
                 'old_inputs': assignment, 'bank': bank, 'required_old_ADD_delta': contribution},
                default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == '__main__':
    main()
