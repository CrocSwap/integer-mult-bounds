"""Test same-clock recovery on the sole earlier exact-endpoint carrier."""
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
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-PRICE.json": "1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R141-REVERSE.json": "508b66c75a45f43b7d231071787d5737feda0505f9d8e633306b19c3423ebad9",
    "inputs/aggregate.py": "8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}
WORD = "inputs/7334-WORD.json.gz"
u, m, f, h, A, B = 36647, 45647, 988, 1540, 260, 1091


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def timeout(*_):
    raise TimeoutError("20-second exact cap")


def touches(event, role):
    return event[1] == role or (event[0] in ("ADD", "COPY") and event[2] == role)


def main():
    assert __debug__ and argv[1:] in ([], ["--price-only"])
    data = {path: checked(path) for path in PINS if path != WORD}
    quote = loads(data["inputs/R137-PRICE.json"])
    prior = loads(data["inputs/R141-REVERSE.json"])
    assert prior["counts"][-1] == [m, 1, 1] and not prior["eligible"]
    one = quote["one"]["1"]
    assert one["paid_delta"] == {"1": -17} and one["productive_delta"] == {}
    assert one["gross"] == ["17", "17"] and Fraction(one["complete_probe"][0]) > 0
    price = dict(key=[m, h, u, f, A, B], head=quote["head"], caller=quote["caller"],
                 one=one, case_cap=1, event_cap=76466, runner_seconds=20, pins=PINS)
    if argv[1:]:
        print(dumps(price, indent=2, sort_keys=True))
        return

    signal(SIGALRM, timeout)
    alarm(20)
    deadline = monotonic() + 20
    payload = decompress(checked(WORD))
    assert sha256(payload).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(payload)
    tape = word["program"]
    assert len(tape) == 76466 and f < word["public"] <= h
    assert tape[u] == ["MOVE", f, A, B, False] and tape[m] == ["MOVE", h, A, B, True]
    assert tape[u + 1][0:3] == ["ADD", 862, f]
    assert tape[m + 1][0:3] == ["ADD", 756, h]
    assert not any(touches(event, h) for event in tape[u:m])
    state = word["initial"][:] + [None] * word["owned_fields"]
    for op, dest, *args in tape[:u]:
        if op in ("INIT", "MOVE"):
            state[dest] = args[-1] if op == "INIT" else args[1]
        elif op == "CLEAR":
            state[dest] = None
    assert state[f] == state[h] == A
    bank_roles = [role for role, chart in enumerate(state) if chart == B]
    helper = run_path(str(ROOT / "inputs/donor_span.py"))
    algebra = run_path(str(ROOT / "inputs/aggregate.py"))
    tests = algebra["controls"](helper)
    banks, targets = helper["snapshot"](word, {u: {(B, h)}}, {u: {f}}, deadline)
    assert set(banks) == {(u, B, h)} and (u, f) in targets
    bank = banks[u, B, h]
    assert set(bank) <= set(bank_roles)
    source = targets[u, f]
    result = algebra["exact_span"](source, bank, deadline, helper)
    if result is None:
        timeout()
    alarm(0)
    receipt = dict(price=price, bank_roles=bank_roles, nonzero_roles=sorted(bank),
                   source={i: str(v) for i, v in source.items()}, controls=tests, result=result)
    print(dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
