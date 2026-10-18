#!/usr/bin/env python3
"""Charles Bethin, with OpenAI Codex assistance. Apache-2.0.
Finite checks for the separately written characteristic-zero proof.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('one_root',ROOT/'one_root.py')
walk=importlib.util.module_from_spec(spec);spec.loader.exec_module(walk)
M=((1,1,1),(1,1,-1),(1,-1,0))
def require(ok,msg):
    if not ok: raise ValueError(msg)

def solve(rows,rhs):
    """Generic rational elimination, including inconsistent and nonunique cases."""
    a=[[F(x) for x in row]+[F(b)] for row,b in zip(rows,rhs)]
    rank=0;pivots=[]
    for col in range(4):
        pivot=next((r for r in range(rank,len(a)) if a[r][col]),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank]
        z=a[rank][col];a[rank]=[x/z for x in a[rank]]
        for r in range(len(a)):
            if r!=rank:
                z=a[r][col];a[r]=[x-z*y for x,y in zip(a[r],a[rank])]
        pivots.append(col);rank+=1
    if any(not any(row[:4]) and row[4] for row in a):return 'inconsistent',None
    if rank<4:return 'nonunique',None
    answer=tuple(a[i][4] for i in range(4))
    require(all(sum(x*y for x,y in zip(row,answer))==b for row,b in zip(rows,rhs)),'linear residual')
    return 'unique',answer

def cube_leaf_proof():
    cases=0;templates=set()
    for signs in product((-1,1),repeat=3):
        pairs=[]
        for row in M:
            found=set()
            for v in range(8):
                for w in range(8):
                    if all(signs[k]*(((v>>k)&1)-((w>>k)&1))==row[k] for k in range(3)):
                        found.add(frozenset((v,w)))
            pairs.append(found)
        require(tuple(map(len,pairs))==(1,1,2),'target endpoint geometry')
        for third in pairs[2]:
            vertices=set(next(iter(pairs[0])))|set(next(iter(pairs[1])))|set(third)
            degrees=[sum((v^(1<<k)) in vertices for k in range(3)) for v in vertices]
            require(len(vertices)==6 and degrees.count(1)==2,'two leaves exclude six-cycle')
            templates.add(tuple(sorted(vertices)));cases+=1
    require(len(templates)==4 and cases==16,'complete sign/height geometry')
    return cases,len(templates)

def height_partitions():
    patterns=[]
    for h in product(range(5),repeat=5):
        if h[0]!=0 or any(h[k]>1+max(h[:k]) for k in range(1,5)):continue
        if h[0]!=h[4] or any(h[k]==h[k+1] for k in range(4)):continue
        patterns.append(h)
        require(all(j-i in (2,4) for i in range(5) for j in range(i+1,5) if h[i]==h[j]),'equal-height interval')
    require(len(patterns)==4,'complete height partitions')
    return patterns

def coefficient_systems():
    checked=0;accepted=0
    for eps in (-1,1):
        for bits in product((0,1),repeat=4):
            q=tuple(eps*x for x in bits)
            for k in range(3):
                interval=[int(j in (k,k+1)) for j in range(4)]
                rest=[j for j in range(4) if not interval[j]]
                for reader in (-1,1):
                    rows=[[1]*4,interval,[reader*interval[j]*q[j] for j in range(4)],list(q)]
                    status,answer=solve(rows,[0,0,1,0]);checked+=1
                    # A separate two-difference derivation solves the same constraints.
                    d=q[k]-q[k+1];e=q[rest[0]]-q[rest[1]]
                    if not d or not e:
                        require(status=='inconsistent','zero difference must reject')
                    else:
                        a=F(reader,d);b=-a*d/e
                        closed=[F(0)]*4
                        closed[k]=a;closed[k+1]=-a;closed[rest[0]]=b;closed[rest[1]]=-b
                        require(status=='unique' and answer==tuple(closed),'independent linear models')
                        require(set(answer)<=set((F(-1),F(1))),'unit rigidity')
                        accepted+=1
    # Changing the required ordinary contribution allows nonunit coefficients.
    status,answer=solve([[1]*4,[1,1,0,0],[1,0,0,0],[1,0,0,1]],[0,0,2,0])
    require(status=='unique' and any(abs(x)!=1 for x in answer),'scaled target sensitivity')
    return checked,accepted

# Ross Richardson PR1651's attaining word, pinned and attributed in PREDECESSORS.json.
# Tuples are destination, source, scalar, operator (None means root transfer).
WORD=[('y0','z',1,'A0'),('z','w',-1,None),('w','x0',-1,'B0'),
 ('y2','w',-1,'A2'),('w','x1',-1,'B1'),('z','w',1,None),
 ('y1','z',-1,'A1'),('z','x2',-1,'B2'),('y0','z',-1,'A0'),
 ('z','w',-1,None),('w','x0',1,'B0'),('y2','w',1,'A2'),
 ('w','x1',1,'B1'),('z','w',1,None),('y1','z',1,'A1'),('z','x2',1,'B2')]
REGS=('x0','x1','x2','y0','y1','y2','z','w')
def formal(word):
    state={r:{(r,()):F(1)} for r in REGS}
    for dst,src,c,op in word:
        for (origin,ops),a in list(state[src].items()):
            key=(origin,((op,)+ops) if op else ops)
            state[dst][key]=state[dst].get(key,F(0))+c*a
            if not state[dst][key]:del state[dst][key]
    return state

def target_formal(sign=1):
    result={r:{(r,()):F(1)} for r in REGS}
    for i in range(3):
        for j in range(3):
            if M[i][j]:result['y'+str(i)][('x'+str(j),('A'+str(i),'B'+str(j)))]=F(sign*M[i][j])
    return result

def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def dense(word):
    # Compose independent 16x16 elementary block matrices on all dirty basis columns.
    ops={'A0':[[1,2],[0,1]],'A1':[[0,1],[1,0]],'A2':[[1,0],[3,1]],
         'B0':[[1,1],[1,0]],'B1':[[2,0],[1,1]],'B2':[[1,3],[0,0]]}
    result=eye(16)
    for dst,src,c,op in word:
        gate=eye(16);a=ops[op] if op else eye(2)
        d=2*REGS.index(dst);s=2*REGS.index(src)
        for i in range(2):
            for j in range(2):gate[d+i][s+j]+=c*a[i][j]
        result=mm(gate,result)
    expected=eye(16)
    for i in range(3):
        for j in range(3):
            block=mm(ops['A'+str(i)],ops['B'+str(j)])
            for k in range(2):
                for l in range(2):expected[6+2*i+k][2*j+l]+=M[i][j]*block[k][l]
    return result,expected

def admissible(word):
    transfers=[e for e in word if e[3] is None]
    queries=[e for e in word if e[3] is not None]
    return (len(transfers)==4 and len(queries)==12
      and all(d=='z' and s=='w' and c!=0 for d,s,c,op in transfers)
      and all(abs(c)==1 for d,s,c,op in queries))

def controls():
    expected=target_formal();require(formal(WORD)==expected,'universal witness')
    inverse=[(d,s,-c,o) for d,s,c,o in reversed(WORD)]
    require(formal(inverse)==target_formal(-1),'formal inverse')
    require(formal(WORD+inverse)=={r:{(r,()):F(1)} for r in REGS},'all dirty restoration')
    require(dense(WORD)[0]==dense(WORD)[1],'noncommuting dense basis witness')
    rejected=0
    for i in range(len(WORD)):
        wrong=WORD[:i]+WORD[i+1:]
        require(formal(wrong)!=expected,'omission control');rejected+=1
    # Balanced nonunit shear mutation preserves zero total height, not the target.
    wrong=list(WORD)
    for i in (1,5):
        d,s,c,o=wrong[i];wrong[i]=(d,s,2*c,o)
    require(admissible(wrong) and formal(wrong)!=expected,'balanced nonunit rejection')
    require(dense(wrong)[0]!=dense(wrong)[1],'dense nonunit rejection');rejected+=1
    # Conjugating the root w by 2 preserves the target but scales ordinary queries.
    outside=[]
    for d,s,c,o in WORD:
        scale=F(2 if d=='w' else 1,2 if s=='w' else 1)
        outside.append((d,s,c*scale,o))
    require(formal(outside)==expected and not admissible(outside),'scaled-query boundary')
    require(dense(outside)[0]==dense(outside)[1],'dense scaled-query boundary')
    # A paid identity pair is valid but breaks the exact four-transfer premise.
    six=[('z','w',2,None),('z','w',-2,None)]+WORD
    require(formal(six)==expected and not admissible(six),'six-transfer boundary')
    return rejected,2

def main():
    count,good,sets=walk.event_model(M);gg,gs,sizes,masks=walk.graph_model(M)
    require(count==720 and good==gg==0 and sets==gs,'independent one-root coverage')
    require(walk.event_model(M[:2])[1]>0 and walk.graph_model(M[:2])[0]>0,'missing-row positive control')
    leaf_cases,templates=cube_leaf_proof();partitions=height_partitions();checked,accepted=coefficient_systems();rejected,boundaries=controls()
    print(json.dumps({'status':'PASS_NONUNIT_SIGNED_CONNECTOR_RIGIDITY',
      'cube_leaf_cases':leaf_cases,'cube_leaf_templates':templates,'height_equality_patterns':len(partitions),'linear_systems':checked,'unique_unit_solutions':accepted,'one_root_traces':count,
      'cube_masks':masks,'signed_vertex_sets':len(sets),'rejected_program_mutations':rejected,
      'valid_outside_class_controls':boundaries,'formal_forward_inverse':True,'dense_dirty_basis_columns':16,
      'scope':'written universal proof plus exact finite checks; no new kappa'},sort_keys=True))
if __name__=='__main__':main()
