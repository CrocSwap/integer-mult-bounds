"""Materialize the single pinned 134/329 contact splice and check its signed maps."""
import argparse
from collections import Counter
from copy import deepcopy
from gzip import compress, decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

CAP = 60
INCUMBENT_HEAD = "d7f82810689ed2cd649ec9aaaf3b1485b585c82e"
PEER_HEAD = "e814828ee5b869c9468282d57ba28c364b07d130"
INCUMBENT_CANONICAL = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
RAW_PINS = {
    "round305/gate.json": "512dbbc3c5133b07400b720f55753e976aca48020e91b2d0086345802de1bc14",
    "round305/independent.json": "7f08c8d69f0bfa7fce39c1ab51794de94586650f8c5167dfaed27f155e7f776d",
    "round305/RUN.json": "2617b9ec5811744a3ae006869ea1a5290a90143435a82f10e360a03e3efd874a",
    "engines/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "engines/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
}
OLD = {
    41049: ["MOVE", 134, 3, 618, False],
    41050: ["MOVE", 329, 373, 618, False],
    41051: ["ADD", 134, 329, "-1/2", 618],
    41142: ["MOVE", 329, 618, 733, False],
    42086: ["MOVE", 134, 618, 913, False],
}
NEW = {
    41049: ["MOVE", 134, 3, 373, False],
    41050: None,
    41051: ["ADD", 134, 329, "-1/2", 373],
    41142: ["MOVE", 329, 373, 733, False],
    42086: ["MOVE", 134, 373, 913, False],
}
OLD_RANKS = [3, 1, 1, 4]
NEW_RANKS = [2, 2, 5]


class GateError(Exception):
    pass


def need(condition, label):
    if not condition:
        raise GateError(label)


def digest(data):
    return sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def span(frame):
    points = {0}
    for v in frame:
        need(0 < v < 512 and v not in points, f"invalid frame vector {v}")
        points |= {p ^ v for p in points}
    return points


