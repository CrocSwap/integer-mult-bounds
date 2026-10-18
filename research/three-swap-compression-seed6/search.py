#!/usr/bin/env python3
"""Bounded, exact Boolean encoding of normalized seven-call three-SWAP words.
Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import time
import z3

ROOT=Path(__file__).resolve().parent

def mm(a,b):
    return sum(((sum(((a>>(2*i+k))&1)*((b>>(2*k+j))&1) for k in range(2))&1)<<(2*i+j)) for i in range(2) for j in range(2))
GROUP=tuple(n for n in range(16) if (((n&1)*((n>>3)&1)^((n>>1)&1)*((n>>2)&1)))==1)
INDEX={g:i for i,g in enumerate(GROUP)}
IDENT,A,B,SWAP=9,11,13,6

def xor(values):
    result=z3.BoolVal(False)
    for x in values:result=z3.Xor(result,x)
    return result

def target(r=4,active=3):
    return [[(1<<INDEX[SWAP if i<active else IDENT]) if i==j else 0 for j in range(r)] for i in range(r)]

def formal(word,r=4):
    state=[[(1<<INDEX[IDENT]) if i==j else 0 for j in range(r)] for i in range(r)]
    for gate in word:
        u,v,g=gate['u'],gate['v'],gate['g']
        if not (u and v and (u&v).bit_count()%2):raise ValueError('not a rank-one idempotent')
        new=[row[:] for row in state]
        for i in range(r):
            operand=0
            for k in range(r):
                if (u>>k)&1:operand^=state[i][k]
            translated=0
            for h in range(6):
                if (operand>>h)&1:translated^=1<<INDEX[mm(GROUP[h],g)]
            delta=operand^translated
            for j in range(r):
                if (v>>j)&1:new[i][j]^=delta
        state=new
    return state

def encode(labels,timeout_ms=15000,pinned=None):
    r=4;solver=z3.Solver();solver.set(timeout=timeout_ms,random_seed=6)
    state=[[[z3.BoolVal(h==INDEX[IDENT] and i==j) for j in range(r)] for i in range(r)] for h in range(6)]
    projectors=[];a_count=0
    for step,label in enumerate(labels):
        if label=='a':
            u=[z3.BoolVal(i==a_count) for i in range(r)];a_count+=1
        else:u=[z3.Bool(f'u_{step}_{i}') for i in range(r)]
        v=[z3.Bool(f'v_{step}_{i}') for i in range(r)]
        solver.add(xor(z3.And(u[i],v[i]) for i in range(r)))
        if pinned is not None:
            solver.add(*[v[i]==z3.BoolVal(bool((pinned[step]['v']>>i)&1)) for i in range(r)])
            solver.add(*[u[i]==z3.BoolVal(bool((pinned[step]['u']>>i)&1)) for i in range(r)])
        projectors.append((u,v))
        g=A if label=='a' else B
        contracted=[[xor(z3.And(state[h][i][k],u[k]) for k in range(r)) for i in range(r)] for h in range(6)]
        new=[[[z3.Bool(f's_{step}_{h}_{i}_{j}') for j in range(r)] for i in range(r)] for h in range(6)]
        for h in range(6):
            predecessor=INDEX[mm(GROUP[h],g)]
            for i in range(r):
                value=z3.Xor(contracted[h][i],contracted[predecessor][i])
                for j in range(r):solver.add(new[h][i][j]==z3.Xor(state[h][i][j],z3.And(value,v[j])))
        state=new
    expected=target(r)
    for h in range(6):
        for i in range(r):
            for j in range(r):solver.add(state[h][i][j]==z3.BoolVal(bool((expected[i][j]>>h)&1)))
    # Redundant sign-quotient consequences improve propagation.
    for i in range(r):
        for j in range(r):solver.add(xor(z3.And(u[i],v[j]) for u,v in projectors)==z3.BoolVal(i==j and i<3))
    return solver,projectors

def solve(labels,timeout_ms):
    started=time.monotonic();solver,projectors=encode(labels,timeout_ms)
    answer=solver.check();out={'labels':labels,'status':str(answer),'elapsed_seconds':round(time.monotonic()-started,6)}
    if answer==z3.sat:
        model=solver.model();word=[]
        for label,(u,v) in zip(labels,projectors):
            word.append({'u':sum(int(z3.is_true(model.eval(x,model_completion=True)))<<i for i,x in enumerate(u)),
                         'v':sum(int(z3.is_true(model.eval(x,model_completion=True)))<<i for i,x in enumerate(v)),
                         'g':A if label=='a' else B})
        if formal(word)!=target():raise RuntimeError('SAT witness fails independent concrete formal replay')
        out['word']=word
    elif answer==z3.unknown:out['reason']=solver.reason_unknown()
    return out

def controls():
    labels='babbabbab'
    word=[{'u':1<<i,'v':1<<i,'g':g} for i in range(3) for g in (B,A,B)]
    if formal(word)!=target():raise RuntimeError('nine-call positive control failed')
    solver,_=encode(labels,15000,pinned=word)
    if solver.check()!=z3.sat:raise RuntimeError('Boolean encoder rejects explicit nine-call witness')
    # Wrong projectors violate the idempotence premise, rather than becoming free wide calls.
    try:formal([{'u':1,'v':2,'g':A}])
    except ValueError:pass
    else:raise RuntimeError('non-idempotent negative control accepted')
    return word

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--timeout-ms',type=int,default=15000)
    ap.add_argument('--pattern',type=int);ap.add_argument('--output',type=Path,default=ROOT/'SEARCH.json')
    args=ap.parse_args();patterns=[''.join('a' if j in active else 'b' for j in range(7)) for active in itertools.combinations(range(7),3)]
    controls();order=list(range(6,35))+list(range(6))
    if args.pattern is not None:order=[args.pattern]
    result={'engine':'Z3 Boolean coefficient recurrence','z3_version':z3.get_version_string(),'assignment_seed':6,
            'registers':4,'active_swap_targets':3,'paid_calls':7,'timeout_ms_per_pattern':args.timeout_ms,'patterns_total':35,'results':[]}
    for index in order:
        item=solve(patterns[index],args.timeout_ms);item['pattern_index']=index;result['results'].append(item)
        args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(item),flush=True)
    print(json.dumps({'completed':len(result['results']),'counts':{x:sum(y['status']==x for y in result['results']) for x in ['sat','unsat','unknown']}}),flush=True)
if __name__=='__main__':main()
