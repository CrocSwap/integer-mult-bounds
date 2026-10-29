# Row 19 tight case, impl A: V = span D4 (Q u Roots(Q)), 5 hyperplanes H_k of V, each triple meets in a D4 root line, 10 distinct.
import sys,pickle,itertools; sys.path.insert(0,'../CARRIER'); from lib import lines
import sympy
Q2r=pickle.load(open('../G777/Q2r.pkl','rb'))
res=[]
for qi,(Q,rs) in enumerate(list(Q2r.items())[:3]):
    X=[t for t in range(120) if Q>>t&1]+sorted(rs); assert len(X)==12
    V=[sympy.Matrix(lines[t]) for t in X]
    assert sympy.Matrix.hstack(*V).rank()==4
    # 3-dim subspaces of V spanned by D4 roots: record as frozenset of D4 lines inside
    hyp=set()
    for tr in itertools.combinations(range(12),3):
        M=sympy.Matrix.hstack(*[V[i] for i in tr])
        if M.rank()<3: continue
        inside=frozenset(i for i in range(12) if sympy.Matrix.hstack(M,V[i]).rank()==3)
        hyp.add(inside)
    big=[h for h in hyp if len(h)==6]
    # any hyperplane H_k must contain >=6 D4 roots (the 6 r_ab, ab in [5]-k); a 3-dim space through 6 roots is spanned by them -> in 'hyp'
    # condition: triple intersection of the 5 hyperplanes = exactly one D4 line, distinct over the 10 triples.
    # the hyperplane itself is determined by its root set (rank 3); intersection of H's: compute via normals
    def normal(h):
        M=sympy.Matrix.hstack(*[V[i] for i in h]).T
        ns=M.nullspace(); return ns  # in R^8: the orthogonal complement; intersect with V below
    sols=0
    for five in itertools.combinations(big,5):
        ok=True; seen=set()
        for T in itertools.combinations(range(5),3):
            common=five[T[0]]&five[T[1]]&five[T[2]]
            # exact: the intersection subspace of three distinct hyperplanes of V has dim >=1; it must be a root line r with r in all three
            # and contain no other; dim check: rank of union of root sets
            if len(common)!=1: ok=False;break
            c=next(iter(common))
            if c in seen: ok=False;break
            seen.add(c)
        if ok: sols+=1
    print('Q',qi,'#3-dim root subspaces',len(hyp),'with 6 roots',len(big),'valid 5-configs',sols)
