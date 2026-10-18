#!/usr/bin/env python3
"""Replay a seed-selected third-order transport census on the PR589 bit word."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCES = PACKAGE / "SOURCES.json"
RESULT = PACKAGE / "RESULT.json"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SELECTED_KAPPA = "836330098538459/500000000000000000"
BIT_C = "1733427039589844234749/1000000000000000000000000"
PR1345_HEAD = "b54a856aa79857d91cd5d65f8f7144e26c8c084f"
PR589_HEAD = "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46"
SEED = 5
EXPECTED_TRIPLE = (927, 928, 930)
EXPECTED_OPS = ((282, 325, 256), (282, 325, 442), (282, 325, 392))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def check_source_pins(sources):
    need(sources["schema_version"] == 1 and sources["base_commit"] == BASE,
         "exact base source manifest")
    for row in sources["base_files"]:
        raw = (ROOT / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "base SHA-256: " + row["path"])
        need(git_blob(raw) == row["git_blob"], "base Git blob: " + row["path"])
    need(len(sources["vendored_files"]) == 1, "single pinned PR1345 source file")
    for row in sources["vendored_files"]:
        raw = (PACKAGE / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "vendored SHA-256: " + row["path"])
        need(git_blob(raw) == row["git_blob"], "vendored Git blob: " + row["path"])
        need(row["upstream_head"] == PR1345_HEAD, "PR1345 exact head")
    pred = sources["predecessors"]
    need(pred["pr589"]["head"] == PR589_HEAD, "selected PR589 source head")
    need(pred["pr1345"]["head"] == PR1345_HEAD, "PR1345 predecessor head")
    need(pred["pr1382"]["head"] == "cf17b06c00c50a22315f210c5f6b5197c860abdd",
         "PR1382 overlap head")
    need(pred["pr1048"]["head"] == "07730cd8302c378607259a9ad0efb73e0b57a2f2",
         "PR1048 scope head")


def load_exact_atlas(vendor_path):
    """Load PR1345's definitions, stopping before its full single/pair census."""
    source = vendor_path.read_text()
    marker = "out = {'word': WORD"
    cut = source.find(marker)
    need(cut >= 0, "pinned PR1345 atlas entry point")
    # The source's own ROOT calculation expects the upstream package path.
    upstream_path = ROOT / "research/bit589-transport-atlas/atlas.py"
    namespace = {"__file__": str(upstream_path), "__name__": "seed05_pinned_pr1345_atlas"}
    old_argv = sys.argv
    try:
        sys.argv = [str(upstream_path)]
        exec(compile(source[:cut], str(upstream_path), "exec"), namespace)
    finally:
        sys.argv = old_argv
    need(namespace["ROOT"].resolve() == ROOT.resolve(), "PR1345 repository root")
    return namespace


def find_seed_triple(ops, opts):
    movable = [i for i in range(len(ops)) if len(opts[i]) > 1]
    by_reg = {}
    for i in movable:
        for register in (ops[i][1], ops[i][2]):
            by_reg.setdefault(register, set()).add(i)

    parent = {i: i for i in movable}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for operation_set in by_reg.values():
        for i, j in itertools.combinations(sorted(operation_set), 2):
            a, b = find(i), find(j)
            if a != b:
                parent[a] = b

    components = {}
    for i in movable:
        components.setdefault(find(i), []).append(i)
    giant = set()
    for operation_set in components.values():
        full_product = math.prod(len(opts[i]) for i in operation_set)
        if full_product > 200_000:
            giant.update(operation_set)

    candidates = set()
    for operation_set in by_reg.values():
        for triple in itertools.combinations(sorted(operation_set & giant), 3):
            product = math.prod(len(opts[i]) for i in triple)
            frame_sensitive = all(len({frame for _, frame in opts[i]}) > 1
                                  for i in triple)
            if product <= 5_000 and frame_sensitive:
                candidates.add(triple)
    ordered = sorted(candidates,
                     key=lambda t: (math.prod(len(opts[i]) for i in t), t))
    need(len(ordered) == 200, "complete seed-selected A-triple candidate pool")
    index = SEED % len(ordered)
    return ordered, index, ordered[index]


