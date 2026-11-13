"""Exact first-use gate for two co-encoded paid arrivals replacing owned1548."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

HERE = Path(__file__).resolve().parent
CASE = "owned1548-early-1197-1358-first-use-pre46664"
CUT = 46664
BANK = [913, 587, 1494]
TARGETS = [1197, 1358]
PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "integer_basis.py": "f7a8b29abde8b6c9f3ad3b55ecb1eba56ba2ac0211db2fac6a2ed294cd980943",
}
EVENTS = {
    37960: ["INIT", 1548, 529],
    39769: ["ADD", 1548, 913, "-1", 529],
    39778: ["ADD", 1548, 927, "-1/2", 529],
    39780: ["ADD", 1197, 913, "-1", 529],
    39781: ["ADD", 1197, 927, "-1", 529],
    39785: ["MOVE", 1548, 529, 531, True],
    39786: ["ADD", 1298, 1548, "-1/2", 531],
    39787: ["ADD", 1429, 1548, "-1/2", 531],
    39788: ["CLEAR", 1548, 531],
    45418: ["MOVE", 1197, 529, 127, False],
    45419: ["ADD", 1197, 587, "1", 127],
    45583: ["ADD", 1494, 913, "1/2", 529],
    45586: ["ADD", 1358, 1494, "-4", 529],
    46663: ["MOVE", 1429, 531, 127, False],
    46664: ["ADD", 1153, 1429, "1", 127],
    47223: ["MOVE", 1358, 529, 127, False],
    47224: ["ADD", 1075, 1358, "1", 127],
    47227: ["MOVE", 913, 529, 127, False],
    47722: ["MOVE", 1298, 531, 127, False],
    47723: ["ADD", 665, 1298, "1", 127],
    56017: ["ADD", 47, 1197, "4", 127],
}


def emit(record):
    print(json.dumps(record, default=str, sort_keys=True), flush=True)


def timeout(_sig, _frame):
    emit(dict(case=CASE, status="UNRESOLVED_CAP", unresolved=[CASE], cap_seconds=30))
    raise SystemExit(124)


def contacts(tape, role, start, stop):
    return [i for i in range(start, stop)
            if role in (tape[i][1:3] if tape[i][0] in ("ADD", "COPY") else tape[i][1:2])]


def evaluate(row, probe):
    return sum(value*probe.get(i, 0) for i, value in row.items())


def det(rows):
    (a,b,c),(d,e,f),(g,h,i) = rows
    return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(30)
    root = Path(sys.argv[1]).resolve()
    source = {name: ((HERE if name == "integer_basis.py" else root) / name).read_bytes() for name in PINS}
    assert {name: sha256(raw).hexdigest() for name, raw in source.items()} == PINS
    app = json.loads(source["7481-APPLICATION.json"])
    raw = decompress(source["7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == app["candidate_canonical_sha256"]
    word = json.loads(raw)
    caller = json.loads(source["7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    tape, public = word["program"], word["public"]
    assert all(tape[i] == event for i, event in EVENTS.items())
    assert contacts(tape, 1548, 0, len(tape)) == [37960,39769,39778,39785,39786,39787,39788]
    assert contacts(tape, 1197, 39782, 56017) == [45418,45419]
    assert contacts(tape, 1358, 45587, 47223) == []
    assert contacts(tape, 913, 45584, 47227) == []
    assert contacts(tape, 1298, 39787, 47722) == []
    assert contacts(tape, 1429, 39788, CUT) == [46663]
    protected = (set(word["live"]) | {r+112 for r in word["live"]} |
                 set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    assert len(protected) == 400 and 927 in protected
    assert not protected & {913,1197,1358,1298,1429}
    live = set()
    old_peak = new_peak = 0
    new_peak_first = None
    for clock, event in enumerate(tape):
        op, role = event[:2]
        if op == "INIT":
            assert role not in live
            live.add(role)
        elif op == "CLEAR":
            live.remove(role)
        old_peak = max(old_peak, len(live))
        edited = len(live) + (39788 <= clock <= 45586)
        if edited > new_peak:
            new_peak, new_peak_first = edited, clock
    assert not live and old_peak == 50 and new_peak == 51 and new_peak_first == 39811
    kit = run_path(str(root/"gate.py"))
    _, active, _ = kit["census"](word, CUT)
    assert {r: active[r] for r in BANK+TARGETS+[1298,1429]} == {
        913:529,587:127,1494:127,1197:127,1358:529,1298:531,1429:127}
    assert 1548 not in active
    read = kit["exact_cut_rows"]
    bank = read(tape[:CUT], BANK, public)
    old_a, old_b = read(tape[:CUT], TARGETS, public)
    u, = read(tape[:39785], [1548], public)
    a0, = read(tape[:39769], [913], public)
    b0, = read(tape[:39778], [927], public)
    historical = {}
    for row, factor in ((a0,-1),(b0,Q(-1,2))):
        for col, value in row.items():
            kit["add"](historical,col,factor*value)
    assert u == historical
    # This only tests the earliest correction. Later restore deadlines cannot
    # make u available before an already required outward response.
    separate = run_path(str(HERE/"integer_basis.py"))["separator"]
    targets = [old_a,old_b,u]
    pivot_rows, probes = bank.copy(), []
    for target in targets:
        probe, _ = separate(pivot_rows,target)
        if probe is not None:
            assert all(not evaluate(row,probe) for row in pivot_rows)
            assert evaluate(target,probe)
            pivot_rows.append(target)
            probes.append(probe)
    matrix = [[evaluate(target,probe) for target in targets] for probe in probes]
    rank = len(probes)
    result = dict(case=CASE, cut=CUT, tested=1, cap_seconds=30, donors=BANK,
                  carried_original_rows=TARGETS, first_use_target="u", quotient_rank=rank,
                  probes=probes, response_matrix=matrix, early_owner_liveness=[50,51],
                  first_edited_peak_old_clock=new_peak_first, signed_paid_delta={1:-17},
                  signed_productive_delta={}, gross_raw=17, pins=PINS)
    if rank == 3:
        result.update(status="EXACT_FIRST_USE_RANK3_EXCLUSION", unresolved=[], determinant=det(matrix))
        assert result["determinant"]
    else:
        # Find the old-carrier dependence needed by a constructive first-use
        # calculation. Deferred carrier restoration is a separate gate.
        witnesses = []
        for i,target in enumerate(targets):
            basis = kit["basis"](bank+targets[:i])
            residual, coeffs = kit["representation"](basis,target)
            if not residual:
                witnesses.append(dict(target=i, preceding_bank_and_target_weights=coeffs))
        result.update(status="FIRST_USE_RANK_GATE_SURVIVOR_STAGGERED_RESTORE_OPEN",
                      unresolved=[CASE], exact_dependencies=witnesses)
    emit(result)
    signal.alarm(0)


if __name__ == "__main__":
    main()
