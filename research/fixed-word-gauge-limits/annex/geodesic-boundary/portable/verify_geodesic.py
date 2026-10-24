"""Check the retained wire paths and the common-boundary rank invoice."""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json


ANNEX = Path(__file__).resolve().parents[1]
PACKAGE = ANNEX.parents[1]

BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE_HASH = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
PLAN_HASH = "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0"
PINS = {
    "history-encoding/FULL-MODE-PROGRAMS.json.gz":
        "ebc17d1d4c51a9c6b3cb05670d970db3d3e1000f26f1d864cdb27523ce1997dd",
    "history-encoding/ONE-SIDED-MODE-PROGRAMS.json.gz":
        "2f7d401c237b915db721d83b426cbe0bfa593e7c61170498f3be115cf20d16a7",
    "history-encoding/ONE-SHOT-MAX48.json":
        "6563798aeebe83d2d62c9d089012d2b7cea3818e673deaa4b2653be183a0ed21",
}
ASSEMBLY_HASH = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
READER_HASH = "1cce6ddeabd60f52e9ebafb02e2db4d289e68cdf5baaa106ca2397bf9cf7241a"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def pin(path, expected):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == expected, str(path) + " source pin")
    return raw


def load_reader(path):
    pin(path, READER_HASH)
    spec = spec_from_file_location("geodesic_source_reader", path)
    reader = module_from_spec(spec)
    spec.loader.exec_module(reader)
    return reader


def audit_program(word, program, original, reader):
    frames, start = word["frames"], word["start"]
    labels = [reader.lagrangian(frame) for frame in frames]
    current = list(start)
    paid = [0] * len(start)
    profile, operations = Counter(), Counter()
    touches = [[] for _ in start]
    native_kinds = ("climb", "adapter", "residual_adapter")
    require([e for e in program if e[0] in native_kinds] ==
            [e for e in original if e[0] in native_kinds],
            "complete retained native inventory")

    def distance(left, right):
        return len(reader.gf2_basis(labels[left] + labels[right])) - 9

    for index, event in enumerate(program):
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate, frame = event[1:]
            operations[gate[0]] += 1
            require(gate[0] in ("add", "scale"), "no persistent reset or copy in this word")
            registers = [gate[1]] + ([gate[2]] if gate[0] == "add" else [])
            for bank, register in registers:
                require(bank == "L" and 0 <= register < len(start), "persistent scalar register")
                require(current[register] == frame, "scalar access frame")
                touches[register].append((index, kind, event))
            continue
        require(kind in native_kinds, "retained native grammar")
        register = event[2]
        touches[register].append((index, kind, event))
        if kind != "climb":
            continue
        _, part, register, before, after, rank = event
        require(current[register] == before, "continuous persistent frame path")
        require(len(reader.gf2_basis(frames[before] + frames[after])) == len(frames[after]),
                "nested upward native step")
        require(rank == len(frames[after]) - len(frames[before]) == distance(before, after),
                "exact paid native rank")
        paid[register] += rank
        profile[rank] += 1
        current[register] = after
    endpoint = [distance(a, b) for a, b in zip(start, current)]
    require(paid == endpoint, "each persistent path attains its endpoint distance")
    require(sum(paid) == 5522 and sum(profile.values()) == 3486, "retained local rank invoice")
    normalized = list(endpoint)
    boundary_rows = []
    for port, q in enumerate(word["ports"]):
        x, y = port, word["v"] + port
        require(frames[start[x]] == [q] and start[y] == 0, "old data input frames")
        require(current[x] == 1, "old source full output frame")
        require(len(reader.gf2_basis(reader.transform(labels[start[x]], q) + labels[0])) == 9,
                "source line gauge gives raw input")
        require(len(reader.gf2_basis(reader.transform(labels[current[y]], q) + labels[1])) == 9,
                "target line gauge gives full output")
        require(endpoint[x] == endpoint[y] == 8, "old two data path distances")
        normalized[x] = distance(0, current[x])
        normalized[y] = distance(start[y], 1)
        require(normalized[x] == normalized[y] == 9, "new two data path distances")
        first, last = touches[x][0], touches[y][-1]
        require(first[1] == last[1] == "adapter", "literal adjacent boundary adapters")
        require(first[2][1] == "old_to_new" and last[2][1] == "new_to_old",
                "literal boundary adapter direction")
        first_climb = next(t for t in touches[x] if t[1] == "climb")
        last_climb = next(t for t in reversed(touches[y]) if t[1] == "climb")
        before = sum(t[1] == "scalar" and first[0] < t[0] < first_climb[0] for t in touches[x])
        after = sum(t[1] == "scalar" and last_climb[0] < t[0] < last[0] for t in touches[y])
        require(before > 0 and after > 0, "scalar access prevents direct paid-child adjacency")
        boundary_rows.append({"port": port, "line": q, "first_X_native_event": first[0],
                              "last_Y_native_event": last[0], "X_scalar_uses_before_paid_child": before,
                              "Y_scalar_uses_after_paid_child": after})
    require(sum(normalized) == 5746, "normalized local endpoint lower bound")
    return {"persistent_paths": len(start), "native_climbs": sum(profile.values()),
            "rank_zero_wrappers": sum(e[0] in ("adapter", "residual_adapter") for e in program),
            "scalar_macros": dict(operations), "persistent_CLEAR_macros": 0,
            "persistent_COPY_macros": 0, "private_C_references": 0,
            "native_profile": dict(sorted(profile.items())), "rank_mass": sum(paid),
            "wire_endpoint_distance_sum": sum(endpoint),
            "normalized_endpoint_distance_sum": sum(normalized),
            "minimum_added_rank_for_both_local_data_boundaries": sum(normalized) - sum(endpoint),
            "boundary_native_adjacency": boundary_rows}


