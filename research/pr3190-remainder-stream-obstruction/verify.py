#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reject PR3190's literal remainder moves with PR3187's exact physical-stream replay.

Default: the port-0 witness, each move isolated, and controls.
--all-ports: all 112 ports of owner replica 0 (about 10 minutes).
--write: regenerate RESULT.json instead of comparing with it.
"""
import argparse
import json
from pathlib import Path

import obstruction as O

HERE = Path(__file__).resolve().parent


def witness(ctx, blocks, moves):
    O.S.require(moves == [(14, 8, O.AXIS72), (15, 10, O.AXIS72)], "literal PR3190 port-0 moves")
    summary, residual, hosts = O.port_result(ctx, blocks, moves)
    O.S.require(residual[14] == residual[15] == [O.AXIS72], "rank-1 hosted remainders")
    before = O.replay(ctx, blocks, hosts, residual, O.AXIS72)
    isolated = {}
    for move in moves:
        key = "%d->%d" % move[:2]
        after = O.replay(ctx, blocks, hosts, O.apply_moves(ctx["recipe"], residual, [move]), O.AXIS72)
        isolated[key] = O.diff(before, after)
        O.S.require(isolated[key], "each move alone changes the operator")
    joint = O.diff(before, O.replay(ctx, blocks, hosts, O.apply_moves(ctx["recipe"], residual, moves), O.AXIS72))
    O.S.require(sorted(joint) == sorted(isolated["14->8"] + isolated["15->10"]), "disjoint isolated changes")
    controls = {}
    for label, bad in (("axis_not_in_donor_remainder", [(14, 8, 1 << 71)]), ("self_move", [(14, 14, O.AXIS72)])):
        try:
            O.apply_moves(ctx["recipe"], residual, bad)
        except ValueError as error:
            controls[label] = "rejected: " + str(error)
        else:
            raise AssertionError("control accepted: " + label)
    O.S.require(O.replay(ctx, blocks, hosts, O.apply_moves(ctx["recipe"], residual, []), O.AXIS72) == before,
                "empty overlay preserves the operator")
    controls["empty_overlay_preserves_operator"] = "PASS"
    return dict(summary=summary, character_bit=72, donor_streams=[2, 3], receiver_streams=[6, 7],
                isolated_differences=isolated, joint_differences=joint, controls=controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-ports", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    moves = O.load_moves()
    ctx0, rows, recipes = O.contexts()
    blocks = O.A.stage_blocks(ctx0["template"])

    def port(p):
        return dict(ctx0, rows=rows[p], recipe=recipes[p])

    got = {"status": "PASS_PR3190_REMAINDER_STREAM_COUNTEREXAMPLE", "admitted": False,
           "selected_frontier_changed": False, "port0_witness": witness(port(0), blocks, moves[0])}
    if args.all_ports or args.write:
        ports = {str(p): O.port_result(port(p), blocks, moves[p])[0] for p in range(112)}
        O.S.require(all(v["changed"] and all(n > 0 for _, n in v["changed"]) for v in ports.values()), "every port changes")
        got["owner_replica0_ports"] = ports
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(got, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    want = json.loads(path.read_text(encoding="utf-8"))
    if not args.all_ports:
        want.pop("owner_replica0_ports")
    O.S.require(json.loads(json.dumps(got)) == want, "recomputed result differs from RESULT.json")
    if args.all_ports:
        print("PASS_PR3190_ALL_PORTS ports=112 changed=112 no_new_kappa")
    else:
        print("PASS_PR3190_REMAINDER_STREAM_COUNTEREXAMPLE port=0 character=2^72 differences=10 isolated=5+5 no_new_kappa")


if __name__ == "__main__":
    main()
