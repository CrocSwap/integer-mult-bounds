"""Test the two frozen cocharted banks for one owned two-write aggregate."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "08a403b6c8d5a3332212042ec69624ab5cf343fb7b6aa6e94f42583653f77912",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return data


def touches(event, owner):
    return owner in event[1:3] if event[0] in ("ADD", "COPY") else event[1] == owner


def legal(value):
    return (value != 0 and value.denominator.bit_count() == 1 and value.denominator <= 2**25
            and abs(value.numerator).bit_length() <= 24 and abs(value) + 1 < 2**16)


def stop(*_):
    raise TimeoutError("20-second hard cap")


def test_bank(bank, owner, owner_row, aggregate, engine, deadline):
    assert owner not in bank
    bank = bank | {owner: owner_row}
    axes = set().union(*(row.keys() for row in bank.values()))
    absent = next((i for i in sorted(aggregate) if i not in axes), None)
    if absent is not None:
        return {"status": "coordinate exclusion", "witness": [absent, str(aggregate[absent])]}
    exact = engine["solve"](aggregate, bank, deadline)
    if exact is None:
        raise TimeoutError("exact rational fallback cap")
    match = exact["matching_coefficients"]
    if match is None:
        return {"status": "rational exclusion", "exact": exact}
    donor = {int(r): Fraction(v) for r, v in match.items()}
    scale = 1 + donor.pop(owner, Fraction(0))
    eligible = len(donor) <= 2 and all(legal(v) for v in donor.values()) and (scale == 1 or legal(scale))
    return {"status": "exact coefficient survivor" if eligible else "coefficient gate unresolved",
            "exact": exact, "destination_scale": str(scale)}


def main():
    assert __debug__
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    checked("inputs/donor_span.py")
    engine = run_path(str(ROOT / "inputs/donor_span.py"))
    controls = engine["controls"]()
    cancellation = {4: Fraction(1, 2)}
    engine["axpy"](cancellation, {4: Fraction(1)}, Fraction(-1, 2))
    assert not cancellation and legal(Fraction(1, 4)) and not legal(Fraction(1, 3))
    controls.append("signed two-write cancellation and coefficient gate")
    if argv[1:] == ["--controls-only"]:
        print(dumps({"controls": controls, "frozen_bank_cuts": price["bank_cuts"]}, sort_keys=True))
        return 0
    assert not argv[1:]
    signal(SIGALRM, stop)
    alarm(20)
    deadline = monotonic() + 18
    results, aggregate, old_adds = [], {}, []
    timeout = None
    try:
        payload = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload, object_pairs_hook=unique)
        tape = word["program"]
        assert len(tape) == price["caps"]["events"]
        row = price["row"]
        f, g, owner = row["key"]
        a, b, c = row["charts"]
        birth, clear = row["lifetime"]
        assert owner >= word["public"] and birth < f < g < clear
        assert tape[birth][:2] == ["INIT", owner] and tape[clear][:2] == ["CLEAR", owner]
        assert tape[f] == ["MOVE", owner, a, b, True] and tape[g] == ["MOVE", owner, b, c, True]
        assert [t for t in range(birth + 1, clear) if tape[t][:2] == ["INIT", owner]
                or tape[t][:2] == ["CLEAR", owner]] == []
        times = [t for t in range(f + 1, g) if touches(tape[t], owner)]
        assert times == [41997, 44241]
        requirements, targets = defaultdict(set), defaultdict(set)
        targets[f].add(owner)
        for cut, chart in price["bank_cuts"]:
            requirements[cut].add((chart, owner))
        for t in times:
            op, dest, source, coefficient, chart = tape[t]
            assert op == "ADD" and dest == owner and source != owner and chart == b
            old_adds.append([t, tape[t]])
            requirements[t].add((b, -1))
            targets[t].add(source)
        banks, values = engine["snapshot"](word, requirements, targets, deadline)
        for t, (_, _, source, coefficient, _) in old_adds:
            if (t, source) not in values:
                raise TimeoutError("old signed source snapshot cap")
            assert banks[t, b, -1][source] == values[t, source]
            engine["axpy"](aggregate, values[t, source], Fraction(coefficient))
        for cut, chart in price["bank_cuts"]:
            if (cut, chart, owner) not in banks or (f, owner) not in values or monotonic() >= deadline:
                raise TimeoutError("endpoint snapshot or exact span cap")
            bank = banks[cut, chart, owner]
            proof = test_bank(bank, owner, values[f, owner], aggregate, engine, deadline)
            results.append({"key": [cut, chart], "read_only_donors": sorted(bank),
                            "old_owner_diagonal_clock": f, **proof})
    except TimeoutError as error:
        timeout = str(error)
    finally:
        alarm(0)
    completed = [r["key"] for r in results]
    print(dumps({
        "pins": PINS, "controls": controls, "head": price["head"], "caller": price["caller"],
        "old_adds": old_adds, "aggregate": {i: str(v) for i, v in aggregate.items()},
        "results": results, "unvisited": [k for k in price["bank_cuts"] if k not in completed],
        "timeout": timeout,
    }, sort_keys=True, indent=2))
    return 124 if timeout else 0


if __name__ == "__main__":
    raise SystemExit(main())
