#!/usr/bin/env python3
"""Compare literal complete callers at the same target, per native source."""
from pathlib import Path
from decimal import Decimal,localcontext
import json,hashlib
H=Path(__file__).resolve().parent

def main():
    basepath=H/'inputs/BASELINE-ADMISSION.json';base=json.loads(basepath.read_text())['branches']['bit']
    goal=json.loads((H/'GOAL-BALANCED-16-CALLER-RESULT.json').read_text())['invoice']
    front=json.loads((H/'BINARY-MIXED-CALLER-RESULT.json').read_text())['invoice']
    rows=[]
    with localcontext()as ctx:
        ctx.prec=70
        for K in (Decimal('.0042'),Decimal('.00424861198'),Decimal('.00424927762')):
            def margin(T,P):return sum(Decimal(n)*Decimal(r)**(1-K)for r,n in T.items())-sum(Decimal(n)*Decimal(r)**(1-K)for r,n in P.items())
            old=-margin(base['targets'],base['paid'])/19
            new=-margin(goal['productive_profile'],goal['paid_profile'])/16
            f18=-margin(front['productive_profile'],front['paid_profile'])/18
            rows.append(dict(kappa=str(K),old_F19_gain_needed_per_native=str(old),frontier_F18_gain_needed_per_native=str(f18),goal_F16_gain_needed_per_native=str(new),budget_reduction_vs_F19=str(old-new),fraction_of_old_gap_closed=str((old-new)/old)))
    out=dict(status='COMPLETE_CALLER_GOAL_COST_COMPARISON',baseline_receipt_sha256=hashlib.sha256(basepath.read_bytes()).hexdigest(),comparison=rows,frontier_caller_children=[7,2,2,7],goal_caller_children=[4,4,4,4],scope='Exact decimal70 complete-invoice repricing for emitted callers. The deficit is required additional net improvement of the unchanged native source per invocation; this is not a claimed new source saving. BalancedF16 was selected by a finite240-leaf binary-child screen, not an asserted unrestricted global caller optimum.')
    (H/'GOAL-ECONOMICS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
