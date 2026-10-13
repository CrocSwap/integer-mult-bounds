"""Exact finite verification; no search code is imported.

Gautam Gupta, with substantial OpenAI Codex assistance. Apache-2.0.
The owning geometry/interface checker is eumemic's PR555/589 xcheck_p.py.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
NATIVE = "research/e8-bit-carrier-skeleton/"
REQUIRED_SOURCES = {WORD, CHECKER, NATIVE + "portable-include/bits/stdc++.h"}
REQUIRED_SOURCES.update(NATIVE + "code/bit/" + p for p in (
    "export_records.py", "regression/stage_cohort.py", "checkers/columns_h.cpp",
    "checkers/columns_k.cpp", "checkers/legality_h.cpp", "checkers/json.hpp"))
REGISTERS = [21, 26, 36, 44, 51, 55, 64, 71, 80, 84, 94, 102]
N = 12


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    need(manifest["base_commit"] == "7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261", "base pin")
    need(REQUIRED_SOURCES == manifest["files"].keys(), "missing or unexpected source pin")
    for path, expected in manifest["files"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, "source pin: " + path)
    return manifest


def matrix(ops, n=N):
    """Propagate each integer basis column independently."""
    columns = []
    for column in range(n):
        values = [int(i == column) for i in range(n)]
        for dst, src in ops:
            need(type(dst) is int and type(src) is int and 0 <= dst < n and 0 <= src < n
                 and dst != src, "invalid operation")
            values[dst] += values[src]
        columns.append(values)
    return [list(row) for row in zip(*columns)]


def dominated(new, old):
    return all(x <= y for a, b in zip(new, old) for x, y in zip(a, b))


def factor_minimum(target):
    """Independent exhaustive subset sums and backward Bellman recursion.

    Base-16 digits encode exact nonnegative integer vectors. At most 11 binary
    donors are added, so carries cannot occur. This does not use the discovery
    program's disjoint-mask cover DP or its forward shortest-path tables.
    """
    need(all(x in (0, 1) for row in target for x in row), "non-binary factor")
    need(all(target[i][i] == 1 for i in range(N)), "factor diagonal")
    packed = [sum(x << (4*j) for j, x in enumerate(row)) for row in target]
    infinity = 10**9
    dist = [infinity] * (1 << N)
    dist[-1] = 0
    feasible = 0
    for done in range((1 << N) - 2, -1, -1):
        for dst in range(N):
            if done >> dst & 1:
                continue
            wanted = packed[dst] - (1 << (4*dst))
            sums = [(0, 0)]
            for src in range(N):
                if src == dst:
                    continue
                value = packed[src] if done >> src & 1 else (1 << (4*src))
                if any(((value >> (4*j)) & 15) > ((wanted >> (4*j)) & 15) for j in range(N)):
                    continue
                sums += [(s + value, cost + 1) for s, cost in sums]
            costs = [cost for total, cost in sums if total == wanted]
            if costs:
                feasible += 1
                nxt = done | (1 << dst)
                dist[done] = min(dist[done], min(costs) + dist[nxt])
    return {"minimum": dist[0], "states": len(dist), "state_destination_pairs": N*(1 << (N-1)),
            "feasible_edges": feasible, "backward_distances_sha256": digest(dist)}


def bind(word, recipe):
    need(recipe["source"] == WORD and recipe["section"] == "B" and recipe["block"] == 4,
         "wrong source/block")
    need(type(recipe["frame"]) is int and recipe["frame"] == 520
         and recipe["slice"] == [242, 283] and recipe["registers"] == REGISTERS, "wrong binding")
    old = word["B"][242:283]
    need(len(old) == 41 and all(f == 520 and len(ss) == 1 for f, t, ss in old), "source block")
    original = [[REGISTERS.index(t), REGISTERS.index(ss[0])] for f, t, ss in old]
    new = recipe["operations"]
    need(len(new) == 31, "candidate addition count")
    need(matrix(new) == matrix(original), "forward integer map")
    need(dominated(matrix(new[::-1]), matrix(original[::-1])), "reverse positive map")
    need(recipe["reverse_dominated"] is True, "reverse metadata")
    need(recipe["original_split"] == 20 and recipe["candidate_split"] == 17, "factor split")
    for i, (a, b) in enumerate(((original[:20], new[:17]), (original[20:], new[17:]))):
        need(matrix(a) == matrix(b), "factor map")
        rows = [sum(x << j for j, x in enumerate(row)) for row in matrix(a)]
        need(rows == recipe["factor_certificates"][i]["target_rows"], "factor target binding")
    result = copy.deepcopy(word)
    result["B"][242:283] = [[520, REGISTERS[d], [REGISTERS[s]]] for d, s in new]
    full = next(i for i, f in enumerate(word["frames"]) if len(f) == word["v"])
    result["C"] = [[full, t, list(ss)] for f, t, ss in reversed(result["A"] + result["B"])
                   if not word["v"] <= t < 2*word["v"]]
    return result, original


def records(word, geometry):
    """Independent literal MOVE/ADD/COPY/ERASE emission, with rational nesting."""
    n, v = 2*word["v"] + word["R"], word["v"]
    current = list(word["start"])
    paths = [[f] for f in current]
    result = []
    def move(r, frame):
        if current[r] != frame:
            need(geometry.nested(current[r], frame), "illegal frame descent")
            rank = geometry.fdim[frame] - geometry.fdim[current[r]]
            need(rank > 0, "non-increasing frame")
            result.append((0, r, current[r], frame, rank, 0))
            current[r] = frame
            paths[r].append(frame)
    def gates(section, phase):
        for frame, dst, sources in word[section]:
            need(len({dst, *sources}) == 1+len(sources), "duplicate operand")
            for r in [dst, *sources]:
                move(r, frame)
            result.extend((1, dst, src, 1, frame, phase) for src in sources)
    gates("D", 1)
    gates("A", 2)
    for k, center in enumerate(word["ret"]):
        frame = current[center]
        result.append((2, center, n, frame, 0, geometry.fdim[frame]))
        result.extend((1, v+t, n, 1, 0, 3) for t, row in enumerate(word["scatter"]) if k in row)
        result.append((3, center, n, frame, 0, 0))
    gates("B", 4)
    gates("C", 5)
    for r, frame in enumerate(word["final"]):
        move(r, frame)
    return result, paths


def replay(stream, v, helpers, reverse=False, positive=False):
    n = 2*v + helpers
    values = [1]*n + [0] if positive else [1 << i for i in range(n)] + [0]
    largest, center = 1, None
    for kind, a, b, c, frame, phase in (reversed(stream) if reverse else stream):
        if kind == 0:
            continue
        if reverse and kind in (2, 3):
            kind = 5-kind
        if kind == 1:
            need(a != n and a != center and (b != n or center is not None), "copy source/lifecycle")
            if positive:
                values[a] += abs(c)*values[b]
                largest = max(largest, values[a])
            elif c & 1:
                values[a] ^= values[b]
        elif kind == 2:
            need(center is None and b == n, "nested copy")
            center, values[n] = a, values[a]
        elif kind == 3:
            need(center == a and b == n, "unmatched erase")
            if not positive:
                need(values[n] == values[a], "changed copied center")
            center, values[n] = None, 0
        else:
            raise ValueError("unknown record")
    need(center is None, "unclosed copy")
    if not positive:
        expected = [(1 << r) ^ ((1 << (r-v)) if v <= r < 2*v else 0) for r in range(n)] + [0]
        need(values == expected, "all-column endpoint")
    return largest


def audit(word, checker, geometry):
    scalar = checker.Word(word)
    scalar.full()
    hypotheses, conclusions, _ = scalar.interface()
    need(all(hypotheses.values()) and all(conclusions.values()), "literal interface")
    stream, paths = records(word, geometry)
    for reverse in (False, True):
        replay(stream, word["v"], word["R"], reverse)
    forward = replay(stream, word["v"], word["R"], positive=True)
    backward = replay(stream, word["v"], word["R"], reverse=True, positive=True)
    profile = Counter(e[4] for e in stream if e[0] == 0)
    profile.update(e[5] for e in stream if e[0] == 2)
    payload = 64*forward**3*backward**2
    need(payload < 1 << 104, "local payload cap")
    report = {"columns": 2*word["v"]+word["R"], "helpers": word["R"],
              "additions": sum(e[0] == 1 for e in stream), "records": len(stream),
              "copies": sum(e[0] == 2 for e in stream), "erasures": sum(e[0] == 3 for e in stream),
              "paid_profile": dict(sorted(profile.items())), "rank_mass": sum(k*v for k, v in profile.items()),
              "positive_prefix": {"forward": forward, "reverse": backward},
              "payload_upper": str(payload), "payload_bits": payload.bit_length(),
              "paths_sha256": digest(paths), "hypotheses": hypotheses, "conclusions": conclusions,
              "canonical_word_sha256": digest(word)}
    return report, stream, paths


def controls(word, recipe, changed, checker, geometry):
    rejected = []
    def reject(name, call):
        try:
            call()
        except (ValueError, checker.Reject):
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    for name, edit in (
        ("dropped_gate", lambda r: r["operations"].pop()),
        ("self_addition", lambda r: r["operations"].__setitem__(0, [0, 0])),
        ("boolean_index", lambda r: r["operations"].__setitem__(0, [True, 0])),
        ("wrong_frame", lambda r: r.__setitem__("frame", 519)),
        ("wrong_register_binding", lambda r: r["registers"].reverse()),
        ("wrong_factor_split", lambda r: r.__setitem__("candidate_split", 16)),
        ("unpriced_F2_identity_pair", lambda r: r["operations"].extend([[0, 1], [0, 1]])),
        ("changed_operand", lambda r: r["operations"].__setitem__(0, [10, 1])),
    ):
        mutant = copy.deepcopy(recipe)
        edit(mutant)
        reject(name, lambda: bind(word, mutant))
    stale = copy.deepcopy(changed)
    stale["C"] = word["C"]
    # F2 endpoint equality alone cannot detect this violation of the literal H4 contract.
    checker.Word(stale).full()
    reject("stale_cleanup_passes_F2_but_fails_H4", lambda: audit(stale, checker, geometry))
    missing = copy.deepcopy(changed)
    missing["C"].pop()
    reject("missing_cleanup", lambda: audit(missing, checker, geometry))
    descent = copy.deepcopy(changed)
    descent["C"][0][0] = 0
    reject("frame_descent", lambda: audit(descent, checker, geometry))
    stream, _ = records(changed, geometry)
    erase_index = next(j for j, q in enumerate(stream) if q[0] == 3)
    no_erase = [e for i, e in enumerate(stream) if i != erase_index]
    reject("missing_erase", lambda: replay(no_erase, word["v"], word["R"]))
    better = [[1, 2], [0, 1]]
    worse = [[0, 1], [0, 2], [1, 2]]
    need(matrix(better, 3) == matrix(worse, 3), "reverse control calibration")
    reject("equal_forward_worse_reverse", lambda: need(dominated(matrix(worse[::-1], 3), matrix(better[::-1], 3)), "reverse cost"))
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    manifest = pins()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    recipe = json.loads((HERE / "CANDIDATE.json").read_text())
    changed, original = bind(word, recipe)
    factors = [factor_minimum(matrix(x)) for x in (original[:20], original[20:])]
    need([f["minimum"] for f in factors] == [17, 14], "factor minima")
    for computed, claimed in zip(factors, recipe["factor_certificates"]):
        need(all(computed[k] == claimed[k] for k in ("minimum", "states", "feasible_edges")), "search coverage")
    spec = importlib.util.spec_from_file_location("owning_xcheck", ROOT / CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    geometry = checker.Word(word)
    labels = geometry.labels()
    before, old_stream, old_paths = audit(word, checker, geometry)
    after, new_stream, new_paths = audit(changed, checker, geometry)
    need(old_paths == new_paths, "register paths changed")
    need(before["paid_profile"] == after["paid_profile"] and before["rank_mass"] == 5129, "paid profile")
    need(before["additions"] == 24305 and after["additions"] == 24285, "complete scalar cost")
    need(before["copies"] == after["copies"] == before["erasures"] == after["erasures"] == 9, "copy count")
    negative_controls = controls(word, recipe, changed, checker, geometry)
    report = {"status": "PASS_R439_BLOCK4_SCHEDULE", "base_commit": manifest["base_commit"],
              "source_sha256": manifest["files"][WORD], "recipe_sha256": digest(recipe),
              "factor_minima": factors, "forward_integer_matrix": matrix(original),
              "original_reverse_positive_matrix": matrix(original[::-1]),
              "candidate_reverse_positive_matrix": matrix(recipe["operations"][::-1]),
              "labels": labels, "before": before, "after": after, "negative_controls": negative_controls,
              "kappa": "not recomputed; no new exponent claimed"}
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    certificate = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        certificate.write_bytes(encoded.encode("utf-8"))
    else:
        need(json.loads(certificate.read_text()) == json.loads(encoded), "stored certificate mismatch")
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "candidate.json.gz").write_bytes(gzip.compress(canonical(changed), mtime=0))
        for label, stream in (("before", old_stream), ("after", new_stream)):
            (args.out / (label + ".bin")).write_bytes(b"".join(struct.pack("<6i", *e) for e in stream))
        (args.out / "result.json").write_bytes(encoded.encode("utf-8"))
    print(f"PASS_R439_BLOCK4_SCHEDULE gates=41->31 ADDs=24305->24285 columns=661 "
          f"factor_minima=17+14 controls={len(negative_controls)} rank_mass=5129 kappa=not_recomputed")


if __name__ == "__main__":
    main()
