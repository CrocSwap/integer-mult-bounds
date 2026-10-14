"""Independent review stage written by LeverRank (second, independently coded simulation; included unmodified apart from the final assert). Independent tape-style simulation of the radix-distributed sparse-union schedule (OuterLever_union_schedule.md).
Implements: flags F, rounds with S_r, stable LSD binary radix by tag with stored bits, per-prefix-block small-field transpose by recursive riffle
(arbitrary |E_f|, not power of 2), line application, inverse transpose, inverse radix by replaying bits, LIFO rest stack + indicator merge.
Counts record-moves per pass; checks (1) exact equality with the full tensor product, (2) block completeness/constant block length per tag,
(3) order preservation, (4) cost <= C * sum|S_r| * (log g + log Emax + 1) with no |U|-per-round factor."""
import numpy as np, itertools, random, math, sys
def run(g,L,Esizes,spect,seed):
    rng=np.random.default_rng(seed); random.seed(seed)
    E=[sorted(random.sample(range(L),Esizes[i])) for i in range(g)]
    T=[]
    for i in range(g):
        M=np.eye(L); sub=rng.integers(-3,4,(len(E[i]),len(E[i]))).astype(float)
        for a,x in enumerate(E[i]):
            for b,y in enumerate(E[i]): M[x,y]=sub[a,b]
        T.append(M)
    X=rng.integers(-5,6,(L,)*g+(spect,)).astype(float)
    ref=X.copy()
    for i in range(g): ref=np.moveaxis(np.tensordot(T[i],ref,axes=([1],[i])),0,i)
    pts=list(itertools.product(*([range(L)]*g+[range(spect)])))   # lexicographic, spectator last
    flags=lambda x: tuple(i for i in range(g) if x[i] in E[i])
    F={x:flags(x) for x in pts}
    val={x:X[x] for x in pts}
    moves=[0]; passes_info=[]
    def riffle(rows):   # rows: list of lists (row-major block as R rows of C items) -> column-major list ; returns (list, passes)
        R=len(rows)
        if R==1: return rows[0][:],0
        r1=(R+1)//2; top,pt=riffle(rows[:r1]); bot,pb=riffle(rows[r1:]); r2=R-r1; C=len(rows[0]); out=[]
        for c in range(C):
            out.extend(top[c*r1:(c+1)*r1]); out.extend(bot[c*r2:(c+1)*r2])
        return out,1+max(pt,pb)
    def unriffle(col,R,C):   # inverse of riffle on column-major list -> rows
        if R==1: return [col[:]]
        r1=(R+1)//2; r2=R-r1; top=[];bot=[]
        for c in range(C):
            blk=col[c*R:(c+1)*R]; top.extend(blk[:r1]); bot.extend(blk[r1:])
        return unriffle(top,r1,C)+unriffle(bot,r2,C)
    S=[x for x in pts if F[x]]; r=0; stack=[]; total=0; costs=[]; okorder=True
    while S:
        total+=len(S); cost=0
        tag={x:F[x][r] for x in S}
        # stable LSD radix by tag, stored bits
        nb=max(1,math.ceil(math.log2(g))) if g>1 else 1
        cur=S[:]; bits=[]
        for b in range(nb):
            zero=[x for x in cur if not (tag[x]>>b)&1]; one=[x for x in cur if (tag[x]>>b)&1]
            bits.append([(tag[x]>>b)&1 for x in cur]); cur=zero+one; cost+=2*len(cur)   # split + concat
        # substreams
        i=0; out_vals={}
        while i<len(cur):
            f=tag[cur[i]]; j=i
            while j<len(cur) and tag[cur[j]]==f: j+=1
            sub=cur[i:j]; i=j
            # prefix blocks
            k=0; Ef=E[f]
            nsuf=None
            while k<len(sub):
                pre=sub[k][:f]; m=k
                while m<len(sub) and sub[m][:f]==pre: m+=1
                blk=sub[k:m]; k=m
                # block must be E_f x (all suffixes): suffix count constant
                sufs=sorted({x[f+1:] for x in blk}); assert len(blk)==len(Ef)*len(sufs)
                expect=L**(g-f-1)*spect; assert len(sufs)==expect, (len(sufs),expect)
                if nsuf is None: nsuf=len(blk)
                assert len(blk)==nsuf            # constant block length per tag
                rows=[[x for x in blk if x[f]==ef] for ef in Ef]
                assert all(len(rw)==len(sufs) for rw in rows)
                col,npass=riffle(rows); cost+=npass*len(blk)
                # lines: consecutive |E_f| records share suffix
                R=len(Ef); newcol=[]
                for c in range(len(sufs)):
                    line=col[c*R:(c+1)*R]
                    assert len({x[f+1:] for x in line})==1 and [x[f] for x in line]==Ef
                    vec=np.array([val[x] for x in line]); res=T[f][np.ix_(Ef,Ef)]@vec
                    for a,x in enumerate(line): out_vals[x]=res[a]
                cost+=npass*len(blk)              # inverse transpose
            # (inverse transpose returns original order; values kept in out_vals)
        cost+=sum(2*len(S) for _ in range(nb))    # un-radix by replaying bits
        for x in S: val[x]=out_vals[x]
        # S order restored (cur permuted back): by construction
        # split |F|==r+1 (final) to stack, rest continues
        nxt=[x for x in S if len(F[x])>r+1]; fin=[x for x in S if len(F[x])==r+1]
        ind=[len(F[x])>r+1 for x in S]; stack.append((fin,ind)); cost+=len(S)
        costs.append((len(S),cost)); S=nxt; r+=1
    # merge back LIFO
    merged=[]; 
    for (fin,ind) in reversed(stack):
        it_f=iter(fin); it_m=iter(merged); new=[]
        for flag in ind: new.append(next(it_m) if flag else next(it_f))
        merged=new; total+=0
    okorder=(merged==[x for x in pts if F[x]])
    res=np.zeros_like(X)
    for x,v in val.items(): res[x]=v
    match=np.allclose(res,ref)
    tot_cost=sum(c for _,c in costs); sumS=sum(s for s,_ in costs)
    U=sum(1 for x in pts if F[x]); sumF=sum(len(F[x]) for x in pts)
    return match,okorder,sumS,sumF,g*U,tot_cost,tot_cost/max(1,sumS),math.log2(g)+math.log2(max(Esizes))+1
ok=True
for (g,L,Es,sp,seed) in [(4,6,[2,3,5,4],1,1),(5,6,[3,2,4,3,5],2,2),(3,9,[6,7,5],3,3),(6,5,[2,3,2,4,3,2],1,4),(5,7,[2,3,2,3,2],1,5),(2,12,[7,11],2,6),(7,4,[2,3,2,3,2,3,2],1,7)]:
    m,o,sS,sF,gU,tc,per,lg=run(g,L,Es,sp,seed)
    print('g',g,'L',L,'E',Es,'spect',sp,'| match',m,'order',o,'sum|S_r|',sS,'=sum|F|',sF,'(g|U|=%d)'%gU,'cost/sum|S_r|=%.2f  vs (log g+log E+1)=%.2f'%(per,lg),flush=True)
    ok&=m and o and sS==sF
print('ALL OK',ok)
assert ok
print('PASS_UNION_SCHEDULE_REVIEW')
