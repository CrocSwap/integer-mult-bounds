"""Exact unit-body control and single physical B2-sign test on one caller block."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

START, STOP, CAP = 1855, 2338, 30
EARLY, LATE = (1855, 1869), (2324, 2337)
PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def emit(**fields):
    print(json.dumps(fields, default=str, sort_keys=True), flush=True)


def forward(block, source, active_factors):
    column = [Q(role == source) for role in range(36, 72)]
    for clock, (_, op, role, *args) in enumerate(block, START):
        r = role-36
        if op == "ADD":
            column[r] += Q(args[1])*column[args[0]-36]
        elif op == "SWAP":
            s = args[0]-36
            column[r], column[s] = column[s], column[r]
        elif op == "SCALE":
            column[r] *= Q(args[0])
        else:
            assert op == "IDLE_ONE" and len(args) == 1
            if clock in active_factors:
                column[r] = -column[r]
    return column


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    root = Path(sys.argv[1]).resolve()
    completed = []

    def cap(_signum, _frame):
        emit(status="UNRESOLVED_CAP", cap_seconds=CAP, completed_columns=completed,
             unvisited_columns=[r for r in range(36,72) if r not in completed])
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, cap)
    signal.alarm(CAP)
    raw = {name:(root/name).read_bytes() for name in PINS}
    assert {name:sha256(data).hexdigest() for name,data in raw.items()} == PINS
    caller = json.loads(raw["7113-CALLER.json"])
    app = json.loads(raw["7481-APPLICATION.json"])
    assert app["source_head"] == "58a9d052143f5d85295ed2d0163591c47f89a331"
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert app["caller_sha256"] == PINS["7113-CALLER.json"]
    assert app["claim_decimal"] == "0.003647081039689"
    bank = caller["types"]["B"]
    ports = bank["ports"]
    assert bank["offset"] == bank["roles"] == 36 and ports == [15,17,27,34,35,42,47,55]
    tape = caller["events"]
    assert len(tape) == 4783 and caller["stages"] == 17
    early_mask, late_mask = list(range(2,9)), list(range(16,8,-1))
    assert tape[1855] == ["B","IDLE_ONE",36,early_mask]
    assert tape[1869] == ["B","IDLE_ONE",38,early_mask]
    assert tape[1887] == ["B","IDLE_ONE",36,list(range(3,9))]
    assert tape[2324] == ["B","IDLE_ONE",36,late_mask]
    assert tape[2337] == ["B","IDLE_ONE",37,late_mask]
    block = tape[START:STOP]
    assert all(event[0] == "B" for event in block)
    opcode_counts = Counter(event[1] for event in block)
    assert opcode_counts == {"ADD":405,"SWAP":38,"SCALE":26,"IDLE_ONE":14}
    old = {i for i,event in enumerate(block,START) if event[1]=="IDLE_ONE" and 2 in event[3]}
    assert old == set(EARLY)
    new = (old-set(EARLY)) | set(LATE)
    lo, hi = map(Q, app["directed_crossing_bracket"])
    H = run_path(str(root/"pricing.py"))["power_bounds"]
    gross = [16*(H(56,hi)[0]+H(64,hi)[0]-H(48,lo)[1]-H(72,lo)[1]),
             16*(H(56,lo)[1]+H(64,lo)[1]-H(48,hi)[0]-H(72,hi)[0])]
    assert Q("0.12311985005206546") <= gross[0] <= gross[1] <= Q("0.12311985005206547")
    emit(status="START", pins=PINS, window=[START,STOP], cap_seconds=CAP, q=1, b2=-1,
         other_bodies=1, tested_port=15, ports=ports, old_clocks=EARLY, new_clocks=LATE,
         signed_paid_delta={48:16,56:-16,64:-16,72:16}, productive_delta={},
         optimistic_gross_8_ports=gross, optimistic_gross_per_port=[x/8 for x in gross])
    witnesses = []
    omitted_control = False
    for source in range(36,72):
        absolute_old, absolute_new = (forward(block,source,c) for c in (old,new))
        if not omitted_control:
            omitted_control = absolute_old != forward(block,source,old-{1855})
        complete = all(a == b for a,b in zip(absolute_old,absolute_new,strict=True))
        if not complete and not witnesses:
            row = next(i for i,(a,b) in enumerate(zip(absolute_old,absolute_new,strict=True),36) if a!=b)
            witnesses.append(dict(input=source, first_output=row, old=absolute_old, edited=absolute_new))
        completed.append(source)
    # At unit bodies the two sets of sign-trigger clocks are both empty.
    assert old and new and old.isdisjoint(new) and omitted_control
    emit(status="EXCLUDED_FIXED_B2_RELOCATION" if witnesses else "B2_SIGN_SURVIVOR",
         tested_columns=completed, excluded_witnesses=witnesses, unit_bodies_both_sign_sets_empty=True,
         omitted_early_reflection_control=omitted_control,
         unresolved=[] if witnesses else ["all-body signed equality and complete physical invoice"])
    signal.alarm(0)


if __name__ == "__main__":
    main()
