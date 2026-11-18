#!/usr/bin/env python3
"""Exact ordered native maps and signed caller bindings for the chart-595 split."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
from time import process_time


HERE = Path(__file__).resolve().parent
SUPPORT = HERE / "native_support"
HEAD = "1b4a4d6f9370b8c93b3f769a6229a9111ef3940e"
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
PARENT_PACKED = "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970"
SOURCE = "ab5653d6b6007f8a7987e7ffc6ebab24c662ba852a0d0b446c3a1be19b88db8a"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_PACKED = "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a"
WITNESS = "1430fe7318a6ada80a46683bca42444facaaca020ffe871d13518bf32095cfa9"
EDIT = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"
PIVOTS = "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85"
ASSETS = "f2d187f1c65f16947593ad1a78bd9d18beb0594c13202839901c7cd30a131065"
HOSTED = "5f9fd60011c100426a3dde09eeda9e0a65e337465083ec68ec712cf1af59ae73"
RELEASE = "progress.kappa-successor-7682-20261118t0927z.00000023"
SPLIT_PAIRS = ((3, 595), (595, 127))


def stamp():
    return datetime.now(timezone.utc).isoformat()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(blob):
    return sha256(blob).hexdigest()


def read(path, pin=None, decoded=None):
    raw = path.read_bytes()
    require(pin is None or digest(raw) == pin, f"byte custody for {path.name}")
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(decoded is None or digest(raw) == decoded, f"decoded custody for {path.name}")
    return json.loads(raw)


def write(path, value):
    raw = encode(value)
    with path.open("xb") as stream:
        stream.write(raw + b"\n")
    return digest(raw + b"\n")


def support_inputs():
    hosted = read(SUPPORT / "PR7682-HOSTED-READBACK.json", HOSTED)
    require(hosted["head"] == HEAD and hosted["equal_exact_candidate_graph"] == PARENT
            and hosted["all_15_saved_signal_markers"]
            and all(result == "success" for result in hosted["required_steps"].values()),
            "exact hosted #7682 source and saved-pivot replay")
    manifest = read(SUPPORT / "PR7682-ASSETS.json", ASSETS)
    pins = {entry["path"]: entry["sha256"] for entry in manifest["files"]}
    phase_pin = pins["evidence/PHASE-RESULT.json"]
    phase = read(SUPPORT / "PR7682-PHASE-RESULT.json", phase_pin)
    require(phase["status"] == "PASS_PAIRED_BANK24_EXACT_NATIVE_MAPS"
            and phase["graph_pins"]["candidate"] == PARENT
            and phase["role230_direct"] == SOURCE and phase["caller_sha256"] == CALLER
            and phase["pivot_manifest_sha256"] == PIVOTS, "committed #7682 phase result custody")
    for name in ("clifford_exact.py", "native_verify.py"):
        require(digest((SUPPORT / name).read_bytes()) == pins[f"engines/frozen/{name}"],
                f"committed attributed engine bytes for {name}")
    archive_pins = phase["artifact_sha256"]
    records = read(SUPPORT / "PR7682-BANK-RECIPES.json.gz", archive_pins["BANK-RECIPES.json.gz"])
    boundaries = read(SUPPORT / "PR7682-MAIN-BOUNDARIES.json", archive_pins["MAIN-BOUNDARIES.json"])
    archive = {tuple(record["pair"]): record for record in records}
    require(len(records) == len(archive) == phase["forward_union"] + phase["diagnostic_only_pivot_orientations"],
            "complete, unique archived ordered recipe inventory")
    return archive, boundaries, phase, {"hosted": HOSTED, "asset_manifest": ASSETS,
                                         "phase_result": phase_pin, **archive_pins}


def spans(ordered_frames):
    result = []
    for basis in ordered_frames:
        members = {0}
        for v in basis:
            require(type(v) is int and 0 < v < 512 and v not in members, "ordered independent axis")
            members |= {u ^ v for u in members}
        result.append(frozenset(members))
    return result


def physical_rank(pair, frames, subspaces, *, target=False):
    a, b = pair
    require(0 <= a < len(frames) and 0 <= b < len(frames)
            and (subspaces[a] < subspaces[b] or (not target and subspaces[b] < subspaces[a])),
            f"strictly nested physical charts {a}->{b}")
    return abs(len(frames[b]) - len(frames[a]))


def inventory(graph, mains, frames, subspaces):
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    n = len(graph["initial"])
    require(len(graph["final"]) == n and len(moves) == len(graph["moves"]) == 6142,
            "exact physical MOVE occurrence count and native endpoints")
    move_pairs, helpers = defaultdict(list), defaultdict(list)
    paid_ranks, target_ranks = Counter(), Counter()
    for k, pair in moves.items():
        paid_ranks[physical_rank(pair, frames, subspaces)] += 1
        move_pairs[pair].append(k)
    for role, pair in enumerate(zip(graph["initial"], graph["final"], strict=True)):
        if role not in mains:
            target_ranks[physical_rank(pair, frames, subspaces, target=True)] += 1
            helpers[pair].append(role)
    return moves, move_pairs, helpers, paid_ranks, target_ranks


def verify_cut(parent, child, edit, moves):
    first = parent["first_output"]
    retired, fresh = edit["retired_role"], edit["fresh_role"]
    require(first == child["first_output"] == 150522 and retired == 281 and fresh == 1501,
            "stable physical role and graph key namespace")
    require(parent["initial"][retired] == 3 and parent["final"][retired] == 127
            and child["initial"] == parent["initial"] + [595]
            and child["final"] == parent["final"][:retired] + [595] + parent["final"][retired + 1:] + [127],
            "exact split changes one checked role and appends one distinct boundary")
    forms = dict(child["forms"])
    schedule = child["schedule"]
    position = {k: i for i, k in enumerate(schedule)}
    require(len(position) == len(schedule) == len(forms) == len(child["forms"])
            and set(forms) == moves.keys() | set(range(first, first + fresh + 1)),
            "one exact chronological entry for each physical row")
    arrivals = {~r: a for r, a in enumerate(child["initial"])}
    arrivals.update({k: b for k, (_, b) in moves.items()})
    loads = 0
    for k, row in forms.items():
        chart = moves[k][0] if k in moves else child["final"][k-first]
        donors = {d for d, _ in row}
        require(len(donors) == len(row) and k in position
                and all(arrivals.get(d) == chart and (d < 0 or position[d] < position[k]) for d in donors),
                f"all donor reads at the literal ordered chart and before consumer {k}")
        loads += len(donors)
    cut = first + retired
    prefix, suffix = dict(edit["prefix"]), dict(edit["injection"])
    require(len(prefix) == 8 and len(suffix) == 10
            and dict(forms[cut]) == prefix and set(prefix).isdisjoint(suffix)
            and {k: dict(row)[~fresh] for k, row in forms.items() if any(d == ~fresh for d, _ in row)} == suffix,
            "literal prefix cut row and only the ten declared new owner reads")
    require(all(moves[k][1] == 595 and position[k] < position[cut] for k in prefix)
            and all(moves[k][0] == 595 and position[cut] < position[k] for k in suffix),
            "complete prefix observations before same-chart injected reads")
    return {"chart": 595, "retired_role": retired, "new_role": fresh, "cocharted_reads": loads,
            "prefix_rows": len(prefix), "suffix_rows": len(suffix),
            "candidate_cut_positions": [max(position[k] for k in prefix), position[cut],
                                        min(position[k] for k in suffix)]}


def main_boundary_checks(graph, frames, subspaces, records, interpret):
    observed, hosted_ports = set(), set()
    for index, record in enumerate(records):
        require(record["j"] == index, "literal order of the 104 native boundaries")
        x, y = record["main_roles"]
        q = record["q"]
        require(y == x + 112 and 0 < q < 512, "literal main port labels")
        a, b, c, d = record["charts"]
        require(frames[a] == [q] and not frames[b]
                and subspaces[d] == frozenset(s for s in range(512) if (s & q).bit_count() % 2 == 0),
                "main input and orthogonal output axes")
        pairs = [record["main_roles"]]
        if record["hosted_roles"] is not None:
            pairs.append(record["hosted_roles"])
            hosted_ports.add(index)
        for u, v in pairs:
            require(u != v and not observed.intersection((u, v))
                    and [graph["initial"][u], graph["initial"][v], graph["final"][u], graph["final"][v]] == [a,b,c,d],
                    "exact disjoint two-plane native chart binding")
            observed.update((u, v))
        frame_a, frame_c, frame_d = (interpret.frame(frames[i], 9) for i in (a, c, d))
        before, after = (record["input_recipe"], record["output_recipe"])
        require(before["rank"] == after["rank"] == 0, "the original main adapters are rank zero")
        interpret.equal(interpret.recipe(before), (("C", q, -1),) + frame_a, f"main {index} signed input")
        interpret.equal(interpret.recipe(after), interpret.adjoint(frame_d) + (("C", q, -1),)
                        + interpret.fourier(9), f"main {index} signed return")
        interpret.equal(frame_c, interpret.fourier(9), f"main {index} full Fourier return")
    require(len(records) == 104 and len(hosted_ports) == 96 and len(observed) == 400,
            "complete 104-port, 96-hosted, 400-main denominator")
    return observed, hosted_ports


def caller_bindings(caller, records, mains, hosted_ports):
    types = caller["types"]
    require(caller["ambient_rank"] == 137 and caller["stages"] == 16 and caller["roles"] == 68
            and len(caller["events"]) == 4192 and set(types) == {"A", "B"}
            and set(types["A"]["ports"]) == hosted_ports
            and set(types["B"]["ports"]) == set(range(104)) - hosted_ports,
            "literal physical 16-stage caller layout")
    roles = {kind: set(range(t["offset"], t["offset"] + t["roles"])) for kind, t in types.items()}
    require(len(roles["A"]) == len(roles["B"]) == 34
            and roles["A"].isdisjoint(roles["B"]), "two disjoint caller field types")
    all_roots = {("main", j, owner) for kind, spec in types.items()
                 for j in spec["ports"] for owner in roles[kind]}
    helper_ids = set(range(1502)) - mains
    require({281, 325, 1087, 1501} <= helper_ids and len(helper_ids) == 1102, "separate arbitrary helper owners")
    tags, roots, helper_tags = [], set(), set()
    for event in caller["events"]:
        if event[0] != "J":
            continue
        _, stage, a, b = event
        require(stage == len(tags) + 1 and len(a) == len(set(a)) == 4 and set(a) <= roles["A"]
                and len(b) == 4 and len(set(b[:2])) == 2 and set(b[:2]) <= roles["B"]
                and tuple(map(Fraction, b[2:])) == (-1, Fraction(1, 2)), "actual chronological joint owner binding")
        mapping = {}
        for record in records:
            j = record["j"]
            native = record["main_roles"]
            if j in hosted_ports:
                native = native + record["hosted_roles"]
            for r, owner in zip(native, a if j in hosted_ports else b[:2], strict=True):
                mapping[r] = ("main", j, owner)
        require(set(mapping) == mains and len(set(mapping.values())) == 400,
                "every stage binds its 400 native main owners injectively")
        roots.update(mapping.values())
        helpers = {r: ("helper", stage, r) for r in helper_ids}
        require(helper_tags.isdisjoint(helpers.values()), "fresh helper owners across all stage occurrences")
        helper_tags.update(helpers.values())
        mapping.update(helpers)
        tags.append([stage, sorted(mapping.items())])
    require(len(tags) == 16 and len(helper_tags) == 17632 and len(all_roots) == 3536
            and len(roots) == 3280 and roots <= all_roots,
            "complete actual native/root ownership on the unchanged caller bytes")
    return {"stages": len(tags), "root_owners": len(all_roots), "root_owners_in_native_calls": len(roots),
            "helper_owners": len(helper_tags),
            "new_owner_tags": [["helper", stage, 1501] for stage in range(1, 17)],
            "physical_binding_sha256": digest(encode(tags))}


def columns(interpret, ideal, actual, label):
    hashes = {}
    for reverse in (False, True):
        kind = "adjoint" if reverse else "forward"
        target = interpret.adjoint(ideal) if reverse else ideal
        implementations = [interpret.adjoint(c) if reverse else c for c in actual]
        column_hash = sha256()
        for col in range(512):
            expected = interpret.state(target, col)
            require(all(interpret.state(c, col) == expected for c in implementations), f"{label} {kind} column {col}")
            column_hash.update(encode([col, sorted(expected[0].items()), expected[1]]) + b"\n")
        hashes[kind] = column_hash.hexdigest()
    return hashes


def validate(args):
    archive, boundary_records, old_phase, custody = support_inputs()
    parent = read(HERE / "data/PARENT-GRAPH.json.gz", PARENT_PACKED, PARENT)
    candidate_path = HERE / "data/CANDIDATE-GRAPH.json.gz"
    candidate = read(candidate_path, args.candidate_gzip_sha, args.candidate_sha)
    caller = read(HERE / "data/CALLER.json.gz", CALLER_PACKED, CALLER)
    edit = read(HERE / "EDIT.json", EDIT)
    require(edit["source_head"] == HEAD and edit["source_graph_sha256"] == PARENT
            and edit["source_word_sha256"] == SOURCE and edit["caller_sha256"] == CALLER
            and edit["source_witness_sha256"] == WITNESS and edit["charts"] == [3, 595, 127],
            "same exact selected source and independent chart-595 cut")
    require(candidate["metadata"]["edit_sha256"] == EDIT
            and candidate["metadata"]["source_bank_graph_sha256"] == PARENT
            and candidate["metadata"]["source_pr_head"] == HEAD
            and candidate["metadata"]["fixed_pivot_sha256"] == PIVOTS,
            "candidate provenance pins match the independent input pins")
    require(parent["frames"] == candidate["frames"] and parent["moves"] == candidate["moves"],
            "stable ordered chart table and every paid MOVE occurrence")
    require(len(parent["initial"]) == len(parent["final"]) == 1501
            and len(candidate["initial"]) == len(candidate["final"]) == 1502,
            "complete parent and candidate public denominators")

    sys.path.insert(0, str(SUPPORT))
    import clifford_exact as produce
    import native_verify as interpret

    require(Path(produce.__file__).parent == Path(interpret.__file__).parent == SUPPORT,
            "compiler and independent checker loaded from exact frozen support")
    frames = candidate["frames"]
    subspaces = spans(frames)
    mains, hosted_ports = main_boundary_checks(candidate, frames, subspaces, boundary_records, interpret)
    binding = caller_bindings(caller, boundary_records, mains, hosted_ports)
    moves, move_pairs, old_helpers, paid, old_targets = inventory(parent, mains, frames, subspaces)
    _, _, new_helpers, new_paid, new_targets = inventory(candidate, mains, frames, subspaces)
    require({r: c for r, c in paid.items()} == {int(r): c for r, c in old_phase["candidate"]["native_paid"].items()}
            and paid == new_paid and dict(old_targets) == {int(r): c for r, c in old_phase["candidate"]["native_targets"].items()}
            and {r: new_targets[r]-old_targets[r] for r in range(1, 10) if new_targets[r] != old_targets[r]}
            == {1: 1, 8: 1, 9: -1}, "exact ordered-map inventory and only the new productive split")
    cut = verify_cut(parent, candidate, edit, moves)
    all_pairs = set(move_pairs) | set(old_helpers)
    require(all_pairs == set(move_pairs) | set(new_helpers) and len(all_pairs) == 3024,
            "every actual candidate ordered map has a source-bound old physical recipe")

    @cache
    def frame(i):
        return interpret.frame(frames[i], 9)

    def ideal(a, b):
        return interpret.adjoint(frame(a)) + frame(b)

    for pair in sorted(all_pairs):
        rec = archive[pair]
        rank = physical_rank(pair, frames, subspaces)
        require(rec["compared_signed_pauli_and_absolute_phase"] and rec["in_forward_union"]
                and sorted(rec["candidate_moves"]) == sorted(move_pairs.get(pair, ()))
                and sorted(rec["productive_roles"]) == sorted(old_helpers.get(pair, ()))
                and rec["recipe"]["rank"] == rank, f"exact archived bank occurrence-and-rank custody for {pair}")
        interpret.equal(interpret.recipe(rec["recipe"]), ideal(*pair), f"unchanged ordered native map {pair}")

    split_maps, circuits = [], []
    for (a, b), rank, role in zip(SPLIT_PAIRS, (1, 8), (281, 1501), strict=True):
        old = archive[a, b]
        recipe, _ = produce.lower_child(produce.canonical_frame(9, tuple(frames[a])).adjoint()
                                        .then(produce.canonical_frame(9, tuple(frames[b]))))
        require(recipe["rank"] == rank == physical_rank((a, b), frames, subspaces, target=True)
                and role in new_helpers[a, b] and role not in old_helpers[a, b],
                "the target uses the fresh checked map at the correct rank and owner")
        actual = interpret.recipe(recipe)
        target = ideal(a, b)
        interpret.equal(actual, target, f"recompiled productive map {a}->{b}")
        exact_columns = columns(interpret, target, [actual, interpret.recipe(old["recipe"])], f"split {a}->{b}")
        wrong = deepcopy(recipe)
        wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
        bad = interpret.recipe(wrong)
        require(interpret.tableau(bad) == interpret.tableau(actual), "wrong phase preserves signed Pauli action")
        try:
            interpret.equal(bad, target, f"phase mutation {a}->{b}")
        except ValueError as error:
            require(str(error).endswith("exact global phase"), "phase-only rejection reason")
        else:
            raise ValueError("phase-only mutation escaped")
        circuits.append(actual)
        split_maps.append({"charts": [a, b], "ordered_bases": [frames[a], frames[b]], "rank": rank,
                           "target_role": role, "recipe": recipe, "prior_recipe": old["recipe"],
                           "prior_paid_keys": old["candidate_moves"], "prior_proof": old["reuse"],
                           "exact_column_sha256": exact_columns, "columns_each_direction": 512,
                           "phase_only_mutation_rejected": True})
    require(87424 in split_maps[0]["prior_paid_keys"] and split_maps[1]["prior_paid_keys"] == [97328, 102698],
            "the exact established paid maps on the literal prefix/suffix cut agree")
    composite = circuits[0] + circuits[1]
    composite_columns = columns(interpret, ideal(3, 127), [composite, interpret.recipe(archive[3,127]["recipe"])],
                                "old full target and composition of the two ordered charts")
    artifact = write(args.out / "SPLIT-RECIPES.json", {"candidate_graph_sha256": args.candidate_sha,
                     "maps": split_maps, "composition_3_to_127_columns_sha256": composite_columns})
    return {"status": "PASS_CHART595_NATIVE_PHASE_AND_BINDING", "candidate_graph_sha256": args.candidate_sha,
            "candidate_graph_gzip_sha256": digest(candidate_path.read_bytes()), "recipient_graph_sha256": PARENT,
            "recipient_head": HEAD, "raw_recipient_word": SOURCE, "caller_sha256": CALLER, "custody": custody,
            "edit_sha256": EDIT,
            "ordered_pairs_rechecked": len(all_pairs), "paid_occurrences_rebound": sum(paid.values()),
            "productive_occurrences_parent": sum(old_targets.values()),
            "productive_occurrences_candidate": sum(new_targets.values()), "main_boundaries_rechecked": len(boundary_records),
            "hosted_correspondences_rechecked": len(hosted_ports), "fresh_split_maps": 2,
            "columns_each_direction_per_split_map": 512, "split_composition_columns_each_direction": 512,
            "wrong_phase_controls_rejected": 2, "cut": cut, "binding": binding,
            "artifact_sha256": {"SPLIT-RECIPES.json": artifact}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--candidate-gzip-sha")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "exact producer assertions must be enabled")
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = process_time()
    start = {"started_at": stamp(), "release_receipt": RELEASE, "recipient_head": HEAD,
             "recipient_graph_sha256": PARENT, "candidate_graph_sha256": args.candidate_sha,
             "candidate_gzip_sha256": args.candidate_gzip_sha, "runner_sha256": digest(Path(__file__).read_bytes())}
    start_sha = write(args.out / "START.json", start)
    try:
        result = validate(args)
    except Exception as exc:
        write(args.out / "FAILURE.json", {**start, "completed_at": stamp(), "error": str(exc),
               "cpu_seconds": process_time()-t0, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        raise
    result.update({"started_at": start["started_at"], "completed_at": stamp(), "start_sha256": start_sha,
                   "cpu_seconds": process_time()-t0, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    write(args.out / "PHASE-RESULT.json", result)
    print(result["status"], args.candidate_sha, result["ordered_pairs_rechecked"], result["fresh_split_maps"], flush=True)


if __name__ == "__main__":
    main()
