# SPDX-License-Identifier: Apache-2.0
"""Bind PR3190's literal idle-axis moves to PR3187's exact eight-stream operator replay.

The operator model, fill authentication and data-event semantics are imported
unchanged from research/rank7-idle-star-stream-obstruction (Nick Petalas/PR3187).
This module adds only: per-port projection of the authenticated fill for owner
replica 0, hosted-remainder residuals, PR3190's declared per-axis rule, and the
before/after comparison.  It is not an independent reimplementation of PR3187.
"""
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "rank7-idle-star-stream-obstruction"))
import algebra as A  # noqa: E402
import source as S  # noqa: E402

MOVES_SHA = "c76310bc9bdb7e693bdb8910e7ea084354251110a02ee629e3e8aad7418b695f"
AXIS72 = 1 << 72


def load_moves():
    raw = S.read_bytes(HERE / "vendor" / "PR3190-MOVES.json.gz")
    S.require(hashlib.sha256(raw).hexdigest() == MOVES_SHA, "PR3190 MOVES pin")
    data = S.decode(raw)
    S.require(data["columns"] == ["replica", "port", "donor_child", "receiver_child", "axis"], "MOVES columns")
    S.require(len(data["moves"]) == 391964, "PR3190 move count")
    by_port = defaultdict(list)
    for replica, port, donor, receiver, axis in data["moves"]:
        if replica == 0:
            by_port[port].append((donor, receiver, int(axis)))
    return by_port


def contexts():
    ctx0 = S.load_context()  # authenticates PR3187's inputs and the complete PR3148 fill
    vendor = S.PACKAGE / "vendor"
    base = S.decode(S.read_bytes(vendor / "BASE-FILL.json.gz"))["rows"]
    edits = S.journal_edits(base, S.decode(S.read_bytes(vendor / "EXCHANGE.json")))
    rows = defaultdict(list)
    for index in range(S.TOTAL_ROWS):
        row = edits[index] if index in edits else S.lifted_row(base, index)
        if row[2] == 0:
            rows[row[4]].append(row)
    S.require(rows[0] == ctx0["rows"], "port-0 projection equals PR3187's authenticated projection")
    recipes = S.decode(S.read_bytes(S.ROOT / S.PHASES))["recipes"]
    S.require(len(recipes) == 112 and all(r["port"] == p for p, r in enumerate(recipes)), "per-port recipes")
    return ctx0, rows, recipes


def residual_and_hosts(ctx):
    used, hosts = defaultdict(set), defaultdict(list)
    for time, helper, owner, child, port, offset in ctx["rows"]:
        stage, replica = ctx["order"][time]
        width = ctx["providers"][ctx["dispatch"][stage, replica % 74]]["widths"][helper]
        axes = list(map(int, ctx["recipe"]["idle_children"][child]["orthogonal_axes"]))
        positions = set(range(offset, offset + width))
        S.require(offset >= 0 and offset + width <= len(axes) and not used[child] & positions, "hosted slice")
        used[child] |= positions
        stream = 2 * ctx["plan"]["pairs"][str(child)] + ctx["plan"]["sides"][str(child)]
        hosts[time].append((stream, axes[offset:offset + width]))
    residual = {}
    for child, entry in enumerate(ctx["recipe"]["idle_children"]):
        S.require(used[child] == set(range(len(used[child]))), "compact hosted prefix")
        residual[child] = [int(v) for i, v in enumerate(entry["orthogonal_axes"]) if i not in used[child]]
    return residual, hosts


def replay(ctx, blocks, hosts, residual, character):
    matrix = A.identity()
    for time, (stage, replica) in enumerate(ctx["order"]):
        for stream, axes in hosts.get(time, ()):
            A.phase(matrix, stream, sum(A.dot(character, v) for v in axes))
        if replica == 0:
            for event in blocks[stage]:
                A.data_event(matrix, event, ctx, residual, character)
    return matrix


def declared_rule(recipe, current, donor, receiver, axis):
    """PR3190's stated per-axis conditions, applied at the time the axis moves."""
    translations = [int(s[k]) for s in recipe["stage_alignment"] for k in ("entry_X", "exit_X", "entry_Y", "exit_Y")]
    translations.append(int(recipe["terminal_Y_translation"]))
    terminal = [int(recipe["idle_children"][c]["translation_after"]) for c in (donor, receiver)]
    return (axis in current[donor] and donor != receiver
            and all(A.dot(axis, v) == 0 for v in current[receiver] + translations + terminal))


def apply_moves(recipe, residual, moves):
    final = {c: list(v) for c, v in residual.items()}
    for donor, receiver, axis in moves:
        S.require(declared_rule(recipe, final, donor, receiver, axis), "PR3190 declared rule")
        final[donor].remove(axis)
        final[receiver].append(axis)
    S.require(all(len(v) <= 51 for v in final.values()), "rank cap 51")
    S.require(all(A.dot(v, w) == int(i == j) for axes in final.values()
                  for i, v in enumerate(axes) for j, w in enumerate(axes)), "orthonormal final axes")
    return final


def diff(left, right):
    return [[i, j, list(left[i][j]), list(right[i][j])] for i in range(8) for j in range(8) if left[i][j] != right[i][j]]


def scalar(character):
    return [[A.rotate((1, 0), character.bit_count()) if i == j else (0, 0) for j in range(8)] for i in range(8)]


def port_result(ctx, blocks, moves):
    residual, hosts = residual_and_hosts(ctx)
    final = apply_moves(ctx["recipe"], residual, moves)
    full = [len(e["orthogonal_axes"]) for e in ctx["recipe"]["idle_children"]]
    changed = []
    for character in sorted({axis for _, _, axis in moves}):
        before = replay(ctx, blocks, hosts, residual, character)
        after = replay(ctx, blocks, hosts, final, character)
        S.require(before == scalar(character), "baseline equals the scalar operator")
        changed.append([character.bit_length() - 1, len(diff(before, after))])
    hosted = sorted({d for d, _, _ in moves if len(residual[d]) < full[d]})
    return dict(moves=len(moves), hosted_remainder_donors=hosted, changed=changed), residual, hosts
