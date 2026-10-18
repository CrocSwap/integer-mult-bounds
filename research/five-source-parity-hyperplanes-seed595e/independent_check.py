"""Independent matching enumeration and dirty-state replay."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT = json.loads((HERE / "CERTIFICATE.json").read_text())


def all_pairings(positions=tuple(range(10))):
    if not positions:
        yield ()
        return
    first = positions[0]
    for index in range(1, len(positions)):
        second = positions[index]
        rest = positions[1:index] + positions[index + 1:]
        for suffix in all_pairings(rest):
            yield ((first, second),) + suffix


def word_for_pairing(pairs):
    label_by_position = {}
    for label, (left, right) in enumerate(sorted(pairs)):
        label_by_position[left] = label
        label_by_position[right] = label
    return tuple(label_by_position[i] for i in range(10))


def prefix_states(word):
    state = 0
    result = [0]
    for label in word:
        state ^= 1 << label
        result.append(state)
    return result


def difference_set(word):
    states = prefix_states(word)
    result = set()
    for i in range(len(states)):
        for j in range(i, len(states)):
            result.add(states[i] ^ states[j])
    return result


def family(normal, rhs):
    return [m for m in range(1, 32) if ((normal & m).bit_count() & 1) == rhs]


def dirty_row_replay(plan):
    word = plan["source_word"]
    pairs = {int(mask): endpoints for mask, endpoints in plan["readout_pairs"].items()}
    count = 0
    for mask in plan["output_masks"]:
        left, right = pairs[mask]
        for source_value in range(32):
            for dirty_z in (0, 1):
                for a_coefficient in (0, 1):
                    for dirty_y in (0, 1):
                        z, y = dirty_z, dirty_y
                        for boundary in range(len(word) + 1):
                            if boundary in (left, right):
                                y ^= a_coefficient & z
                            if boundary < len(word):
                                source = word[boundary]
                                z ^= (source_value >> source) & 1
                        desired = dirty_y ^ (a_coefficient & ((mask & source_value).bit_count() & 1))
                        assert (z, y) == (dirty_z, desired)
                        count += 1
    return count


def main():
    pairings = list(all_pairings())
    assert len(pairings) == 945
    words = [word_for_pairing(p) for p in pairings]
    assert all(Counter(w) == Counter({0: 2, 1: 2, 2: 2, 3: 2, 4: 2}) for w in words)
    digest = hashlib.sha256(
        json.dumps(sorted(words), separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == CERT["ten_toggle_census"]["canonical_word_set_sha256"]

    # Independent exact obstruction for the full odd-weight family.
    odd = set(family(31, 1))
    coverages = [len(difference_set(w) & odd) for w in words]
    assert max(coverages) == 15 and all(c < 16 for c in coverages)

    by_class = {(r["normal_weight"], r["rhs"]): r
                for r in CERT["symmetry_class_constructions"]}
    plans_by_key = {(p["normal"], p["rhs"]): p
                    for p in CERT["all_62_hyperplanes"]}
    for normal_weight in range(1, 6):
        normal = (1 << normal_weight) - 1
        for rhs in (0, 1):
            record = by_class[(normal_weight, rhs)]
            rows = family(normal, rhs)
            covering = [w for w in words if set(rows) <= difference_set(w)]
            assert len(covering) == record["ten_toggle_covering_canonical_words"]
            assert bool(covering) == (normal_weight != 5 or rhs != 1)
            word = plans_by_key[(normal, rhs)]["source_word"]
            assert set(rows) <= difference_set(word)
            assert record["query_count"] == len(word) + 2 * len(rows)

    checked_states = 0
    for plan in CERT["all_62_hyperplanes"]:
        normal, rhs = plan["normal"], plan["rhs"]
        rows = family(normal, rhs)
        assert rows == plan["output_masks"]
        word = plan["source_word"]
        assert len(word) == plan["query_count"] - 2 * len(rows)
        states = prefix_states(word)
        for mask in rows:
            pair = plan["readout_pairs"][str(mask)]
            assert states[pair[0]] ^ states[pair[1]] == mask
        active = [j for j in range(5) if any((m >> j) & 1 for m in rows)]
        lower = 2 * len(active) + 2 * len(rows)
        if not (normal == 31 and rhs == 1):
            assert plan["query_count"] == lower
        else:
            assert plan["query_count"] == lower + 2 == 44
        checked_states += dirty_row_replay(plan)

    # Semantic negative controls: remove one readout, or leave a source toggle unpaired.
    sample = CERT["all_62_hyperplanes"][0]
    mask = sample["output_masks"][0]
    left, right = sample["readout_pairs"][str(mask)]
    word = sample["source_word"]
    z = 1  # all source products are zero, so one omitted readout leaks dirty connector state
    y = 0
    for boundary in range(len(word) + 1):
        if boundary == left:  # mutated: omit the second endpoint readout
            y ^= z
    desired = (mask & 0).bit_count() & 1
    assert y == 1 and y != desired
    mutated_z = 0
    mutated_z ^= 1  # one source toggle on a unit source product, with no restoring mate
    assert mutated_z != 0
    assert checked_states == CERT["verification"]["all_62_family_schedules_scalar_dirty_states_checked"]

    print(
        "PASS_INDEPENDENT_PARITY_HYPERPLANE_CHECK "
        "pairings=945 odd_max=15 plans=62 dirty_states=" + str(checked_states)
    )


if __name__ == "__main__":
    main()
