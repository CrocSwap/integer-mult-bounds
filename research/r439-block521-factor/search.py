#!/usr/bin/env python3
"""Reproduce the bounded nomination for selected R439 frame 521. Apache-2.0.

Prepared with substantial OpenAI assistance. This is a search, not an optimality proof.
"""
import argparse, gzip, hashlib, json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SOURCE_SHA='e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
SLICE=(314,361); FRAME=521

def matrix(ops,n):
    rows=[[int(i==j) for j in range(n)] for i in range(n)]
    for a,b in ops: rows[a]=[x+y for x,y in zip(rows[a],rows[b])]
    return rows

def nominate(seed=10,trials=12000):
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA: raise ValueError('source pin mismatch')
    word=json.loads(gzip.decompress(raw)); gates=word['B'][slice(*SLICE)]
    if len(gates)!=47 or any(f!=FRAME or len(ss)!=1 for f,_,ss in gates): raise ValueError('source slice changed')
    regs=sorted({d for _,d,_ in gates}|{s for _,_,ss in gates for s in ss}); idx={r:i for i,r in enumerate(regs)}
    old=[(idx[d],idx[ss[0]]) for _,d,ss in gates]; n=len(regs)
    target,identity=matrix(old,n),matrix([],n); old_reverse=matrix(old[::-1],n)
    rng=random.Random(seed); best=len(old); best_ops=old; trace=[]; success=accepted=dead=cutoff=0
    for trial in range(trials):
        m=[r[:] for r in target]; first=[]; last=[]; mode=trial%7
        while m!=identity and len(first)+len(last)<best:
            columns=list(zip(*m)); options=[]
            for a in range(n):
                for b in range(n):
                    if a==b: continue
                    if m[a][a]>m[b][a] and all(x>=y for x,y in zip(m[a],m[b])): options.append((sum(m[b]),0,a,b))
                    if m[b][b]>m[b][a] and all(x>=y for x,y in zip(columns[b],columns[a])): options.append((sum(columns[a]),1,a,b))
            if not options: dead+=1; break
            if mode==0:
                high=max(o[0] for o in options); op=rng.choice([o for o in options if o[0]==high])
            else: op=max(options,key=lambda o:o[0]*rng.random()**(mode/2))
            _,side,a,b=op
            if side==0: m[a]=[x-y for x,y in zip(m[a],m[b])]; last.append((a,b))
            else:
                for row in m: row[b]-=row[a]
                first.append((a,b))
        else:
            if m!=identity: cutoff+=1
        if m!=identity: continue
        success+=1; ops=first+last[::-1]
        if matrix(ops,n)!=target: raise RuntimeError('factorization invariant')
        rev=matrix(ops[::-1],n)
        if not all(x<=y for a,b in zip(rev,old_reverse) for x,y in zip(a,b)): continue
        accepted+=1
        if len(ops)<best:
            best,best_ops=len(ops),ops; trace.append({'trial':trial,'gates':best})
    return {'schema':'r439-block521-positive-factor/1','base_commit':'f567884aeb8851b6e794af1184119a3bfbe1e631','assignment_seed':10,
      'binding':{'source':str(SOURCE.relative_to(ROOT)),'section':'B','slice':list(SLICE),'frame':FRAME,'registers':regs},
      'original_gates':len(old),'gates':[[FRAME,regs[a],[regs[b]]] for a,b in best_ops],
      'search':{'method':'seeded bidirectional dominated integer subtraction','seed':seed,'trials':trials,'integer_factorizations':success,
      'reverse_dominated_factorizations':accepted,'dead_ends':dead,'gate_budget_cutoffs':cutoff,'improvement_trace':trace,
      'stopping_rule':'Exactly 12,000 trials; each stops at identity, no legal dominated subtraction, or the incumbent gate count.','optimality_claim':False}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--seed',type=int,default=10); ap.add_argument('--trials',type=int,default=12000); a=ap.parse_args()
    if a.output.exists(): ap.error('output exists')
    result=nominate(a.seed,a.trials); a.output.write_text(json.dumps(result,indent=2)+'\n')
    print('NOMINATED_R439_BLOCK521',result['original_gates'],'->',len(result['gates']),json.dumps(result['search'],sort_keys=True))
if __name__=='__main__': main()
