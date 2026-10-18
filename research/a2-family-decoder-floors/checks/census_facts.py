# Assertions on the output of unitcensus.py (one or more files):  python census_facts.py FILE...    (unit and triangle are read from the header line)
# Facts (A2COST section 2): (R) rows: the 63 X-avoiding classes have rank r(O) = 8; the other row-deficient classes are those with |O cap X| = 1, or O cap X = X, and rank r(O \ X) = 7;
#   there are 11 (P112) / 19 (P104) / 3 (E8); each has a 1-dim nullspace and the normals are pairwise distinct.
# (S) spans: r(O_{u_i} \ (E6 u X)) spans r_i^perp (rank 7); no line off X is non-orthogonal to all of X.
# (C) columns, generic gamma: exactly six killable classes, three 'sixty' classes (|O cap X| = 1) and three 'merged' classes (|O cap X| = 2); exactly three co-killable triples {merged_ij, sixty_i, sixty_j}, no other triple.
import sys, re, ast
from fractions import Fraction as Fr
EXP={'P112':11,'P104':19,'E8':3}
def norm(x):
    x=[Fr(a) for a in x]; i=next(k for k in range(8) if x[k]!=0); return tuple(a/x[i] for a in x)
for fn in sys.argv[1:]:
    T=open(fn).read().split('\n')
    m=re.match(r'(\w+) v (\d+) X \[([\d, ]+)\]',T[0]); unit=m.group(1); X=tuple(map(int,m.group(3).split(',')))
    spans=[l for l in T if l.startswith(' span O_u')]
    assert len(spans)==3 and all(l.strip()=='span O_u\\E6 7 (7) lines non-orth to all of X off X: 0' for l in spans)
    rc=ast.literal_eval(next(l for l in T if l.startswith('row census')).split(':',1)[1].strip())
    rc=dict(rc); assert rc[(0,8)]==63 and (0,7) not in rc and (2,7) not in rc
    r7=sum(c for (s,r),c in rc.items() if r==7); assert r7==EXP[unit],(unit,r7)
    rows=[ast.literal_eval(l.split('rank<8:')[1].strip()) for l in T if 'rank<8:' in l]
    assert len(rows)==r7 and all(isinstance(r[3],list) for r in rows)          # 1-dim nullspaces
    nrm=[norm(r[3]) for r in rows]; assert len(set(nrm))==len(nrm)             # pairwise distinct normals
    assert all((len(r[1])==1 or tuple(r[1])==tuple(sorted(X))) for r in rows)
    gk=ast.literal_eval(next(l for l in T if l.startswith('generic-gamma killable')).split(':',1)[1].strip())
    assert len(gk)==6 and sorted(len(g[2]) for g in gk)==[1,1,1,2,2,2]
    sixty={g[0] for g in gk if len(g[2])==1}; merged={g[0] for g in gk if len(g[2])==2}
    assert all(g[3]==((3,1,2) if len(g[2])==1 else (2,0,2)) for g in gk)
    ck=ast.literal_eval(next(l for l in T if l.startswith('co-killable 2-dim')).split(':',1)[1].strip())
    assert len(ck)==3
    for a,b,c,t in ck:
        assert a^b==c and t==(2,0,2) and len({a,b,c}&merged)==1 and len({a,b,c}&sixty)==2
    tri=[l for l in T if l.startswith(' 3 gen classes co-killable')]
    assert len(tri)==3, len(tri)                                                # no further co-killable triple
    ng=int(re.search(r'Gram-deficient \(eta=0\) classes: (\d+)',"\n".join(T)).group(1)); assert ng==EXP[unit]
    print('PASS census facts %s triangle %s: %d row-deficient classes (1-dim, distinct normals), 6 killable column classes, 3 co-killable triples'%(unit,list(X),r7))
