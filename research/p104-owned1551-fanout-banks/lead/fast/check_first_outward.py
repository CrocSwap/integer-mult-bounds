"""Check one fixed-chart repair before the first outward read of a fanout recipient."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[2] / "inputs"
CUT, SOURCE = 47956, 45636
WRITES = {45639: 817, 45641: 790, 45643: 873, 45646: 1497, 45649: 878, 45651: 833}
EARLY_RECIPIENTS = {873, 878}


def cap(_signal, _frame):
    raise SystemExit(124)


def main():
    assert __debug__
    signal(SIGALRM, cap)
    alarm(30)
    helper = ROOT / "gate.py"
    assert sha256(helper.read_bytes()).hexdigest() == "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"
    engine = run_path(str(helper))
    raw = (ROOT / "7481-WORD.json.gz").read_bytes()
    assert sha256(raw).hexdigest() == engine["PINS"]["7481-WORD.json.gz"]
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(payload)
    tape = word["program"]
    assert tape[SOURCE] == ["ADD", 1551, 862, "-1", 1091]
    assert tape[CUT - 1:CUT + 1] == [
        ["MOVE", 878, 267, 127, False], ["ADD", 549, 878, "1", 127],
    ]
    for clock, role in WRITES.items():
        assert tape[clock] == ["ADD", role, 1551, "1", 267]
    for clock in range(min(WRITES) + 1, CUT):
        op, dst, *parts = tape[clock]
        if op in ("ADD", "COPY") and parts[0] in WRITES.values():
            assert clock <= next(k for k,v in WRITES.items() if v == parts[0])
        if dst in WRITES.values() and clock > next(k for k,v in WRITES.items() if v == dst):
            assert op == "MOVE" or (clock == 46149 and tape[clock] == ["ADD",873,862,"1",127])
    _, live, _ = engine["census"](word, CUT)
    bank = sorted(role for role, chart in live.items() if chart == 127)
    assert len(bank) == 644 and set(bank).intersection(WRITES.values()) == EARLY_RECIPIENTS
    print(dumps({"stage": "authenticated_and_chronology_checked", "cut": CUT, "bank": bank}), flush=True)

    def forward(direction):
        values = {role: Q(value) for role, value in direction.items()}
        u = None
        for clock, (op, dst, *parts) in enumerate(tape[:CUT]):
            if clock == SOURCE:
                u = values.get(862, 0)
            if clock in WRITES:
                continue
            if op in ("CLEAR", "INIT", "COPY"):
                if op in ("INIT", "COPY"):
                    assert not values.get(dst, 0)
                values.pop(dst, None)
            if op in ("ADD", "COPY"):
                engine["add"](values, dst, Q(parts[1]) * values.get(parts[0], 0))
            elif op == "SCALE" and dst in values:
                values[dst] *= Q(parts[0])
        assert u is not None
        return u, [values.get(role, 0) for role in bank]

    probe = {230: -1, 547: 1}
    u, responses = forward(probe)
    if not u or any(responses):
        print(dumps({"stage": "prior_probe_inconclusive", "probe": probe, "old_source": str(u),
                     "edited_bank_nonzero_count": sum(map(bool, responses))}), flush=True)
        read = engine["exact_cut_rows"]
        target, = read(tape[:SOURCE], [862], word["public"])
        rows = read(tape[:CUT], bank, word["public"])
        for role, row in zip(bank, rows):
            if role in EARLY_RECIPIENTS:
                for coordinate, value in target.items():
                    engine["add"](row, coordinate, value)
        print(dumps({"stage": "full_bank_rows_reconstructed", "count": len(rows)}), flush=True)
        separate = run_path(str(Path(__file__).resolve().with_name("integer_basis.py")))["separator"]
        probe, rank = separate(rows, target)
        if probe is None:
            print(dumps({"status": "INCLUSION_DETECTED_COEFFICIENTS_PENDING", "pivot_count": rank}))
            alarm(0)
            return
        u, responses = forward(probe)
    assert u and not any(responses)
    print(dumps({"status": "FULL_FIXED_BANK_EXCLUDED", "case_count": 1, "cap_seconds": 30,
                 "cut": CUT, "probe": probe, "old_source_response": u,
                 "edited_bank_size": len(bank), "edited_bank_nonzero_count": 0}, default=str, sort_keys=True))
    alarm(0)


if __name__ == "__main__":
    main()
