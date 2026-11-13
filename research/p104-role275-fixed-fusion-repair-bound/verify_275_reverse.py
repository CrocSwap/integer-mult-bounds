"""Independently recover input-100 coefficients by reverse tape action."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

CUT = 31438
ROOT = Path(__file__).resolve().parent


def timeout(_signal, _frame):
    raise SystemExit(124)


def reverse_row(tape, role):
    weights = {role: Q(1)}
    for op, dst, *args in reversed(tape):
        if dst not in weights or op == "MOVE":
            continue
        coefficient = weights[dst]
        if op in ("INIT", "CLEAR", "COPY"):
            del weights[dst]
        if op == "SCALE":
            weights[dst] *= Q(args[0])
        if op in ("ADD", "COPY"):
            src, factor, _ = args
            value = weights.get(src, Q(0)) + coefficient * Q(factor)
            if value:
                weights[src] = value
            else:
                weights.pop(src, None)
    return weights


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    blob = (ROOT / "7481-WORD.json.gz").read_bytes()
    assert sha256(blob).hexdigest() == "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
    raw = decompress(blob)
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    for op, role, *args in tape[:CUT]:
        if op == "INIT":
            active[role] = args[0]
        elif op == "CLEAR":
            del active[role]
        elif op == "MOVE":
            active[role] = args[1]
    bank = sorted(role for role, frame in active.items() if frame == 3)
    assert len(bank) == 898
    assert tape[31438] == ["MOVE", 274, 3, 93, False]
    assert tape[31439] == ["ADD", 274, 100, "1", 93]
    assert tape[31442] == ["ADD", 275, 274, "1", 93]
    donor = reverse_row(tape[:31439], 100)
    assert donor == {100: 1}
    prefix = tape[:CUT]
    coefficients = {role: reverse_row(prefix, role).get(100, 0) for role in bank}
    assert not any(coefficients.values())
    required = reverse_row(tape[:31442], 274).get(100, 0)
    assert required == 1
    print(dumps({"cut": CUT, "input": {100: 1}, "bank": bank, "nonzero_bank_coefficients": {},
                 "required_donor_value": required, "status": "PASS_REVERSE_SOURCE_SEPARATOR"},
                indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
