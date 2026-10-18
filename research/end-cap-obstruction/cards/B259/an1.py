import gzip,json,sys,itertools,collections
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
V=G.V=C.V=112
sp=G.span
def load(p): return json.loads(gzip.decompress(open(p,'rb').read()))
def frames(w):
    R=w['report']['R'];n=2*V+R;P=w['ports']
    cur={r:((P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())) for r in range(n)}
    readers=collections.defaultdict(set)
    for part in 'AB':
        for e in w[part]:
            F=e[-1]
            if e[0]=='add': readers[e[1]].add(e[2])
            for r in [e[1]]+([e[2]] if e[0]=='add' else []): cur[r]=G.basis(list(cur[r])+list(F))
    return cur,readers
def dimint(spaces_perp_vecs):  # dim of intersection of u^perp over vectors
    b=[]
    for v in spaces_perp_vecs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return 9-len(b)
def perpset(vs): return G.perp_of(vs) if hasattr(G,'perp_of') else None
if __name__=='__main__':
    w=load(sys.argv[1]);P=w['ports'];cur,rd=frames(w)
    bad=[]
    for t in range(V):
        r=V+t;Pp=G.perp(P[t])
        if G.basis(list(cur[r])+list(Pp))!=Pp: bad.append(t)
    print('violator targets',bad,'blocks',sorted({t//8 for t in bad}))
    # group by 4
    I=dimint([P[t] for t in bad]);print('dim ∩ over all violators',I)
    for g in range(0,len(bad),4):
        grp=bad[g:g+4];print(grp,'blocks',[t//8 for t in grp],'dim∩',dimint([P[t] for t in grp]))
