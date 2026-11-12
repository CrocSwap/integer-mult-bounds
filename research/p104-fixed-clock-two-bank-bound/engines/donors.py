"""Test the two literal-clock cocharted donor banks for four fixed paid edits."""
from collections import Counter, defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "97df4e628a30f516862ef8acc1862ddfabfee1806fe046446c473edc8b0de009",
    "inputs/R116-PRICE.json": "8226a2b9c9240455d6fcdaf3a38929e3336e89f35aed3f15b81564f07ed8387f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def touches(event, role):
    return role in event[1:3] if event[0] in ("ADD", "COPY") else event[1] == role


def legal_dyadic(value):
    return (value != 0 and value.denominator.bit_count() == 1
            and value.denominator <= 2**25 and abs(value.numerator).bit_length() <= 24
            and abs(value) + 1 < 2**16)


def classify(row, values, banks, public, engine, deadline):
    key, clock, old_chart, chart, source, dest, coefficient = row
    target = values[clock, source]
    target = {i: Fraction(coefficient) * val for i, val in target.items()}
    occupied = banks[clock, chart, source]
    bank = {r: v for r, v in occupied.items() if r < public}
    if chart != old_chart:
        assert dest not in bank
        bank[dest] = values[clock, dest]
    assert source not in bank
    assert bank[dest] == values[clock, dest]
    old_bank = banks[clock, old_chart, -1]
    assert old_bank[source] == values[clock, source]
    assert old_bank[dest] == values[clock, dest]
    support = set().union(*(v.keys() for v in bank.values()))
    coordinate = next((i for i in sorted(target) if i not in support), None)
    result = {
        "key": key, "clock": clock, "source": source, "destination": dest,
        "old_chart": old_chart, "destination_chart": chart, "literal_coefficient": coefficient,
        "bank_roles": sorted(bank), "excluded_owned_roles": sorted(set(occupied) - set(bank)),
        "target_nnz": len(target),
    }
    if coordinate is not None:
        return dict(result, status="coordinate exclusion", witness=[coordinate, str(target[coordinate])])
    exact = engine["solve"](target, bank, deadline)
    if exact is None:
        return None
    if exact["matching_coefficients"] is None:
        return dict(result, status="rational exclusion", exact=exact)
    match = {int(role): Fraction(value) for role, value in exact["matching_coefficients"].items()}
    destination_scale = 1 + match.pop(dest, Fraction(0))
    if (len(match) <= 2 and all(legal_dyadic(value) for value in match.values())
            and (destination_scale == 1 or legal_dyadic(destination_scale))):
        return dict(result, status="legal exact coefficients", exact=exact,
                    destination_scale=str(destination_scale))
    return dict(result, status="coefficient gate unresolved", exact=exact,
                destination_scale=str(destination_scale))


def timeout(*_):
    raise TimeoutError("20-second runner cap")


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(20)
    deadline = monotonic() + 18
    requirements, targets = defaultdict(set), defaultdict(set)
    rows, results, controls = [], [], []
    reason = None
    try:
        price = loads(checked("inputs/R116-PRICE.json"), object_pairs_hook=unique)
        frozen = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
        assert frozen["limits"] == {"windows": 4, "banks": 8, "events": 76466, "seconds": 20}
        assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
        payload = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest() == price["payload_sha256"]
        word = loads(payload, object_pairs_hook=unique)
        tape, public = word["program"], word["public"]
        assert len(tape) == 76466 and public == 1501
        checked("inputs/donor_span.py")
        engine = run_path(str(ROOT / "inputs/donor_span.py"))
        controls = engine["controls"]()
        assert legal_dyadic(Fraction(1, 4)) and not legal_dyadic(Fraction(1, 3))
        for case in price["cases"]:
            f, g, mover = case["key"]
            a, b, c = case["charts"]
            peer = case["peer"]
            assert mover != peer and 0 <= mover < public and 0 <= peer < public
            assert tape[f] == ["MOVE", mover, a, b, False]
            assert tape[g] == ["MOVE", mover, b, c, False]
            assert not any(touches(event, mover) for event in tape[f + 3:g])
            for i, (clock, add) in enumerate(case["original_pair"], start=1):
                op, dest, source, coeff, old_chart = add
                assert op == "ADD" and {dest, source} == {mover, peer}
                assert tape[clock] == add and clock == f + i and old_chart == b
                chart = c if dest == mover else b
                requirements[clock].update(((chart, source), (b, -1)))
                targets[clock].update((source, dest))
                rows.append((case["key"], clock, b, chart, source, dest, coeff))
        assert len(rows) == len(requirements) == 8
        for row, pinned in zip(rows, frozen["banks"], strict=True):
            key, clock, old_chart, chart, source, dest, coeff = row
            assert pinned == {
                "key": [*key, clock], "source": source, "destination": dest,
                "old_coframe": old_chart, "new_coframe": chart, "coefficient": coeff,
                "exclude_other_operand": True, "include_destination_as_diagonal": True,
            }
        banks, values = engine["snapshot"](word, requirements, targets, deadline)
        for row in rows:
            _, clock, _, chart, source, dest, _ = row
            if monotonic() >= deadline or (clock, source) not in values:
                break
            assert (clock, dest) in values and (clock, chart, source) in banks
            entry = classify(row, values, banks, public, engine, deadline)
            if entry is None:
                break
            results.append(entry)
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    assert len(results) <= 8
    tested = {(tuple(r["key"]), r["clock"]) for r in results}
    unresolved = [[key, clock] for key, clock, *_ in rows if (tuple(key), clock) not in tested]
    unsupported = {tuple(r["key"]) for r in results if r["status"].endswith("exclusion")}
    viable = [key for key in {tuple(r["key"]) for r in results}
              if sum(tuple(r["key"]) == key and r["status"] == "legal exact coefficients"
                     for r in results) == 2]
    print(dumps({
        "pins": PINS, "caps": {"windows": 4, "banks": 8, "seconds": 20},
        "controls": controls + ["literal predecessor sources and destinations at both old clocks"],
        "results": results, "counts": Counter(r["status"] for r in results),
        "excluded_windows": sorted(unsupported), "viable_windows": sorted(viable),
        "unvisited_banks": unresolved, "unvisited_count": 8 - len(results),
        "timeout": reason,
    }, sort_keys=True, indent=2))
    if reason:
        raise SystemExit(124)


if __name__ == "__main__":
    main()
