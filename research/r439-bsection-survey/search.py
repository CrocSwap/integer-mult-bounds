#!/usr/bin/env python3
"""Discovery search for whole-block programs on the ten phase-B blocks of
PR589's tuned punctured R439 word, covering the six unclaimed blocks and four
cross-checks against the blocks changed by open PRs.

Class (the whole-block single-write class of open PR #873, Gautam Gupta's
fixed-factor framing in #844 and #857's factorization search): each register's
final integer row is realized once, in some realization order, as its entry
singleton plus a subset of donors, where each donor is either the completed
final row of a register realized earlier or the entry singleton of a register
realized later, and each donor is used at most once per row.  The number of
additions of a row is its donor count.  The search is a dynamic program over
realized-register subsets with meet-in-the-middle subset sums.  For blocks no
program in the class realizes, a per-row donor-supply obstruction is reported
when one exists.

No optimality outside this class is claimed: programs that consume a register
mid-construction (multi-write interleavings) are not searched here.

Writes CANDIDATES.json and CERTIFICATE.json.  Deterministic; no randomness;
standard library only.  Prepared with help from opencode.  Apache-2.0.
"""
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"

# The ten phase-B blocks of the tuned word: frame, first B index, last B index
# (inclusive).  Frames 506/507/519/521/522/524 are unclaimed; frames 508, 509,
# 520 and 523 are cross-checks against the objects of open PRs #873, #843,
# #844 and #857.  Only 506 and 523 are spliced into the verified word.
BLOCKS = [
    (506, 102, 127),
    (507, 128, 162),
    (519, 163, 204),
    (508, 205, 241),
    (520, 242, 282),
    (509, 283, 313),
    (521, 314, 360),
    (522, 361, 403),
    (523, 404, 448),
    (524, 449, 489),
]
SPLICED = {506, 523}


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


def block_model(blk):
    regs = sorted({t for _, t, _ in blk} | {s for _, _, ss in blk for s in ss})
    index = {r: i for i, r in enumerate(regs)}
    n = len(regs)
    ops = [(index[t], index[s[0]]) for _, t, s in blk]
    forward = [[int(i == j) for j in range(n)] for i in range(n)]
    for t, s in ops:
        for j in range(n):
            forward[t][j] += forward[s][j]
    return regs, ops, forward


def subset_min(donors, goal):
    """Minimum donor count whose values sum to goal exactly (each donor at
    most once); None when unreachable.  Meet in the middle."""
    k = len(donors)
    half = k // 2
    first, second = donors[:half], donors[half:]

    def sums(part):
        zero = tuple(0 for _ in goal)
        table = {zero: 0}
        for value in part:
            for total, count in list(table.items()):
                merged = tuple(a + b for a, b in zip(total, value))
                if all(a <= b for a, b in zip(merged, goal)):
                    if merged not in table or count + 1 < table[merged]:
                        table[merged] = count + 1
        return table

    left, right = sums(first), sums(second)
    best = None
    for total, count in left.items():
        rest = tuple(b - a for a, b in zip(total, goal))
        if rest in right:
            cost = count + right[rest]
            if best is None or cost < best:
                best = cost
    return best


def search(forward):
    """Minimum donor-addition count and an attaining realization; also the
    dynamic-program statistics for the record."""
    n = len(forward)
    goal = []
    for i in range(n):
        row = list(forward[i])
        row[i] -= 1
        if min(row) < 0:
            return None
        goal.append(tuple(row))
    infinity = 10 ** 9
    size = 1 << n
    dist = [infinity] * size
    parent = [None] * size
    dist[0] = 0
    edges = 0
    for mask in range(size):
        if dist[mask] >= infinity:
            continue
        for dst in range(n):
            if mask >> dst & 1:
                continue
            donors = []
            for src in range(n):
                if src == dst:
                    continue
                value = tuple(forward[src]) if mask >> src & 1 else tuple(int(j == src) for j in range(n))
                if all(a <= b for a, b in zip(value, goal[dst])):
                    donors.append((src, value))
            best = subset_min([v for _, v in donors], goal[dst])
            if best is None:
                continue
            edges += 1
            nxt = mask | (1 << dst)
            if dist[mask] + best < dist[nxt]:
                dist[nxt] = dist[mask] + best
                parent[nxt] = (mask, dst)
    if dist[size - 1] >= infinity:
        return None
    # Reconstruct the realization order and the donor subset of each row.
    chain = []
    mask = size - 1
    while mask:
        prev, dst = parent[mask]
        chain.append(dst)
        mask = prev
    chain.reverse()
    donors_of = {}
    for step, dst in enumerate(chain):
        mask = sum(1 << r for r in chain[:step])
        goal_row = goal[dst]
        candidates = []
        for src in range(n):
            if src == dst:
                continue
            value = tuple(forward[src]) if mask >> src & 1 else tuple(int(j == src) for j in range(n))
            if all(a <= b for a, b in zip(value, goal_row)):
                candidates.append((src, value))
        chosen = recover(candidates, goal_row)
        donors_of[dst] = chosen
    gates = [(dst, src) for dst in chain for src in donors_of[dst]]
    return {
        "minimum": dist[size - 1],
        "realization_order": chain,
        "donors": {str(k): v for k, v in donors_of.items()},
        "gates": gates,
        "states": size,
        "state_destination_pairs": n * (1 << (n - 1)),
        "feasible_edges": edges,
        "distances_sha256": digest(dist),
    }


