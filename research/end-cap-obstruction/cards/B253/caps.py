import gzip,json,sys
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()))
V=112;R=w['report']['R'];n=2*V+R;P=w['ports']
cur={}
for r in range(n): cur[r]=(P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())
first={}
for part in 'AB':
    for i,e in enumerate(w[part]):
        F=G.basis(e[-1]);rr=[e[1]]+([e[2]] if e[0]=='add' else [])
        for r in rr:
            nf=G.basis(list(cur[r])+list(F))
            if r in range(V,2*V) and r not in first and G.basis(list(nf)+list(G.perp(P[r-V])))!=G.perp(P[r-V]): first[r]=(part,i,e[:3])
            cur[r]=nf
bad=[r for r in range(V,2*V) if G.basis(list(cur[r])+list(G.perp(P[r-V])))!=G.perp(P[r-V])]
print('final cap violators',bad)
for r in bad: print(r,first.get(r))
