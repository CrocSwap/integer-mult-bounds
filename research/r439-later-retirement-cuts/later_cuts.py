# SPDX-License-Identifier: Apache-2.0
"""All fixed-B-prefix cuts; exact necessary conditions, not suffix synthesis."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('station_verify',HERE/'verify.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
HELPERS=[465,466,468,469,470,476]


def compute():
    w=V.load(); n=2*w['v']+w['R']; v=w['v']; rows,current,_=V.cut(w)
    fb=[V.basis([w['lines'][i] for i in f]) for f in w['frames']]
    gates=w['D']+w['A']+[[0,v+t,[w['ret'][j]]] for t,js in enumerate(w['scatter']) for j in js]
    inv=[1<<r for r in range(n)]
    for _,t,ss in reversed(gates):
        for s in ss:inv[t]^=inv[s]
    restore={h:inv[h] for h in HELPERS}
    target=[inv[v+t]^inv[t] for t in range(v)]
    cache,contain={},{}
    def join(regs):
        key=tuple(sorted(set(current[r] for r in regs)))
        if key not in cache:cache[key]=V.basis([x for f in key for x in fb[f]])
        return cache[key]
    def subset(b,f):
        key=(tuple(tuple(x for x in r) for r in b),f)
        if key not in contain:contain[key]=V.contained(b,fb[f])
        return contain[key]
    all_rows={h:[] for h in HELPERS}
    for cut in range(len(w['B'])+1):
        for h in HELPERS:
            donors=list(V.bits(restore[h]))
            dirt=[r for r,value in enumerate(rows) if value>>h&1]
            U=join(donors+dirt+[h])
            record={'joint_rank':len(U)}
            if len(U)<=7:
                J=join(donors+[h]);mask=sum(1<<r for r in set(donors+[h]))
                lost=[t+v for t in range(v) if target[t]&mask and not subset(J,w['final'][v+t])]
                record.update(restoration_rank=len(J),lost_targets=lost,restore_donors=donors)
            all_rows[h].append(record)
        if cut<len(w['B']):
            f,t,ss=w['B'][cut]
            # Source operands are distinct in the pinned word.
            V.require(len(ss)==len(set(ss)) and t not in ss,'invalid B transvection')
            sm=sum(1<<s for s in ss)
            for r in [t,*ss]:current[r]=f
            for s in ss:rows[t]^=rows[s]
            for h in HELPERS:
                if restore[h]>>t&1:restore[h]^=sm
            for i in range(v):
                if target[i]>>t&1:target[i]^=sm
    result=[]
    for h in HELPERS:
        runs=[]
        for cut,row in enumerate(all_rows[h]):
            if not runs or runs[-1]['conditions']!=row:
                runs.append({'first_cut':cut,'last_cut':cut,'conditions':row})
            else:runs[-1]['last_cut']=cut
        passed=[i for i,row in enumerate(all_rows[h]) if row.get('lost_targets')==[]]
        windows=[]
        for i in passed:
            if not windows or windows[-1][1]+1!=i:windows.append([i,i])
            else:windows[-1][1]=i
        result.append({'helper':h,'joint_rank_seven_cuts':sum(r['joint_rank']==7 for r in all_rows[h]),
                       'necessary_condition_pass_count':len(passed),'windows':windows,'runs':runs})
    return {'schema_version':1,'source_sha256':V.DIGEST,'B_gate_count':len(w['B']),
            'cuts_per_helper':len(w['B'])+1,'helper_cut_pairs':len(HELPERS)*(len(w['B'])+1),
            'cut_convention':'cut k is after exactly the first k B records, with D/A/scatter fixed',
            'meaning':'Passing both necessary tests is not a legal suffix or new supplier.',
            'helpers':result,'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
    result=compute()
    if args.output:
        with args.output.open('x') as out:json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
    else:V.require(result==json.loads((HERE/'LATER-CUTS.json').read_text()),'later-cut certificate mismatch')
    print('PASS_LATER_BIT_CUTS pairs=4278 windows=465:10-48,468:31-88,470:0-517 excluded=466,469,476 no_new_kappa')

if __name__=='__main__':main()
