"""Check one paid bypass and its unchanged chart-549 read on exact #7481."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent
WORD_PIN = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
CANONICAL_PIN = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
APPLICATION_PIN = "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799"
PRICING_PIN = "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182"
GATE_PIN = "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"
ROLE, ENTRY, READ, EXIT = 235, 39248, 39249, 46996


def pin(name, digest):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == digest, name
    return raw


def span(frame):
    seen = {0}
    for column in frame:
        assert column not in seen
        seen |= {column ^ old for old in seen}
    return seen


def value(row, assignment):
    return sum(c * assignment.get(j, 0) for j, c in row.items())


def main():
    assert __debug__
    alarm(30)
    raw = decompress(pin("7481-WORD.json.gz", WORD_PIN))
    assert sha256(raw).hexdigest() == CANONICAL_PIN
    word = loads(raw)
    app = loads(pin("7481-APPLICATION.json", APPLICATION_PIN))
    pin("pricing.py", PRICING_PIN)
    pin("gate.py", GATE_PIN)
    price = run_path(str(ROOT / "pricing.py"))["power_bounds"]
    helpers = run_path(str(ROOT / "gate.py"))
    tape = word["program"]
    assert tape[ENTRY] == ["MOVE", ROLE, 550, 549, False]
    assert tape[READ] == ["ADD", 173, ROLE, "-1/2", 549]
    assert tape[EXIT] == ["MOVE", ROLE, 549, 127, False]
    touches = [clock for clock in range(ENTRY + 1, EXIT)
               if tape[clock][1] == ROLE or (
                   tape[clock][0] in {"ADD", "COPY"} and tape[clock][2] == ROLE)]
    assert touches == [READ]
    first, middle, last = (word["frames"][chart] for chart in (550, 549, 127))
    assert span(first) < span(middle) < span(last)
    assert (len(first), len(middle), len(last)) == (3, 7, 9)
    _, live, old_paid = helpers["census"](word, READ)
    bank = sorted(role for role, chart in live.items() if chart == 549 and role != ROLE)
    assert bank == [173, 881, 937, 999, 1549]
    old_rows = helpers["exact_cut_rows"](tape[:READ], bank + [ROLE], word["public"])
    bank_rows, read_row = old_rows[:-1], old_rows[-1]
    assert bank_rows[-1] == {}
    pivots = helpers["basis"](bank_rows)
    missing, coefficients = helpers["representation"](pivots, read_row)
    known_row, _ = helpers["representation"](pivots, bank_rows[0])
    assert not known_row
    witness = None
    if missing:
        index = min(missing)
        assert index not in pivots
        witness = {index: Fraction(1)}
        for pivot, (row, _) in sorted(pivots.items(), reverse=True):
            assert row[pivot] == 1 and min(row) == pivot
            result = -sum(c * witness.get(j, 0) for j, c in row.items() if j != pivot)
            if result:
                witness[pivot] = result
        assert all(value(row, witness) == 0 for row in bank_rows)
        assert value(read_row, witness) != 0
    else:
        assert all(read_row.get(j, 0) == sum(
            coef * bank_rows[i].get(j, 0) for i, coef in coefficients.items()
        ) for j in range(word["public"]))
    low, high = map(Fraction, app["directed_crossing_bracket"])
    lower = 17 * (price(4, high)[0] + price(2, high)[0] - price(6, low)[1])
    upper = 17 * (price(4, low)[1] + price(2, low)[1] - price(6, high)[0])
    assert Fraction("0.2355") < lower <= upper < Fraction("0.2356")
    new_paid = dict(old_paid)
    new_paid[2] -= 1
    new_paid[4] -= 1
    new_paid[6] += 1
    result = {
        "decision": "excluded at fixed bank" if missing else "rational span survives",
        "completed_cases": 1,
        "runner_cap_seconds": 30,
        "word_sha256": WORD_PIN,
        "role": ROLE,
        "clocks": [ENTRY, READ, EXIT],
        "charts": [550, 549, 127],
        "bank": bank,
        "bank_rank": len(pivots),
        "union_rank": len(helpers["basis"](old_rows)),
        "exact_separating_old_input": witness,
        "separating_read_value": None if witness is None else value(read_row, witness),
        "rational_coefficients_by_bank_role": None if missing else {
            bank[i]: coefficient for i, coefficient in coefficients.items()},
        "optimistic_signed_saving": [lower, upper],
        "conditional_native_paid_histogram": new_paid,
        "conditional_signed_paid_delta": {2: -17, 4: -17, 6: 17},
        "conditional_signed_productive_delta": {},
    }
    alarm(0)
    print(dumps(result, default=str, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