def main(args):
    lanes = ANNEX / "frozen/lanes"
    reader = load_reader(PACKAGE / "checkers/review_wire_gauge.py")
    word, original = reader.load_source()
    programs = {}
    for name in ("FULL-MODE", "ONE-SIDED-MODE"):
        relative = "history-encoding/" + name + "-PROGRAMS.json.gz"
        programs[name] = json.loads(gzip.decompress(pin(lanes / relative, PINS[relative])))
    checks = {name: {side: audit_program(word, program, original[side], reader)
                     for side, program in variants.items()} for name, variants in programs.items()}

    controls = []
    for label, operation in (("wrong_native_rank", "rank"), ("persistent_clear", "clear"),
                             ("wrong_scalar_frame", "frame")):
        changed = json.loads(json.dumps(programs["FULL-MODE"]["forward"]))
        if operation == "rank":
            next(e for e in changed if e[0] == "climb")[-1] -= 1
        elif operation == "clear":
            changed.insert(0, ["scalar", ["clear", ["L", 0]], word["start"][0]])
        else:
            event = next(e for e in changed if e[0] == "scalar")
            event[-1] = 1 if event[-1] == 0 else 0
        try:
            audit_program(word, changed, original["forward"], reader)
        except ValueError as error:
            controls.append({"control": label, "rejected_by": str(error)})
        else:
            raise ValueError("negative control accepted: " + label)

    plan_raw = (ANNEX / "sources" / PLAN).read_bytes()
    require(sha256(plan_raw).hexdigest() == PLAN_HASH, "pinned controller plan")
    plan = json.loads(plan_raw)
    require((plan["T"], plan["M"], plan["live"], plan["K"], plan["L"]) ==
            (16, 73, 14336, 4, 9), "global productive geometry")
    assembly_path = ANNEX / "sources/research/community-frontier1094-audit/ASSEMBLY.json"
    assembly = json.loads(pin(assembly_path, ASSEMBLY_HASH))
    old_profile = Counter({int(r): count for r, count in assembly["complex_profile"].items()})
    old_mass = sum(r * count for r, count in old_profile.items())
    require(old_mass == 1041408 and old_profile[8] == 1152, "selected whole invoice")
    mode_plan = json.loads(pin(lanes / "history-encoding/ONE-SHOT-MAX48.json",
                               PINS["history-encoding/ONE-SHOT-MAX48.json"]))
    mode_count = sum(stage["mode_copies_all_replicas"] for stage in mode_plan["stages"])
    require(mode_count == 1152, "nine fresh mode cohorts")
    tails = Counter()
    for stage in mode_plan["stages"]:
        preparation = stage["preparation"]["children_in_execution_order"]
        completion = stage["completion"]["children_in_execution_order"]
        ranks = [child["rank"] for child in preparation + completion]
        require(sum(ranks) + stage["active"]["rank"] == 73, "each mode has full rank history")
        for rank in ranks:
            tails[rank] += stage["mode_copies_all_replicas"]
    delta = Counter(tails)
    delta[8] -= 1152
    delta[9] += 1152
    require(dict(sorted(delta.items())) ==
            {int(r): count for r, count in mode_plan["conditional_child_profile_delta"].items()},
            "complete inherited mode delta")
    before = Counter(old_profile)
    before.update(delta)
    live = plan["live"] + mode_count
    bound = 73 * live
    before_mass = sum(r * count for r, count in before.items())
    normalized = Counter(before)
    normalized[1] += plan["live"]
    require(old_mass - 8 * 1152 == 72 * plan["live"], "old non-centre geodesic mass")
    require(before_mass == 72 * plan["live"] + 73 * mode_count == 1116288,
            "one-shot pre-normalization whole invoice")
    require(sum(r * count for r, count in normalized.items()) == bound == 1130624,
            "common-boundary normalized invoice reaches the lower bound")
    require(all(0 < r <= 48 and count >= 0 for r, count in normalized.items()),
            "proper child ranks and nonnegative multiplicities")
    report = {"status": "PASS_COMMON_BOUNDARY_GEODESIC_PREMISES_AND_INVOICE",
              "source_base": BASE, "archive_sha256": ARCHIVE_HASH,
              "source_program_pins": PINS, "reader_sha256": READER_HASH,
              "assembly_sha256": ASSEMBLY_HASH, "plan_sha256": PLAN_HASH,
              "local_words": checks, "negative_controls": controls,
              "global_ledger": {"ambient_rank": 73, "replicas": 16,
                                "old_productive_families": plan["live"], "new_mode_families": mode_count,
                                "productive_families": live, "old_native_rank_mass": old_mass,
                                "before_boundary_rank_mass": before_mass,
                                "common_boundary_path_lower_bound": bound,
                                "minimum_added_rank": bound - before_mass,
                                "minimum_added_rank_per_replica_average": (bound - before_mass) // 16,
                                "literal_normalized_profile": dict(sorted(normalized.items())),
                                "moment_at_b_zero": "1", "moment_for_every_b_positive": ">1"},
              "scope": "Retained persistent wire paths and scalar accesses, arbitrary Clifford frame gauges, "
                       "and priced fusions, with raw input and full-F output frames on every productive path. "
                       "The global one-shot application inherits the owner-job invoice and exact mode history. "
                       "This check is not a global native emitter or supplier admission.",
              "scratch_scope": "No array COPY or CLEAR occurs in the two emitted mode macro words. "
                               "This does not assert absence of private scratch in real-arithmetic lowering. "
                               "Private zero arrays are excluded from productive paths; the allowed rewrite "
                               "does not move a productive lifetime into them or reset its frame for free."}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])
    print("local rank 5522 -> at least 5746; whole common-boundary rank 1130624; added rank 14336")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