def make_word(word, ops, choice, frame_sets, wlib):
    candidate = copy.deepcopy(word)
    flat = [(f, t, s) for f, t, sources in candidate["A"] for s in sources]
    need(len(flat) == len(ops), "A operation flattening")
    events = []
    for j, (frame, target, source) in enumerate(flat):
        if j in choice:
            slot, new_frame = choice[j]
            key = (slot - 0.5, j)
        else:
            new_frame = frame
            key = (j, j)
        events.append((key, j, new_frame, target, source))
    events.sort()
    candidate["A"] = [[frame, target, [source]]
                       for _, _, frame, target, source in events]
    # Include the exact PR1345 closure frames used by the option enumerator.
    candidate["frames"] = frame_sets
    candidate["C"] = wlib.rebuild_C(candidate)
    return candidate


def profile_payload(profile):
    return {str(k): v for k, v in sorted(profile.items())}


def profile_sha(profile):
    return sha(canonical(profile_payload(profile)))


def profile_price_interval(ns, baseline, profile):
    """Reprice the full profile delta from rank counts, with signed intervals."""
    low = high = ns["Q"](0)
    for rank in set(baseline) | set(profile):
        delta_count = profile.get(rank, 0) - baseline.get(rank, 0)
        unit_low, unit_high = ns["P"][rank]
        if delta_count >= 0:
            low += delta_count * unit_low
            high += delta_count * unit_high
        else:
            low += delta_count * unit_high
            high += delta_count * unit_low
    return low, high


def reject_replay(wlib, frame_obj, word):
    try:
        wlib.replay(word, frame_obj)
    except AssertionError:
        return True
    return False


