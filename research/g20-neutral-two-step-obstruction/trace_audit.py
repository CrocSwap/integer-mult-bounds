"""Audit the finite neutral paths using interval scans and ordered role traces.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No primary or predecessor executable is imported. This corroborates a finite
neutral subset; it neither enumerates the whole domain nor proves an all-depth
invariant. Credit #5708, #6290 and #6305 as in PROOF.md.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EXPECTED_SHA256 = "b0d62e1faa9aaa7bdde5aac5b55b5d226272461238fa960cc0ad0df0b054bb47"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load():
    data = {}
    for pin in json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] == "input":
            value = (ROOT / pin["path"]).read_bytes()
            need(sha256(value).hexdigest() == pin["sha256"], "source mismatch: " + pin["path"])
            data[Path(pin["path"]).name] = value
    payload = gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes())
    need(sha256(payload).hexdigest() == EXPECTED_SHA256, "two-step certificate mismatch")
    word = json.loads(gzip.decompress(data["WORD.json.gz"]))
    paths = json.loads(data["PATHS.json"])
    edges = {(v[0][0], v[0][1]): v[0][2] for v in paths.values()}
    records = [tuple(v) for v in word["records"] if v[0] not in ("Q", "ZERO_Q")]
    return word, records, edges, json.loads(payload)


def apply_interval(records, recipe):
    left, right, a, b, count = recipe
    need(0 <= left < right < len(records), "interval limits")
    need(records[left][:3] == records[right][:3] == ("ADD", a, b), "unequal gates")
    corrections = {}
    for index in range(left + 1, right):
        op, d = records[index][:2]
        if op in ("INIT", "ERASE"):
            need(d not in (a, b), "destructive interval barrier")
        elif op == "ADD":
            s, frame = records[index][2:]
            need((d, s) != (b, a), "reversed contact")
            if d == b:
                corrections[index] = ("ADD", a, s, frame)
            elif s == a:
                corrections[index] = ("ADD", d, b, frame)
        else:
            raise ValueError("unexpected scalar event")
    need(len(corrections) == count, "contact count")
    result = []
    for i, event in enumerate(records):
        if i not in (left, right):
            result.append(event)
            if i in corrections:
                result.append(corrections[i])
    return result


def walk(records, start, final, owned, edges):
    """Materialize per-role paid-edge sequences; count only after the walk."""
    rows = [1 << i for i in range(len(start))]
    frames = list(start)
    traces = [[] for _ in start]

    def visit(role, target):
        origin = frames[role]
        if origin == target:
            return
        if origin is None:
            need(role in owned and rows[role] == 0, "nonzero uninitialized role")
        else:
            need((origin, target) in edges, "missing published route")
            if rows[role]:
                traces[role].append((origin, target, edges[origin, target]))
        frames[role] = target

    for event in records:
        op, role = event[:2]
        if op in ("INIT", "ERASE"):
            need(role in owned and (op != "INIT" or not rows[role]), "owned event")
            frames[role], rows[role] = event[2], 0
        else:
            need(op == "ADD", "scalar opcode")
            source, target = event[2:]
            if rows[source]:
                visit(role, target)
                visit(source, target)
                rows[role] ^= rows[source]
    for role, target in enumerate(final):
        if role in owned:
            need(rows[role] == 0, "owned return")
            frames[role] = target
        else:
            visit(role, target)
    need(frames == list(final), "final frames")
    return rows, traces


def audit(word, records, edges, certificate):
    owned = set(word["owned"])
    endpoint, reference = walk(records, word["start"], word["final"], owned, edges)
    nodes = {tuple(records): len(records)}
    neutral_paths = 0
    first_words = set()
    for branch in certificate["branches"]:
        first = apply_interval(records, branch["first"])
        rows, trace = walk(first, word["start"], word["final"], owned, edges)
        need(rows == endpoint and trace == reference, "first route-trace drift")
        first_words.add(tuple(first))
        nodes[tuple(first)] = len(first)
        for recipe in branch["outcomes"]:
            if recipe[5] is not None or recipe[6] != []:
                continue
            final = apply_interval(first, recipe[:5])
            rows, trace = walk(final, word["start"], word["final"], owned, edges)
            need(rows == endpoint and trace == reference, "neutral role-trace drift")
            nodes[tuple(final)] = len(final)
            neutral_paths += 1
    need(len(first_words) == 14 and neutral_paths == 297 and len(nodes) == 221,
         "finite neutral domain")
    return {"schema": "g20-neutral-role-traces/v1", "first_words": len(first_words),
            "neutral_second_paths": neutral_paths, "distinct_words_including_root": len(nodes),
            "word_lengths": dict(sorted(Counter(nodes.values()).items())),
            "reference_role_trace_sha256": sha256(encoded(reference)).hexdigest(),
            "reference_paid": dict(sorted(Counter(edge[2] for role in reference for edge in role).items())),
            "two_step_certificate_sha256": EXPECTED_SHA256}


def controls():
    edges = {(a, b): 1 for a in range(3) for b in range(3) if a != b}
    first = [("ADD", 0, 1, 1), ("ADD", 2, 3, 2)]
    second = [("ADD", 0, 1, 2), ("ADD", 2, 3, 1)]
    r1, t1 = walk(first, [0]*4, [0]*4, set(), edges)
    r2, t2 = walk(second, [0]*4, [0]*4, set(), edges)
    price = lambda trace: Counter(edge[2] for role in trace for edge in role)
    need(r1 == r2 and price(t1) == price(t2) and t1 != t2, "role-swap discrimination")
    first = [("ADD", 0, 1, 1), ("ADD", 0, 1, 2)]
    second = list(reversed(first))
    r1, t1 = walk(first, [0, 0], [0, 0], set(), edges)
    r2, t2 = walk(second, [0, 0], [0, 0], set(), edges)
    need(r1 == r2 and price(t1) == price(t2) and t1 != t2, "route-order discrimination")
    bad = dict(edges)
    del bad[0, 1]
    try:
        walk(first, [0, 0], [0, 0], set(), bad)
    except ValueError as error:
        need(str(error) == "missing published route", "missing-route failure mode")
    else:
        raise ValueError("missing route accepted")
    return 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(*load())
    result["controls"] = controls()
    payload = encoded(result)
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT), "output must be outside checkout")
        args.output.write_bytes(payload)
    else:
        need(json.loads(payload) == json.loads((PACKAGE / "TRACE-SUMMARY.json").read_bytes()),
             "trace summary mismatch")
    print(payload.decode())
    print("PASS_G20_NEUTRAL_ROLE_TRACES first=14 second=297 distinct_words=221")


if __name__ == "__main__":
    main()
