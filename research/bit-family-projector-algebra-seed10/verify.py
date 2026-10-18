#!/usr/bin/env python3
"""Independent rational projector-algebra audit of PR1351's frozen family."""
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TARGET = PACKAGE / "PR1351-RESULT.json"
REPORT = PACKAGE / "RESULT.json"
DIM = 64
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_root(relative):
    return (ROOT / relative).read_bytes()


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    header = b"blob " + str(len(raw)).encode() + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def zero_matrix():
    return [[Q(0) for _ in range(DIM)] for _ in range(DIM)]


def identity_matrix():
    result = zero_matrix()
    for i in range(DIM):
        result[i][i] = Q(1)
    return result


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    n = len(a)
    result = [[Q(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k, left in enumerate(a[i]):
            if left:
                for j, right in enumerate(b[k]):
                    if right:
                        result[i][j] += left * right
    return result


def add(*matrices):
    n = len(matrices[0])
    return [[sum((m[i][j] for m in matrices), Q(0))
             for j in range(n)] for i in range(n)]


def trace(a):
    return sum((a[i][i] for i in range(len(a))), Q(0))


def is_symmetric(a):
    return a == transpose(a)


def is_projector(a):
    return is_symmetric(a) and multiply(a, a) == a


def q_perp(q):
    need(len(q) == 8 and sum(x * x for x in q) == 4,
         "selected port line has norm squared four")
    k = [[Q(int(i == j)) - Q(q[i] * q[j], 4)
          for j in range(8)] for i in range(8)]
    need(k == transpose(k), "q-perp symmetry")
    need([[sum(k[i][m] * k[m][j] for m in range(8))
           for j in range(8)] for i in range(8)] == k,
         "q-perp idempotence")
    need(all(sum(k[i][j] * q[j] for j in range(8)) == 0
             for i in range(8)), "q-perp annihilates selected line")
    need(sum(k[i][i] for i in range(8)) == 7, "q-perp rank seven")
    return k


def ambient_projector(axes, q):
    axes = tuple(axes)
    need(len(set(axes)) == len(axes), "unique axes")
    need(all(isinstance(a, int) and 0 <= a < DIM for a in axes),
         "axis in ambient space")
    local = {a for a in axes if a < 8}
    need(local in (set(), set(range(1, 8))),
         "local axes contain the whole q-perp block")
    p = zero_matrix()
    if local:
        k = q_perp(q)
        for i in range(8):
            for j in range(8):
                p[i][j] = k[i][j]
    for axis in axes:
        if axis >= 8:
            p[axis][axis] = Q(1)
    need(is_projector(p), "ambient projector symmetry and idempotence")
    need(trace(p).denominator == 1, "projector trace integral")
    return p


def orthogonal_decomposition(factors, source):
    if not is_projector(source):
        return False
    if not all(is_projector(p) for p in factors):
        return False
    for i, p in enumerate(factors):
        for q in factors[i + 1:]:
            if multiply(p, q) != zero_matrix():
                return False
            if multiply(q, p) != zero_matrix():
                return False
    total = add(*factors)
    return total == source and is_projector(total)


def source_data(target, sources):
    need(sources["base_commit"] == BASE, "exact base commit")
    for row in sources["files"]:
        if row["usage"] == "provenance":
            continue
        raw = read_root(row["path"])
        need(sha256(raw) == row["sha256"], "source SHA-256: " + row["path"])
        need(git_blob(raw) == row["git_blob"], "source Git blob: " + row["path"])

    remote = sources["predecessor_record"]
    target_raw = TARGET.read_bytes()
    need(remote["pr"] == 1351 and remote["commit"] ==
         "6060e62e9d42a16eff493aba74c8a617a12d8041", "pinned PR1351 head")
    need(sha256(target_raw) == remote["sha256"], "PR1351 result SHA-256")
    need(git_blob(target_raw) == remote["git_blob"], "PR1351 result Git blob")

    input_pins = {row["path"]: row for row in sources["files"]
                  if row["usage"] == "input"}
    all_pins = {row["path"]: row for row in sources["files"]}
    for path, expected in target["source_hashes"].items():
        need(path in all_pins and all_pins[path]["sha256"] == expected,
             "predecessor source pin: " + path)

    selected = json.loads(read_root("certificates/selected-result.json"))
    assembly = json.loads(read_root(
        "research/community-frontier1094-audit/ASSEMBLY.json"))
    need(selected["kappa"] == "836330098538459/500000000000000000",
         "selected kappa")
    need(589 in selected["source_prs"], "PR589 is a selected source")
    need(assembly["bit_supplier"]["commit"] ==
         "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46",
         "selected PR589 source commit")
    selected_manifest = json.loads(read_root(
        "research/community-frontier1094-audit/SELECTED-SOURCE.json"))
    need(selected_manifest["files"][
        "research/e8-bit-p111-tuned/tune/EXPECTED.json"] ==
         input_pins["research/e8-bit-p111-tuned/tune/EXPECTED.json"]["sha256"],
         "selected PR589 receipt binding")
    word_raw = read_root(
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz")
    word = json.loads(gzip.decompress(word_raw))
    return selected, tuple(word["lines"][0])


def verify():
    target = json.loads(TARGET.read_text())
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    selected, q = source_data(target, sources)
    k = q_perp(q)
    need(target["base_commit"] == BASE, "predecessor exact base")
    need(target["status"] == "PASS_PR589_PHYSICAL_FAMILY",
         "predecessor positive status")

    family = target["family"]
    need((family["pair"], family["copy"], family["side"], family["port"]) ==
         (1, 0, 0, 0), "selected physical family key")
    expected_roles = [[0, 0, 0, 8, 1, 0],
                      [7, 0, 0, 8, 5, 429],
                      [7, 0, 8, 8, 5, 430],
                      [7, 0, 16, 8, 5, 431]]
    need(family["roles"] == expected_roles, "pinned family roles")
    need(q == (2, 0, 0, 0, 0, 0, 0, 0), "family port-zero line")

    expected = {
        0: {"host_axes": [[1, 2, 3, 4, 5, 6, 7, 8]],
            "remainder_axes": list(range(9, 15)),
            "source_axes": list(range(1, 15)), "host_event_positions": [1],
            "deadline_event_position": 2},
        7: {"host_axes": [list(range(36, 44)), list(range(44, 52)),
                          list(range(52, 60))],
            "remainder_axes": list(range(60, 64)),
            "source_axes": list(range(36, 64)),
            "host_event_positions": [13, 13, 13],
            "deadline_event_position": 22}}
    intervals = target["interval_results"]
    need(set(intervals) == {"0", "7"}, "exact interval set")
    summarized = []
    for child in (0, 7):
        data = intervals[str(child)]
        shape = expected[child]
        for field, value in shape.items():
            need(data[field] == value, f"child {child} {field}")
        hosts = [ambient_projector(axes, q) for axes in shape["host_axes"]]
        remainder = ambient_projector(shape["remainder_axes"], q)
        source = ambient_projector(shape["source_axes"], q)
        factors = hosts + [remainder]
        need(orthogonal_decomposition(factors, source),
             f"child {child} exact orthogonal decomposition")
        ranks = [int(trace(p)) for p in factors]
        need(ranks == ([8, 6] if child == 0 else [8, 8, 8, 4]),
             f"child {child} exact factor ranks")
        need(int(trace(source)) == (14 if child == 0 else 28),
             f"child {child} source rank")
        summarized.append({"child": child, "factor_ranks": ranks,
                           "source_rank": int(trace(source)),
                           "host_event_positions": shape["host_event_positions"],
                           "deadline_event_position": shape["deadline_event_position"]})

    # Negative controls are mutations of the exact projector decomposition.
    child7 = intervals["7"]
    factors7 = [ambient_projector(a, q) for a in expected[7]["host_axes"]]
    rem7 = ambient_projector(expected[7]["remainder_axes"], q)
    source7 = ambient_projector(expected[7]["source_axes"], q)
    omitted = orthogonal_decomposition(factors7[:-1] + [rem7], source7)
    need(not omitted, "omitted-helper negative control")

    child0 = intervals["0"]
    good_host0 = expected[0]["host_axes"][0]
    bad_host0 = [a for a in good_host0 if a != 8] + [22]
    p_good = ambient_projector(good_host0, q)
    p_bad = ambient_projector(bad_host0, q)
    need(trace(p_good) == trace(p_bad), "wrong-axis control preserves rank")
    source0 = ambient_projector(expected[0]["source_axes"], q)
    rem0 = ambient_projector(expected[0]["remainder_axes"], q)
    wrong_axis = orthogonal_decomposition([p_bad, rem0], source0)
    need(not wrong_axis, "wrong-axis negative control")

    duplicate = orthogonal_decomposition(factors7 + [factors7[0], rem7], source7)
    need(not duplicate, "duplicate-helper negative control")

    return {
        "status": "PASS_BIT_FAMILY_PROJECTOR_ALGEBRA",
        "base_commit": BASE,
        "pr1351_head": sources["predecessor_record"]["commit"],
        "pr1351_result_git_blob": sources["predecessor_record"]["git_blob"],
        "selected_kappa": selected["kappa"],
        "family": {"pair": 1, "copy": 0, "side": 0, "port": 0},
        "q_perp_rank": int(trace(k)),
        "intervals": summarized,
        "block_identity": "pairwise orthogonal P_i imply product D(P_i)=D(sum P_i)",
        "negative_controls": {"omitted_helper": "rejected",
                              "same_rank_wrong_axis": "rejected",
                              "duplicate_helper": "rejected"},
        "no_new_kappa": True,
        "scope": "Exact operator identities conditional on the pinned PR1351 role map; no independent family selection, chronology replay, helper lowering, or supplier admission."
    }


def main():
    write = len(sys.argv) == 2 and sys.argv[1] == "--write"
    need(len(sys.argv) == 1 or write, "usage: verify.py [--write]")
    result = verify()
    if write:
        need(not REPORT.exists(), "refusing to overwrite RESULT.json")
        REPORT.write_text(json.dumps(result, indent=2) + "\n")
        print("WROTE_RESULT " + str(REPORT.relative_to(ROOT)))
        return
    expected = json.loads(REPORT.read_text())
    need(result == expected, "stored RESULT.json differs from exact replay")
    print("PASS_BIT_FAMILY_PROJECTOR_ALGEBRA children=0,7 factors=2+4 q_rank=7 controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
