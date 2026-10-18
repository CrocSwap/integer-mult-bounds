import gzip,json,sys,os
GK=__import__('os').environ['EO_ROOT']+'/inputs/repo/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
sys.path.insert(0,GK)
import gk_word as G,gk_common as C
G.V=C.V=112
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()))
watch=[int(x) for x in sys.argv[2].split(',')]
V=112;R=w['report']['R'];n=2*V+R;P=w['ports']
cur={}
for r in range(n): cur[r]=(P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())
tgt=G.perp(P[watch[0]-V]) if V<=watch[0]<2*V else None
print('target',tgt)
for part in 'AB':
    for i,e in enumerate(w[part]):
        F=G.basis(e[-1])
        rr=[e[1]]+([e[2]] if e[0]=='add' else [])
        if any(r in watch for r in rr):
            print(part,i,e[:-1],'dim',len(F),'cur',[len(cur[r]) for r in rr], 'inperp' , [G.basis(list(F)+list(tgt))==tgt for _ in [0]] if tgt else '')
        for r in rr:
            if tuple(cur[r])!=tuple(F) and G.basis(list(cur[r])+list(F))==F: cur[r]=F
            elif tuple(cur[r])!=tuple(F): print('  VIOL',part,i,r)
