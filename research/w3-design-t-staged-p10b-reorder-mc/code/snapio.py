"""Snapshot IO + cube geometry for the p10b word (h=20). Own implementation."""
import json,collections,numpy as np,os
H=20
LAB=[tuple(l) for l in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','labels.json')))['lab']]
class Snap:
    def __init__(s,d):
        s.d=d;st=json.load(open(d+'/249-states.json'));fr=json.load(open(d+'/frames.json'))
        s.st=st;s.fr=fr;s.F=fr['frames'];s.v=st['v'];s.n=st['n'];s.ZERO=st['ZERO'];s.FULL=st['FULL']
        s.dim={int(k):len(x['B']) for k,x in s.F.items()}
        s.rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
        s.init={r:int(st['initial'][str(r)]) for r in range(s.n)};s.fin={r:int(st['final'][str(r)]) for r in range(s.n)}
        v=s.v;s.chi=np.zeros((v,H),dtype=np.int64)
        for i in range(v):
            for p in LAB[i]: s.chi[i,p]=1
        s.cube_of=[tuple(sorted(p//2 for p in LAB[i])) for i in range(v)]
        s.bits=[tuple(p%2 for p in LAB[i]) for i in range(v)]
        s._ic={}
        s.moves=collections.defaultdict(list)
        for k in np.nonzero(s.rec[:,0]==0)[0]: s.moves[int(s.rec[k,1])].append(int(k))
    def items_in(s,f):
        if f in s._ic: return s._ic[f]
        r=None
        if 1<=s.dim[f]<=3:
            A=np.array(s.F[str(f)]['A'],dtype=np.int64)
            I=frozenset(np.nonzero(np.all(s.chi@A.T==0,axis=1))[0].tolist())
            r=I or None
        s._ic[f]=r;return r
    def cubeframe(s,f):
        I=s.items_in(f)
        if not I: return None
        cs={s.cube_of[i] for i in I}
        return next(iter(cs)) if len(cs)==1 else None
