#!/usr/bin/env python3
"""Bounded exact positive elementary-factor search for R439 B[242:283].

Apache-2.0. Ross, with substantial OpenAI Codex AI assistance (2026-10-13).
Domain: row/column subtraction trajectories keeping all coefficients nonnegative
and each diagonal entry at least one. All gates are single additions on the
original 12 ordered registers. A completed search is not an impossibility proof.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, math, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
BASE = '91a2094f2e022930069e8cfdc810a3ea1b81cd09'
SOURCE_SHA256 = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'

def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]

def transfer(program, n):
    m = identity(n)
    for d,s in program:
        m[d] = [x+y for x,y in zip(m[d],m[s])]
    return m

def dominated(a,b):
    return all(x <= y for ar,br in zip(a,b) for x,y in zip(ar,br))

def trajectory(target, rng, strategy):
    m=[r[:] for r in target]; n=len(m); left=[]; right=[]
    while m != identity(n):
        moves=[]
        for transpose in (False,True):
            rows=list(map(list,zip(*m))) if transpose else m
            for d in range(n):
                for s in range(n):
                    if d == s or rows[d][d]-rows[s][d] < 1:
                        continue
                    if all(a>=b for a,b in zip(rows[d],rows[s])):
                        gain=sum(rows[s])
                        # Six fixed priority families, with Gumbel noise only
                        # in strategy 5. Exact arithmetic decides feasibility
                        # and certificate acceptance.
                        if strategy == 0: priority=math.log(gain)+0.05*rng.random()
                        elif strategy == 1: priority=math.log(gain)+rng.random()
                        elif strategy == 2: priority=math.log(gain)+2*rng.random()
                        elif strategy == 3: priority=rng.random()
                        elif strategy == 4: priority=-math.log(gain)+rng.random()
                        else: priority=math.log(gain)-math.log(-math.log(max(1e-300,rng.random())))
                        moves.append((priority,transpose,d,s))
        if not moves: return None
        _,transpose,d,s=max(moves)
        if transpose:
            for row in m: row[d]-=row[s]
            right.append((s,d))
        else:
            m[d]=[a-b for a,b in zip(m[d],m[s])]
            left.append((d,s))
        # Strict-improvement domain: longer partial words cannot shorten later.
        if len(left)+len(right)>=41: return None
    return right+list(reversed(left))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=5)
    ap.add_argument('--trajectories',type=int,default=5000)
    ap.add_argument('--output',type=Path,default=Path(__file__).with_name('candidate.json'))
    args=ap.parse_args()
    if not 1<=args.trajectories<=5000: raise SystemExit('trajectories must be in [1,5000]')
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError('immutable source SHA-256 mismatch')
    src=json.loads(gzip.decompress(raw)); wires=src['frames'][520]; ix={v:i for i,v in enumerate(wires)}
    old=src['B'][242:283]
    if len(old)!=41 or not all(f==520 and len(ss)==1 for f,d,ss in old):
        raise ValueError('source block must be 41 single ADDs in frame 520')
    if len(wires)!=12 or len(set(wires))!=12 or wires!=sorted(wires):
        raise ValueError('frame must contain 12 distinct sorted registers')
    prog=[(ix[d],ix[ss[0]]) for _,d,ss in old]
    target=transfer(prog,len(wires)); oldrev=transfer(prog[::-1],len(wires)); rng=random.Random(args.seed)
    completed=0; successes=0; best=None; histogram={}; best_any=None
    for attempt in range(args.trajectories):
        candidate=trajectory(target,rng,attempt%6); completed+=1
        if candidate is None: continue
        successes+=1
        if transfer(candidate,len(wires))!=target:
            raise ValueError('factor search produced an incorrect integer map')
        histogram[len(candidate)]=histogram.get(len(candidate),0)+1
        reverse=transfer(candidate[::-1],len(wires)); dom=dominated(reverse,oldrev)
        growth=max(sum(r) for r in reverse)
        score=(len(candidate),growth)
        if best_any is None or score<best_any[0]:
            best_any=(score,candidate,reverse,attempt)
            print(json.dumps({'attempt':attempt,'gates':len(candidate),'reverse_dominated':dom,'reverse_max_rowsum':growth}),flush=True)
        if dom and (best is None or score<best[0]):
            best=(score,candidate,reverse,attempt)
            break
    chosen=best or best_any
    output={'status':'strict_forward_improvement_reverse_dominated' if best else ('strict_forward_improvement_requires_growth_pricing' if chosen else 'bounded_search_no_candidate'),
      'base_commit':BASE,'source':str(SOURCE.relative_to(ROOT)),'source_sha256':SOURCE_SHA256,
      'assignment_seed':5,'search_seed':args.seed,'frame':520,'phase':'B','start':242,'stop':283,'wires':wires,
      'domain':'at most 5000 seeded nonnegative row/column subtraction trajectories; positive diagonal retained; same 12 ordered registers; 40-gate ceiling',
      'stopping_rule':'first exact shorter candidate whose literal reverse positive transfer is entrywise bounded by the original; otherwise trajectory limit',
      'requested_trajectories':args.trajectories,'completed_trajectories':completed,'exact_factorizations':successes,
      'length_histogram':histogram,'original_gate_count':len(prog),'original_ops':old,
      'forward_transfer':target,'original_reverse_positive_transfer':oldrev,
      'scope':'finite exact integer block identity; no full theorem claim or new kappa',
      'attribution':'Ross; substantial OpenAI Codex AI assistance; source R439 PR589'}
    if chosen:
        score,candidate,reverse,attempt=chosen
        output.update(operations=[[wires[d],wires[s]] for d,s in candidate],candidate_ops=[[520,wires[d],[wires[s]]] for d,s in candidate],candidate_gate_count=len(candidate),
          selected_attempt_zero_based=attempt,candidate_reverse_positive_transfer=reverse,
          reverse_positive_entrywise_dominated=dominated(reverse,oldrev))
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:output[k] for k in ('status','completed_trajectories','exact_factorizations','length_histogram')}))
if __name__=='__main__': main()
