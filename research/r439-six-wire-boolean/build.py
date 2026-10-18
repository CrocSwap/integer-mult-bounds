#!/usr/bin/env python3
"""Bounded complete-block Boolean Gaussian nominations. Apache-2.0.

Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance.
Search results are constructions, not minimum-length certificates.
"""
import argparse
import copy
import gzip
import itertools
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need = C["need"]
SEED = 19


def blocks(word):
    offset = 0
    out = []
    for frame, group in itertools.groupby(word["A"], key=lambda x: x[0]):
        gates = list(group)
        if 266 <= frame <= 325:
            wires = sorted({x for _, d, ss in gates for x in [d, *ss]})
            need(len(wires) == 6, "six-wire block domain")
            lookup = {w: i for i, w in enumerate(wires)}
            ops = [(lookup[d], lookup[s]) for _, d, ss in gates for s in ss]
            out.append((frame, offset, offset + len(gates), wires, ops))
        offset += len(gates)
    need(len(out) == 60, "sixty complete blocks")
    return out


def binary(ops):
    rows = [1 << i for i in range(6)]
    for d, s in ops:
        rows[d] ^= rows[s]
    return tuple(rows)


def positive(ops):
    rows = [[int(i == j) for j in range(6)] for i in range(6)]
    for d, s in ops:
        rows[d] = [x + y for x, y in zip(rows[d], rows[s])]
    return rows


def nominate(target, order, mode, priority):
    rows = list(target)
    left, right = [], []

    def row(d, s):
        rows[d] ^= rows[s]
        left.append((d, s))

    def column(d, s):
        # Right multiplication by elementary matrix E[d,s]: col_s += col_d.
        for i in range(6):
            if (rows[i] >> d) & 1:
                rows[i] ^= 1 << s
        right.append((d, s))

    remaining = set(range(6))
    for p in order:
        if not ((rows[p] >> p) & 1):
            donor = next(j for j in priority if j in remaining and (rows[j] >> p) & 1)
            row(p, donor)
        for i in priority:
            if i != p and (rows[i] >> p) & 1:
                row(i, p)
        if mode == "mixed":
            for j in priority:
                if j != p and (rows[p] >> j) & 1:
                    column(p, j)
        remaining.remove(p)
    need(rows == [1 << i for i in range(6)], "elimination did not reach identity")
    # I = L M R, hence M = L^-1 R^-1. Gates execute right factor first.
    result = tuple(right + left[::-1])
    need(binary(result) == target, "elimination word order")
    return result


def dominates(old_positive, new_positive):
    return all(b <= a for ra, rb in zip(old_positive, new_positive) for a, b in zip(ra, rb))


def build(parent):
    orders = list(itertools.permutations(range(6)))
    priority = list(range(6))
    priority = priority[SEED % 6:] + priority[:SEED % 6]
    priorities = [priority, priority[::-1]]
    certificate = {
        "format": "r439-six-wire-boolean/1", "seed": SEED,
        "parent_sha256": C["digest"](parent), "blocks": [],
        "domain": {"blocks": 60, "pivot_orders": 720, "modes": ["row", "mixed"],
                   "donor_priorities": priorities, "trials_per_block": 2880},
    }
    replacements = {}
    for frame, start, end, wires, old in blocks(parent):
        target = binary(old)
        old_pos = [positive(old), positive(old[::-1])]
        seen = set()
        admissible = []
        trials = shorter = guarded = 0
        for mode in ("row", "mixed"):
            for donor_order in priorities:
                for order in orders:
                    program = nominate(target, order, mode, donor_order)
                    trials += 1
                    if program in seen:
                        continue
                    seen.add(program)
                    if len(program) >= len(old):
                        continue
                    shorter += 1
                    if all(dominates(old_pos[k], positive(program[::-1] if k else program))
                           for k in range(2)):
                        guarded += 1
                        admissible.append((len(program), program, mode, order, donor_order))
        best = min(admissible) if admissible else None
        item = {"frame": frame, "start": start, "end": end, "wires": wires,
                "old": old, "trials": trials, "distinct_programs": len(seen),
                "shorter_programs": shorter, "guarded_programs": guarded}
        if best:
            length, program, mode, order, donor_order = best
            item.update({"new": program, "saved_A": len(old) - length,
                         "nomination": {"mode": mode, "order": order, "priority": donor_order}})
            replacements[start] = (end, [[frame, wires[d], [wires[s]]] for d, s in program])
        else:
            item.update({"new": None, "saved_A": 0, "nomination": None})
        certificate["blocks"].append(item)
        print(f"frame={frame} old={len(old)} new={len(best[1]) if best else len(old)} "
              f"shorter={shorter} guarded={guarded}", flush=True)
    candidate = copy.deepcopy(parent)
    result, i = [], 0
    while i < len(parent["A"]):
        if i in replacements:
            end, gates = replacements[i]
            result.extend(gates)
            i = end
        else:
            result.append(parent["A"][i])
            i += 1
    candidate["A"] = result
    v = parent["v"]
    z_ops = [g for phase in ("A", "B") for g in candidate[phase] if not v <= g[1] < 2 * v]
    candidate["C"] = [[1, d, list(ss)] for _, d, ss in z_ops[::-1]]
    certificate["candidate_sha256"] = C["digest"](candidate)
    certificate["summary"] = {"trials": sum(r["trials"] for r in certificate["blocks"]),
                              "selected": len(replacements),
                              "saved_A": sum(r["saved_A"] for r in certificate["blocks"])}
    return candidate, certificate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    parent = C["load"](C["HERE"] / "vendor/pr936/candidate.json.gz")
    candidate, certificate = build(parent)
    C["write"](args.out / "CERTIFICATE.json", certificate)
    (args.out / "candidate.json.gz").write_bytes(gzip.compress(C["canonical"](candidate), mtime=0))
    print(certificate["summary"])


if __name__ == "__main__":
    main()
