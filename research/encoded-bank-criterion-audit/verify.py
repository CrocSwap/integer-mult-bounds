#!/usr/bin/env python3
"""Independent finite audit of formal paired-word crossing support.

DLamdata with OpenAI Codex assistance, Apache-2.0.
No predecessor implementation or matrix encoding is imported.
"""
import argparse
from collections import Counter, deque
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def paired_words(n):
    """Enumerate position matchings, labelled by first occurrence."""
    def match(positions, pairs):
        if not positions:
            word = [None] * (2 * n)
            for label, (a, b) in enumerate(sorted(pairs)):
                word[a] = word[b] = label
            yield tuple(word)
            return
        a, *rest = positions
        for b in rest:
            yield from match([x for x in rest if x != b], pairs + [(a, b)])
    yield from match(list(range(2 * n)), [])


def validate(word, n, mask):
    require(type(n) is int and n >= 0, "invalid alphabet")
    require(all(type(x) is int for x in word), "non-integer letter")
    require(Counter(word) == Counter({j: 2 for j in range(n)}), "not a paired word")
    require(type(mask) is int and 0 <= mask < 1 << (n * (n - 1) // 2),
            "invalid commutation mask")


def dependencies(n, mask):
    """Noncommuting neighbors, computed without inspecting a word."""
    deps = [[] for _ in range(n)]
    for bit, (a, b) in enumerate(combinations(range(n), 2)):
        if not (mask >> bit) & 1:
            deps[a].append(b)
            deps[b].append(a)
    return deps


def piling_identity(word, deps):
    """Involution-group piling, with beads and noncommutation blockers.

    A 1 records a letter; its 0 blockers prevent cancellation across an
    uncancelled dependent letter. A matching top bead removes its blockers.
    This procedure does not compute crossings or choose shortest intervals.
    """
    stacks = [[] for _ in deps]
    cancelled = [0] * len(deps)
    for a in word:
        if stacks[a] and stacks[a][-1] == 1:
            stacks[a].pop()
            for b in deps[a]:
                require(stacks[b] and stacks[b][-1] == 0, "piling blocker mismatch")
                stacks[b].pop()
            cancelled[a] += 1
        else:
            stacks[a].append(1)
            for b in deps[a]:
                stacks[b].append(0)
    empty = not any(stacks)
    if empty:
        require(cancelled == [1] * len(deps), "lost or duplicated self phase")
    return empty


def literal_identity(word, n, mask):
    """All adjacent swaps and adjacent-double deletions, no search cutoff."""
    commute = {pair for bit, pair in enumerate(combinations(range(n), 2))
               if (mask >> bit) & 1}
    todo, seen = deque([word]), {word}
    while todo:
        current = todo.popleft()
        if not current:
            return True
        for k in range(len(current) - 1):
            a, b = current[k:k + 2]
            if a == b:
                nxt = current[:k] + current[k + 2:]
            elif tuple(sorted((a, b))) in commute:
                nxt = current[:k] + (b, a) + current[k + 2:]
            else:
                continue
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return False


def crossing_mask(word, n):
    """Independent prediction from occurrence positions alone."""
    ends = [[k for k, letter in enumerate(word) if letter == j] for j in range(n)]
    result = 0
    for bit, (a, b) in enumerate(combinations(range(n), 2)):
        x, y = ends[a]
        z, t = ends[b]
        if x < z < y < t or z < x < t < y:
            result |= 1 << bit
    return result


def run():
    rows, literal_cases = [], 0
    for n in range(6):
        graphs = [(mask, dependencies(n, mask)) for mask in range(1 << (n * (n - 1) // 2))]
        words = list(paired_words(n))
        require(len(words) == len(set(words)), "duplicate matching")
        expected_words = 1
        for k in range(1, 2 * n, 2):
            expected_words *= k
        require(len(words) == expected_words, "incomplete matching enumeration")
        accepted = rejected = 0
        for word in words:
            required = crossing_mask(word, n)
            for mask, deps in graphs:
                validate(word, n, mask)
                actual = piling_identity(word, deps)
                require(actual == (required & mask == required),
                        f"crossing discrepancy: {word}, {mask}")
                accepted += actual
                rejected += not actual
                if n <= 3:
                    require(literal_identity(word, n, mask) == actual,
                            f"literal rewrite discrepancy: {word}, {mask}")
                    literal_cases += 1
        rows.append({"columns": n, "words": len(words), "graphs": len(graphs),
                     "accepted": accepted, "rejected": rejected})
    cycle = (0, 1, 4, 0, 3, 4, 2, 3, 1, 2)
    needed = crossing_mask(cycle, 5)
    edges = list(combinations(range(5), 2))
    require([edges[k] for k in range(10) if needed >> k & 1] ==
            [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4)], "wrong C5")
    require(piling_identity(cycle, dependencies(5, needed)), "C5 positive fixture")
    omitted = 0
    for k in range(10):
        if needed >> k & 1:
            require(not piling_identity(cycle, dependencies(5, needed ^ (1 << k))),
                    "omitted C5 relation accepted")
            omitted += 1
    require(piling_identity((0, 1, 1, 0), dependencies(2, 0)), "nested positive fixture")
    require(not piling_identity((0, 1, 0, 1), dependencies(2, 0)), "crossing negative fixture")
    invalid = [((0, 1, 0), 2, 0), ((0, 0, 0, 0), 2, 0), ((-1, -1), 1, 0),
               ((True, True), 1, 0), ((0, 0), 1, 1), ((0, 0), 1, -1)]
    for args in invalid:
        try:
            validate(*args)
        except ValueError:
            continue
        raise ValueError("malformed domain accepted")
    return {"status": "PASS_ENCODED_BANK_CRITERION_AUDIT", "domain": rows,
            "word_graph_cases": sum(r["accepted"] + r["rejected"] for r in rows),
            "literal_rewrite_cases": literal_cases, "omitted_C5_edge_controls": omitted,
            "invalid_domain_controls": len(invalid), "empty_word_checked": True,
            "scope": "Formal involutive letters only; no universal matrix or supplier certificate."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if not args.emit:
        expected = json.loads(Path(__file__).with_name("RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "receipt mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