def operands(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def audit_word(word, spans, state, label):
    public = word["public"]
    chart = word["initial"] + [None] * word["owned_fields"]
    peak = live = 0
    owned_events = []
    pairs = Counter()
    rank_counts = Counter()
    for clock, e in enumerate(word["program"]):
        state["clock"] = clock
        op, field, *args = e
        need(all(isinstance(r, int) and 0 <= r < len(chart) for r in operands(e)),
             f"{label}: invalid field at {clock}")
        if any(r >= public for r in operands(e)):
            owned_events.append(e)
        if op == "MOVE":
            a, b, private = args
            need(private is (field >= public) and chart[field] == a,
                 f"{label}: MOVE ownership or source at {clock}")
            need(spans[a] < spans[b] or (private and spans[b] < spans[a]),
                 f"{label}: nonnested MOVE at {clock}")
            chart[field] = b
            pairs[a, b] += 1
            rank_counts[abs(len(word["frames"][a])-len(word["frames"][b]))] += 1
        elif op == "INIT":
            need(field >= public and chart[field] is None, f"{label}: invalid INIT at {clock}")
            chart[field] = args[0]
            live += 1
            peak = max(peak, live)
        elif op == "CLEAR":
            need(field >= public and chart[field] == args[0], f"{label}: invalid CLEAR at {clock}")
            chart[field] = None
            live -= 1
        else:
            need(op in ("ADD", "COPY", "SCALE") and chart[field] == args[-1],
                 f"{label}: scalar destination chart at {clock}")
            if op != "SCALE":
                need(field != args[0] and chart[args[0]] == args[-1],
                     f"{label}: scalar source chart at {clock}")
    need(live == 0 and chart == word["final"] + [None] * word["owned_fields"],
         f"{label}: final chart or lifetime mismatch")
    return owned_events, peak, pairs, rank_counts


def phase_check(word, old_pairs, new_pairs, engines, state):
    comp = run_path(str(engines / "clifford_exact.py"))
    interp = run_path(str(engines / "native_verify.py"))
    pairs = sorted(set(old_pairs + new_pairs))
    frame_ids = sorted({f for pair in pairs for f in pair})
    frames = {f: word["frames"][f] for f in frame_ids}
    canonical_frames = {f: comp["canonical_frame"](9, tuple(frames[f])) for f in frame_ids}
    direct_frames = {f: interp["frame"](frames[f], 9) for f in frame_ids}
    routes = {}
    result = {}

    def exact_equality(left, right, label):
        for name, l, r in (("forward", left, right),
                           ("adjoint", interp["adjoint"](left), interp["adjoint"](right))):
            state["subject"] = label
            state["direction"] = name
            interp["equal"](l, r, f"{label} {name}")
            for j in range(512):
                state["column"] = j
                need(interp["state"](l, j) == interp["state"](r, j), f"{label} {name} column {j}")
        result[label] = {"forward_columns": 512, "adjoint_columns": 512,
                         "signed_pauli_and_absolute_phase": True}

    control_passed = False
    for a, b in pairs:
        label = f"{a}->{b}"
        rank = len(frames[b])-len(frames[a])
        recipe, _ = comp["lower_child"](canonical_frames[a].adjoint().then(canonical_frames[b]))
        need(recipe["rank"] == rank, f"wrong compiled rank {label}")
        actual = routes[a, b] = interp["recipe"](recipe)
        expected = interp["adjoint"](direct_frames[a]) + direct_frames[b]
        exact_equality(actual, expected, label)
        result[label]["rank"] = rank
        if (a, b) == (373, 913):
            tampered = deepcopy(recipe)
            tampered["left"]["phase"] = (tampered["left"]["phase"] + 1) % 4
            try:
                interp["equal"](interp["recipe"](tampered), expected, "one quarter turn fault")
            except ValueError as error:
                need("exact global phase" in str(error), "phase control rejected for the wrong reason")
                control_passed = True
            else:
                raise GateError("wrong absolute phase accepted")
    need(control_passed, "missing wrong-phase control")
    exact_equality(routes[3, 618] + routes[618, 913],
                   routes[3, 373] + routes[373, 913], "134 retained value")
    exact_equality(routes[373, 618] + routes[618, 913],
                   routes[373, 913], "329 contribution to 134")
    exact_equality(routes[373, 618] + routes[618, 733],
                   routes[373, 733], "329 retained value")
    return result


def gate(args, state):
    state["stage"] = "authenticate"
    sources = {"word.json.gz": args.word}
    sources.update({f"round305/{n}": args.round305 / n for n in ("gate.json", "independent.json", "RUN.json")})
    sources.update({f"engines/{n}": args.engine_root / n for n in ("clifford_exact.py", "native_verify.py")})
    data = {n: p.read_bytes() for n, p in sources.items()}
    need({n: digest(data[n]) for n in RAW_PINS} == RAW_PINS, "dependency hash mismatch")
    old_raw = decompress(data["word.json.gz"])
    need(digest(old_raw) == INCUMBENT_CANONICAL, "word canonical hash mismatch")
    word = json.loads(old_raw)
    primary = json.loads(data["round305/gate.json"])
    secondary = json.loads(data["round305/independent.json"])
    summary = json.loads(data["round305/RUN.json"])
    need(primary["status"] == "ELIGIBLE_FOR_BUILD"
         and secondary["status"] == "PASS_CONTACT_LOCAL_INDEPENDENT"
         and summary["status"] == "ELIGIBLE_FOR_LITERAL_BUILD"
         and summary["stages"] == {"gate": 0, "independent": 0}
         and primary["incumbent_word_sha256"] == secondary["incumbent_word_sha256"] == INCUMBENT_CANONICAL
         and secondary["primary_receipt_sha256"] == RAW_PINS["round305/gate.json"]
         and primary["peer_head"] == PEER_HEAD, "round 305 inputs or outcome mismatch")
    need({int(k): v for k, v in primary["old_events"].items()} == OLD
         and {int(k): v for k, v in primary["proposed_events"].items()} == NEW, "literal frozen edit mismatch")

    state["stage"] = "materialize and compare scalar schedules"
    tape = word["program"]
    need(len(tape) == 76646 and all(tape[i] == e for i, e in OLD.items()), "incumbent edit clock or event mismatch")
    new_tape = [ev for i, old in enumerate(tape) if (ev := NEW.get(i, old)) is not None]
    candidate = {**word, "program": new_tape}
    need(len(new_tape) == 76645, "changed event total")
    for role, clocks in ((134, [41049, 41051, 42086]), (329, [41050, 41051, 41142])):
        need([i for i in range(clocks[0], clocks[-1]+1) if role in operands(tape[i])] == clocks,
             f"extra incident baseline contact on role {role}")
    scalar_old = [e for i, e in enumerate(tape) if e[0] != "MOVE" and i != 41051]
    scalar_new = [e for i, e in enumerate(new_tape) if e[0] != "MOVE" and i != 41050]
    need(scalar_old == scalar_new and tape[41051][:-1] == new_tape[41050][:-1],
         "scalar or guard sequence changed beyond the specified ADD chart")
    old_pairs = [tuple(e[2:4]) for e in OLD.values() if e[0] == "MOVE"]
    new_pairs = [tuple(e[2:4]) for e in NEW.values() if e and e[0] == "MOVE"]
    state["stage"] = "chart and ownership"
    spans = list(map(span, word["frames"]))
    old_owned, old_peak, old_vocab, old_paid = audit_word(word, spans, state, "old")
    new_owned, new_peak, new_vocab, new_paid = audit_word(candidate, spans, state, "candidate")
    owned_census = Counter(e[0] for e in new_owned)
    need(old_owned == new_owned and old_peak == new_peak == 50
         and owned_census["INIT"] == owned_census["CLEAR"] == 74
         and owned_census["MOVE"] == 47 and word["owned_fields"] == 68,
         "owned chart, guard or schedule mismatch")
    need(not (new_vocab.keys() - old_vocab.keys() - set(new_pairs)), "unaccounted-for pair")
    delta = new_paid.copy()
    delta.subtract(old_paid)
    paid_delta = {str(r): n * 17 for r, n in sorted(delta.items()) if n}
    ranks = [[len(word["frames"][b])-len(word["frames"][a]) for a, b in pairs]
             for pairs in (old_pairs, new_pairs)]
    need(ranks == [OLD_RANKS, NEW_RANKS]
         and paid_delta == primary["paid_delta"] == secondary["paid_delta"], "paid-rank reconstruction differs")
    state.pop("clock")
    state["stage"] = "compiled signed action"
    phase = phase_check(word, old_pairs, new_pairs, args.engine_root, state)
    state["stage"] = "write authenticated candidate"
    out = canonical(candidate)
    packed = compress(out, mtime=0)
    with args.candidate.open("xb") as f:
        f.write(packed)
    return {
        "status": "PASS_LITERAL_CONTACT_AND_SIGNED_PHASE",
        "incumbent_head": INCUMBENT_HEAD, "incumbent_canonical_sha256": INCUMBENT_CANONICAL,
        "incumbent_gzip_sha256_observed": digest(data["word.json.gz"]),
        "round305_incumbent_gzip_sha256": primary["word_gzip_sha256"],
        "peer": 7612, "peer_head": PEER_HEAD, "candidate_canonical_sha256": digest(out),
        "candidate_gzip_sha256": digest(packed), "candidate_events": len(new_tape),
        "scalar_events_unchanged_except_one_rechart": len(scalar_new), "recharted_scalar_clock": 41051,
        "owned_schedule_events": dict(owned_census), "owned_peak": new_peak,
        "same_chart_endpoints": True, "paid_delta": paid_delta, "case_cap": 1, "seconds_cap": CAP,
        "pair_occurrences": {f"{a}->{b}": [old_vocab[a, b], new_vocab[a, b]]
                             for a, b in sorted(set(old_pairs + new_pairs))},
        "wrong_global_phase_rejected": True, "phase": phase, "input_pins": RAW_PINS,
        "scope": "literal local arbitrary-input action and chart/schedule checks; complete native and signed cost replay pending",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("word", "round305", "engine-root", "candidate"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        parser.error("assertions must be enabled for the pinned compiler")
    state = {"stage": "starting"}

    def cap(_sig, _frame):
        raise TimeoutError

    signal.signal(signal.SIGALRM, cap)
    signal.alarm(CAP)
    try:
        receipt = gate(args, state)
        code = 0
    except TimeoutError:
        receipt = {"status": "UNRESOLVED_CAP", "seconds_cap": CAP, "last": state}
        code = 124
    except (GateError, ValueError, OSError, AssertionError, KeyError, IndexError) as e:
        receipt = {"status": "GATE_FAILED", "last": state, "error": str(e)}
        code = 1
    finally:
        signal.alarm(0)
    print(json.dumps(receipt, sort_keys=True), flush=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
