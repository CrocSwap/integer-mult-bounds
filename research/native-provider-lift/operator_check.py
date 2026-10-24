"""Portable exact-head logical/frame check in an authenticated temporary tree."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import json,gzip,sys

def need(ok,why):
    if not ok:raise ValueError(why)

def main():
    R=Path(sys.argv[1]);sys.path.insert(0,str(R/'research/joint-helper-lattice'))
    import native_joint as J
    F=J.F
    new=json.loads(gzip.decompress((R/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
    c=new['canonical'];old,base,*_=J.construct()
    need(c['frames'][:len(old['frames'])]==old['frames'],'base chart prefix')
    need(c['start'][:224]==old['start'][:224] and c['final'][:224]==old['final'][:224],'canonical main interfaces')
    need(len(c['start'])==len(c['final'])==632,'all independent fields')
    H=Counter()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r];A,B=map(F.span,(c['frames'][a],c['frames'][b]))
        need(A<B,'strict independent helper');H[len(c['frames'][b])-len(c['frames'][a])]+=1
    need(H=={4:28,7:7,8:47,9:326},'whole helper census')
    def image(cols,x):
        y=0
        for i,col in enumerate(cols):
            if x>>i&1:y^=col
        return y
    G={w['op']:w['G_columns'] for w in c['warps']}
    need(set(G)==set(range(1,73)),'all native maps')
    for cols in G.values():need(len({image(cols,x) for x in range(512)})==512,'invertible map')
    V=F.load(R/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','portable_rows')
    X=F.load(R/'research/kappa-rebuild/complex/native_extensions.py','portable_literal')
    classes=set()
    for d,p in new['programs'].items():
        need([e[1] for e in p if e[0]=='scalar']==[e[1] for e in base[d] if e[0]=='scalar'],'literal scalar word')
        need([(e[1],e[2]) for e in p if e[0]=='warp']==[(e[1],e[2]) for e in base[d] if e[0]=='warp'],'logical warp word')
        for e in p:
            if e[0]!='warp':continue
            op,a,b=e[2:5];A,B=map(F.span,(c['frames'][a],c['frames'][b]));cols=G[abs(op)]
            need(({image(cols,x) for x in A}==B) if op>0 else ({image(cols,x) for x in B}==A),'actual warp chart')
            classes.add((op,a,b))
        rows,rec=X.literal_replay(V,c,p,d=='backward')
        need(all(rows['L',r]==V.expected(('L',r),[],d=='backward',False) for r in range(632)),'all arbitrary columns')
        paid={int(k):v for k,v in rec['paid_profile'].items()}
        need(paid=={1:2201,2:412,3:510,4:127,5:40,8:8},'complete local paid invoice')
        rebound=deepcopy(c);rebound['R']=408;rebound['local_profile']=paid
        V.replay(p,rebound,[],d=='backward',False)
    print(json.dumps(dict(status='PASS',columns_per_orientation=632,orientations=2,interpreters=2,native_maps=72,map_image_columns=36864,warp_classes=len(classes),helpers=408)))
if __name__=='__main__':main()
