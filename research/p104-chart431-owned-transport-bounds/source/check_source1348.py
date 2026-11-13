"""One-cut gate for pre-encoding old provider 1513 onto the existing 1348 route."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

CUT, OLD_SOURCE, ARRIVAL = 34566, 34527, 1348
PINS = {
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
}
CASE = "7481:1348:pre34566:chart3:old1513@34527"


def cap(_signal, _frame):
    raise SystemExit(124)


def probe_forward(tape, direction, public):
    active = {i: Q(v) for i, v in direction.items()}
    assert all(i < public for i in active)
    old_provider = None
    for clock, (op, dest, *args) in enumerate(tape[:CUT]):
        if clock == OLD_SOURCE:
            old_provider = active.get(1513, Q(0))
        if op in ("CLEAR", "INIT", "COPY"):
            if op in ("INIT", "COPY"):
                assert not active.get(dest)
            active.pop(dest, None)
        if op in ("ADD", "COPY"):
            active[dest] = active.get(dest, Q(0)) + Q(args[1]) * active.get(args[0], Q(0))
        elif op == "SCALE":
            active[dest] = Q(args[0]) * active.get(dest, Q(0))
        else:
            assert op in ("MOVE", "CLEAR", "INIT")
    assert old_provider is not None
    return active, old_provider


def solve(engine, tape, bank, public):
    read = engine["exact_cut_rows"]
    target, = read(tape[:OLD_SOURCE], [1513], public)
    rows = read(tape[:CUT], bank, public)
    pivots = engine["basis"](rows)
    residual, coefficients = engine["representation"](pivots, target)
    if not residual:
        return {}, {bank[i]: v for i, v in coefficients.items()}
    probe = {min(residual): Q(1)}
    for pivot, (row, _) in sorted(pivots.items(), reverse=True):
        value = -sum(coefficient * probe.get(role, 0)
                     for role, coefficient in row.items() if role != pivot)
        if value:
            probe[pivot] = value
    return probe, {}


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("reverse", "probe-first"), required=True)
    parser.add_argument("--inputs", type=Path, default=Path(__file__).resolve().parents[1] / "inputs")
    args = parser.parse_args()
    signal(SIGALRM, cap)
    alarm(30)
    paths = {name: args.inputs / name for name in PINS}
    assert {name: sha256(path.read_bytes()).hexdigest() for name, path in paths.items()} == PINS
    engine = run_path(str(paths["gate.py"]))
    raw = decompress(paths["7481-WORD.json.gz"].read_bytes())
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    tape = word["program"]
    assert tape[OLD_SOURCE] == ["ADD", 1518, 1513, "1", 243]
    assert tape[CUT:CUT+3] == [["MOVE", 1348, 3, 431, False],
                             ["ADD", 1348, 1137, "4", 431],
                             ["ADD", 375, 1507, "-4", 431]]
    assert word["final"][ARRIVAL] == 431
    _, charts, _ = engine["census"](word, CUT)
    bank = sorted(role for role, chart in charts.items() if chart == 3)
    assert ARRIVAL in bank
    witness, representation = {}, {}
    forward_response = None
    if args.method == "probe-first":
        values, u = probe_forward(tape, {2: 1}, word["public"])
        if u and all(not values.get(role) for role in bank):
            witness = {2: 1}
            forward_response = u
    if not witness:
        witness, representation = solve(engine, tape, bank, word["public"])
    if witness and forward_response is None:
        values, u = probe_forward(tape, witness, word["public"])
        assert u and all(not values.get(role) for role in bank)
        forward_response = u
    print(dumps({"case_id": CASE, "method": args.method, "cap_seconds": 30,
                 "case_cap": 1, "bank": bank, "witness": witness,
                 "old_u_response": forward_response, "representation": representation,
                 "decision": "FIXED_SOURCE_BANK_EXCLUDED" if witness else "SOURCE_SUPPORT_PASSES"},
                sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
