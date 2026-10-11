"""Cube-layer interface and role classification (Design T prerequisites). Own reimplementation of w3's interface/gather logic.
usage: classify.py SNAPDIR OUT.pkl"""
import sys,pickle,collections,numpy as np
sys.path.insert(0,__import__('os').path.dirname(__file__))
from snapio import Snap,H
def interface(S):
    v,n=S.v,S.n;R=n+1;Wd=(v+63)//64
    val=np.zeros((R,Wd),np.uint64)
    for i in range(v): val[i,i//64]|=np.uint64(1)<<np.uint64(i%64)
    def its(r):
        b=np.unpackbits(val[r].view(np.uint8),bitorder='little')[:v];return tuple(np.nonzero(b)[0].tolist())
    cur=dict(S.init);part={}
    for r in range(n):
        c=S.cubeframe(S.init[r])
        if c is not None: part[r]=dict(cube=c,entry=S.init[r],fromzero=False,frames=[S.init[r]],exit=None)
    rec=S.rec
    for k in range(len(rec)):
        o,a,b,c,f,z=map(int,rec[k])
        if o==0:
            cq=S.cubeframe(c);p=part.get(a)
            if p is not None and p['exit'] is None:
                if cq==p['cube']: p['frames'].append(c)
                else: p['exit']=(c,S.dim[c],k);p['exit_content']=its(a)
            elif p is None and cq is not None and S.dim[cur[a]]==0:
                part[a]=dict(cube=cq,entry=c,fromzero=True,frames=[c],exit=None,firstk=k)
            cur[a]=c
        elif o==1:
            if c&1: val[a]^=val[b]
        elif o==2: val[n]=val[a]
        elif o==3: val[n]=0
    return part
def roles(S,part):
    v=S.v;dim=S.dim;cnt=collections.Counter();cubes=collections.defaultdict(set)
    for r,d in part.items(): cubes[d['cube']].add(r)
    info={}
    for cube,regs in cubes.items():
        items=sorted(i for i in range(v) if S.cube_of[i]==cube)
        C=dict(items=items,byb={S.bits[i]:i for i in items},BH={},single={},carrier=[],death=[],upper=[],other=[],X={})
        for r in regs:
            d=part[r];e=d['exit']
            if r<v: C['X'][r]=d;continue
            if r<2*v or e is None:
                C['other'].append(r);cnt['noexit' if r>=2*v else 'Y']+=1;continue
            c=d.get('exit_content',());last=d['frames'][-1]
            if d['fromzero'] and dim[d['entry']]==3 and e[1] not in (H-1,H) and len(c)==4: C['upper'].append(r);continue
            if e[1]==H: C['death'].append(r);continue
            if e[1]==H-1 and len(c)==1: C['single'][r]=d;continue
            if len(c)==4 and dim[last]==3:
                pl=frozenset(c)
                if pl in C['BH']: cnt['dupBH']+=1
                C['BH'][pl]=(r,last,e);continue
            if d['fromzero'] and dim[d['entry']]==2 and dim[last]==2: C['other'].append(r);cnt['Mup']+=1;continue
            C['carrier'].append(r)
        info[cube]=C
        cnt['BH%d'%len(C['BH'])]+=1;cnt['S%d'%len(C['single'])]+=1;cnt['D%d'%len(C['death'])]+=1;cnt['X%d'%len(C['X'])]+=1
    return info,cnt
if __name__=='__main__':
    S=Snap(sys.argv[1]);part=interface(S);info,cnt=roles(S,part)
    print(sorted(cnt.items()))
    pickle.dump(dict(part=part,info=info),open(sys.argv[2],'wb'))
