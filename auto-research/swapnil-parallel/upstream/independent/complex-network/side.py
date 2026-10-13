"""Own reimplementation of the paired-triple complex side circuit (PR7 spec),
with optional retained totals (PR4) and producer variants."""
from itertools import combinations
from collections import defaultdict
import sys
sys.setrecursionlimit(10000)

class Side:
    def __init__(s, h, base=4, retain=None, star='prefix'):
        s.h=h; s.base=base
        s.triples=list(combinations(range(h),3)); s.tid={t:i for i,t in enumerate(s.triples)}
        s.sup=[0]; s.args=[None]; s.kind=[None]; s.look={}
        for i,t in enumerate(s.triples):
            s.sup.append(1<<i); s.args.append(None); s.kind.append('in')
        s.cov={}
        s.pieces=[]   # (S, node, coef)
        s.retained=[] # (name, node)
        s.K='d0'
        w={t:s.tid[t]+1 for t in s.triples}
        s.results=s.triple(list(range(h)), w)
        for S in s.triples: s.emit(S, s.results[S], 1)   # +1/2
        if retain is not None:
            for i in range(h):
                if i!=retain: s.retained.append((('E',i), s.results[(i,)]))
            s.retained.append((('*',), s.results[()]))
        s.K='d2'
        s.build_stars(star)
        s.prune()

    # node store ---------------------------------------------------------
    def add(s,a,b,kind=None):
        if not a: return b
        if not b: return a
        assert not s.sup[a]&s.sup[b], 'cancellation'
        kind=kind or s.K
        key=(kind, s.sup[a]|s.sup[b]); n=s.look.get(key)
        if n is None:
            n=len(s.sup); s.look[key]=n; s.sup.append(key[1]); s.args.append((a,b)); s.kind.append(kind)
        return n
    def total(s,vals):
        if not vals: return 0
        if len(vals)==1: return vals[0]
        m=len(vals)//2
        return s.add(s.total(vals[:m]), s.total(vals[m:]))
    def vector(s,vals):
        n=len(vals); pre=[0]
        for x in vals: pre.append(s.add(pre[-1],x))
        suf=[0]*(n+1)
        for i in range(n-1,-1,-1): suf[i]=s.add(vals[i],suf[i+1])
        return pre[-1],[s.add(pre[i],suf[i+1]) for i in range(n)]
    def grouping(s,pts): return [pts[i:i+2] for i in range(0,len(pts),2)]

    # paired pair-exclusion block -----------------------------------------
    def block(s,points,edges,weights):
        T=s.total
        if len(points)<=4:
            tot=lambda om: T([x for p,x in edges.items() if not set(p)&set(om)]+[x for p,x in weights.items() if p not in om])
            return tot(()),{a:tot((a,)) for a in points},{(a,b):tot((a,b)) for a,b in combinations(points,2)}
        groups=s.grouping(points); ng=len(groups); e=lambda a,b: edges[tuple(sorted((a,b)))]
        coarse={(i,j):T([e(a,b) for a in groups[i] for b in groups[j]]) for i,j in combinations(range(ng),2)}
        wt={i:T([weights[a] for a in g]+[e(a,b) for a,b in combinations(g,2)]) for i,g in enumerate(groups)}
        total,outside,far=s.block(list(range(ng)),coarse,wt)
        strips={}; sums={}
        for i,g in enumerate(groups):
            other=[j for j in range(ng) if j!=i]
            for a in g:
                carry=T([weights[u] for u in g if u!=a])
                vals=[T([e(u,v) for u in g if u!=a for v in groups[j]]) for j in other]
                st,one=s.vector([carry]+vals)
                strips[a]={j:z for j,z in zip(other,one[1:])}; sums[a]=st
        out={}; single={a:s.add(outside[i],sums[a]) for i,g in enumerate(groups) for a in g}
        for i,g in enumerate(groups):
            for a,b in combinations(g,2): out[a,b]=outside[i]
        for i,j in combinations(range(ng),2):
            for a in groups[i]:
                left=s.add(far[i,j],strips[a][j])
                for b in groups[j]:
                    cross=T([e(u,v) for u in groups[i] if u!=a for v in groups[j] if v!=b])
                    out[a,b]=s.add(left,s.add(strips[b][i],cross))
        return total,single,out

    # paired triple exclusion --------------------------------------------
    def triple(s,pts,w):
        T=s.total
        subsets=[c for k in range(4) for c in combinations(pts,k)]
        if len(pts)<=s.base:
            return {c:T([v for t,v in w.items() if not set(c)&set(t)]) for c in subsets}
        groups=s.grouping(pts); ng=len(groups)
        gof={u:i for i,g in enumerate(groups) for u in g}
        cp=defaultdict(list)
        for t,v in w.items(): cp[tuple(sorted({gof[u] for u in t}))].append(v)
        coarse={c:T(xs) for c,xs in cp.items()}
        oc=s.triple(list(range(ng)),coarse)
        one={}
        for u in pts:
            g=gof[u]; others=[j for j in range(ng) if j!=g]
            pieces=defaultdict(list)
            for t,v in w.items():
                if u not in t: continue
                rest=[a for a in t if a!=u]
                if any(gof[a]==g for a in rest): continue
                pieces[tuple(sorted({gof[a] for a in rest}))].append(v)
            coeff={c:T(xs) for c,xs in pieces.items()}
            edges={c:coeff.get(c,0) for c in combinations(others,2)}
            weights={j:coeff.get((j,),0) for j in others}
            tot,single,pair=s.block(others,edges,weights)
            const=coeff.get((),0)
            one[u]={():s.add(const,tot)}
            one[u].update({(j,):s.add(const,x) for j,x in single.items()})
            one[u].update({c:s.add(const,x) for c,x in pair.items()})
        two={}
        for u,v in combinations(pts,2):
            i,j=gof[u],gof[v]
            if i==j: continue
            others=[k for k in range(ng) if k not in (i,j)]
            vals=[T([w.get(tuple(sorted((u,v,a))),0) for a in groups[k]]) for k in others]
            tot,leave=s.vector([w.get((u,v),0)]+vals)
            two[u,v]={():tot}|{(k,):x for k,x in zip(others,leave[1:])}
        res={}
        for ex in subsets:
            E=set(ex); G=tuple(sorted({gof[a] for a in E}))
            surv=[u for i in G for u in groups[i] if u not in E]
            assert len(surv)<=3
            pc={():oc[G]}
            for u in surv: pc[u,]=one[u][tuple(i for i in G if i!=gof[u])]
            for u,v in combinations(surv,2): pc[u,v]=two[u,v][tuple(i for i in G if i not in (gof[u],gof[v]))]
            if len(surv)==3:
                pc[tuple(surv)]=w.get(tuple(surv),0)
                a,b,c=surv; order=[(),(a,),(b,),(a,b),(c,),(a,c),(b,c),(a,b,c)]
            else: order=[c for k in range(len(surv)+1) for c in combinations(surv,k)]
            res[ex]=T([pc[c] for c in order])
        return res

    # pair stars ---------------------------------------------------------
    def x(s,*p): return s.tid[tuple(sorted(p))]+1
    def build_stars(s,mode):
        h=s.h
        for a,b in combinations(range(h),2):
            oth=[u for u in range(h) if u not in (a,b)]; n=len(oth)
            pre=[0]
            for u in oth: pre.append(s.add(pre[-1],s.x(a,b,u)))
            suf=[0]*(n+1)
            for i in range(n-1,-1,-1): suf[i]=s.add(s.x(a,b,oth[i]),suf[i+1])
            for i,c in enumerate(oth):
                S=tuple(sorted((a,b,c)))
                s.emit(S,pre[i],-1); s.emit(S,suf[i+1],-1)

    def cover(s,n):
        if n not in s.cov:
            sp=s.sup[n]; m=0
            while sp:
                lo=sp&-sp; m|=sum(1<<p for p in s.triples[lo.bit_length()-1]); sp^=lo
            s.cov[n]=m
        return s.cov[n]
    def emit(s,S,n,coef):
        if not n: return
        Sm=sum(1<<p for p in S)
        if s.cover(n)|Sm==(1<<s.h)-1:
            a,b=s.args[n]; s.emit(S,a,coef); s.emit(S,b,coef)
        else: s.pieces.append((S,n,coef))
    def prune(s):
        s.active=set(); st=[n for _,n,_ in s.pieces]+[n for _,n in s.retained]
        while st:
            n=st.pop()
            if n in s.active: continue
            s.active.add(n)
            if s.args[n]: st.extend(s.args[n])
        s.additions=sum(1 for n in s.active if s.args[n])
        s.roles=s.additions+len(s.pieces)+len(s.retained)
    def stats(s):
        return dict(h=s.h,v=len(s.triples),add=s.additions,pieces=len(s.pieces),retained=len(s.retained),R=s.roles,
                    d0=sum(1 for n in s.active if s.kind[n]=='d0'),d2=sum(1 for n in s.active if s.kind[n]=='d2'))

if __name__=='__main__':
    import json,time
    for h in map(int,sys.argv[1:]):
        t=time.time(); c=Side(h); print(json.dumps(c.stats()),round(time.time()-t,1),flush=True)
