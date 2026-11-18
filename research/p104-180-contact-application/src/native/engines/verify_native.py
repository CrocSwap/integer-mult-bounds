#!/usr/bin/env python3
"""Verify a frozen public rechart relative to the exact #7660 native word."""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path
from time import monotonic_ns
from types import ModuleType

import physical
import walsh


SOURCE_HEAD = "d12b854d4825e9edfa3a3466909e1abf3525e929"
SOURCE_RAW = "f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669"
SOURCE_GZIP = "4e9cd9cc70a5423db44f870b35d8d6da9ac5746aa352f3af1420443f6dda350e"
PARENT_DRIVER = "6cc127ed1b1eddeadb50b69e672587e2c64378e5e5790357e526a9c022e32760"
PARENT_COMPILER = "334e37a3fb31c8cd374bc4ecafcdb9fb2597eb3192d3d49373417830458cb696"
PARENT_PHASE = "3b340b468d119fcca8bca015b0bab187119cd2593b25737ec496c9dc3564ebc6"
PARENT_RESULT = "01490a7539289511a367602466bb2e8749ce36e3aec642e9066c68dfdebd78b7"
PARENT_MOVE_CENSUS = "6ee58da2a668539882e635f7596ecf54f2029ad1b81347aa8c5f04f7030b7859"
PARENT_PRIME_RECEIPTS = {
    1000000009: "ab8f75845f296ca2789e225867f97b64758182caed2344c86a4b720a9aa5c167",
    998244353: "2b1ef0f69fe5bbdb35606e2b7d9a9ebe2c07f901abb0e1c13ad33a72e3dcb4a2",
}
MODULI = ((1000000009, 11), (998244353, 37))
SOURCE_EVENTS = 150009
SCALAR_EVENTS = 143844
CLEAR_COUNT = 234


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pinned(path, digest):
    require(path.is_file() and not path.is_symlink(), f"input is missing or symlinked: {path}")
    data = path.read_bytes()
    require(sha(data) == digest, f"input SHA-256: {path}")
    return data


def stamp():
    return datetime.now(timezone.utc).isoformat()


