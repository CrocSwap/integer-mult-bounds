"""Exact source-walk construction for five-source parity hyperplanes."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR_CERT = "research/universal-connector-boundary/CERTIFICATE.json"
PREDECESSOR_README = "research/universal-connector-boundary/README.md"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"


def weight(x):
    return x.bit_count()


def output_masks(normal, rhs):
    return [m for m in range(1, 32) if (weight(normal & m) & 1) == rhs]


def canonical_ten_words():
    """One restricted-growth word for every pairing of ten source positions."""
    def extend(prefix, counts, largest):
        if len(prefix) == 10:
            if counts == (2, 2, 2, 2, 2):
                yield prefix
            return
        highest = min(4, largest + 1)
        for label in range(highest + 1):
            if counts[label] == 2:
                continue
            updated = list(counts)
            updated[label] += 1
            yield from extend(prefix + (label,), tuple(updated), max(largest, label))

    yield from extend((), (0, 0, 0, 0, 0), -1)


def prefixes(word):
    state = 0
    result = [state]
    for label in word:
        state ^= 1 << label
        result.append(state)
    return result


def differences(word):
    q = prefixes(word)
    return {q[i] ^ q[j] for i in range(len(q)) for j in range(i, len(q))}


def first_boundary_pair(word, mask):
    q = prefixes(word)
    for left in range(len(q)):
        for right in range(left + 1, len(q)):
            if q[left] ^ q[right] == mask:
                return [left, right]
    raise ValueError(f"mask {mask} is not a boundary difference")


def active_sources(masks):
    return [j for j in range(5) if any((m >> j) & 1 for m in masks)]


def canonical_to_normal_permutation(normal):
    support = [j for j in range(5) if (normal >> j) & 1]
    complement = [j for j in range(5) if not ((normal >> j) & 1)]
    return support + complement


def permute_mask(mask, permutation):
    result = 0
    for old, new in enumerate(permutation):
        if (mask >> old) & 1:
            result |= 1 << new
    return result


def ten_word_templates(words):
    templates = {}
    coverage_counts = {}
    for k in range(1, 6):
        normal = (1 << k) - 1
        for rhs in (0, 1):
            masks = output_masks(normal, rhs)
            covering = [word for word in words if set(masks) <= differences(word)]
            coverage_counts[(k, rhs)] = len(covering)
            templates[(k, rhs)] = covering[0] if covering else None
    return templates, coverage_counts


def scalar_dirty_replay(plan):
    """Exhaust the unit-width F2 model for all sources, z0 and one dirty target."""
    word = plan["source_word"]
    pairs = {int(m): pair for m, pair in plan["readout_pairs"].items()}
    checked = 0
    for mask in plan["output_masks"]:
        for source_value in range(32):
            for z0 in (0, 1):
                for a_map in (0, 1):
                    for y0 in (0, 1):
                        z, y = z0, y0
                        left, right = pairs[mask]
                        for boundary in range(len(word) + 1):
                            if boundary == left or boundary == right:
                                y ^= a_map & z
                            if boundary < len(word):
                                j = word[boundary]
                                z ^= (source_value >> j) & 1
                        expected = y0 ^ (a_map & (weight(mask & source_value) & 1))
                        assert z == z0 and y == expected
                        checked += 1
    return checked


def build_certificate():
    selected = (ROOT / "certificates/selected-result.json").read_bytes()
    assert hashlib.sha256(selected).hexdigest() == SELECTED_SHA256
    predecessor = json.loads((ROOT / PREDECESSOR_CERT).read_text())
    ten_predecessor = predecessor["schedules"]["five_extra_output"]["source_word"]
    twelve_predecessor = predecessor["schedules"]["five_extra_source"]["source_word"]
    assert ten_predecessor == [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]
    assert len(twelve_predecessor) == 12 and set(differences(twelve_predecessor)) == set(range(32))

    words = list(canonical_ten_words())
    assert len(words) == 945
    assert all(Counter(word) == Counter({0: 2, 1: 2, 2: 2, 3: 2, 4: 2}) for word in words)
    word_digest = hashlib.sha256(
        json.dumps(words, separators=(",", ":")).encode()
    ).hexdigest()
    word_set_digest = hashlib.sha256(
        json.dumps(sorted(words), separators=(",", ":")).encode()
    ).hexdigest()
    difference_histogram = dict(sorted(Counter(len(differences(w)) for w in words).items()))
    expected_histogram = {16: 42, 19: 120, 21: 180, 22: 56, 23: 45,
                          24: 220, 26: 110, 28: 150, 31: 22}
    assert difference_histogram == expected_histogram
    templates, coverage_counts = ten_word_templates(words)
    assert all(coverage_counts[(k, rhs)] > 0
               for k in range(1, 6) for rhs in (0, 1)
               if not (k == 5 and rhs == 1))
    assert coverage_counts[(5, 1)] == 0

    odd_masks = set(output_masks(31, 1))
    odd_coverages = [len(differences(w) & odd_masks) for w in words]
    assert max(odd_coverages) == 15
    best_odd_word = words[odd_coverages.index(max(odd_coverages))]
    assert len(differences(best_odd_word) & odd_masks) == 15

    class_records = []
    for k in range(1, 6):
        normal = (1 << k) - 1
        for rhs in (0, 1):
            masks = output_masks(normal, rhs)
            if rhs == 0 and k == 1:
                template = [1, 2, 1, 2, 3, 4, 3, 4]
                construction = "four_source_universal_word"
            elif k == 5 and rhs == 1:
                template = twelve_predecessor
                construction = "twelve_toggle_universal_repair"
            else:
                template = list(templates[(k, rhs)])
                construction = "ten_toggle_boundary_cover"
            assert set(masks) <= differences(template)
            src = active_sources(masks)
            lower = 2 * len(src) + 2 * len(masks)
            root_queries = len(template) + 2 * len(masks)
            assert root_queries == lower or (k == 5 and rhs == 1 and root_queries == lower + 2)
            readouts = {str(m): first_boundary_pair(template, m) for m in masks}
            class_records.append({
                "normal_weight": k,
                "canonical_normal": normal,
                "rhs": rhs,
                "family_size": len(masks),
                "output_masks": masks,
                "active_sources": src,
                "source_word": template,
                "prefixes": prefixes(template),
                "difference_set": sorted(differences(template)),
                "readout_pairs": readouts,
                "source_calls": len(template),
                "output_calls": 2 * len(masks),
                "query_count": root_queries,
                "counting_lower_bound": lower,
                "ten_toggle_covering_canonical_words": coverage_counts[(k, rhs)],
                "construction": construction,
            })

    plans = []
    scalar_checks = 0
    for normal in range(1, 32):
        k = weight(normal)
        permutation = canonical_to_normal_permutation(normal)
        for rhs in (0, 1):
            canonical = next(x for x in class_records
                             if x["normal_weight"] == k and x["rhs"] == rhs)
            word = [permutation[j] for j in canonical["source_word"]]
            masks = output_masks(normal, rhs)
            assert set(masks) <= differences(word)
            readouts = {str(m): first_boundary_pair(word, m) for m in masks}
            plan = {
                "normal": normal,
                "normal_bits": f"{normal:05b}",
                "rhs": rhs,
                "output_masks": masks,
                "active_sources": active_sources(masks),
                "source_word": word,
                "readout_pairs": readouts,
                "query_count": len(word) + 2 * len(masks),
                "symmetry_class": {"normal_weight": k, "canonical_normal": (1 << k) - 1},
            }
            scalar_checks += scalar_dirty_replay(plan)
            plans.append(plan)

    # Mutation controls: a single omitted source occurrence leaves connector dirt;
    # and no ten-toggle word covers the all-odd output family.
    dirty_mutant = list(ten_predecessor)
    dirty_mutant.append(0)
    mutant_source_counts = Counter(dirty_mutant)
    mutant_connector_change = 0
    for label in dirty_mutant:
        if label == 0:
            mutant_connector_change ^= 1
    assert mutant_source_counts[0] == 3 and mutant_connector_change == 1
    assert max(odd_coverages) < len(odd_masks)

    class_summary = []
    for record in class_records:
        class_summary.append({
            key: record[key] for key in (
                "normal_weight", "canonical_normal", "rhs", "family_size",
                "active_sources", "source_calls", "output_calls", "query_count",
                "counting_lower_bound", "ten_toggle_covering_canonical_words",
                "construction",
            )
        })

    return {
        "schema_version": 1,
        "result": "EXACT_FIVE_SOURCE_AFFINE_HYPERPLANE_QUERY_MINIMA",
        "sources": {
            "selected_record_sha256": SELECTED_SHA256,
            "predecessor_certificate_path": PREDECESSOR_CERT,
            "predecessor_ten_source_word": ten_predecessor,
            "predecessor_twelve_source_word": twelve_predecessor,
        },
        "model": {
            "field": "F2",
            "source_count": 5,
            "outputs": "one independent target for each mask in S(n,b)",
            "family": "S(n,b)={m in F2^5: m!=0 and dot(n,m)=b}, n!=0, b in {0,1}",
            "dirty_state": "all sources, connector and targets arbitrary; source rows read-only; connector restored",
            "allowed_calls": ["B_j: z += B_j x_j", "A_m: y_m += A_m z"],
            "cost": "one complete unit-cost call per B_j or A_m query; no extra operations, frames, helpers or copies",
        },
        "ten_toggle_census": {
            "canonical_pairings_checked": 945,
            "canonical_words_sha256": word_digest,
            "canonical_word_set_sha256": word_set_digest,
            "difference_set_size_histogram": {str(k): v for k, v in difference_histogram.items()},
            "covering_words_by_symmetry_class": [
                {"normal_weight": k, "rhs": rhs, "count": coverage_counts[(k, rhs)]}
                for k in range(1, 6) for rhs in (0, 1)
            ],
            "all_odd_output_masks": sorted(odd_masks),
            "maximum_odd_masks_covered_by_any_ten_toggle_word": max(odd_coverages),
            "one_best_odd_word": list(best_odd_word),
        },
        "symmetry_class_constructions": class_summary,
        "all_62_hyperplanes": plans,
        "query_minima": {
            "rhs0_normal_weight1": 38,
            "rhs0_normal_weight2_to5": 40,
            "rhs1_normal_weight1_to4": 42,
            "rhs1_normal_weight5": 44,
            "reason": "two calls per active source and output; the all-odd family additionally has no ten-toggle covering word",
        },
        "verification": {
            "all_62_family_schedules_scalar_dirty_states_checked": scalar_checks,
            "dirty_connector_restored_for_every_schedule": True,
            "every_target_has_two_readouts": True,
            "negative_controls": {
                "extra_unpaired_source_toggle_detected": True,
                "ten_toggle_all_odd_family_claim_rejected": True,
            },
        },
        "limits": {
            "no_selected_supplier_instantiation": True,
            "no_new_kappa": True,
            "no_claim_beyond_affine_hyperplane_output_families": True,
        },
    }


if __name__ == "__main__":
    print(json.dumps(build_certificate(), indent=2, sort_keys=True))
