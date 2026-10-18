#!/usr/bin/env python3
"""Independent search-domain oracle; never run the retained full census.

@krzysztofwojt with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import itertools
import json
import math
import os
import pathlib
import shutil
import subprocess
import tempfile
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/connector-covering-code/cycle_search.cpp"
SOURCE_SHA = "597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_bytes():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "live input changed: " + row["path"])
    data = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(data).hexdigest() == SOURCE_SHA, "unexpected census source")
    return data.decode()


def prefix_points(word):
    state, points = 0, []
    for label in word:
        points.append(state)
        state ^= 1 << label
    return points, state


def multiset_words(counts):
    """Assign position subsets, with no first-appearance or dihedral pruning."""
    word = [-1] * sum(counts)

    def assign(label, slots):
        if label == len(counts) - 1:
            for slot in slots:
                word[slot] = label
            yield tuple(word)
            return
        for chosen in itertools.combinations(slots, counts[label]):
            occupied = set(chosen)
            for slot in chosen:
                word[slot] = label
            yield from assign(label + 1, tuple(slot for slot in slots if slot not in occupied))

    yield from assign(0, tuple(range(len(word))))


def low_oracle(pattern_b):
    counts = (4, 2, 2, 2) if pattern_b else (2, 2, 2, 2)
    universal, all_words = set(), 0
    for word in multiset_words(counts):
        all_words += 1
        points, end = prefix_points(word)
        require(end == 0, "multiset restoration")
        if len({a ^ b for a in points for b in points}) == 16:
            universal.add(word)
    expected_total = math.factorial(sum(counts)) // math.prod(math.factorial(c) for c in counts)
    require(all_words == expected_total, "multiset cardinality")
    permutations = [(0,) + p for p in itertools.permutations((1, 2, 3))] if pattern_b else list(itertools.permutations(range(4)))
    unseen, representatives, orbit_sizes = set(universal), [], Counter()
    while unseen:
        seed, orbit = min(unseen), set()
        for mapping in permutations:
            renamed = tuple(mapping[label] for label in seed)
            for oriented in (renamed, renamed[::-1]):
                for rotation in range(len(seed)):
                    orbit.add(oriented[rotation:] + oriented[:rotation])
        require(orbit <= universal, "symmetry changed low coverage or multiplicities")
        require(orbit <= unseen, "overlapping group orbits")
        unseen.difference_update(orbit)
        representatives.append(min(orbit))
        orbit_sizes[len(orbit)] += 1
    return representatives, {"labeled_words": all_words, "universal_words": len(universal),
                             "orbits": len(representatives), "orbit_sizes": dict(sorted(orbit_sizes.items())),
                             "representatives_sha256": digest(representatives)}


def vertex_path_oracle():
    """Every ordered subset of the nonzero vertices; no coordinate DFS."""
    grouped = {}
    for size in range(8):
        for tail in itertools.permutations(range(1, 8), size):
            vertices = (0,) + tail
            differences = tuple(a ^ b for a, b in zip(vertices, vertices[1:]))
            if any(d not in (1, 2, 4) for d in differences):
                continue
            counts = tuple(differences.count(1 << axis) for axis in range(3))
            key = (sum(1 << v for v in vertices), vertices[-1], *counts)
            grouped.setdefault(key, []).append(tuple(d.bit_length() - 1 for d in differences))
    return grouped


def replacement_controls(paths):
    """Every nontrivial quotient collision, translated to every high origin."""
    cases = 0
    for words in paths.values():
        if len(words) < 2:
            continue
        reference = words[0]
        # Close the full word after a fixed restored low excursion. The final
        # high suffix is held fixed when the first path is replaced.
        low = tuple(label + 3 for label in (0, 1, 0, 1, 2, 3, 2, 3))
        original = reference + low + reference[::-1]
        points, end = prefix_points(original)
        require(end == 0, "replacement positive fixture is not restored")
        for alternative in words[1:]:
            changed = alternative + low + reference[::-1]
            other, end = prefix_points(changed)
            require(end == 0 and Counter(original) == Counter(changed), "replacement endpoint/counts")
            for origin in range(8):
                require({point ^ origin for point in points} == {point ^ origin for point in other},
                        "path replacement changed full prefix set")
                cases += 1
    require(cases > 0, "path quotient replacement controls vacuous")
    return cases


def replace_once(source, old, new):
    require(source.count(old) == 1, "source correspondence anchor not unique: " + old)
    return source.replace(old, new, 1)


def gap_instrumentation(source):
    # Preserve recursive loop, bounds, terminal test, flags and counters.
    # Capture terminal compositions; stop before capacity or word search.
    source = replace_once(source, "++stats.compositions;", "++stats.compositions; audit_gap(gaps);")
    return replace_once(source, "if (!capacity(gaps)) return;", "return; // domain audit: no word search")


def build(directory, source):
    (directory / "subject.cpp").write_text(source)
    (directory / "audit.cpp").write_bytes((HERE / "audit.cpp").read_bytes())
    compiler = shutil.which(os.environ.get("CXX", "c++"))
    require(compiler is not None, "C++17 compiler required (CXX or c++)")
    result = subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Wextra",
                             str(directory / "audit.cpp"), "-o", str(directory / "audit")],
                            capture_output=True, timeout=60)
    require(result.returncode == 0, "compile failed: " + result.stderr.decode(errors="replace"))
    return directory / "audit"


def run(executable, *arguments):
    result = subprocess.run([str(executable), *arguments], capture_output=True, timeout=120)
    require(result.returncode == 0, "native audit failed: " + result.stderr.decode(errors="replace"))
    return result.stdout


def check_catalogue(raw, low, paths):
    rows = [(line[:1].decode(), tuple(map(int, line[2:].split()))) for line in raw.splitlines()]
    require(Counter(kind for kind, _ in rows) == {"T": 82, "P": len(paths), "C": 8*len(paths), "D": 256},
            "catalogue record inventory")
    for pattern in (0, 1):
        actual = [row[1:] for kind, row in rows if kind == "T" and row[0] == pattern]
        require(actual == low[pattern][0], "complete low orbit representatives differ")
    actual_paths = [row for kind, row in rows if kind == "P"]
    require([row[:5] for row in actual_paths] == sorted(paths), "complete path quotient differs")
    for row in actual_paths:
        require(row[5:] in paths[row[:5]], "invalid compressed-path representative")
    candidates = [row for kind, row in rows if kind == "C"]
    expected = []
    for normal, (mask, end, *counts) in enumerate(sorted(paths)):
        for start in range(8):
            translated = sum(1 << (v ^ start) for v in range(8) if (mask >> v) & 1)
            expected.append((normal, start, end ^ start, translated, sum(counts), *counts))
    require(candidates == expected, "translated candidate catalogue differs")
    specifications = set()
    for kind, row in rows:
        if kind != "D":
            continue
        pattern, first_length, second_length, slot = row[:4]
        spec = row[:4]
        require(spec not in specifications, "duplicate initial domain case")
        specifications.add(spec)
        first = slot == 0
        length = first_length if first else second_length
        parity = 0 if first else first_length % 2
        ids = tuple(i for i, c in enumerate(expected) if c[4] == length and
                    (c[1] == 0 if first else c[1].bit_count() % 2 == parity))
        require(row[4:] == ids, "incorrect initial domain: " + str(spec))
    require(specifications == set(itertools.product(range(2), range(8), range(8), range(2))),
            "missing initial domain case")
    return {"candidates": len(candidates), "initial_domain_cases": len(specifications),
            "catalogue_sha256": digest(rows)}


def gap_oracle(blocks, total):
    """Stars-and-bars subsets, independent of the native recursive loop."""
    vectors = []
    for bars in itertools.combinations(range(total + blocks - 1), blocks - 1):
        positions = (-1,) + bars + (total + blocks - 1,)
        gaps = tuple(b - a - 1 for a, b in zip(positions, positions[1:]))
        if max(gaps) <= 7:
            vectors.append(bytes(gaps))
    return vectors


def check_gaps(raw, expected, blocks, total):
    require(len(raw) % blocks == 0, "truncated gap capture")
    actual = [raw[i:i + blocks] for i in range(0, len(raw), blocks)]
    require(actual == expected, "incomplete or reordered bounded composition domain")
    count = sum((-1)**j * math.comb(blocks, j) * math.comb(total - 8*j + blocks - 1, blocks - 1)
                for j in range(min(blocks, total // 8) + 1))
    require(len(actual) == count and len(set(actual)) == count, "gap count/uniqueness identity")
    require(any(0 in row for row in actual) and any(7 in row for row in actual), "missing gap boundaries")
    return {"blocks": blocks, "high_steps": total, "compositions": count,
            "ordered_bytes_sha256": hashlib.sha256(raw).hexdigest()}


def expect_rejected(action, label):
    try:
        action()
    except (ValueError, subprocess.SubprocessError):
        return label
    raise ValueError("control unexpectedly accepted: " + label)


def audit(controls=False):
    source = source_bytes()
    low = {0: low_oracle(False), 1: low_oracle(True)}
    paths = vertex_path_oracle()
    replacements = replacement_controls(paths)
    expected_gaps = {"A": gap_oracle(8, 14), "B": gap_oracle(10, 12)}
    with tempfile.TemporaryDirectory(prefix="connector-domain-") as temporary:
        directory = pathlib.Path(temporary)
        executable = build(directory, source)
        catalogue_raw = run(executable)
        catalogue = check_catalogue(catalogue_raw, low, paths)
        executable = build(directory, gap_instrumentation(source))
        gap_receipts = {}
        for pattern, blocks, total in (("A", 8, 14), ("B", 10, 12)):
            gap_receipts[pattern] = check_gaps(run(executable, pattern), expected_gaps[pattern], blocks, total)
        if controls:
            mutations = [
                ("omit low orbit", 'throw std::runtime_error("low-dihedral orbit count mismatch");\n  return result;',
                 'throw std::runtime_error("low-dihedral orbit count mismatch");\n  result.pop_back(); return result;'),
                ("discard path counts", "paths.push_back({mask, end, frequency, representative});",
                 "paths.push_back({mask, end, Counts{}, representative});"),
                ("reset high start parity", "start_parity ^= gaps[i] & 1;", "start_parity = 0;"),
            ]
            for label, old, new in mutations:
                executable = build(directory, replace_once(source, old, new))
                expect_rejected(lambda: check_catalogue(run(executable), low, paths), label)
            mutant = replace_once(gap_instrumentation(source), "std::min(7, remaining)", "std::min(6, remaining)")
            executable = build(directory, mutant)
            expect_rejected(lambda: check_gaps(run(executable, "A"), expected_gaps["A"], 8, 14), "omit gap seven")
            expect_rejected(lambda: check_catalogue(catalogue_raw.splitlines()[0], low, paths), "truncated catalogue")
            expect_rejected(lambda: check_gaps(b"\0", expected_gaps["A"], 8, 14), "truncated gap stream")
            expect_rejected(lambda: replace_once(source + "\n++stats.compositions;", "++stats.compositions;", ""), "ambiguous source anchor")
            print("PASS_DOMAIN_CONTROLS compiled_mutants=4 truncations=2 correspondence=1")
    collisions = {key: words for key, words in paths.items() if len(words) > 1}
    example_key = min(collisions)
    return {"source_sha256": SOURCE_SHA, "low_words": {"AB"[k]: v[1] for k, v in low.items()},
            "high_paths": {"literal_paths": sum(map(len, paths.values())), "quotient_classes": len(paths),
                           "translated_replacement_controls": replacements,
                           "class_size_histogram": dict(sorted(Counter(map(len, paths.values())).items())),
                           "quotient_keys_sha256": digest(sorted(paths)),
                           "collision_example": {"key": example_key, "words": collisions[example_key]}},
            "native_catalogue": catalogue, "gaps": gap_receipts,
            "scope": "Complete representation domains for the pinned simple A/B contract; no full census or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print receipt without overwriting evidence")
    parser.add_argument("--controls", action="store_true", help="also compile four semantic mutants")
    args = parser.parse_args()
    result = audit(args.controls)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.loads(json.dumps(result)) == json.loads((HERE / "RESULT.json").read_text()),
                "committed receipt mismatch")
        print("PASS_CONNECTOR_DOMAIN_COMPLETENESS low_orbits=82 path_classes=106 initial_domains=256 no_full_census")


if __name__ == "__main__":
    main()
