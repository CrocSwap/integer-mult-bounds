#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Census of every single-axis idle-remainder transfer at owner replica 0.

For each port, each hosted child with a nonempty remainder (donor), each other
idle child (receiver) and each remainder axis that passes PR3190's declared rule,
replay the exact operator at the moved-axis character.  A transfer is rejected
when the operator changes there; survivors would still need every other
character.  Compares with CENSUS.json (--write regenerates it).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import obstruction as O


def main():
    ctx0, rows, recipes = O.contexts()
    blocks = O.A.stage_blocks(ctx0["template"])
    write = "--write" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--write"]
    lo, hi = (int(args[0]), int(args[1])) if len(args) == 2 else (0, 112)
    ports = {}
    total = Counter()
    survivors = []
    for p in range(lo, hi):
        ctx = dict(ctx0, rows=rows[p], recipe=recipes[p])
        residual, hosts = O.residual_and_hosts(ctx)
        full = [len(e["orthogonal_axes"]) for e in ctx["recipe"]["idle_children"]]
        baseline = {}
        stats = Counter()
        for donor, axes in residual.items():
            if not axes or len(axes) == full[donor]:
                continue  # unhosted children are PR3204's domain
            for receiver in residual:
                if receiver == donor or full[receiver] == 0:
                    continue
                for axis in axes:
                    if not O.declared_rule(ctx["recipe"], residual, donor, receiver, axis):
                        stats["rule_rejects"] += 1
                        continue
                    try:
                        final = O.apply_moves(ctx["recipe"], residual, [(donor, receiver, axis)])
                    except ValueError:
                        stats["cap_or_frame_rejects"] += 1
                        continue
                    if axis not in baseline:
                        baseline[axis] = O.replay(ctx, blocks, hosts, residual, axis)
                        O.S.require(baseline[axis] == O.scalar(axis), "scalar baseline")
                    after = O.replay(ctx, blocks, hosts, final, axis)
                    if after == baseline[axis]:
                        stats["preserved_at_axis_character"] += 1
                        survivors.append([p, donor, receiver, axis.bit_length() - 1])
                    else:
                        stats["operator_changed"] += 1
        total.update(stats)
        ports[str(p)] = dict(stats)
    result = {"ports": ports, "summary": dict(total), "survivors": survivors}
    O.S.require(not survivors, "a remainder transfer preserved the operator at its axis character")
    path = Path(__file__).resolve().parent / "CENSUS.json"
    if (lo, hi) == (0, 112):
        if write:
            path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        else:
            O.S.require(json.loads(path.read_text(encoding="utf-8")) == json.loads(json.dumps(result)), "stored CENSUS.json")
    print("PASS_REMAINDER_TRANSFER_CENSUS ports=%d rule_passing=%d changed=%d survivors=0" % (
        hi - lo, total["operator_changed"], total["operator_changed"]))


if __name__ == "__main__":
    main()