def recover(candidates, goal):
    """One minimum donor subset summing to goal (same recursion as
    subset_min, with the chosen subset returned)."""
    k = len(candidates)
    half = k // 2
    first, second = candidates[:half], candidates[half:]

    def sums(part):
        zero = tuple(0 for _ in goal)
        table = {zero: (0, [])}
        for idx, (src, value) in enumerate(part):
            for total, (count, chosen) in list(table.items()):
                merged = tuple(a + b for a, b in zip(total, value))
                if all(a <= b for a, b in zip(merged, goal)):
                    if merged not in table or count + 1 < table[merged][0]:
                        table[merged] = (count + 1, chosen + [src])
        return table

    left, right = sums(first), sums(second)
    best = None
    for total, (count, chosen) in left.items():
        rest = tuple(b - a for a, b in zip(total, goal))
        if rest in right:
            cost = count + right[rest][0]
            if best is None or cost < best[0]:
                best = (cost, chosen + right[rest][1])
    assert best is not None
    return sorted(best[1])


def supply_witness(forward):
    """First per-row donor-supply obstruction, or None.

    A donor of row i is an entry singleton or a completed final row and must
    fit the row's goal entrywise.  Summing every fitting donor (including
    mutually exclusive singleton/row pairs) over-approximates the achievable
    column supply, so a column whose demand exceeds it certifies that no
    program in the class realizes the row, independent of realization order.
    """
    n = len(forward)
    for i in range(n):
        goal = [forward[i][j] - (1 if j == i else 0) for j in range(n)]
        supply = [0] * n
        for k in range(n):
            if k == i:
                continue
            for value in ([1 if j == k else 0 for j in range(n)], list(forward[k])):
                if all(a <= b for a, b in zip(value, goal)):
                    for j in range(n):
                        supply[j] += value[j]
        for j in range(n):
            if goal[j] > supply[j]:
                return {"row": i, "col": j, "demand": goal[j], "supply": supply[j]}
    return None


def main():
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    out = {"source": WORD,
           "source_content_sha256": digest(json.loads(gzip.decompress((ROOT / WORD).read_bytes()))),
           "blocks": []}
    certificate = {
        "schema": "r439-bsection-survey/1",
        "base_commit": "f567884aeb8851b6e794af1184119a3bfbe1e631",
        "source_sha256": {
            WORD: hashlib.sha256((ROOT / WORD).read_bytes()).hexdigest(),
            "research/e8-bit-p111-tuned/code/xcheck_p.py":
                hashlib.sha256((ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py").read_bytes()).hexdigest(),
            "research/e8-bit-carrier-skeleton/code/bit/export_records.py":
                hashlib.sha256((ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py").read_bytes()).hexdigest(),
        },
        "blocks": [],
    }
    for frame, first, last in BLOCKS:
        blk = word["B"][first:last + 1]
        assert all(f == frame and len(ss) == 1 for f, t, ss in blk), (frame, first, last)
        regs, ops, forward = block_model(blk)
        found = search(forward)
        witness = supply_witness(forward) if found is None else None
        entry = {
            "frame": frame,
            "slice": [first, last + 1],
            "registers": regs,
            "original_gates": len(ops),
            "forward_sha256": digest(forward),
            "diagonal": [forward[i][i] for i in range(len(regs))],
        }
        cert = {"section": "B", "frame": frame, "slice": [first, last + 1],
                "registers": regs, "original_gates": len(ops), "spliced": False}
        if found is None:
            entry["class_covered"] = False
            entry["supply_witness"] = witness
            cert["status"] = "infeasible"
            cert["witness"] = witness
        else:
            touched = sorted({regs[t] for t, _ in found["gates"]} | {regs[s] for _, s in found["gates"]})
            entry.update({
                "class_covered": True,
                "minimum": found["minimum"],
                "saving": len(ops) - found["minimum"],
                "candidate_gates": [[frame, regs[t], [regs[s]]] for t, s in found["gates"]],
                "local_gates": found["gates"],
                "realization_order": [regs[i] for i in found["realization_order"]],
                "donors": {str(regs[int(k)]): [regs[i] for i in v] for k, v in found["donors"].items()},
                "touched_registers": touched,
                "all_registers_touched": touched == regs,
                "states": found["states"],
                "state_destination_pairs": found["state_destination_pairs"],
                "feasible_edges": found["feasible_edges"],
                "distances_sha256": found["distances_sha256"],
            })
            cert["status"] = "class-minimum"
            cert["minimum"] = found["minimum"]
            if frame in SPLICED:
                assert touched == regs, ("spliced block breaks frame paths", frame)
                cert["spliced"] = True
                cert["gates"] = entry["candidate_gates"]
        out["blocks"].append(entry)
        certificate["blocks"].append(cert)
        print(frame, entry.get("original_gates"), "->", entry.get("minimum"),
              "witness:", witness)
    (HERE / "CANDIDATES.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    (HERE / "CERTIFICATE.json").write_text(json.dumps(certificate, indent=1) + "\n", encoding="utf-8")
    total = sum(b["original_gates"] - b["minimum"] for b in certificate["blocks"] if b["spliced"])
    print("spliced frames:", sorted(SPLICED), "forward gates saved:", total,
          "-> full word ADDs", 24305 - 2 * total, "(forward + literal reverse cleanup)")


if __name__ == "__main__":
    main()
