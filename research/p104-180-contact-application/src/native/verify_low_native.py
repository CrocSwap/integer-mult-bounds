#!/usr/bin/env python3
"""Exact chart and dense finite replay of the repaired #7636 source and combination."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import json
from math import gcd
from pathlib import Path
import sys
from time import monotonic_ns
from types import ModuleType

import build_low as build


HERE = Path(__file__).resolve().parent
ENGINES = HERE / "engines"
MODULI = ((1000000009, 11), (998244353, 37))
PHASE_CODE = "3b340b468d119fcca8bca015b0bab187119cd2593b25737ec496c9dc3564ebc6"
ENGINE_PINS = {
    "verify_native.py": "b0e073a89ef4d24745e63dfddb1b8b4307d2d1edcee783ad76ab055cb54f836b",
    "physical.py": "e76bc78b132607890b2d9ea234d3a52e608e0e919bdc48308cc0727a2a07c73e",
    "walsh.py": "c8d29246c26967315a223cb01f822060e83b3fdedad96d8dbcf878be94c51fac",
    "check_native_7660.py": "6cc127ed1b1eddeadb50b69e672587e2c64378e5e5790357e526a9c022e32760",
    "phase-source7636.py": "72dfc0f5435cea2630a0d4e8f466fbb7b866404a22804769c3e690845ca72d2b",
}
INPUT_PINS = {
    "source-word.json.gz": build.SOURCE_GZIP,
    "source-clear.json": build.SOURCE_CLEAR,
    "raw-combined.json.gz": build.C_GZIP,
    "combined-clear.json": build.C_CLEAR,
    "combined-prior.json": "6b0672e4f3329a351ca0e6006274102b32b274fd0b1dde727b2063ca9682943b",
    "prior-native.json": "a2e29cb40f971aba674487d71002a19b40af124d76fb2a4962958e0ea5e460da",
    "prior-pairs.json": "a6645322a783f6160381205b455d410f0a1287f208f18deba156ae7c4aa7f16a",
    "prior-physical-1000000009.json": "c96a11f0104fc9930a392cee0d3862d039c3de8de9e08c7ee4f7c70f781b3ff8",
    "prior-physical-998244353.json": "4bd3cdce0b6042edde5f4cb418e6d348fee78b87509daf6bfbb8586f03f3a2bc",
}
REPLAY_EVENT = "p7636-180-lowering-native-running"
CLAIM = "https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19698656"
SCALAR_EVENTS = 196441
PAID_DELTA = {1: -3, 2: 1, 4: -1, 5: 1}

require = build.require
dump = build.write_json
pinned = build.pinned
sha = build.sha


def stamp():
    return datetime.now(timezone.utc).isoformat()


def load_engine(filename, name):
    path = ENGINES / filename
    data = pinned(path, ENGINE_PINS[filename])
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def checked_inputs(root, materialized):
    raw_source, lowered_source, lowered_c, clock_map, source_terms, candidate_terms = build.matched(root)
    binding_path = materialized / "BINDING.json"
    binding_bytes = binding_path.read_bytes()
    binding = json.loads(binding_bytes)
    require(binding["status"] == "PASS_7636_MATCHED_SCALAR_LOWERING_BUILD"
            and binding["source_head"] == build.HEAD
            and binding["source_parent_raw_sha256"] == build.SOURCE_RAW
            and binding["candidate_parent_raw_sha256"] == build.C_RAW,
            "materialization receipt")
    pins = {binding_path: sha(binding_bytes)}
    for side, expected, terms in (("source", lowered_source, source_terms), ("candidate", lowered_c, candidate_terms)):
        meta = binding[side]
        word_file = materialized / side / "WORD.json.gz"
        cert_file = materialized / side / "CLEAR-CERTIFICATES.json"
        require(meta["raw_sha256"] == meta["canonical_sha256"] == sha(build.canonical(expected))
                and meta["events"] == len(expected["program"]), f"canonical {side} identity")
        require(build.load_word(word_file, meta["gzip_sha256"], meta["raw_sha256"]) == expected,
                f"materialized {side} tape")
        require(build.read_certificates(cert_file, meta["clear_sha256"], expected) == terms,
                f"materialized {side} certificate binding")
        pins[word_file] = meta["gzip_sha256"]
        pins[cert_file] = meta["clear_sha256"]
    require(binding["role_379_phase_control_clock"] == clock_map[131294]
            and binding["contact_control_clock"] == clock_map[127446], "candidate control clocks")
    return raw_source, lowered_source, lowered_c, clock_map, source_terms, candidate_terms, binding, pins


def native_law(common, source, candidate, clock_map):
    """Prove arbitrary rows by aligning the actual ordered common-coordinate tape."""
    old_scalars, old_moves = common.group_tape(source)
    new_scalars, new_moves = common.group_tape(candidate)
    require(len(old_scalars) == len(new_scalars) == SCALAR_EVENTS, "repaired scalar denominator")
    contacts = []
    for ordinal, ((old_j, old), (new_j, new)) in enumerate(zip(old_scalars, new_scalars, strict=True)):
        if old != new:
            require(old_j == 127446 and new_j == clock_map[old_j]
                    and old == build.OLD[old_j] and new == build.REPLACEMENT[old_j],
                    f"unexpected public/protected scalar change at {old_j}/{new_j}")
            contacts.append({"scalar_ordinal": ordinal, "source_clock": old_j, "source": old,
                             "candidate_clock": new_j, "candidate": new})
    require(len(contacts) == 1, "one contact annotation changed")

    old_ordinal = {clock: ordinal for ordinal, rows in old_moves.items() for clock, _ in rows}
    new_ordinal = {clock: ordinal for ordinal, rows in new_moves.items() for clock, _ in rows}
    blocks = {"contact": {"changed_public_move_roles": [902, 1091], "recharted_contacts": contacts, "move_edits": []},
              "role379": {"changed_public_move_roles": [379], "recharted_contacts": [], "move_edits": []}}
    for clock, old in build.OLD.items():
        if old[0] != "MOVE":
            continue
        new = build.REPLACEMENT[clock]
        new_clock = clock_map.get(clock)
        ordinal = old_ordinal[clock]
        if new is not None:
            require(new_ordinal[new_clock] == ordinal, f"changed scalar anchor at {clock}")
        block = blocks["role379" if old[1] == 379 else "contact"]
        block["move_edits"].append({"before_scalar_ordinal": ordinal, "source": [(clock, old)],
                                    "candidate": [] if new is None else [(new_clock, new)]})

    original = Fraction(build.ORIGINAL[3])
    whole, fraction = (Fraction(e[3]) for e in build.SPLIT)
    require(whole.denominator == 1 and fraction.denominator == original.denominator
            and original == whole + fraction and whole > 0 and fraction > 0
            and gcd(fraction.numerator, fraction.denominator) == 1,
            "exact shear, preserved division domain and same-sign intermediate")
    require(whole - fraction != original, "wrong-sign split fails the shear identity")
    return blocks, {"ordered_scalar_events": SCALAR_EVENTS, "contact_annotations": contacts,
                    "split_sum": str(original), "split_wrong_sign_rejected": True,
                    "original_literal_bits": abs(original.numerator).bit_length(),
                    "split_literal_bits": [abs(whole.numerator).bit_length(), abs(fraction.numerator).bit_length()]}


def witness_charts(word, certificates):
    charts = word["initial"] + [None] * word["owned_fields"]
    recorded = []
    for clock, event in enumerate(word["program"]):
        operation, r = event[:2]
        if operation == "MOVE":
            charts[r] = event[3]
        elif operation == "INIT":
            charts[r] = event[2]
        elif operation == "CLEAR":
            terms = []
            for s_text, q in sorted(certificates[str(clock)].items(), key=lambda item: int(item[0])):
                s = int(s_text)
                require(0 <= s < len(charts) and s != r and charts[s] is not None and Fraction(q),
                        f"CLEAR witness is not live and non-self at {clock}")
                terms.append((s, charts[s], q))
            recorded.append((r, charts[r], terms))
            charts[r] = None
    require(len(recorded) == build.CLEARS, "witness chart denominator")
    return recorded


def prior_coverage(driver, root, raw_source):
    result = json.loads(pinned(root / "prior-native.json", INPUT_PINS["prior-native.json"]))
    require(result["status"] == "PASS_STRICT_379_NATIVE_FINITE"
            and result["source"]["raw_sha256"] == build.SOURCE_RAW
            and result["candidate"]["raw_sha256"] == build.B_RAW
            and result["phase_code_sha256"] == PHASE_CODE
            and result["artifacts"]["MOVE-PAIRS.json"] == INPUT_PINS["prior-pairs.json"], "the pinned low native run")
    role379, _ = build.apply_splice(raw_source, {j: build.REPLACEMENT[j] for j in (131142, 131294)})
    require(sha(build.canonical(role379)) == build.B_RAW, "reconstruct historical role-379 baseline")
    frames = raw_source["frames"]
    a = driver.groups_for(raw_source["program"], frames)
    b = driver.groups_for(role379["program"], frames)
    census = json.loads(pinned(root / "prior-pairs.json", INPUT_PINS["prior-pairs.json"]))
    require(census["counts"] == result["pair_counts"] and len(a) == 2986 and len(b) == 2987
            and sum(map(len, a.values())) == 6228 and sum(map(len, b.values())) == 6227
            and len(census["rows"]) == 2987, "low parent all-pair denominators")
    union = a.keys() | b.keys()
    accepted = set()
    for row in census["rows"]:
        pair = tuple(row["ascent"])
        require(pair in union and pair not in accepted
                and row["rank"] == len(frames[pair[1]]) - len(frames[pair[0]])
                and row["forward_columns"] == row["adjoint_columns"] == 512 and row["wrong_phase_rejected"] is True
                and row["source_occurrences"] == a.get(pair, []) and row["candidate_occurrences"] == b.get(pair, []),
                f"accepted all-pair occurrence transfer {pair}")
        accepted.add(pair)
    require(accepted == union, "incomplete parent catalogue")
    return accepted, result


def pair_columns(common, driver, phase, source, candidate, blocks, accepted):
    frames = source["frames"]
    a = driver.groups_for(source["program"], frames)
    b = driver.groups_for(candidate["program"], frames)
    fresh = {tuple(e[2:4]) for block in blocks.values() for move in block["move_edits"]
             for side in ("source", "candidate") for _, e in move[side]}
    union = a.keys() | b.keys()
    require(len(fresh) == 10 and fresh <= union and union - fresh <= accepted,
            "all changed and inherited transition checks are covered")
    rows = []
    for pair in sorted(union):
        row = {"ascent": pair, "source_occurrences": a.get(pair, []), "candidate_occurrences": b.get(pair, [])}
        if pair in fresh:
            row["fresh"] = common.exact_pair(phase, frames, *pair)
        else:
            row["transferred_from"] = INPUT_PINS["prior-pairs.json"]
        rows.append(row)
    return {"source_moves": sum(map(len, a.values())), "candidate_moves": sum(map(len, b.values())),
            "source_ascending_pairs": len(a), "candidate_ascending_pairs": len(b), "fresh_pairs": len(fresh),
            "transferred_pairs": len(union - fresh), "rows": rows}


def controls(common, driver, source, candidate, clock_map):
    c = clock_map[127446]
    m = clock_map[131294]

    def trial(clock, event):
        modified = driver.changed_event(candidate, clock, event)
        return driver.schedule(modified, build.SOURCE_EVENTS - 1, build.CLEARS, 281)

    bad_sign = driver.changed_event(candidate, c, ["ADD", 1091, 902, "-1/2", 373])
    driver.schedule(bad_sign, build.SOURCE_EVENTS - 1, build.CLEARS, 281)
    return {
        "old_contact_chart": driver.rejected(f"ADD frame at {c}", lambda: trial(c, build.OLD[127446])),
        "aliased_contact": driver.rejected(f"ADD frame at {c}", lambda: trial(c, ["ADD", 1091, 1091, "1/2", 373])),
        "legal_wrong_contact_sign": driver.rejected("unexpected public/protected scalar change", lambda: native_law(
            common, source, bad_sign, clock_map)),
        "wrong_move_chart": driver.rejected(f"MOVE source at {m}", lambda: trial(m, build.OLD[131294])),
        "wrong_public_flag": driver.rejected(f"MOVE flag at {m}", lambda: trial(m, ["MOVE", 379, 748, 1072, True])),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("inputs", "materialized", "out", "authorization"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    started = monotonic_ns()
    auth_bytes = args.authorization.read_bytes()
    auth = json.loads(auth_bytes)
    require(auth["public_claim"] == CLAIM and auth["running_event"] == REPLAY_EVENT
            and auth["source_raw_sha256"] == build.SOURCE_RAW and auth["raw_combined_sha256"] == build.C_RAW
            and auth["receipt_id"], "authorized native scope")
    args.out.mkdir(exist_ok=False)
    dump(args.out / "START.json", {"started_at": stamp(), "authorization": auth,
                                   "engine_pins": ENGINE_PINS, "input_pins": INPUT_PINS, "moduli": MODULI})
    pins = {args.inputs / filename: digest for filename, digest in INPUT_PINS.items()}
    pins.update({ENGINES / filename: digest for filename, digest in ENGINE_PINS.items()})
    pins[args.authorization] = sha(auth_bytes)
    for path, digest in pins.items():
        pinned(path, digest)
    raw_source, source, candidate, clock_map, source_terms, candidate_terms, binding, materialized = checked_inputs(
        args.inputs, args.materialized)
    pins.update(materialized)
    require(auth["candidate_raw_sha256"] == binding["candidate"]["raw_sha256"], "native candidate authorization")

    previous = json.loads(pinned(args.inputs / "combined-prior.json", INPUT_PINS["combined-prior.json"]))
    require(previous["status"] == "PASS_SCOPED_COMBINATION" and previous["candidate"]["decoded_sha256"] == build.C_RAW
            and previous["certificates"] == {"source": 180, "candidate": 180, "nonzero": 174}, "raw C predecessor")
    physical = load_engine("physical.py", "physical")
    load_engine("walsh.py", "walsh")
    common = load_engine("verify_native.py", "common_native")
    driver = load_engine("check_native_7660.py", "prior_native_driver")
    phase_code = driver.read_engine(ENGINES / "phase-source7636.py", ENGINE_PINS["phase-source7636.py"])
    require(sha(phase_code.encode()) == PHASE_CODE, "exact scalar-independent phase compiler")
    phase = driver.engine_from(phase_code)

    schedule_a = driver.schedule(source, build.SOURCE_EVENTS + 1, build.CLEARS, 281)
    schedule_b = driver.schedule(candidate, build.SOURCE_EVENTS - 1, build.CLEARS, 281)
    require(schedule_a["lifetime_trace"] == schedule_b["lifetime_trace"]
            and schedule_a["owned_paid"] == schedule_b["owned_paid"], "ordered owned schedules")
    paid = Counter(schedule_b["paid"])
    paid.subtract(schedule_a["paid"])
    require({rank: n for rank, n in paid.items() if n} == PAID_DELTA, "native paid profile delta")
    blocks, scalar = native_law(common, source, candidate, clock_map)
    a_witness = witness_charts(source, source_terms)
    b_witness = witness_charts(candidate, candidate_terms)
    require(a_witness == b_witness, "a retained CLEAR witness chart or coefficient changed")
    require(sum(bool(terms) for _, _, terms in a_witness) == 174, "nonzero erasure denominator")
    scalar["ordered_clear_witness_charts_sha256"] = sha(build.canonical(a_witness))
    scalar["ordered_clears"] = len(a_witness)

    mutations = controls(common, driver, source, candidate, clock_map)
    accepted, parent = prior_coverage(driver, args.inputs, raw_source)
    move = pair_columns(common, driver, phase, source, candidate, blocks, accepted)
    dump(args.out / "MOVE-PAIRS.json", move)
    paths = {name: common.route_columns(phase, source, candidate, edits) for name, edits in blocks.items()}
    require(sum(len(block["composed_paths"]) for block in paths.values()) == 4, "four changed composition paths")
    paths = {"all_forward": 512, "all_adjoint": 512, "wrong_phase": "rejected", "blocks": paths}
    ports = physical.raw_ports(phase, source, require)
    dump(args.out / "OPERATORS.json", {"scalar_law": scalar, "controls": mutations, "raw_ports": ports,
                                      "route_columns": paths})

    finite = []
    for prime, seed in MODULI:
        report = physical.evaluate(phase, source, candidate, prime, seed, clock_map[131294],
                                   prime == MODULI[0][0], require)
        name = f"prior-physical-{prime}.json"
        baseline = json.loads(pinned(args.inputs / name, INPUT_PINS[name]))
        require(parent["artifacts"][f"PHYSICAL-{prime}.json"] == INPUT_PINS[name]
                and baseline["prime"] == prime and baseline["seed"] == seed
                and report["endpoint_rows"] == baseline["endpoint_rows"] == 1501
                and report["owned_zero_rows"] == baseline["owned_zero_rows"] == 68
                and report["digests"] == baseline["digests"], f"repair changes the historical dense outputs at {prime}")
        for side in ("source", "candidate"):
            counters = report[side]
            require(counters["clears"] == 180 and counters["copy_zero_checks"] == 1
                    and counters["ordered_clear_values"] == baseline["source"]["ordered_clear_values"],
                    f"repair changes ordered physical CLEAR payloads at {prime} ({side})")
        dump(args.out / f"PHYSICAL-{prime}.json", report)
        finite.append(report)

    for path, digest in pins.items():
        pinned(path, digest)
    output = {"status": "PASS_7636_LOWERED_C_NATIVE", "pr": 7636, "head": build.HEAD,
              "source": binding["source"], "candidate": binding["candidate"],
              "source_parent_raw_sha256": build.SOURCE_RAW, "candidate_parent_raw_sha256": build.C_RAW,
              "public_claim": CLAIM, "running_event": REPLAY_EVENT, "raw_ports": ports, "route_columns": paths,
              "finite_replays": finite, "scalar_law": scalar, "controls": mutations, "native_paid_delta": PAID_DELTA,
              "pair_counts": {k: v for k, v in move.items() if k != "rows"}, "phase_code_sha256": PHASE_CODE,
              "source_schedules": {"source": schedule_a, "candidate": schedule_b},
              "artifacts": {p.name: sha(p.read_bytes()) for p in sorted(args.out.glob("*.json"))},
              "completed_at": stamp(), "elapsed_ns": monotonic_ns() - started}
    dump(args.out / "RESULT.json", output)
    print(f"{output['status']} word={binding['candidate']['raw_sha256']} pairs={move['fresh_pairs']} "
          "path_columns=2048/2048 endpoints=1501x2 clears=180x2", flush=True)


if __name__ == "__main__":
    main()