def dump(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")


def word(path, packed_digest, raw_digest):
    raw = gzip.decompress(pinned(path, packed_digest))
    require(sha(raw) == raw_digest, f"decoded SHA-256: {path}")
    obj = json.loads(raw)
    require(raw == canonical(obj), f"decoded word is not canonical: {path}")
    return obj


def parent_numerics(root):
    driver_path = root / "application-evidence/native-replay/check_native.py"
    driver = ModuleType("pinned_7660_native_driver")
    exec(compile(pinned(driver_path, PARENT_DRIVER), str(driver_path), "exec"), driver.__dict__)
    phase_code = driver.read_engine(root / "retained/pr7658/check.py", PARENT_COMPILER)
    require(sha(phase_code.encode()) == PARENT_PHASE, "phase engine differs from #7660")
    return driver, driver.engine_from(phase_code)


def group_tape(word):
    """Anchor MOVE order to the ordinal of each normalized scalar operator."""
    scalars, moves = [], defaultdict(list)
    for clock, event in enumerate(word["program"]):
        if event[0] == "MOVE":
            moves[len(scalars)].append((clock, event))
        else:
            scalars.append((clock, event))
    return scalars, moves


def public_scalar(event, count):
    op = event[0]
    if op == "SCALE":
        return event[1] < count
    if op == "ADD":
        return event[1] < count and event[2] < count
    return False


def normalized_edits(source, candidate):
    n = source["public"]
    require(source.keys() == candidate.keys()
            and all(candidate[k] == v for k, v in source.items() if k != "program"),
            "native word header changed")
    old_scalars, old_moves = group_tape(source)
    new_scalars, new_moves = group_tape(candidate)
    require(len(old_scalars) == len(new_scalars) == SCALAR_EVENTS, "scalar denominator")
    contacts, move_edits, owned = [], [], 0
    for ordinal, ((old_clock, old), (new_clock, new)) in enumerate(zip(old_scalars, new_scalars)):
        if old != new:
            require(public_scalar(old, n) and old[:-1] == new[:-1],
                    f"normalized or protected scalar changed at {old_clock}/{new_clock}")
            contacts.append({"scalar_ordinal": ordinal, "source_clock": old_clock, "source": old,
                             "candidate_clock": new_clock, "candidate": new})
        if not public_scalar(old, n):
            owned += 1

    for ordinal in sorted(old_moves.keys() | new_moves.keys()):
        old, new = old_moves[ordinal], new_moves[ordinal]
        old_events = [tuple(e) for _, e in old]
        new_events = [tuple(e) for _, e in new]
        if old_events == new_events:
            continue
        matcher = SequenceMatcher(a=old_events, b=new_events, autojunk=False)
        for op, a, b, c, d in matcher.get_opcodes():
            if op == "equal":
                continue
            drop, put = old[a:b], new[c:d]
            require(all(e[1] < n and e[4] is False for _, e in (*drop, *put)),
                    f"protected MOVE changed before scalar {ordinal}")
            move_edits.append({"before_scalar_ordinal": ordinal, "source": drop, "candidate": put})

    require(move_edits, "no changed MOVE")
    roles = sorted({event[1] for edit in move_edits for side in ("source", "candidate")
                    for _, event in edit[side]})
    return {"scalar_events": SCALAR_EVENTS, "protected_scalar_events": owned,
            "changed_public_move_roles": roles, "recharted_contacts": contacts,
            "move_edits": move_edits}


def parent_pairs(driver, source, result, census_bytes):
    require(result["status"] == "PASS_STRICT_379_NATIVE_FINITE"
            and result["candidate"]["raw_sha256"] == SOURCE_RAW
            and result["candidate"]["gzip_sha256"] == SOURCE_GZIP
            and result["phase_code_sha256"] == PARENT_PHASE
            and result["artifacts"]["MOVE-PAIRS.json"] == PARENT_MOVE_CENSUS,
            "prior result binding")
    census = json.loads(census_bytes)
    actual = driver.groups_for(source["program"], source["frames"])
    count = {"ascent_groups": len(actual), "move_occurrences": sum(map(len, actual.values())),
             "directed_pairs": len({(x[2], x[3]) for entries in actual.values() for x in entries})}
    require(census["counts"]["candidate"] == result["pair_counts"]["candidate"] == count
            == {"ascent_groups": 2959, "move_occurrences": 6165, "directed_pairs": 2981},
            "prior MOVE denominator")
    accepted = set()
    for row in census["rows"]:
        key = tuple(row["ascent"])
        require(key in actual and key not in accepted and row["candidate_occurrences"] == actual[key]
                and row["rank"] == len(source["frames"][key[1]]) - len(source["frames"][key[0]])
                and row["forward_columns"] == row["adjoint_columns"] == walsh.SIZE
                and row["wrong_phase_rejected"] is True, f"prior MOVE entry {key}")
        accepted.add(key)
    require(accepted == set(actual), "prior MOVE coverage is incomplete")
    return actual


def exact_pair(phase, frames, a, b):
    before, after = tuple(frames[a]), tuple(frames[b])
    expected = phase.dagger(phase.frame_circuit(before)) + phase.frame_circuit(after)
    recipe = phase.lower(phase.frame_op(before).dag().then(phase.frame_op(after)))
    require(recipe["rank"] == len(after) - len(before), f"paid ascent rank {a},{b}")
    compiled = phase.recipe_circuit(recipe)
    require(phase.tableau(compiled) == phase.tableau(expected), f"signed action {a},{b}")
    for x, y, direct_circuit, recipe_circuit in (
        (before, after, expected, compiled),
        (after, before, phase.dagger(expected), phase.dagger(compiled)),
    ):
        wrong = recipe_circuit + (("phase", 1),)
        require(phase.tableau(wrong) == phase.tableau(recipe_circuit), "phase control tableau premise")
        for unit in range(walsh.SIZE):
            oracle = walsh.transition(x, y, unit)
            require(walsh.equal_gaussian_columns(oracle, phase.column(direct_circuit, unit)),
                    f"canonical Walsh basis disagreement {a},{b}, column {unit}")
            require(walsh.equal_gaussian_columns(oracle, phase.column(recipe_circuit, unit)),
                    f"compiled Walsh basis disagreement {a},{b}, column {unit}")
            if unit == 0:
                require(not walsh.equal_gaussian_columns(oracle, phase.column(wrong, unit)),
                        f"absolute phase control accepted {a},{b}")
    return {"rank": recipe["rank"], "forward_columns": walsh.SIZE, "adjoint_columns": walsh.SIZE,
            "absolute_phase_rejections": 2}


def pair_replay(driver, phase, source, candidate, prior, edits):
    frames = source["frames"]
    current = driver.groups_for(candidate["program"], frames)
    changed_pairs = set()
    for edit in edits["move_edits"]:
        for side in ("source", "candidate"):
            for _, (_, _, a, b, _) in edit[side]:
                if len(frames[a]) > len(frames[b]):
                    a, b = b, a
                changed_pairs.add((a, b))
    fresh = changed_pairs | (current.keys() - prior.keys())
    rows = []
    for a, b in sorted(prior.keys() | current.keys()):
        row = {"ascent": (a, b), "source_occurrences": prior.get((a, b), []),
               "candidate_occurrences": current.get((a, b), [])}
        if (a, b) in fresh:
            row["fresh"] = exact_pair(phase, frames, a, b)
        else:
            row["prior_census_sha256"] = PARENT_MOVE_CENSUS
        rows.append(row)
    require(fresh <= (prior.keys() | current.keys()), "missing changed transition")
    return {"source_groups": len(prior), "candidate_groups": len(current),
            "source_moves": sum(map(len, prior.values())), "candidate_moves": sum(map(len, current.values())),
            "fresh_groups": len(fresh), "transferred_groups": len(rows) - len(fresh), "rows": rows}


def route_columns(phase, source, candidate, edits):
    """Verify separate cross-contact terms along the two literal route histories."""
    contacts = edits["recharted_contacts"]
    ordinals = [edit["before_scalar_ordinal"] for edit in edits["move_edits"]]
    ordinals.extend(contact["scalar_ordinal"] for contact in contacts)
    low, high = min(ordinals), max(ordinals)
    roles = set(edits["changed_public_move_roles"])
    for contact in contacts:
        event = contact["source"]
        roles.update(event[1:3] if event[0] == "ADD" else [event[1]])

    def cut(word):
        charts = {r: word["initial"][r] for r in roles}
        routes = {r: [] for r in roles}
        ordinal = 0
        for clock, event in enumerate(word["program"]):
            if ordinal > high:
                break
            if event[0] != "MOVE":
                ordinal += 1
                continue
            _, r, a, b, _ = event
            if r in roles:
                if ordinal < low:
                    charts[r] = b
                else:
                    routes[r].append((clock, a, b))
        return charts, routes

    source_enter, source_routes = cut(source)
    candidate_enter, candidate_routes = cut(candidate)
    require(source_enter == candidate_enter, "edited route cut has different entry charts")
    frames = source["frames"]

    @cache
    def compiled(a, b):
        recipe = phase.lower(phase.frame_op(frames[a]).dag().then(phase.frame_op(frames[b])))
        require(recipe["rank"] == len(frames[b]) - len(frames[a]), f"composed path rank {a},{b}")
        return phase.recipe_circuit(recipe)

    def charts(enter, moves):
        result = [enter]
        for _, a, b in moves:
            require(result[-1] == a, "route composition lost an intermediate chart")
            result.append(b)
        return result

    def circuit(path):
        return tuple(g for a, b in zip(path, path[1:]) for g in compiled(a, b))

    def compare(label, old_path, new_path):
        require((old_path[0], old_path[-1]) == (new_path[0], new_path[-1]), f"restoration chart {label}")
        old, new = map(circuit, (old_path, new_path))
        for a, b in ((old, new), (phase.dagger(old), phase.dagger(new))):
            require(phase.tableau(a) == phase.tableau(b), f"composed signed action {label}")
            for unit in range(walsh.SIZE):
                require(phase.column(a, unit) == phase.column(b, unit),
                        f"composed exact column {label}, {unit}")
        wrong = new + (("phase", 1),)
        require(phase.tableau(wrong) == phase.tableau(new) and phase.column(wrong) != phase.column(old),
                f"composed absolute phase control {label}")
        return {"path": label, "source": old_path, "candidate": new_path,
                "forward_columns": walsh.SIZE, "adjoint_columns": walsh.SIZE, "wrong_phase": "rejected"}

    def contribution(enter, moves, contact, side):
        r, s = contact[side][1:3]
        clock = contact[f"{side}_clock"]
        before = [(j, a, b) for j, a, b in moves[s] if j < clock]
        after = [(j, a, b) for j, a, b in moves[r] if j > clock]
        prefix = charts(enter[s], before)
        require(prefix[-1] == contact[side][-1], f"contribution chart at {clock}")
        return charts(enter[s], before + after)

    rows = [compare(f"role {r} independent entry to return",
                    charts(source_enter[r], source_routes[r]), charts(candidate_enter[r], candidate_routes[r]))
            for r in sorted(roles)]
    for contact in contacts:
        if contact["source"][0] == "ADD":
            r, s, coefficient, _ = contact["source"][1:]
            row = compare(f"role {s} contribution to {r} at source {contact['source_clock']}",
                          contribution(source_enter, source_routes, contact, "source"),
                          contribution(candidate_enter, candidate_routes, contact, "candidate"))
            row["coefficient"] = coefficient
            rows.append(row)
    return {"all_forward": walsh.SIZE, "all_adjoint": walsh.SIZE, "wrong_phase": "rejected",
            "first_scalar_ordinal": low, "last_scalar_ordinal": high, "composed_paths": rows}


def contact_controls(driver, source, candidate, edits, test_clock):
    new_events = len(candidate["program"])
    changed_arrivals = {clock for edit in edits["move_edits"] for clock, _ in edit["candidate"]}
    require(test_clock in changed_arrivals, "phase control is not on an edited candidate MOVE")

    def mutate(clock, event):
        return driver.changed_event(candidate, clock, event)

    def schedule(trial):
        return driver.schedule(trial, new_events, CLEAR_COUNT, 281)

    move = candidate["program"][test_clock]
    controls = {"wrong_move_source": driver.rejected(
        f"MOVE source at {test_clock}", lambda: schedule(mutate(test_clock, move[:2] + [move[3], *move[3:]]))),
        "public_owned_flag": driver.rejected(
            f"MOVE flag at {test_clock}", lambda: schedule(mutate(test_clock, [*move[:4], True])))}
    contacts = edits["recharted_contacts"]
    if contacts:
        contact = contacts[0]
        clock = contact["candidate_clock"]
        event = contact["candidate"]
        controls["wrong_contact_chart"] = driver.rejected(
            f"{event[0]} frame at {clock}", lambda: schedule(mutate(clock, contact["source"])))
        coefficient_index = 2 if event[0] == "SCALE" else 3
        signed = list(event)
        signed[coefficient_index] = str(-Fraction(event[coefficient_index]))
        sign_mutant = mutate(clock, signed)
        schedule(sign_mutant)
        controls["legal_same_rank_wrong_coefficient_sign"] = driver.rejected(
            "normalized or protected scalar changed", lambda: normalized_edits(source, sign_mutant))

    first_add = next((j for j in contacts if j["candidate"][0] == "ADD"), None)
    if first_add is not None:
        clock, event = first_add["candidate_clock"], first_add["candidate"]
        controls["aliased_public_contact"] = driver.rejected(
            f"ADD frame at {clock}", lambda: schedule(mutate(clock, [*event[:2], event[1], *event[3:]])))
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("parent-package", "parent-census", "candidate", "binding", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    started = monotonic_ns()
    parent = args.parent_package
    spec_raw = args.binding.read_bytes()
    spec = json.loads(spec_raw)
    require(spec["source_head"] == SOURCE_HEAD and spec["source_raw_sha256"] == SOURCE_RAW,
            "binding source pin")
    require(spec["public_claim"] and spec["running_event"], "missing public claim or goal event")
    source_path = parent / "application-evidence/signed-replay/data/WORD.json.gz"
    parent_result_path = parent / "application-evidence/receipts/native/RESULT.json"
    driver_path = parent / "application-evidence/native-replay/check_native.py"
    compiler_path = parent / "retained/pr7658/check.py"
    prior_fields = {p: parent / f"application-evidence/receipts/native/PHYSICAL-{p}.json" for p, _ in MODULI}
    pins = {source_path: SOURCE_GZIP, args.candidate: spec["candidate_gzip_sha256"],
            args.binding: sha(spec_raw), driver_path: PARENT_DRIVER, compiler_path: PARENT_COMPILER,
            parent_result_path: PARENT_RESULT, args.parent_census: PARENT_MOVE_CENSUS}
    pins.update({path: PARENT_PRIME_RECEIPTS[p] for p, path in prior_fields.items()})
    scripts = (Path(__file__), Path(physical.__file__), Path(walsh.__file__))
    script_pins = {p: sha(p.read_bytes()) for p in scripts}
    args.out.mkdir(exist_ok=False)
    dump(args.out / "START.json", {"started_at": stamp(), "binding": spec,
                                  "pins": {str(p): s for p, s in pins.items()},
                                  "scripts": {p.name: s for p, s in script_pins.items()},
                                  "primes_and_seeds": MODULI})

    source = word(source_path, SOURCE_GZIP, SOURCE_RAW)
    candidate = word(args.candidate, spec["candidate_gzip_sha256"], spec["candidate_raw_sha256"])
    result = json.loads(pinned(parent_result_path, PARENT_RESULT))
    driver, phase = parent_numerics(parent)
    source_schedule = driver.schedule(source, SOURCE_EVENTS, CLEAR_COUNT, 281)
    candidate_schedule = driver.schedule(candidate, spec["candidate_events"], CLEAR_COUNT, 281)
    require(source_schedule["lifetime_trace"] == candidate_schedule["lifetime_trace"]
            and source_schedule["owned_paid"] == candidate_schedule["owned_paid"],
            "protected owned lifetime sequence")
    edits = normalized_edits(source, candidate)
    require(edits["changed_public_move_roles"] == spec["changed_public_move_roles"], "public edit role scope")
    if "recharted_contact_count" in spec:
        require(len(edits["recharted_contacts"]) == spec["recharted_contact_count"], "contact edit denominator")
    dump(args.out / "EDITS.json", edits)

    test_clock = spec["phase_control_clock"]
    controls = contact_controls(driver, source, candidate, edits, test_clock)
    prior = parent_pairs(driver, source, result, pinned(args.parent_census, PARENT_MOVE_CENSUS))
    pairs = pair_replay(driver, phase, source, candidate, prior, edits)
    dump(args.out / "MOVE-PAIRS.json", pairs)
    raw_ports = physical.raw_ports(phase, source, require)
    routes = route_columns(phase, source, candidate, edits)
    dump(args.out / "OPERATORS.json", {"controls": controls, "raw_ports": raw_ports,
                                      "fresh_pairs": pairs["fresh_groups"], "walsh_basis_size": walsh.SIZE,
                                      "route_columns": routes})

    finite = []
    for prime, seed in MODULI:
        field = physical.evaluate(phase, source, candidate, prime, seed, test_clock,
                                  prime == MODULI[0][0], require)
        earlier = json.loads(pinned(prior_fields[prime], PARENT_PRIME_RECEIPTS[prime]))
        require(earlier["prime"] == prime and earlier["seed"] == seed
                and field["endpoint_rows"] == earlier["endpoint_rows"] == 1501
                and field["owned_zero_rows"] == earlier["owned_zero_rows"] == 68
                and field["digests"]["initial"] == earlier["digests"]["initial"]
                and field["digests"]["source"] == earlier["digests"]["candidate"]
                and field["digests"]["reference_public"] == earlier["digests"]["reference_public"]
                and field["source"] == earlier["candidate"], f"prior physical replay transfer at {prime}")
        dump(args.out / f"PHYSICAL-{prime}.json", field)
        finite.append(field)

    for path, digest in (pins | script_pins).items():
        pinned(path, digest)
    report = {
        "status": "PASS_7660_PUBLIC_RECHART_NATIVE",
        "pr": 7660, "head": SOURCE_HEAD,
        "candidate": {"raw_sha256": spec["candidate_raw_sha256"], "gzip_sha256": spec["candidate_gzip_sha256"],
                      "canonical_sha256": spec["candidate_raw_sha256"]},
        "source": {"pr": 7660, "head": SOURCE_HEAD, "raw_sha256": SOURCE_RAW, "gzip_sha256": SOURCE_GZIP,
                   "canonical_sha256": SOURCE_RAW},
        "public_claim": spec["public_claim"], "running_event": spec["running_event"],
        "source_schedule": source_schedule, "candidate_schedule": candidate_schedule,
        "phase_code_sha256": PARENT_PHASE, "prior_result_sha256": PARENT_RESULT,
        "exact": {k: v for k, v in pairs.items() if k != "rows"},
        "controls": controls, "raw_ports": raw_ports, "finite_replays": finite, "route_columns": routes,
        "artifacts": {p.name: sha(p.read_bytes()) for p in sorted(args.out.glob("*.json"))},
        "completed_at": stamp(), "elapsed_ns": monotonic_ns() - started,
    }
    dump(args.out / "RESULT.json", report)
    print(f"{report['status']} word={spec['candidate_raw_sha256']} pairs={pairs['fresh_groups']}", flush=True)


if __name__ == "__main__":
    main()
