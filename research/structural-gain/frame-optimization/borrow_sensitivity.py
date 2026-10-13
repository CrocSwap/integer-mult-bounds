#!/usr/bin/env python3
"""Price free removal of the actual 28 late-retired factory helper paths.

This is a counterfactual design target. The missing restoration/circuit costs
are deliberately zero; none of these helpers is proved removable. A rational
packing and exact moment price the hypothetical inventory, not a multiplier.
Prepared with OpenAI Codex (GPT-6 Astra) assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research/larger-gain/patterns'))
sys.path.insert(0,str(ROOT/'research/larger-gain/providers'))
import capacity_ceiling as cap
from coupled_frames_base import Chains


def main():
    import numpy as np
    from scipy.optimize import linprog
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():raise ValueError('Use a fresh output')
    family=ROOT/'research/larger-gain/providers'
    extras=[]
    measured=[]
    registers=[224+16*block+(i-8) for block in range(14) for i in (17,21)]
    for kind in ('words','width7'):
        for name in ('zero','four','eight'):
            path=family/kind/name/'FULL-WORD.json.gz'
            word=json.loads(gzip.decompress(path.read_bytes()));graph=Chains(word)
            for register in registers:
                chain=graph.regs[register]
                paid=Counter(len(graph.nodes[b]['F'])-len(graph.nodes[a]['F']) for a,b in zip(chain,chain[1:]))
                paid.pop(0,None)
                if paid!={1:3,6:1} or graph.nodes[chain[0]]['F']:
                    raise ValueError('Hypothetical path differs from measured word')
            measured.append(dict(word=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            if kind=='width7':
                construction=path.with_name('CONSTRUCTION.json')
                extras.append(dict(path=str(construction.relative_to(ROOT)),sha256=hashlib.sha256(construction.read_bytes()).hexdigest()))
    columns,rhs,descriptors,source_sha=cap.instance(3,'all',extras)
    widths=sorted({r for d in descriptors if d['kind']=='provider' for r in d['widths']})
    capacity_count=len(rhs)-len(widths)-1
    records=[]
    for count in (0,6,14,28):
        cols=[list(c) for c in columns]
        ds=json.loads(json.dumps(descriptors))
        for i,d in enumerate(ds):
            if d['kind']=='provider':
                d['profile']={int(r):n for r,n in d['profile'].items()}
                d['widths']={int(r):n for r,n in d['widths'].items()}
                d['profile'][1]-=3*count;d['profile'][6]-=count;d['widths'][9]-=count
                cols[i][capacity_count+widths.index(9)]+=count
                if sum(r*n for r,n in d['profile'].items())-sum(r*n for r,n in d['widths'].items())!=1856:
                    raise ValueError('Counterfactual mass invariant failed')
        matrix=np.asarray(cols).T
        def solve(rate):
            price=lambda r:r*math.expm1(rate*math.log(73/r))/rate if r else 0
            cost=[price(d['remainder']) if d['kind']=='bin' else sum(n*price(r) for r,n in d['profile'].items()) for d in ds]
            sol=linprog(cost,A_eq=matrix,b_eq=rhs,bounds=(0,None),method='highs')
            if not sol.success:raise ValueError(sol.message)
            return sol
        lo,hi=.0015,.003
        for _ in range(42):
            rate=(lo+hi)/2
            if rate*solve(rate).fun<2560:lo=rate
            else:hi=rate
        sol=solve(hi)
        active=[i for i,n in enumerate(sol.x) if n>1e-7]
        if len(active)!=len(rhs):raise ValueError('Non-square nominated basis')
        primal=cap.solve_rational([[cols[i][r] for i in active] for r in range(len(rhs))],rhs)
        if not all(n>=0 for n in primal):raise ValueError('Negative exact multiplicity')
        if any(sum(cols[i][r]*n for i,n in zip(active,primal))!=rhs[r] for r in range(len(rhs))):
            raise ValueError('Exact packing mismatch')
        histogram=Counter()
        for i,n in zip(active,primal):
            d=ds[i]
            if d['kind']=='provider':histogram.update({r:n*v for r,v in d['profile'].items() if v})
            elif d['remainder']:histogram[d['remainder']]+=n
        denominator=math.lcm(*(n.denominator for n in histogram.values()))
        profile={r:int(n*denominator) for r,n in histogram.items() if n}
        if sum(r*n for r,n in profile.items())!=520704*denominator:raise ValueError('Wrong global mass')
        root=cap.load_engine('moment').certify(profile,73,7168*denominator)
        lower=Q(root['lower'])
        check=cap.load_engine('base_two_moment').moment(73,7168*denominator,list(profile.items()),lower)
        if not check[1]<1:raise ValueError('Independent moment failed')
        kappa=lower/(1+lower)
        records.append(dict(hypothetical_helpers_removed=count,removed_registers=registers[:count],
            removed_paid_profile={1:3*count,6:count},removed_width_nine=count,
            exact_packing=[dict(column=i,multiplicity=str(n)) for i,n in zip(active,primal)],
            exact_profile={str(r):str(n) for r,n in sorted(histogram.items()) if n},
            moment=root,independent_moment_residual_upper=str(check[1]-1),
            hypothetical_kappa=float(kappa),gain_over_pr569_percent=float(100*(kappa/Q('0.001600067494703216')-1))))
    output=dict(status='EXACT_COUNTERFACTUAL_PACKING_NOT_A_CONSTRUCTION',word_inputs=measured,
                source_plan_sha256=source_sha,records=records,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                register_mapping='PR531 ordered Hamming blocks allocate16 helpers each; module registers17 and21 map to224+16*block+9 and+13.',
                scope='Assumes the measured late-retired helper paths disappear with no replacement cost or output-path penalty. '
                      'All exact packing and moment signs concern only that hypothetical model. No restoration, phases, '
                      'whole-owner hosting, bit-supplier replacement or new kappa is established.')
    args.out.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ('hypothetical_helpers_removed','hypothetical_kappa','gain_over_pr569_percent')} for r in records],indent=2))


if __name__=='__main__':main()
