"""Review the full pure-reset family from the pinned scalar word."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
CENTRES = [92, 57, 81, 224, 11, 240, 9, 256]
GROUPS = [15, 48, 192]
CUT = 12995
PINS = {
    "core": (LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz", "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205", True),
    "payload": (LANES / "temporal-reuse/EXACT-TAGGED-RESETS.json.gz", "d0ebeeca3e9e610023d0f155ad4b0989181c547ca1601558993abd8b97303612", True),
    "summary": (LANES / "temporal-reuse/EXACT-TAGGED-RESETS.json", "b54d45d9e8775d56d59511dfe83b7782461c35666988fc2e03f0dcff81762dee", False),
    "producer": (LANES / "temporal-reuse/check_exact_tagged_resets.py", "69610baa2fdbd88dbf39d821fe9d3cd08dab99f2eac4c99dbbc286a0c6cb97f5", False),
    "proof": (LANES / "temporal-reuse/EXACT-TAGGED-RESETS.md", "3a5f2bd40804d6106192f75c3abe7aefdf4d98c829cec03979bd79e8adb3d3b4", False),
    "physical_review": (HERE.parent / "centre-reset-review/REVIEW-V2.json", "b2086bd9bb0e62c6fb8120f011c0ec307f20d7e084db6b5074c9bf75bb3cd7cc", False),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def scalar(event):
    gate = event[1]
    return gate[0], gate[1][1], gate[2][1] if gate[0] == "add" else None, Q(*gate[-2:])


def add(target, source, factor):
    for key, value in source.items():
        result = target.get(key, 0) + factor*value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def main(args):
    data = {}
    for label, (path, pin, compressed) in PINS.items():
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if compressed else raw
        need(sha256(payload).hexdigest() == pin, "Source pin: "+label)
        if path.suffix in (".json", ".gz"):
            data[label] = json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)
    events = data["core"]["backward"][:CUT]
    reference = data["payload"]
    rows = [{j: Q(1)} for j in range(704)]
    pure, inputs = {}, {}
    operations = []
    first_native = next(i for i, event in enumerate(events) if event[0] == "climb")
    for index, event in enumerate(events):
        target = None
        if event[0] == "scalar":
            kind, target, source, factor = scalar(event)
            need(factor != 0, "Every retained scalar is nonzero")
            if kind == "add":
                add(rows[target], rows[source], factor)
            else:
                rows[target] = {j: factor*value for j, value in rows[target].items()}
            operations.append((index, kind, target, source, factor))
        elif event[0] == "climb":
            target = event[2]
            inputs[index] = rows[target].copy()
            operations.append((index, "native", target, None, event[5]))
        if target is not None:
            has_data = any(j < 224 for j in rows[target])
            has_helper = any(j >= 224 for j in rows[target])
            need(has_data or has_helper, "There is no zero ideal target row")
            if not (has_data and has_helper):
                pure[index] = (target, "data" if has_data else "helper")
    need(first_native == 9742 and max(i for i, (_, kind) in pure.items() if kind == "data") == 637, "All pure-data resets precede native errors")
    need(len(pure) == 860, "Complete eligible reset count")
    post_native = {i: value for i, value in pure.items() if i >= first_native}
    need(len(post_native) == 216 and all(kind == "helper" for _, kind in post_native.values()), "All later eligible resets are pure helper resets")

    supports = [1 << CENTRES.index(j) if j in CENTRES else 0 for j in range(704)]
    reset_support, native_support = {}, {}
    group_programs = {group: [] for group in GROUPS}
    for operation in reversed(operations):
        index, kind, target, source, factor = operation
        mask = supports[target]
        if index in post_native:
            reset_support[index] = mask
        if kind == "native" and mask:
            native_support[index] = mask
            need(any(j < 224 for j in inputs[index]) and any(j >= 224 for j in inputs[index]), "Every Boolean native ancestor is mixed")
        if index >= first_native:
            for group in GROUPS:
                if mask & group:
                    group_programs[group].append(operation)
        if kind == "add":
            supports[source] |= mask
    need(reset_support == {int(i): mask for i, mask in reference["reset_boolean_support"].items()}, "All reset Boolean supports")
    need(native_support == {int(i): mask for i, mask in reference["native_boolean_support"].items()}, "All native Boolean supports")
    for mask in list(reset_support.values()) + list(native_support.values()):
        need(sum(bool(mask & group) for group in GROUPS) <= 1, "No reset or native output error crosses groups")
    ignored = sorted(i for i, mask in reset_support.items() if not mask)
    need(len(ignored) == 180 and ignored == reference["irrelevant_post_native_reset_events"], "All irrelevant reset sites")
    need(len(native_support) == 176, "All Boolean native ancestors")
    sites = {group: sorted(i for i, mask in reset_support.items() if mask & group) for group in GROUPS}
    need([len(sites[group]) for group in GROUPS] == [12, 12, 12], "Independent twelve-site groups")

    # Each query uses an independent scalar rational response calculation.
    def responses(program, policy, modes):
        combined = {}
        for mode in modes:
            vector = [Q(0)]*704
            vector[CENTRES[mode]] = Q(1)
            for index, kind, target, source, factor in program:
                if index in policy:
                    vector[target] = Q(0)
                if kind == "native":
                    combined.setdefault(index, {})[mode] = vector[target]
                elif kind == "add":
                    vector[source] += factor*vector[target]
                else:
                    vector[target] *= factor
        return combined

    all_minima = {}
    group_reports = {}
    all_case_digest = sha256()
    for group in GROUPS:
        program = group_programs[group]
        published = reference["groups"][str(group)]
        modes = [mode for mode in range(8) if group & (1 << mode)]
        need(published["modes"] == modes and published["reset_events"] == sites[group], "Exact group sources")
        converted = [["native", i, t, f] if kind == "native" else [kind, i, t, s, f.numerator, f.denominator] for i, kind, t, s, f in program]
        need(converted == published["plan"], "Independent Boolean-filtered native program")
        submasks = [mask for mask in range(1, 256) if not mask & ~group]
        best = {mask: None for mask in submasks}
        for policy_mask in range(4096):
            policy = {event for k, event in enumerate(sites[group]) if policy_mask & (1 << k)}
            columns = responses(program, policy, modes)
            histogram = Counter()
            for index, values in columns.items():
                support = sum(1 << mode for mode, value in values.items() if value)
                if support:
                    histogram[(events[index][5], support)] += 1
            packed = [[rank, mask, count] for (rank, mask), count in sorted(histogram.items())]
            need(packed == published["cases"][policy_mask], "Every exact rational local policy profile")
            all_case_digest.update(json.dumps([group, policy_mask, packed], separators=(",", ":")).encode())
            need(all(rank in (1, 4) for rank, _ in histogram), "Only ranks one and four occur")
            for mask in submasks:
                one = sum(count for (rank, support), count in histogram.items() if rank == 1 and support & mask)
                four = sum(count for (rank, support), count in histogram.items() if rank == 4 and support & mask)
                need(four == mask.bit_count(), "Rank-four count is fixed in every policy")
                candidate = (one, len(policy), policy_mask)
                if best[mask] is None or candidate < best[mask]:
                    best[mask] = candidate
        for mask, (one, _, policy_mask) in best.items():
            expected = {"rank_one": one, "rank_four": mask.bit_count(), "reset_mask": policy_mask}
            need(expected == published["minima"][str(mask)], "Each local optimum and policy witness")
            all_minima[mask] = (one, [event for k, event in enumerate(sites[group]) if policy_mask & (1 << k)])
        group_reports[str(group)] = {"cases": 4096, "query_subsets": len(submasks), "reset_events": sites[group], "native_ancestors": len({i for i, kind, _, _, _ in program if kind == "native"})}
        print("independent rational group", group, "passed", flush=True)

    subsets = []
    for mask in range(1, 256):
        one, policy = 0, []
        for group in GROUPS:
            part = mask & group
            if part:
                one += all_minima[part][0]
                policy += all_minima[part][1]
        size = mask.bit_count()
        expected = {"mask": mask, "mode_count": size, "rank_one": one, "rank_four": size, "mass": one+4*size,
                    "reset_events": sorted(policy), "rank_one_surplus_over_removed_mass": one-8*size}
        need(expected == reference["subsets"][mask-1], "Every global query subset optimum")
        need(one >= 8*size+13 and 4*(one+4*size) >= 65*size, "Uniform exact family inequalities")
        need(one-4*size >= 17, "Sharper moment surplus")
        subsets.append(expected)
    best_by_count = [min(item["mass"] for item in subsets if item["mode_count"] == size) for size in range(1, 9)]
    need(best_by_count == [25, 44, 60, 65, 90, 109, 134, 153], "Exact minima by query size")
    need(subsets[-1]["reset_events"] == [10008, 10012], "Best all-query policy")
    sharp_masks = [item["mask"] for item in subsets if item["rank_one"]-4*item["mode_count"] == 17]
    need(sharp_masks == [32, 128], "Sharp constant seventeen witnesses")

    pulse_reports = {}
    policies = {"none": set(), "all": set(pure), "best": set(subsets[-1]["reset_events"])}
    for name, policy in policies.items():
        reverse = {}
        for group in GROUPS:
            reverse.update(responses(group_programs[group], policy, [mode for mode in range(8) if group & (1 << mode)]))
        digest = sha256()
        zeros = 0
        for index in native_support:
            pulse = [Q(0)]*704
            pulse[events[index][2]] = Q(1)
            if index in policy:
                pulse[pure[index][0]] = Q(0)
            for later in range(index+1, CUT):
                event = events[later]
                if event[0] == "scalar":
                    kind, target, source, factor = scalar(event)
                    if kind == "add":
                        pulse[target] += factor*pulse[source]
                    else:
                        pulse[target] *= factor
                if later in policy:
                    pulse[pure[later][0]] = Q(0)
            column = [pulse[field] for field in CENTRES]
            need(column == [reverse[index].get(mode, Q(0)) for mode in range(8)], "Full raw forward impulse under each policy")
            zeros += not any(column)
            digest.update(json.dumps([index, list(map(str, column))], separators=(",", ":")).encode())
        pulse_reports[name] = {"native_impulses": len(native_support), "zero_responses": zeros, "digest": digest.hexdigest()}
    need([pulse_reports[name]["zero_responses"] for name in ("none", "all", "best")] == [44, 18, 47], "Independent impulse controls")

    result = {"status": "PASS_INDEPENDENT_ALL_PURE_RESET_POLICIES", "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_pins": {label: pin for label, (_, pin, _) in PINS.items()},
              "complete_input_columns": 704, "eligible_reset_sites": len(pure), "post_native_sites": len(post_native),
              "irrelevant_post_native_sites": len(ignored), "first_native_event": first_native, "last_pure_data_reset": 637,
              "groups": group_reports, "local_policies_checked": 12288, "global_query_subsets": 255,
              "exact_rational_case_digest": all_case_digest.hexdigest(), "best_mass_by_query_count": best_by_count,
              "all_query_profile": {"1": 121, "4": 8}, "all_query_reset_events": [10008, 10012],
              "sharp_moment_surplus": 17, "sharp_surplus_masks_at_sigma_one": sharp_masks,
              "direct_impulses": pulse_reports,
              "scope": "Every subset of individual ideal pure-target post-scalar or post-native resets before the fixed centre cut. The cost result assumes the declared independent relative-error width model. No new chronology, basis, joint reset, access edge, native error contract, supplier or kappa claim."}
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(result["status"])
    print(sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "CHECKS.json")
    main(parser.parse_args())
