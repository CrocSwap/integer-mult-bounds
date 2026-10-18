"""Independent column simulation and grouped donor enumeration; no source imports."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[1]


def need(ok,msg):
    if not ok:raise ValueError(msg)


def main():
    expected=json.loads((P/'EXPECTED.json').read_text())
    source='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
    raw=(ROOT/source).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==json.loads((P/'SOURCES.json').read_text())['files'][source],'source word hash')
    word=json.loads(gzip.decompress(raw));counts=[];tested=0
    for block in expected['blocks']:
        lo,hi=block['slice'];regs=block['registers'];n=len(regs);matrix=[[0]*n for _ in regs]
        for column in range(n):
            state={r:int(j==column) for j,r in enumerate(regs)}
            for f,t,ss in word['B'][lo:hi]:
                need(f==block['frame'] and len(ss)==1,'column source')
                state[t]+=state[ss[0]]
            for row,r in enumerate(regs):matrix[row][column]=state[r]
        need(matrix==block['matrix'],'independent column map')
        for d in range(n):
            goal=tuple(matrix[d][j]-int(j==d) for j in range(n))
            groups=[]
            for s in range(n):
                if s==d:continue
                groups.append([(0,)*n,tuple(int(j==s) for j in range(n)),tuple(matrix[s])])
            # Enumerate each donor's three mutually exclusive states. Nonnegative
            # overshoot pruning cannot discard a representation of the goal.
            solutions=[]
            def visit(k,total,pattern):
                nonlocal tested
                tested+=1
                if k==len(groups):
                    if total==goal:solutions.append(pattern)
                    return
                for kind,row in enumerate(groups[k]):
                    merged=tuple(a+b for a,b in zip(total,row))
                    if all(a<=b for a,b in zip(merged,goal)):visit(k+1,merged,pattern+[kind])
            visit(0,(0,)*n,[])
            row=block['rows'][d];witness=row['witness']
            need(bool(solutions)==(witness is None),'separator matches exact feasibility')
            # Independent brute force of all individually fitting choices checks
            # each small dual bound, even permitting globally inconsistent orders.
            if witness:
                choices=[[v for v in group if all(a<=b for a,b in zip(v,goal))] for group in groups]
                maximum=None;vectors=0
                weights=witness['weights']
                for values in itertools.product(*choices):
                    score=sum(sum(w*x for w,x in zip(weights,v)) for v in values)
                    maximum=score if maximum is None else max(maximum,score);vectors+=1
                need(maximum==witness['supply'],'independent maximum')
                need(sum(w*g for w,g in zip(weights,goal))>maximum,'independent separation')
            else:vectors=0
            counts.append(dict(frame=block['frame'],wire=regs[d],representations=len(solutions),dual_assignments=vectors))
    need(len(counts)==23 and sum(c['representations']==0 for c in counts)==4,'row inventory')
    print('PASS_INDEPENDENT17 rows=23 zero_rows=4 representation_counts='+json.dumps([c['representations'] for c in counts])+' dual_assignments='+str(sum(c['dual_assignments'] for c in counts)))


if __name__=='__main__':main()
