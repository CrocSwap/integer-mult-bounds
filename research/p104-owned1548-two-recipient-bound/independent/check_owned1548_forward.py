"""Independently verify the owned1548 two-output fixed correction by forward substitution."""
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
OWNER, CUT, CAP = 1548, 46664, 30
ASCENT, OMIT, CLEAR = 39785, (39786, 39787), 39788
RECEIVERS = (1298, 1429)
DONORS = (913, 1197, 587, 1494)
ADVANCED = {47227: 913, 47722: 1298}
READS = {CUT: (1153, 1429), 47723: (665, 1298)}
CASE = "owned1548-two-receivers-advanced-913-1298-pre46664"


def emit(**result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def span(basis):
    result = {0}
    for generator in basis:
        assert generator not in result
        result |= {generator ^ x for x in result}
    return result


def contacts(tape, role, start, stop):
    return [i for i in range(start, stop) if tape[i][1] == role or
            tape[i][0] in ("ADD", "COPY") and tape[i][2] == role]


def chronology(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    protected = set(word["live"]) | {r + 112 for r in word["live"]}
    protected |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(protected) == 400 and 927 in protected
    assert not protected.intersection({913, 1197, *RECEIVERS})
    a, b, c = (span(word["frames"][chart]) for chart in (529, 531, 127))
    assert a < b < c and len(b) == 2 * len(a)
    assert tape[ASCENT:CLEAR + 1] == [
        ["MOVE", OWNER, 529, 531, True], ["ADD", 1298, OWNER, "-1/2", 531],
        ["ADD", 1429, OWNER, "-1/2", 531], ["CLEAR", OWNER, 531],
    ]
    assert tape[47227] == ["MOVE", 913, 529, 127, False]
    assert tape[47722] == ["MOVE", 1298, 531, 127, False]
    assert tape[46663] == ["MOVE", 1429, 531, 127, False]
    for i, (dst, donor) in READS.items():
        assert tape[i] == ["ADD", dst, donor, "1", 127]
    assert contacts(tape, 913, 45584, 47227) == []
    assert contacts(tape, 1298, 39786, 47724) == [39786, 47722, 47723]
    assert contacts(tape, 1429, 39787, CUT + 1) == [39787, 46663, CUT]
    assert contacts(tape, 1197, 39782, CUT) == [45418, 45419]
    birth = max(i for i in range(ASCENT) if tape[i][:2] == ["INIT", OWNER])
    history = contacts(tape, OWNER, birth, CLEAR + 1)
    assert history == [birth, 39769, 39778, ASCENT, *OMIT, CLEAR]
    return {i: tape[i] for i in history}


def plus(left, right, factor):
    out = left.copy()
    for j, v in right.items():
        new = out.get(j, 0) + factor * v
        if new:
            out[j] = new
        else:
            out.pop(j, None)
    return out


def replay(word, initial, edited=False, correction=None, injected=None):
    tape = word["program"]
    active = dict(enumerate(word["initial"]))
    rows = initial.copy()
    owners, retirement, owned_moves, copy_rows = {}, {}, {}, {}
    reads = {}
    samples = {}
    bank = {}
    before_repair, after_repair = {}, {}
    advanced_rows = {}
    counts = {"init": 0, "clear": 0, "copy": 0, "move": 0}
    empty = {}

    def get(role):
        return rows.get(role, empty)

    def apply(event, clock):
        op, dst, *args = event
        old = get(dst)
        if op == "MOVE":
            src, dest, flag = args
            assert src != dest and active[dst] == src and flag == (dst in owners) == (dst >= word["public"])
            active[dst] = dest
            counts["move"] += 1
            if flag:
                owned_moves[clock] = owners[dst], event, old
            return
        if op == "INIT":
            assert dst >= word["public"] and dst not in owners and dst not in active and not old
            active[dst] = args[0]
            owners[dst] = clock
            counts["init"] += 1
            return
        if op == "CLEAR":
            assert dst in owners and active.pop(dst) == args[0]
            retirement[clock] = owners.pop(dst), event, old
            rows.pop(dst, None)
            counts["clear"] += 1
            return
        if op == "SCALE":
            weight, chart = args
            assert active[dst] == chart
            result = plus({}, old, Q(weight))
        else:
            assert op in ("COPY", "ADD")
            donor, weight, chart = args
            assert dst != donor and active[dst] == active[donor] == chart
            source = get(donor)
            if op == "COPY":
                assert not old
                copy_rows[clock] = event, old, source
                counts["copy"] += 1
            result = plus(old, source, Q(weight))
            if clock in READS and (dst, donor) == READS[clock]:
                reads[clock] = old, source, result
        if result:
            rows[dst] = result
        else:
            rows.pop(dst, None)

    sampled = {
        39769: (913,), 39778: (927,), 39780: (1197,), 39782: (1197,),
        ASCENT: (OWNER,), CLEAR: (OWNER,),
    }
    for clock, event in enumerate(tape[:max(READS) + 1]):
        if clock in sampled:
            samples[clock] = {r: get(r) for r in sampled[clock]}
        if clock in ADVANCED:
            r = ADVANCED[clock]
            advanced_rows[clock] = get(r)
            if edited:
                assert active[r] == 127
                continue
        if edited:
            if clock in (ASCENT, *OMIT):
                continue
            if clock == CLEAR:
                event = ["CLEAR", OWNER, 529]
            if clock == CUT:
                for old_clock in ADVANCED:
                    apply(tape[old_clock], old_clock)
        if clock == CUT:
            assert OWNER not in active and OWNER not in owners
            assert [active[r] for r in DONORS] == [127 if edited else 529, 127, 127, 127]
            assert [active[r] for r in RECEIVERS] == [127 if edited else 531, 127]
            assert all(r not in owners and r < word["public"] for r in DONORS + RECEIVERS)
            bank = {r: get(r) for r in DONORS}
            before_repair = {r: get(r) for r in RECEIVERS}
            if correction is not None:
                assert edited
                for r in RECEIVERS:
                    for donor, coefficient in correction.items():
                        if coefficient:
                            apply(["ADD", r, donor, coefficient, 127], CUT)
            if injected is not None:
                assert edited
                for r in RECEIVERS:
                    v = plus(get(r), injected, Q(1))
                    if v:
                        rows[r] = v
                    else:
                        rows.pop(r, None)
            after_repair = {r: get(r) for r in RECEIVERS}
        apply(event, clock)
    return {
        "samples": samples, "bank": bank, "before_repair": before_repair, "after_repair": after_repair,
        "advanced_rows": advanced_rows, "reads": reads, "retirement": retirement,
        "owned_moves": owned_moves, "copy_rows": copy_rows, "owners": owners, "counts": counts,
    }


def source_identity(samples):
    a, b = samples[39769][913], samples[39778][927]
    early, late = samples[39780][1197], samples[39782][1197]
    u = plus(plus({}, a, Q(-1)), b, Q(-1, 2))
    assert u == samples[ASCENT][OWNER] == samples[CLEAR][OWNER]
    difference = plus(plus(late, early, Q(-1)), a, Q(-1))
    assert u == plus({}, difference, Q(1, 2))
    return u, plus({}, u, Q(-1, 2))


def compare(word, initial, coefficients=None):
    old = replay(word, initial)
    edited = replay(word, initial, edited=True, correction=coefficients)
    assert old["samples"] == edited["samples"]
    u, required = source_identity(old["samples"])
    assert old["bank"] == edited["bank"]
    assert old["owners"] == edited["owners"] and old["copy_rows"] == edited["copy_rows"]
    assert {i: v for i, v in old["owned_moves"].items() if i != ASCENT} == edited["owned_moves"]
    assert old["retirement"].keys() == edited["retirement"].keys()
    for i, before in old["retirement"].items():
        after = edited["retirement"][i]
        assert (before == after) if i != CLEAR else (before[0], before[2]) == (after[0], after[2])
    assert old["counts"]["move"] == edited["counts"]["move"] + 1
    assert all(old["counts"][k] == edited["counts"][k] for k in ("init", "clear", "copy"))
    assert old["advanced_rows"][47227] == edited["advanced_rows"][47227] == old["bank"][913]
    for r in RECEIVERS:
        assert old["before_repair"][r] == plus(edited["before_repair"][r], required, Q(1))
    for clock in READS:
        x, y = old["reads"][clock], edited["reads"][clock]
        assert x[0] == y[0]
        if coefficients is None:
            assert x[1] == plus(y[1], required, Q(1))
            assert x[2] == plus(y[2], required, Q(1))
        else:
            assert x == y
    return old, edited, u, required


def rationals(values):
    result = {int(j): Q(v) for j, v in values.items()}
    assert len(result) == len(values)
    return result


def scalar(row):
    assert set(row) <= {0}
    return row.get(0, Q(0))


def controls(word, initial, original, required):
    # Supply the oracle correction directly only as a sign/target harness control.
    good = replay(word, initial, edited=True, injected=required)
    wrong = replay(word, initial, edited=True, injected=plus({}, required, Q(-1)))
    assert good["reads"] == original["reads"]
    assert all(wrong["reads"][clock][2] != original["reads"][clock][2] for clock in READS)
    return {"oracle_target_restores_both": True, "sign_flip_rejected_by_both": True}


def separator(word, lead):
    probe = rationals(lead["probe"])
    assert probe and all(0 <= r < word["public"] and v for r, v in probe.items())
    initial = {r: {0: v} for r, v in probe.items()}
    old, edited, u, required = compare(word, initial)
    assert not any(old["bank"].values()) and scalar(required) == 1 and scalar(u) == -2
    assert sum(weight * probe.get(r, 0) for r, weight in rationals(lead["required_each"]).items()) == 1
    return {
        "status": "PASS_INDEPENDENT_NAMED_DONOR_EXCLUSION", "probe": probe,
        "required_each": 1, "owner1548_source_and_retirement": scalar(u),
        "donor_responses": {r: scalar(v) for r, v in old["bank"].items()},
        "old_cut_recipients": {r: scalar(v) for r, v in old["before_repair"].items()},
        "unrepaired_cut_recipients": {r: scalar(v) for r, v in edited["before_repair"].items()},
        "first_reads_old_before_donor_after": {k: list(map(scalar, v)) for k, v in old["reads"].items()},
        "first_reads_edited_before_donor_after": {k: list(map(scalar, v)) for k, v in edited["reads"].items()},
        "old_guards": old["counts"], "edited_guards": edited["counts"],
        "controls": controls(word, initial, old, required),
    }


def support(word, lead):
    coefficients = rationals(lead["representation"])
    assert coefficients.keys() <= set(DONORS)
    initial = {r: {r: Q(1)} for r in range(word["public"])}
    old, edited, _u, required = compare(word, initial, coefficients)
    recovered = {}
    for donor, coefficient in coefficients.items():
        recovered = plus(recovered, old["bank"][donor], coefficient)
    assert recovered == required == rationals(lead["required_each"])
    return {
        "status": "PASS_INDEPENDENT_RATIONAL_SUPPORT", "coefficients": coefficients,
        "checked_input_basis_dimension": word["public"], "old_guards": old["counts"],
        "edited_guards": edited["counts"], "controls": controls(word, initial, old, required),
    }


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
    raw_word = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(raw_word).hexdigest() == NATIVE
    word = loads(raw_word, object_pairs_hook=unique_pairs)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    assert app["candidate_canonical_sha256"] == NATIVE and app["caller_head"] == CALLER
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    lifecycle = chronology(word)
    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["cut"] == CUT and tuple(lead["donors"]) == DONORS
    assert tuple(lead["recipients"]) == RECEIVERS and lead["tested"] == 1 and lead["unresolved"] == []
    if lead["status"] == "EXACT_NAMED_DONOR_EXCLUSION":
        result = separator(word, lead)
    else:
        assert lead["status"] == "EXACT_RATIONAL_SUPPORT_FULL_PRICE_PENDING"
        result = support(word, lead)
    emit(**result, case=CASE, lifecycle=lifecycle, cap_seconds=CAP, input_pins=PINS, native_sha256=NATIVE,
         caller_head=CALLER, lead_sha256=args.lead_sha256, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
