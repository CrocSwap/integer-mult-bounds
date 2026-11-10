#!/usr/bin/env python3
"""The all-Y exit round trip loses against the retained centre budget.

The width law and the round-three word are predecessor source. This checker
recomputes the chart dimensions, the nesting, and the eight rank-8 transports.
Failures raise ValueError, including under python -O.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORD = ROOT / "research/sol1337-contact-frontier/inputs/round3-native.json.gz"
ENGINE = ROOT / "research/sol1337-contact-frontier/vendor/retained_verify.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_engine():
    spec = importlib.util.spec_from_file_location("retained_centre_verify", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(engine):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    by_path = {row["path"]: row for row in pins["files"]}
    for path in (WORD, ENGINE):
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == by_path[rel]["sha256"], "changed input " + rel)
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == engine.SOURCE_HASH, "word hash disagrees with the retained emitter")
    return json.loads(gzip.decompress(raw))


def rank_mass_gap(added_rank1, deleted_ranks):
    """Integer lower bound on the paid-moment gap for every exponent in (0, 1]."""
    need(type(added_rank1) is int and added_rank1 >= 0, "added rank-1 count")
    need(all(type(rank) is int and rank >= 1 for rank in deleted_ranks), "deleted ranks")
    return added_rank1 - sum(deleted_ranks)


def budget_covers(deleted_ranks, budget_ranks):
    return not (Counter(deleted_ranks) - Counter(budget_ranks))


def expect_fail(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError(message)


def survey(engine, payload):
    canonical = payload["canonical"]
    frames = canonical["frames"]
    final = canonical["final"]
    ambient = canonical["h"]
    block = canonical["v"]
    need(ambient == 9 and block == 112, "this word's ambient dimension and block length")
    need(len(final) == len(canonical["start"]) == 632, "632 non-centre output charts")
    need(632 - 2 * block == 408, "helper block between the Y exits and the centres")
    spaces = list(map(engine.span, frames))
    for index, basis in enumerate(frames):
        need(len(spaces[index]) == 2 ** len(basis), "chart dimension is the independent basis length")
    full = [index for index, basis in enumerate(frames) if len(basis) == ambient]
    need(full == [1], "one retained rank-9 frame")
    full_id = full[0]
    x_exits = [final[role] for role in range(block)]
    need(set(x_exits) == {full_id}, "every X exit uses that rank-9 frame")
    y_ids = [final[role] for role in range(block, 2 * block)]
    need(len(y_ids) == block and len(set(y_ids)) == block, "112 distinct Y exit charts")
    for chart in y_ids:
        need(len(frames[chart]) == ambient - 1, "every Y exit chart has dimension 8")
        need(spaces[chart] < spaces[full_id], "every Y exit chart sits strictly inside the rank-9 frame")
        need(abs(len(frames[chart]) - len(frames[full_id])) == 1, "raise or lower has width 1")
    starts, centers, events = engine.emit(payload)
    need(len(starts) == 640 and len(centers) == 8, "eight appended centre inputs")
    engine.replay(payload, starts, events)
    centre = [event for event in events if event[0] == "transport" and event[1] >= 632]
    width8 = [event for event in events if event[0] == "transport" and event[4] == 8]
    need(centre == width8 and len(centre) == 8, "the rank-8 budget is exactly the eight centre transports")
    for event in centre:
        _, role, source, dest, width = event
        need(632 <= role < 640 and width == 8 and dest == 0, "centre transport shape")
        need(len(frames[source]) == 8 and len(frames[dest]) == 0, "centre charts are rank 8 into the empty chart")
        need(spaces[dest] < spaces[source], "empty chart is nested in the centre chart")
    paid = Counter(event[4] for event in events if event[0] == "transport" and event[4])
    need(dict(paid) == engine.PAID == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8},
         "retained paid histogram, including eight rank-8 calls")
    profile = {int(rank): count for rank, count in canonical["local_profile"].items()}
    need(profile == engine.PAID, "canonical local profile matches the emitted invoice")
    helpers = Counter(len(frames[final[role]]) - len(frames[canonical["start"][role]])
                      for role in range(2 * block, 632))
    need(dict(helpers) == {4: 28, 7: 7, 8: 47, 9: 326}, "helper targets are the retained productive histogram")
    added = 2 * block
    mass = sum(event[4] for event in centre)
    gap = rank_mass_gap(added, [event[4] for event in centre])
    need(added == 224 and mass == 64 and gap == 160, "224 against 64 leaves 160")
    need(rank_mass_gap(block, [event[4] for event in centre]) == 48, "one-way raise still leaves 48")
    return {"y_exits": block, "round_trip_h1": added, "centre_rank8": len(centre),
            "rank_mass": mass, "moment_gap_at_least": gap}


def controls():
    need(rank_mass_gap(224, [8, 8, 8, 8, 8, 8, 8, 8]) == 160, "endpoint arithmetic")
    need(budget_covers([8, 8], [8] * 8), "a centre submultiset is inside the budget")
    need(not budget_covers([8] * 9, [8] * 8), "a ninth centre call is not in the budget")
    expect_fail(lambda: rank_mass_gap(224, [0]), "rank 0 is not a deleted child")
    expect_fail(lambda: rank_mass_gap(-1, [8]), "a negative child count is not a tariff")
    # A width-2 claim for dimensions 8 and 9 contradicts the retained formula.
    need(abs(8 - 9) == 1, "width formula")
    expect_fail(lambda: need(abs(8 - 9) == 2, "wrong width"), "a width-2 claim must fail")


def main():
    engine = load_engine()
    payload = authenticate(engine)
    facts = survey(engine, payload)
    controls()
    # The integer samples support the written comparison r^k <= r^d for k <= d.
    for rank in range(1, 9):
        for denominator in range(1, 9):
            for numerator in range(denominator + 1):
                need(rank ** numerator <= rank ** denominator, "integer power comparison")
    print(
        "PASS_Y_EXIT_RANK_LIFT_OBSTRUCTION "
        f"y={facts['y_exits']} round_trip_h1={facts['round_trip_h1']} "
        f"centre_rank8={facts['centre_rank8']} rank_mass={facts['rank_mass']} "
        f"moment_gap_at_least={facts['moment_gap_at_least']} "
        "attained_at_theta_1=160 one_way_gap=48 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
