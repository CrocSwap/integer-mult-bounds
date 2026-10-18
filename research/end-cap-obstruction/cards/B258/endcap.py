# B258: per violating y, final frame geometry vs perp(P_t). usage: endcap.py WORD.json.gz [...]
import gzip,json,sys
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
V=G.V=C.V=112
def sp(B): return G.span(B)
for path in sys.argv[1:]:
    w=json.loads(gzip.decompress(open(path,'rb').read()))
    R=w['report']['R'];n=2*V+R;P=w['ports']
    cur={r:((P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())) for r in range(n)}
    for part in 'AB':
        for e in w[part]:
            F=e[-1]
            for r in [e[1]]+([e[2]] if e[0]=='add' else []): cur[r]=G.basis(list(cur[r])+list(F))
    bad=[];d9=0;comp=0;ex=0
    for t in range(V):
        r=V+t;u=P[t];Pp=G.perp(u);c=cur[r]
        if G.basis(list(c)+list(Pp))!=Pp:
            S=sp(c);inter=len(G.basis([x for x in S if x in sp(Pp)])) if S else 0
            full=len(c)==9; uin=u in S
            d9+=full; comp+=(not uin); ex+=len(c)-inter
            bad.append((r,len(c),inter,uin))
    print(path.split('/')[-2],'R',R,'viol',len(bad),'dim9',d9,'complement-hyperplane-possible(u not in frame)',comp,'sum(dim-dim∩perp)',ex, bad[:6])
