"""Replay the staged owned1548 carrier schedule and first-use quotient gate."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CASE = "owned1548-early-1197-1358-first-use-pre46664"
OWNER, CUT, CAP = 1548, 46664, 30
FIRST_ENCODE, SECOND_ENCODE = 39781, 45586
ASCENT, DELETED_WRITES, CLEAR = 39785, (39786, 39787), 39788
CARRIERS, BANK, RECEIVERS = (1197, 1358), (913, 587, 1494), (1298, 1429)
ADVANCED = (47223, 47227, 47722)
READS = {46664: (1153, 1429), 47224: (1075, 1358), 47723: (665, 1298), 56017: (47, 1197)}


def emit(**result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def span(basis):
    out = {0}
    for vector in basis:
        assert vector not in out
        out |= {vector ^ x for x in out}
    return out


def contacts(tape, role, start, stop):
    return [i for i in range(start, stop) if tape[i][1] == role or
            tape[i][0] in ("ADD", "COPY") and tape[i][2] == role]


def chronology(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400 and 927 in protected
    assert not protected.intersection({913, *CARRIERS, *RECEIVERS})
    a, b, c = (span(word["frames"][chart]) for chart in (529, 531, 127))
    assert a < b < c and len(b) == 2 * len(a) and len(c) == 4 * len(a)
    assert tape[37960] == ["INIT", OWNER, 529]
    assert tape[39769] == ["ADD", OWNER, 913, "-1", 529]
    assert tape[39778] == ["ADD", OWNER, 927, "-1/2", 529]
    assert tape[FIRST_ENCODE] == ["ADD", 1197, 927, "-1", 529]
    assert tape[SECOND_ENCODE] == ["ADD", 1358, 1494, "-4", 529]
    assert tape[ASCENT:CLEAR + 1] == [
        ["MOVE", OWNER, 529, 531, True], ["ADD", 1298, OWNER, "-1/2", 531],
        ["ADD", 1429, OWNER, "-1/2", 531], ["CLEAR", OWNER, 531],
    ]
    assert [tape[i] for i in ADVANCED] == [
        ["MOVE", 1358, 529, 127, False], ["MOVE", 913, 529, 127, False], ["MOVE", 1298, 531, 127, False],
    ]
    for clock, (dst, donor) in READS.items():
        assert tape[clock] == ["ADD", dst, donor, "4" if clock == 56017 else "1", 127]
    owner = contacts(tape, OWNER, 0, len(tape))
    assert owner == [37960, 39769, 39778, ASCENT, *DELETED_WRITES, CLEAR]
    assert contacts(tape, 1197, FIRST_ENCODE + 1, 56018) == [45418, 45419, 56017]
    assert tape[45418:45420] == [["MOVE", 1197, 529, 127, False], ["ADD", 1197, 587, "1", 127]]
    assert contacts(tape, 1358, SECOND_ENCODE + 1, 47225) == [47223, 47224]
    assert contacts(tape, 913, 45584, 47227) == []
    assert contacts(tape, 1298, DELETED_WRITES[0], 47724) == [39786, 47722, 47723]
    assert contacts(tape, 1429, DELETED_WRITES[1], CUT + 1) == [39787, 46663, CUT]
    return {i: tape[i] for i in owner}


def add(left, right, factor=Q(1)):
    result = left.copy()
    for j, v in right.items():
        total = result.get(j, 0) + factor * v
        if total:
            result[j] = total
        else:
            result.pop(j, None)
    return result


def replay(word, initial, encode=None):
    active = dict(enumerate(word["initial"]))
    owners = {}
    rows = initial.copy()
    observed = {}
    guards = {"init": 0, "clear": 0, "copy": 0, "move": 0}
    retirement, copies, earlier_owned_moves = {}, {}, {}
    peak = (0, None)
    empty = {}

    def get(r):
        return rows.get(r, empty)

    def execute(event, clock, track_rows):
        op, dst, *args = event
        before = get(dst)
        if op == "INIT":
            assert dst >= word["public"] and dst not in active and dst not in owners and not before
            active[dst] = args[0]
            owners[dst] = clock
            guards["init"] += 1
        elif op == "CLEAR":
            assert dst in owners and active.pop(dst) == args[0]
            birth = owners.pop(dst)
            if track_rows:
                retirement[clock] = birth, dst, before
            rows.pop(dst, None)
            guards["clear"] += 1
        elif op == "MOVE":
            src, dest, owned = args
            assert src != dest and active[dst] == src and owned == (dst in owners) == (dst >= word["public"])
            active[dst] = dest
            guards["move"] += 1
            if owned and track_rows and clock < CUT:
                earlier_owned_moves[clock] = owners[dst], event, before
        else:
            assert op in ("ADD", "COPY", "SCALE")
            donor = dst if op == "SCALE" else args[0]
            assert active[dst] == active[donor] == args[-1]
            assert (dst == donor) == (op == "SCALE")
            if op == "COPY":
                assert not before
                if track_rows:
                    copies[clock] = event, before, get(donor)
                guards["copy"] += 1
            if not track_rows:
                return
            source = get(donor)
            value = add({} if op == "SCALE" else before, source, Q(args[-2]))
            if value:
                rows[dst] = value
            else:
                rows.pop(dst, None)
            if clock in READS and (dst, donor) == READS[clock]:
                observed[clock] = before, source, value

    tape = word["program"]
    for clock, event in enumerate(tape):
        track_rows = clock <= max(READS)
        if clock == 39769:
            historical_913 = get(913)
        if clock == 39778:
            historical_927 = get(927)
        if clock == ASCENT:
            u = get(OWNER)
            assert u == add(add({}, historical_913, Q(-1)), historical_927, Q(-1, 2))
        if encode is not None:
            if clock in (ASCENT, *DELETED_WRITES, CLEAR, *ADVANCED):
                continue
            if clock == CUT:
                for old_clock in ADVANCED:
                    execute(tape[old_clock], old_clock, track_rows)
        if clock == CUT:
            assert OWNER not in owners and OWNER not in active
            assert [active[r] for r in BANK] == [127 if encode is not None else 529, 127, 127]
            assert [active[r] for r in CARRIERS] == [127, 127 if encode is not None else 529]
            assert [active[r] for r in RECEIVERS] == [127 if encode is not None else 531, 127]
            bank = {r: get(r) for r in BANK}
            carriers = {r: get(r) for r in CARRIERS}
            receivers = {r: get(r) for r in RECEIVERS}
            owners_at_cut = owners.copy()
        execute(event, clock, track_rows)
        if encode is not None and clock in (FIRST_ENCODE, SECOND_ENCODE):
            carrier = CARRIERS[int(clock == SECOND_ENCODE)]
            assert owners[OWNER] == 37960
            execute(["ADD", carrier, OWNER, encode, 529], clock, track_rows)
            if clock == SECOND_ENCODE:
                execute(["CLEAR", OWNER, 529], clock, track_rows)
        if len(owners) > peak[0]:
            peak = len(owners), clock
    assert not owners and active == dict(enumerate(word["final"]))
    return {
        "u": u, "bank": bank, "carriers": carriers, "receivers": receivers, "peak": peak,
        "guards": guards, "owners_at_cut": owners_at_cut, "earlier_owned_moves": earlier_owned_moves,
        "retirement": retirement, "copies": copies, "reads": observed,
    }


def compare(word, initial):
    old = replay(word, initial)
    encoded = replay(word, initial, Q(1))
    u = old["u"]
    assert u == encoded["u"]
    assert old["bank"] == encoded["bank"] and old["owners_at_cut"] == encoded["owners_at_cut"]
    assert old["peak"][0] == 50 and encoded["peak"] == (51, 39811)
    assert old["guards"]["init"] == encoded["guards"]["init"] == 74
    assert old["guards"]["clear"] == encoded["guards"]["clear"] == 74
    assert old["guards"]["move"] == encoded["guards"]["move"] + 1
    assert old["copies"] == encoded["copies"] and old["guards"]["copy"] == encoded["guards"]["copy"]
    assert {i: v for i, v in old["earlier_owned_moves"].items() if i != ASCENT} == encoded["earlier_owned_moves"]
    assert old["retirement"][CLEAR] == encoded["retirement"][SECOND_ENCODE] == (37960, OWNER, u)
    assert {i: v for i, v in old["retirement"].items() if i != CLEAR and i < CUT} == {
        i: v for i, v in encoded["retirement"].items() if i != SECOND_ENCODE and i < CUT}
    assert all(encoded["carriers"][r] == add(old["carriers"][r], u) for r in CARRIERS)
    assert all(encoded["receivers"][r] == add(old["receivers"][r], u, Q(1, 2)) for r in RECEIVERS)
    for clock in READS:
        before, donor, after = old["reads"][clock]
        newer_before, newer_donor, newer_after = encoded["reads"][clock]
        assert before == newer_before
        factor = {46664: Q(1, 2), 47224: Q(1), 47723: Q(1, 2), 56017: Q(1)}[clock]
        assert newer_donor == add(donor, u, factor)
        assert newer_after == add(after, u, factor * (4 if clock == 56017 else 1))
    return old, encoded


def rationals(values):
    result = {int(i): Q(v) for i, v in values.items()}
    assert len(result) == len(values)
    return result


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def det(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return a * (e*i - f*h) - b * (d*i - f*g) + c * (d*h - e*g)


def exclusion(word, lead):
    records = []
    for raw in lead["probes"]:
        probe = rationals(raw)
        assert probe and all(0 <= j < word["public"] and v for j, v in probe.items())
        old, encoded = compare(word, {j: {0: v} for j, v in probe.items()})
        assert not any(old["bank"].values())
        records.append({
            "probe": probe, "bank": {r: scalar(v) for r, v in old["bank"].items()},
            "a_b_u": [*(scalar(old["carriers"][r]) for r in CARRIERS), scalar(old["u"])],
            "encoded_alpha_beta_one": {r: scalar(v) for r, v in encoded["carriers"].items()},
            "old_read_outputs": {clock: scalar(v[2]) for clock, v in old["reads"].items()},
            "encoded_unrepaired_read_outputs": {clock: scalar(v[2]) for clock, v in encoded["reads"].items()},
            "old_peak": old["peak"], "edited_peak": encoded["peak"],
            "old_guards": old["guards"], "edited_guards": encoded["guards"],
        })
    matrix = [r["a_b_u"] for r in records]
    assert len(matrix) == lead["quotient_rank"] == 3
    assert matrix == [[Q(v) for v in row] for row in lead["response_matrix"]]
    determinant = det(matrix)
    assert determinant == Q(lead["determinant"]) != 0
    return {"status": "PASS_INDEPENDENT_FIRST_USE_RANK3_EXCLUSION", "records": records,
            "response_matrix": matrix, "determinant": determinant}


def support(word, lead):
    old, _edited = compare(word, {j: {j: Q(1)} for j in range(word["public"])})
    b = [old["bank"][r] for r in BANK]
    targets = [*(old["carriers"][r] for r in CARRIERS), old["u"]]
    for record in lead["exact_dependencies"]:
        index = record["target"]
        sources = b + targets[:index]
        coeffs = rationals(record["preceding_bank_and_target_weights"])
        assert all(0 <= j < len(sources) for j in coeffs)
        total = {}
        for j, coefficient in coeffs.items():
            total = add(total, sources[j], coefficient)
        assert total == targets[index]
    assert len(lead["exact_dependencies"]) == 3 - lead["quotient_rank"]
    return {"status": "PASS_INDEPENDENT_FIRST_USE_DEPENDENCIES_ONLY",
            "verified_dependencies": lead["exact_dependencies"],
            "deferred_restores_and_full_price_open": True}


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", unresolved=[CASE], cap_seconds=CAP, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    data = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    raw = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == NATIVE
    word = loads(raw, object_pairs_hook=unique_pairs)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["candidate_canonical_sha256"] == NATIVE and app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    lifecycle = chronology(word)
    lead_raw = args.lead_receipt.read_bytes()
    assert sha256(lead_raw).hexdigest() == args.lead_sha256
    lead = loads(lead_raw, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["cut"] == CUT and lead["tested"] == 1
    assert tuple(lead["donors"]) == BANK and tuple(lead["carried_original_rows"]) == CARRIERS
    assert lead["early_owner_liveness"] == [50, 51] and lead["first_edited_peak_old_clock"] == 39811
    if lead["status"] == "EXACT_FIRST_USE_RANK3_EXCLUSION":
        assert lead["unresolved"] == []
        result = exclusion(word, lead)
    else:
        assert lead["status"] == "FIRST_USE_RANK_GATE_SURVIVOR_STAGGERED_RESTORE_OPEN"
        result = support(word, lead)
    emit(**result, case=CASE, old_lifecycle=lifecycle, input_pins=PINS, caller_head=CALLER,
         native_sha256=NATIVE, cap_seconds=CAP, lead_sha256=args.lead_sha256, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
