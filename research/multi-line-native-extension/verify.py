"""Independent literal GL corroboration and frozen native-contact adapter.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from extension import extend, need


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linear(columns, vector, q):
    return tuple(sum(c * column[i] for c, column in zip(vector, columns)) % q
                 for i in range(len(vector)))


def span(rows, n, q):
    values = {(0,) * n}
    for row in rows:
        values = {tuple((v[i] + c * row[i]) % q for i in range(n))
                  for v in values for c in range(q)}
    return frozenset(values)


def literal_basis(space, n, q):
    rows, current = [], frozenset({(0,) * n})
    for v in sorted(space):
        if v not in current:
            rows.append(v)
            current = span(rows, n, q)
    return tuple(rows)


def subspaces(n, q):
    vectors = tuple(product(range(q), repeat=n))
    spaces = [frozenset({(0,) * n})]
    seen = set(spaces)
    for space in spaces:
        rows = literal_basis(space, n, q)
        for v in vectors:
            if v in space:
                continue
            larger = span((*rows, v), n, q)
            if larger not in seen:
                spaces.append(larger)
                seen.add(larger)
    return sorted(spaces, key=lambda s: (len(s), sorted(s)))


def witness(result, n, q, source, capacity, pairs):
    columns = result["columns"]
    need(result["count"] > 0 and columns is not None, "missing positive witness")
    vectors = tuple(product(range(q), repeat=n))
    need(len({linear(columns, v, q) for v in vectors}) == q ** n, "singular witness")
    need(all(linear(columns, v, q) in capacity for v in source), "late contact")
    need(all(linear(columns, x, q) == y for x, y in pairs), "prelude contact")


def literal_domain(n, q):
    """Every partial injection and every A,C; GL enumeration supplies counts."""
    vectors = tuple(product(range(q), repeat=n))
    spaces = subspaces(n, q)
    bases = [literal_basis(s, n, q) for s in spaces]
    indices = {s: i for i, s in enumerate(spaces)}
    over = [[i for i, c in enumerate(spaces) if a <= c] for a in spaces]
    partials, gl_count = {}, 0
    for columns in product(vectors[1:], repeat=n):
        permutation = {v: linear(columns, v, q) for v in vectors}
        if len(set(permutation.values())) != q ** n:
            continue
        gl_count += 1
        images = [indices[frozenset(permutation[v] for v in a)] for a in spaces]
        for ui, u in enumerate(bases):
            key = ui, tuple(permutation[v] for v in u)
            counts = partials.setdefault(key, Counter())
            for ai, image_index in enumerate(images):
                counts.update((ai, ci) for ci in over[image_index])
    digest = hashlib.sha256()
    cases = positive = witnesses = 0
    for (ui, images), counts in sorted(partials.items()):
        pairs = tuple(zip(bases[ui], images))
        for ai, a in enumerate(bases):
            for ci, c in enumerate(bases):
                result = extend(n, q, a, c, pairs)
                expected = counts[ai, ci]
                need(type(result["count"]) is int and result["count"] == expected,
                     f"literal count mismatch {(n, q, ui, ai, ci, images)}")
                if expected:
                    positive += 1
                    if n < 3 or cases % 19 == 0:
                        witness(result, n, q, spaces[ai], spaces[ci], pairs)
                        witnesses += 1
                else:
                    need(result["columns"] is None, "zero count has witness")
                digest.update(encoded([ui, images, ai, ci, expected]).encode())
                cases += 1
    return {"n": n, "q": q, "spaces": len(spaces), "gl": gl_count,
            "partial_injections": len(partials), "cases": cases,
            "positive": positive, "literal_witnesses": witnesses,
            "table_sha256": digest.hexdigest()}


def binary(mask, n=9):
    return tuple((mask >> i) & 1 for i in range(n))


def actual_contacts():
    payload = json.loads(gzip.decompress(
        (ROOT / "research/warp-interface-20261022/ACTUAL-WORD.json.gz").read_bytes()))
    canonical = payload["canonical"]
    frames = [tuple(binary(v) for v in b) for b in canonical["frames"]]
    frame_sets = [span(b, 9, 2) for b in frames]
    originals = {w["op"]: tuple(binary(v) for v in w["G_columns"])
                 for w in canonical["warps"]}
    records, pair_operators, catalogue_cases = [], set(), 0
    for direction, word in sorted(payload["programs"].items()):
        for operator in range(1, 73):
            proper = []
            for e in word:
                if e[0] != "warp" or abs(e[2]) != operator:
                    continue
                if len(frames[e[3]]) in (0, 9) and len(frames[e[4]]) in (0, 9):
                    continue
                proper.append((e[3], e[4]) if e[2] > 0 else (e[4], e[3]))
            need(bool(proper), "missing source operator")
            late = max(proper, key=lambda pair: len(frames[pair[0]]))
            earlier = [pair for pair in proper if pair != late]
            need(not earlier or len(set(earlier)) == 1, "source single-pair premise")
            need(all(len(frames[a]) == len(frames[b]) == 1 for a, b in earlier),
                 "source prelude dimension")
            pairs = tuple((frames[a][0], frames[b][0]) for a, b in earlier)
            source, capacity = frames[late[0]], frames[late[1]]
            result = extend(9, 2, source, capacity, pairs)
            witness(result, 9, 2, frame_sets[late[0]], frame_sets[late[1]], pairs)
            need(all(linear(originals[operator], v, 2) in frame_sets[late[1]]
                     for v in frame_sets[late[0]]), "retained late image")
            need(all(linear(originals[operator], a, 2) == b for a, b in pairs),
                 "retained prelude image")
            record = {"direction": direction, "operator": operator,
                      "late": late, "prelude_contacts": len(pairs),
                      "count": result["count"]}
            if pairs:
                pair_operators.add(operator)
                a, b = pairs[0]
                sa = frame_sets[late[0]]
                for ci, sc in enumerate(frame_sets):
                    old = (len(source) <= len(frames[ci]) and
                           ((b in sc) if a in sa else
                            (len(source) < len(frames[ci]) or b not in sc)))
                    new = extend(9, 2, source, frames[ci], pairs)
                    need(bool(new["count"]) == old, "source one-line predicate")
                    catalogue_cases += 1
                standard = [binary(1 << i) for i in range(9)]
                extra = next(v for v in standard if v not in span([a], 9, 2))
                stronger = (*pairs, (extra, linear(originals[operator], extra, 2)))
                augmented = extend(9, 2, source, capacity, stronger)
                witness(augmented, 9, 2, sa, frame_sets[late[1]], stronger)
                need(result["count"] > augmented["count"] > 0,
                     "additional line must reduce completion freedom")
                record["augmented_count"] = augmented["count"]
            records.append(record)
    need(pair_operators == set(range(47, 59)), "actual twelve prelude operators")
    need(len(records) == 144, "two orientations and 72 native maps")
    return {"contracts": len(records), "prelude_operators": sorted(pair_operators),
            "catalogue_predicates": catalogue_cases, "records": records}


def controls():
    e1, e2, e3 = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    p1, p2 = (e1, e1), (e2, e2)
    need(extend(3, 2, [e3], [e1, e2], [p1])["count"] == 8, "first line")
    need(extend(3, 2, [e3], [e1, e2], [p2])["count"] == 8, "second line")
    failures = [
        ([e3], [e1, e2], [p1, p2], "quotient-capacity"),
        ([e1], [e2], [p1], "prescribed-intersection"),
        ([], [], [(e1, e1), (e1, e2)], "inconsistent-or-noninjective"),
        ([], [], [(e1, e1), (e2, e1)], "inconsistent-or-noninjective"),
        ([], [], [((0, 0, 0), e1)], "inconsistent-or-noninjective"),
        ([], [], [p1, p2, ((1, 1, 0), e3)], "inconsistent-or-noninjective"),
    ]
    for a, c, pairs, reason in failures:
        result = extend(3, 2, a, c, pairs)
        need(result["count"] == 0 and result["reason"] == reason, "boundary control")
    redundant = extend(3, 2, [e3], [e1, e2, e3],
                       [p1, p2, ((1, 1, 0), (1, 1, 0)), p1])
    need(redundant["count"] == 4, "consistent dependent equations")
    malformed = [(True, 2, [], [], []), (2, True, [], [], []),
                 (2, 4, [], [], []), (2, 3, [(True, 0)], [], []),
                 (2, 3, [(3, 0)], [], []), (2, 3, [], [], [[(1, 0)]])]
    for args in malformed:
        try:
            extend(*args)
        except ValueError:
            continue
        raise ValueError("malformed control accepted")
    return {"independent_conditions": len(failures), "single_line_count": 8,
            "joint_line_count": 0, "redundant_relations": 1,
            "malformed_controls": len(malformed)}


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    live = {}
    for item in sources["files"]:
        if item["usage"] == "input":
            actual = checksum(ROOT / item["path"])
            need(actual == item["sha256"], "source authentication: " + item["path"])
            live[item["path"]] = actual
    return live


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "occupied receipt output")
    sources = authenticate()
    domains = [literal_domain(n, q) for n, q in [(0, 2), (2, 2), (2, 3),
                                                (2, 5), (3, 2)]]
    result = {"schema_version": 1, "claim_type": "scoped-proof-finite-corroboration",
              "domains": domains, "actual_source": actual_contacts(),
              "controls": controls(), "sources": sources,
              "local_sha256": {p.name: checksum(p) for p in sorted(HERE.iterdir())
                               if p.is_file() and p.name != "RESULT.json"},
              "new_kappa": False, "physical_admission": False,
              "formal_kernel_verified": False}
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(encoded(expected) == encoded(result), "type-sensitive receipt mismatch")
    print("PASS_MULTI_LINE_NATIVE_EXTENSION " + encoded({
        "cases": sum(d["cases"] for d in domains),
        "source_contracts": result["actual_source"]["contracts"],
        "catalogue_predicates": result["actual_source"]["catalogue_predicates"]}))


if __name__ == "__main__":
    main()
