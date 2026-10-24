#!/usr/bin/env python3
"""Exact rooted classification; standard library, read-only, no Git required.

Prepared for Krzysztof Wójt with substantial OpenAI Codex assistance.
Apache-2.0. The mathematical coverage argument is in PROOF.md.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
EXPECTED = ((1296, 2176, 496, 0), (1296, 1728, 816, 16),
            (324, 324, 112, 0), (81, 81, 4, 0))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encode(rows):
    require(len(rows) == 15, "exactly fifteen rows required")
    result = []
    for row in rows:
        require(isinstance(row, (list, tuple)) and len(row) == 3,
                "each row needs three distinct neighbors")
        require(all(type(d) is int and 0 <= d < 15 for d in row),
                "neighbor outside the fifteen-vertex part")
        require(len(set(row)) == 3, "duplicate edge")
        result.append(sum(1 << d for d in row))
    require(all(sum((row >> d) & 1 for row in result) == 3 for d in range(15)),
            "column degree differs from three")
    return tuple(result)


def six_cycles(rows):
    """All (B triple, D triple) cycles, or None if a C4 exists.

    In a C4-free graph each pair of B vertices has at most one common D
    neighbor. A triple forms a C6 exactly when its three common neighbors
    exist and are distinct. A single shared D neighbor is a claw, not C6.
    """
    common = {}
    for a, b in combinations(range(15), 2):
        mask = rows[a] & rows[b]
        if mask.bit_count() > 1:
            return None
        if mask:
            common[a, b] = mask.bit_length() - 1
    cycles = []
    for a, b, c in combinations(range(15), 3):
        ds = (common.get((a, b)), common.get((a, c)), common.get((b, c)))
        if None not in ds and len(set(ds)) == 3:
            cycles.append(((a, b, c), tuple(sorted(ds))))
    return tuple(cycles)


def cycle_cap(cycles):
    memberships = Counter((side, v) for cycle in cycles
                          for side, vertices in enumerate(cycle) for v in vertices)
    return all(count <= 1 for count in memberships.values())


def attachment_options(size):
    """Neighbor sets in the three free vertices for an ordered inner pair."""
    if size == 2:
        return tuple(((a,), (b,)) for a, b in permutations(range(3), 2))
    require(size == 1, "diagonal matching must have size one or two")
    return tuple(((a,), tuple(b for b in range(3) if b != a)) for a in range(3))


def fixed_rows(sizes):
    rows = [0] * 15
    for i, size in enumerate(sizes):
        rows[i] = sum(1 << j for j in range(3) if i != j) | (1 << (3 + i))
        rows[3 + i] = (1 << i) | (3 << (6 + 2 * i))
        for k in range(2):
            rows[6 + 2 * i + k] = 1 << (3 + i)
        for k in range(size):
            rows[6 + 2 * i + k] |= 1 << (6 + 2 * i + k)
    return rows


def free_blocks():
    """Every 3x3 Boolean matrix, indexed by its row and column sums."""
    result = defaultdict(list)
    for mask in range(1 << 9):
        rows = tuple((mask >> (3 * i)) & 7 for i in range(3))
        key = (tuple(row.bit_count() for row in rows),
               tuple(sum((row >> j) & 1 for row in rows) for j in range(3)))
        result[key].append(rows)
    require(sum(map(len, result.values())) == 512, "incomplete free-block family")
    return result


def complete_rows(sizes, b_options, d_options, blocks):
    rows = fixed_rows(sizes)
    for i in range(3):
        for k in range(2):
            for j in b_options[i][k]:
                rows[6 + 2 * i + k] |= 1 << (12 + j)
            for j in d_options[i][k]:
                rows[12 + j] |= 1 << (6 + 2 * i + k)
    margins = (tuple(3 - rows[12 + j].bit_count() for j in range(3)),
               tuple(3 - sum((r >> (12 + j)) & 1 for r in rows) for j in range(3)))
    for block in blocks.get(margins, ()):
        full = rows[:]
        for j in range(3):
            full[12 + j] |= block[j] << 12
        require(all(row.bit_count() == 3 for row in full), "row completion failed")
        require(all(sum((r >> d) & 1 for r in full) == 3 for d in range(15)),
                "column completion failed")
        yield tuple(full)


def enumerate_rooted():
    blocks = free_blocks()
    report, winners = [], []
    for singles in range(4):
        sizes = (1,) * singles + (2,) * (3 - singles)
        choices = [attachment_options(size) for size in sizes]
        # Independent permutations of the three free vertices on each side
        # put the first pair's attachment into the first displayed option.
        choices[0] = choices[0][:1]
        counts = Counter()
        for b_options in product(*choices):
            for d_options in product(*choices):
                counts["attachment_patterns"] += 1
                for rows in complete_rows(sizes, b_options, d_options, blocks):
                    counts["cubic_completions"] += 1
                    cycles = six_cycles(rows)
                    if cycles is None:
                        continue
                    counts["c4_free"] += 1
                    if cycle_cap(cycles):
                        winners.append(rows)
                        counts["admitted"] += 1
                        require(len(cycles) == 4, "unexpected admissible cycle count")
        actual = tuple(counts[key] for key in
                       ("attachment_patterns", "cubic_completions", "c4_free", "admitted"))
        require(actual == EXPECTED[singles], f"rooted enumeration drift: {sizes}: {actual}")
        report.append({"matching_sizes": sizes, **dict(zip(
            ("attachment_patterns", "cubic_completions", "c4_free", "admitted"), actual))})
    require([row["matching_sizes"] for row in report] ==
            [(2, 2, 2), (1, 2, 2), (1, 1, 2), (1, 1, 1)],
            "a matching-size pattern was omitted")
    require(len(winners) == len(set(winners)) == 16, "winner count or duplicate drift")
    return report, tuple(winners)


def relabel(rows, b_map, d_map):
    require(sorted(b_map) == sorted(d_map) == list(range(15)), "invalid relabeling")
    out = [0] * 15
    for b, row in enumerate(rows):
        out[b_map[b]] = sum(1 << d_map[d] for d in range(15) if (row >> d) & 1)
    return tuple(out)


def witness_orbit(rows):
    """Sixteen explicit isomorphisms; no graph-isomorphism oracle is used."""
    orbit = set()
    for flags in product((0, 1), repeat=4):
        b_map, d_map = list(range(15)), list(range(15))
        if flags[0]:
            b_map[13], b_map[14] = b_map[14], b_map[13]
        if flags[1]:
            d_map[13], d_map[14] = d_map[14], d_map[13]
        for flag, start in zip(flags[2:], (8, 10)):
            if flag:
                b_map[start], b_map[start + 1] = b_map[start + 1], b_map[start]
                d_map[start], d_map[start + 1] = d_map[start + 1], d_map[start]
        orbit.add(relabel(rows, b_map, d_map))
    return orbit


def rejects(action):
    try:
        action()
    except ValueError:
        return True
    return False


def controls(witness, cycles, winners):
    decoded = [[d for d in range(15) if (r >> d) & 1] for r in witness]
    require(rejects(lambda: encode(decoded[:-1])), "missing-row control survived")
    bad = [row[:] for row in decoded]
    bad[0] = [1, 1, 3]
    require(rejects(lambda: encode(bad)), "duplicate-edge control survived")
    bad[0] = [1, 2, 15]
    require(rejects(lambda: encode(bad)), "out-of-range control survived")
    bad[0] = [1, 2, True]
    require(rejects(lambda: encode(bad)), "Boolean-label control survived")
    bad[0] = [1, 2, 4]
    require(rejects(lambda: encode(bad)), "column-degree control survived")
    require(not cycle_cap(cycles + cycles[:1]), "repeated-cycle control survived")
    require(set(winners[:-1]) != witness_orbit(witness), "omitted-winner control survived")
    bad_masks = list(witness)
    bad_masks[1] = bad_masks[0]
    require(six_cycles(bad_masks) is None, "C4 control survived")
    require(all(bs != (0, 6, 7) for bs, _ in cycles), "claw counted as a cycle")
    return 9


def main():
    fixture = json.loads((PACKAGE / "WITNESS.json").read_text(encoding="utf-8"))
    witness = encode(fixture["rows"])
    cycles = six_cycles(witness)
    require(cycles is not None and cycle_cap(cycles), "witness violates the graph hypotheses")
    expected_cycles = tuple((tuple(x["B"]), tuple(x["D"])) for x in fixture["six_cycles"])
    require(cycles == expected_cycles and len(cycles) == 4, "witness cycle list differs")
    report, winners = enumerate_rooted()
    require(witness_orbit(witness) == set(winners), "the explicit isomorphisms miss a winner")
    control_count = controls(witness, cycles, winners)
    encoded = json.dumps(sorted(winners), separators=(",", ":")).encode("ascii")
    print(json.dumps({
        "status": "PASS_CENTRE_EQUALITY_SIX_CYCLES",
        "classification": "Every admissible graph containing a C6 is isomorphic to WITNESS.json",
        "proof_boundary": "Written rooted-normal-form coverage plus exact finite enumeration",
        "normalized_counts": report,
        "normalized_winner_sha256": sha256(encoded).hexdigest(),
        "explicit_isomorphism_images": len(witness_orbit(witness)),
        "witness_six_cycles": fixture["six_cycles"],
        "controls": control_count,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
