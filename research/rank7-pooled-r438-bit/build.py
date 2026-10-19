#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pool R438's width-8 slack across the 32 bit replicas with an explicit cross-replica owner map.

R438 (PR1043 word, PR2423 re-hosting) has 54 width-8 slack units per replica.  Its proven replica-local
optimum is 10 empty capacity-42 copies plus one capacity-42 copy holding one residual (idle 34).
Pooled over 32 replicas, 32*54 = 345*5 + 3, and the pooled32 slot-model optimum
(research/bit-partial-width7-optimum, k = 1 row, 0.001734900431583947) is 345 empty 42-copies plus one empty
capacity-28 copy.  This builder realizes it literally: the 32 single residuals (one per replica, child 6)
and the three residuals of one full capacity-28 copy of replica 0 (child 7, stages 5-8, inside child 6's
window 3-8) move into seven previously empty child-6 copies of replicas 0..6, five per copy.

Input: ALLOC-R438.json.gz, R438's per-replica placement, bound to slot_list_sha256 in
research/bit-r438-transport-rehost/verify_rehost.receipt.json on main.  Output: POOL-MOVES.json.
"""
import gzip, hashlib, json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V, T, COPIES, STAGES = 111, 32, 222, 9
PAIR = {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 0, 7: 1, 8: 2}          # host child -> pair (R438 receipt windows)


def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)


def family(rep, child, cp):
    return rep * 8 * V + (2 * PAIR[child] + cp // V) * V + cp % V


def main():
    raw = gzip.decompress((HERE / 'ALLOC-R438.json.gz').read_bytes())
    receipt = json.loads((ROOT / 'research/bit-r438-transport-rehost/verify_rehost.receipt.json').read_text())
    need(hashlib.sha256(raw).hexdigest() == receipt['placement']['slot_list_sha256'], 'R438 placement binding')
    alloc = [tuple(t) for t in json.loads(raw)]
    occ = defaultdict(list)                      # (child, copy) -> [(offset, stage, helper)]
    for child, cp, off, w, s, h in alloc:
        occ[child, cp].append((off, s, h))
    single = [cp for cp in range(COPIES) if len(occ.get((6, cp), [])) == 1]
    empty = [cp for cp in range(COPIES) if not occ.get((6, cp))]
    need(len(single) == 1 and len(empty) == 10, 'R438 replica-local optimum shape in child 6')
    src28 = min(cp for cp in range(COPIES) if len(occ.get((7, cp), [])) == 3)
    movers = [(s, rep, h, 6, single[0], off) for rep in range(T) for off, s, h in occ[6, single[0]]]
    movers += [(s, 0, h, 7, src28, off) for off, s, h in sorted(occ[7, src28])]
    need(len(movers) == 35, '35 residuals')
    dests = [(rep, empty[0]) for rep in range(7)]
    fill = defaultdict(list)
    for mv in sorted(movers):
        d = next(d for d in dests if len(fill[d]) < 5)
        fill[d].append(mv)
    moves = []
    for (rep_d, cp_d), lst in sorted(fill.items()):
        for k, (s, rep, h, child, cp, off) in enumerate(lst):
            moves.append(dict(stage=s, call_replica=rep, helper=h,
                              old=dict(family=family(rep, child, cp), child=child, offset=off),
                              new=dict(family=family(rep_d, 6, cp_d), child=6, offset=8 * k)))
    (HERE / 'POOL-MOVES.json').write_text(json.dumps(dict(alloc_sha256=hashlib.sha256(raw).hexdigest(), moves=moves), indent=1) + '\n')
    print('PASS pooled moves', len(moves))


if __name__ == '__main__':
    main()
