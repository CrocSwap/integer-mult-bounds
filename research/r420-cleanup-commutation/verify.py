"""Exact finite cleanup experiment. @thakrarsagar / OpenAI Codex; Apache-2.0.

Run from any directory with Python 3.11+. No third-party Python dependencies.
Optional --emit-word PATH writes the verified candidate for native replay.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def expand(gates):
    return [(d, s) for _, d, sources in gates for s in sources]


def commute(a, b):
    return a[0] != b[1] and b[0] != a[1]


def census(gates):
    positions = defaultdict(list)
    # Seed 10 rotates the finite scan; sorting makes the certificate order canonical.
    for i in list(range(10, len(gates))) + list(range(min(10, len(gates)))):
        positions[gates[i]].append(i)
    rows = []
    for a, indices in positions.items():
        indices.sort()
        for i, j in zip(indices, indices[1:]):
            blockers = [k for k in range(i + 1, j) if not commute(a, gates[k])]
            rows.append([i, j, list(a), len(blockers), blockers[0] if blockers else None])
    return sorted(rows)


def rewrite(gates, recipe):
    k = recipe["insert_after"]
    removed = recipe["delete"]
    need(len(removed) == len(set(removed)) == 4, "recipe deletion count")
    pairs = [(removed[0], removed[3]), (removed[1], removed[2])]
    replacements = []
    for i, j in pairs:
        need(0 <= i < k < j < len(gates), "recipe indices")
        a, b = gates[i], gates[k]
        need(a == gates[j], "sandwich endpoints differ")
        blockers = [q for q in range(i + 1, j) if not commute(a, gates[q])]
        need(blockers == [k], "sandwich does not have exactly the declared blocker")
        need(a[0] == b[1] and a[1] != b[0], "not the certified three-register chain")
        replacements.append((b[0], a[1]))
    need(replacements == [tuple(g) for g in recipe["insert_gates"]], "wrong conjugate gates")
    need(commute(gates[removed[0]], gates[removed[1]]), "outer gates do not commute")
    result = []
    for i, gate in enumerate(gates):
        if i not in removed:
            result.append(gate)
        if i == k:
            result.extend(replacements)
    return result


def matrix(gates, n):
    rows = [1 << r for r in range(n)]
    for d, s in gates:
        need(0 <= d < n and 0 <= s < n and d != s, "bad XOR operands")
        rows[d] ^= rows[s]
    return rows


def scalar_stream(word):
    temp = 2 * word["v"] + word["R"]
    stream = [("add", d, s) for name in ("D", "A") for d, s in expand(word[name])]
    for k, q in enumerate(word["ret"]):
        stream.append(("copy", temp, q))
        stream.extend(("add", word["v"] + t, temp)
                      for t, row in enumerate(word["scatter"]) if k in row)
        stream.append(("erase", temp, q))
    stream.extend(("add", d, s) for name in ("B", "C") for d, s in expand(word[name]))
    return stream


def prefix_bounds(stream, n):
    bounds = []
    for reverse in (False, True):
        norms = [1] * (n + 1)
        largest, opened = 1, False
        for kind, d, s in reversed(stream) if reverse else stream:
            if reverse and kind != "add":
                kind = "erase" if kind == "copy" else "copy"
            if kind == "add":
                norms[d] += norms[s]
                largest = max(largest, norms[d])
            elif kind == "copy":
                need(not opened, "nested COPY")
                norms[d], opened = norms[s], True
            else:
                need(opened, "unmatched ERASE")
                norms[d], opened = 0, False
        need(not opened, "unclosed COPY")
        bounds.append(largest)
    return bounds


def frame_paths(word):
    paths = [[f] for f in word["start"]]
    for name in ("D", "A", "B", "C"):
        for f, d, sources in word[name]:
            for r in [d] + sources:
                if paths[r][-1] != f:
                    paths[r].append(f)
    for r, f in enumerate(word["final"]):
        if paths[r][-1] != f:
            paths[r].append(f)
    return paths


def expect_rejection(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-word", type=Path)
    args = parser.parse_args()
    cert = json.loads((HERE / "certificate.json").read_text())
    for path, digest in cert["source_sha256"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "source pin: " + path)
    word = json.loads(gzip.decompress((ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz").read_bytes()))
    need(hashlib.sha256(canonical(word)).hexdigest() == cert["canonical_input_sha256"], "input content pin")
    before = expand(word["C"])
    rows = census(before)
    need(rows == cert["duplicate_census"], "duplicate census mismatch")
    need(all(row[3] > 0 for row in rows), "commutation-only cancellation exists")
    need(sum(row[3] == 1 for row in rows) == 2, "one-blocker coverage changed")
    after = rewrite(before, cert["recipe"])
    n = 2 * word["v"] + word["R"]
    expected = matrix(before, n)
    need(matrix(after, n) == expected, "cleanup matrix mismatch")
    need([len(before), len(after)] == cert["cleanup_binary_adds"], "cleanup count")
    candidate = deepcopy(word)
    full = cert["recipe"]["full_frame_id"]
    need(all(f == full for f, _, _ in word["C"]), "baseline C not at full frame")
    candidate["C"] = [[full, d, [s]] for d, s in after]
    need(hashlib.sha256(canonical(candidate)).hexdigest() == cert["canonical_candidate_sha256"],
         "candidate content pin")
    need(frame_paths(word) == frame_paths(candidate), "a paid register path changed")

    checker_path = ROOT / "research/e8-bit-r420/code/xcheck.py"
    spec = importlib.util.spec_from_file_location("pinned_r420_xcheck", checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    baseline, labels, _, hypotheses, conclusion, _ = checker.check(word)
    need(all(hypotheses.values()) and all(conclusion.values()), "baseline interface")
    # Geometry is byte-identical; reuse the checked geometry for the candidate replay.
    baseline.w = candidate
    finite = baseline.full()
    h, c, _ = baseline.interface()
    need([k for k, v in h.items() if not v] == ["H4_C_literal_reverse_at_full"], "unexpected interface change")
    need(all(c.values()), "candidate inverse/decomposition")
    need(baseline.fdim[full] == 8, "replacement frame is not full")
    need(all(not 120 <= r < 240 for gate in after for r in gate), "cleanup touches a target")
    paths = frame_paths(candidate)
    ranks = Counter(baseline.fdim[b] - baseline.fdim[a] for path in paths for a, b in zip(path, path[1:]))
    ranks[8] += len(word["ret"])
    need(dict(ranks) == {1: 1320, 2: 1440, 4: 60, 5: 120, 8: 9}, "paid histogram")
    streams = [scalar_stream(w) for w in (word, candidate)]
    need([sum(k == "add" for k, _, _ in s) for s in streams] == cert["native_adds"], "native ADD count")
    bounds = [prefix_bounds(s, n) for s in streams]
    need(bounds == cert["positive_prefix_before_after"], "positive prefix receipt")
    need(all(b <= a for a, b in zip(*bounds)), "positive prefix increased")

    # These controls address the changed identity, its blocker premise, and its price.
    for added in cert["recipe"]["insert_gates"]:
        broken = list(after)
        broken.remove(tuple(added))
        need(matrix(broken, n) != expected, "missing conjugate not detected")
    bad_recipe = deepcopy(cert["recipe"])
    bad_recipe["insert_gates"][0][1] = 531
    expect_rejection(lambda: rewrite(before, bad_recipe), "wrong conjugate source")
    broken = list(before)
    broken[800] = (530, 0)
    expect_rejection(lambda: rewrite(broken, cert["recipe"]), "extra noncommuting blocker")
    need(matrix([(616, 530), (466, 616), (616, 530)], n)
         != matrix([(466, 616)], n), "unpaid conjugate not detected")
    illegal = deepcopy(candidate)
    illegal["C"][0][0] = 0
    baseline.w = illegal
    try:
        baseline.full()
    except checker.Reject:
        pass
    else:
        raise ValueError("negative control accepted: illegal cleanup descent")
    baseline.w = candidate
    # Exhaust the local identity independently as a four-bit truth table.
    for bits in range(16):
        x = [(bits >> i) & 1 for i in range(4)]
        y = list(x)
        for d, s in [(0, 2), (0, 3), (1, 0), (0, 3), (0, 2)]:
            x[d] ^= x[s]
        for d, s in [(1, 0), (1, 2), (1, 3)]:
            y[d] ^= y[s]
        need(x == y, "local truth table")
    print(json.dumps({"labels": labels, "columns": finite["columns"],
                      "duplicate_pairs": len(rows), "paid_histogram": dict(sorted(ranks.items())),
                      "positive_prefix_before_after": bounds,
                      "candidate_content_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
                      "controls_rejected": 6, "local_truth_table_inputs": 16}, sort_keys=True))
    if args.emit_word:
        args.emit_word.write_bytes(canonical(candidate))
    print("PASS_R420_CLEANUP_CONJUGATION C=2973->2971 native_adds=26916->26914 columns=660 kappa=unchanged")


if __name__ == "__main__":
    main()
