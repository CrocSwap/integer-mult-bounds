"""Calibrate the frame-cost oracle on the published pivot-554 kernel (PR1672, k554-signed-001) using PR1672's step-0 word.
Checks: exact price of the kernel (-1850), deletion-only relaxation of B342 (-6763), oracle costs of every inserted gate
(0, 4913, 0, 0 and tail 0: the kernel's whole cost is one rank-2 split on target 126), and that gencomp2's cost-aware search
rediscovers a kernel of the same exact price."""
import json, sys
import _paths
import harness as H
from fc3 import solve
from costorc import CostOracle
import gencomp2 as G
P = H.Pricer(str(_paths.STEP0))
ed = json.load(open(_paths.INPUTS / 'EDITS-k554.json'))['edit']
r = P.price(ed); assert r['status'] == 'ok' and r['delta'] == -1850, r
w2, rd = solve(P, dict(delete=ed['delete'])); ddel = rd['cost'] - P.base_cost; assert ddel == -6763, ddel
co = CostOracle(w2, P.costs.c); NB = len(P.base['B']); d = ed['delete'][0]
ins = [co.cost(g[1], g[2], p - (1 if p > d else 0)) for p, g in ed['insert']]
tl = [co.cost(g[1], g[2], NB - 1 + j) for j, g in ed['tail']]
assert ins == [0, 4913, 0, 0] and tl == [0], (ins, tl)
ddel2, res = G.run(P, [342], 10, 1, 30, None)
assert ddel2 == -6763 and res and res[0]['status'] == 'ok' and res[0]['delta'] == -1850, res[:1]
print(json.dumps(dict(status='PASS_ORACLE_CALIBRATION_K554', kernel_delta=r['delta'], deletion_relaxation=ddel, oracle_insert_costs=ins, oracle_tail_costs=tl,
                      rediscovered=res[0]['terms'], rediscovered_delta=res[0]['delta'])))