def verify():
    sources = json.loads(SOURCES.read_bytes())
    check_source_pins(sources)
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == SELECTED_KAPPA, "selected conditional kappa")
    assembly = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_bytes())
    need(assembly["kappa"] == SELECTED_KAPPA, "selected assembly kappa")
    bit = assembly["bit_supplier"]
    need(bit["pr"] == 589 and bit["commit"] == PR589_HEAD and
         bit["word"]["v"] == 111 and bit["word"]["decoder_constant"] == 63,
         "selected PR589 supplier identity")

    expected = json.loads((ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json").read_bytes())
    need(expected["nine"]["bit_lower"] == BIT_C, "exact PR589 bit saving")
    word_path = ROOT / "research/e8-bit-p111-tuned" / expected["word"]["file"]
    need(sha(word_path.read_bytes()) == expected["word"]["file_sha256"],
         "exact selected tuned word bytes")
    need(expected["word"]["local_histogram"] ==
         {"1": 1323, "2": 1342, "3": 79, "4": 44, "5": 102, "6": 11, "7": 19},
         "selected PR589 baseline profile")

    ns = load_exact_atlas(PACKAGE / "vendor/pr1345/atlas.py")
    need(str(ns["C"]) == BIT_C, "PR1345 exact objective c")
    need(ns["w"]["v"] == 111 and ns["w"]["R"] == 439,
         "PR589 tuned word parameters")
    ops, tl, opts = ns["options"]("A")
    ordered, seed_index, triple = find_seed_triple(ops, opts)
    need(seed_index == 5 and triple == EXPECTED_TRIPLE,
         "OS-seed-indexed exact frame-sensitive triple")
    need(tuple(tuple(ops[i]) for i in triple) == EXPECTED_OPS,
         "selected operation identity and shared target")
    common = set(ops[triple[0]][1:]) & set(ops[triple[1]][1:]) & set(ops[triple[2]][1:])
    need(common == {325}, "three operations share only target register 325")
    domains = [opts[i] for i in triple]
    need([len(x) for x in domains] == [7, 6, 5], "complete individual option counts")
    joint_count = math.prod(len(x) for x in domains)
    need(joint_count == 210, "complete fixed single-move option product")

    word = ns["w"]
    wlib = ns["wlib"]
    frame_sets = [[k for k in range(ns["NL"]) if mask >> k & 1]
                  for mask in ns["masks"]]
    expanded_word = copy.deepcopy(word)
    expanded_word["frames"] = frame_sets
    frame_obj = wlib.Frames(expanded_word)
    baseline = wlib.paid(word, frame_obj)
    need(profile_payload(baseline) == expected["word"]["local_histogram"],
         "baseline full replay profile")

    assignment_rows = []
    profile_classes = {profile_sha(baseline): profile_payload(baseline)}
    counts = {"joint_chain_invalid": 0, "profile_tie": 0, "strict_loss": 0,
              "strict_improvement": 0, "unresolved": 0}
    zero_price = []
    loss_price = []
    home_choice = {i: next(option for option in domains[k]
                           if option == (i, ops[i][0]))
                   for k, i in enumerate(triple)}

    for combo in itertools.product(*domains):
        choice = {i: option for i, option in zip(triple, combo)}
        moves = [(i, q, frame) for i, (q, frame) in choice.items()]
        interval = ns["score"]("A", ops, tl, moves)
        candidate = make_word(word, ops, choice, frame_sets, wlib)
        row = {"moves": [[i, q, frame] for i, (q, frame) in choice.items()]}
        if interval is None:
            counts["joint_chain_invalid"] += 1
            need(reject_replay(wlib, frame_obj, candidate),
                 "joint-chain-invalid assignment rejected by full replay")
            row.update({"classification": "joint_chain_invalid",
                        "price_interval": None, "profile_sha256": None,
                        "full_map_replay": "rejected_by_frame_nesting"})
        else:
            lo, hi = interval
            price = [str(lo), str(hi)]
            try:
                profile = wlib.paid(candidate, frame_obj)
            except AssertionError as exc:
                raise ValueError("scored triple assignment failed full 661-register replay") from exc
            direct_interval = profile_price_interval(ns, baseline, profile)
            need(lo <= direct_interval[0] <= direct_interval[1] <= hi,
                 "full-chain score encloses independently aggregated profile price")
            phash = profile_sha(profile)
            profile_classes[phash] = profile_payload(profile)
            equal = profile == baseline
            if equal:
                need(lo <= 0 <= hi, "profile-preserving move has zero in its exact price enclosure")
                need(direct_interval == (0, 0), "equal profiles have exactly zero direct price delta")
                counts["profile_tie"] += 1
                zero_price.append(price)
                classification = "profile_tie"
            elif hi < 0:
                counts["strict_improvement"] += 1
                classification = "strict_improvement"
            elif lo > 0:
                counts["strict_loss"] += 1
                loss_price.append(price)
                classification = "strict_loss"
            else:
                counts["unresolved"] += 1
                classification = "unresolved"
            row.update({"classification": classification,
                        "price_interval": price, "profile_sha256": phash,
                        "full_map_replay": "passed_661_registers"})
        assignment_rows.append(row)

    need(counts == {"joint_chain_invalid": 46, "profile_tie": 100,
                    "strict_loss": 64, "strict_improvement": 0, "unresolved": 0},
         "complete 210-assignment outcome census")
    need(len(profile_classes) == 2, "only baseline and one changed profile")
    need(len(set(tuple(x) for x in zero_price)) == 1 and
         len(set(tuple(x) for x in loss_price)) == 1,
         "uniform exact tie and loss enclosures")
    changed_profiles = [v for key, v in profile_classes.items()
                        if key != profile_sha(baseline)]
    need(changed_profiles == [{"1": 1326, "2": 1342, "3": 78, "4": 44,
                               "5": 102, "6": 11, "7": 19}],
         "single exact changed profile")
    need(FractionTextPositive(loss_price[0][0]), "all profile-changing moves strictly worsen price")

    # Positive identity and two semantic/coverage failure controls.
    home_word = make_word(word, ops, home_choice, frame_sets, wlib)
    need(wlib.paid(home_word, frame_obj) == baseline,
         "all-home schedule identity control")
    wrong_source = copy.deepcopy(home_word)
    wrong_source["A"][triple[0]][2][0] += 1
    wrong_source["C"] = wlib.rebuild_C(wrong_source)
    need(reject_replay(wlib, frame_obj, wrong_source), "wrong source operand rejected")
    missing_add = copy.deepcopy(home_word)
    missing_add["A"].pop(triple[0])
    missing_add["C"] = wlib.rebuild_C(missing_add)
    need(reject_replay(wlib, frame_obj, missing_add), "omitted A ADD rejected")

    return {
        "status": "PASS_PR589_A_TRIPLE_TRANSPORT_CENSUS",
        "base_commit": BASE,
        "assignment_seed": SEED,
        "track": "bit supplier",
        "selected_kappa_unchanged": SELECTED_KAPPA,
        "bit_saving_c": BIT_C,
        "predecessors": {k: v["head"] for k, v in sources["predecessors"].items()
                          if "head" in v},
        "word_sha256": expected["word"]["file_sha256"],
        "search_domain": {
            "section": "A",
            "giant_component_gate_count": len(giant_component_indices(opts, ops)),
            "eligible_frame_sensitive_triples": len(ordered),
            "ordering": "(individual option product, operation index triple)",
            "seed_index": seed_index,
            "selected_operations": [list(ops[i]) for i in triple],
            "shared_register": 325,
            "individual_option_domains": [[[q, frame] for q, frame in opts[i]] for i in triple],
            "joint_assignments": joint_count,
            "option_source": "fixed PR1345 individually legal single-move option lists on unchanged PR589 word",
            "joint_construction": "Cartesian product of frozen option lists, then deterministic reinsertion by (slot - 0.5, original_index) and full-chain replay",
            "complete_fixed_option_product_coverage": True,
            "all_jointly_enabled_frame_options_covered": False,
            "all_alternative_commutation_schedules_covered": False
        },
        "summary": counts,
        "baseline_paid_profile": profile_payload(baseline),
        "changed_paid_profile": changed_profiles[0],
        "profile_class_sha256": profile_classes,
        "profile_preserving_price_interval": zero_price[0],
        "profile_worsening_price_interval": loss_price[0],
        "assignment_results": assignment_rows,
        "controls": {
            "all_home_identity": "passed",
            "mutated_source_operand": "rejected",
            "omitted_A_ADD": "rejected"
        },
        "scope": "Exact negative result only for the 210-tuple Cartesian product of fixed individually legal single-move options for one A-section triple on a pinned PR589 word and a deterministic reinsertion order; no exclusion of jointly enabled frame/commutation options, other triples, other move classes, or a better bit supplier."
    }


def giant_component_indices(opts, ops):
    movable = [i for i in range(len(ops)) if len(opts[i]) > 1]
    by_reg = {}
    for i in movable:
        for register in (ops[i][1], ops[i][2]):
            by_reg.setdefault(register, set()).add(i)
    parent = {i: i for i in movable}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for operation_set in by_reg.values():
        for i, j in itertools.combinations(sorted(operation_set), 2):
            a, b = find(i), find(j)
            if a != b:
                parent[a] = b
    components = {}
    for i in movable:
        components.setdefault(find(i), []).append(i)
    giant = []
    for operation_set in components.values():
        if math.prod(len(opts[i]) for i in operation_set) > 200_000:
            giant.extend(operation_set)
    return sorted(set(giant))


def FractionTextPositive(text):
    from fractions import Fraction
    return Fraction(text) > 0


def main():
    write = len(sys.argv) == 2 and sys.argv[1] == "--write"
    need(len(sys.argv) == 1 or write, "usage: verify.py [--write]")
    result = verify()
    if write:
        need(not RESULT.exists(), "refusing to overwrite RESULT.json")
        RESULT.write_text(json.dumps(result, indent=2) + "\n")
        print("WROTE_RESULT " + str(RESULT.relative_to(ROOT)))
        return
    expected = json.loads(RESULT.read_bytes())
    need(canonical(result) == canonical(expected), "stored result differs from complete replay")
    print("PASS_PR589_A_TRIPLE_TRANSPORT seed=5 ops=927,928,930 assignments=210 valid=164 ties=100 losses=64 incompatible=46 controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
