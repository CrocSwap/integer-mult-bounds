"""alias_build.py WORD_IN WORD_OUT PATCH_OUT h:L[:E,E,..] ... -- builds dirty-borrow aliases (helper h -> retired lender L, warp U->E with an explicit invertible G, E = entrance frame of h by default) on a BORROW-WORD and writes the patch (new/borrow/inputs/alias2_43*.json were produced by: alias_build.py <PR2526 shipped word> ... 606:68 653:49:288,160,75,25)."""
import json,gzip,sys,copy,random
from collections import Counter
from pathlib import Path as _P;sys.path.insert(0,str(_P(__file__).resolve().parent))
from audit_local import basis,contained,registers
import word_patch
def load(p):return json.loads(gzip.decompress(open(p,'rb').read()))
def lin(cols,x):
    o=0
    for i,c in enumerate(cols):
        if x>>i&1:o^=c
    return o
def rk(xs):return len(basis(list(xs)))
def make_G(U,E,n=9):
    """deterministic invertible G with G(U)=E: U basis -> E basis, completed by unit vectors on both sides"""
    U=list(U);E=list(E);assert len(U)==len(E)
    src=list(U);dst=list(E)
    for i in range(n):
        if rk(src+[1<<i])>len(src):src.append(1<<i)
    for i in range(n):
        if rk(dst+[1<<i])>len(dst):dst.append(1<<i)
    img={0:0}
    for i in range(n):
        for k,v in list(img.items()):img[k^src[i]]=v^dst[i]
    cols=[img[1<<j] for j in range(n)];assert rk(cols)==n
    assert basis([lin(cols,x) for x in U])==basis(E)
    return cols
def frame_at_B(w,r,P):
    """frame of register r just before B[P] (after warps at P are NOT applied)"""
    v=112;start={int(q):basis(U) for q,U in w['start_extra'].items()}
    cur=basis([w['ports'][r]]) if r<v else start.get(r,())
    for e in w['A']:
        if e[0]=='warp':
            if e[1]==r:cur=basis(e[4] if e[2]>0 else e[3])
            continue
        if r in registers(e):cur=basis(e[-1])
    byp={}
    for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append(op)
    for p in range(P+1):
        for op in byp.get(p,[]):
            if p<P and w['warps'][op-1][1]==r:cur=basis(w['warps'][op-1][4])
            if p==P and w['warps'][op-1][1]==r:raise RuntimeError('lender already warped at P')
        if p<P and r in registers(w['B'][p]):cur=basis(w['B'][p][-1])
    return cur
def alias(w,h,L,E=None):
    w=copy.deepcopy(w);rs=word_patch.restored_of(w)
    assert str(h) not in w['helper_final'] and h not in rs
    first=min(p for p,e in enumerate(w['B']) if e[0]!='warp' and h in registers(e))
    assert not any(h in registers(e) for sec in ('precondition','compensation','A','cut') for e in w[sec] if e[0]!='warp')
    lastL=max([p for p,e in enumerate(w['B']) if L in registers(e)],default=-1)
    assert lastL<first and not any(L in registers(e) for e in w['restore']),('lender not retired',L,lastL,first)
    assert all(not(rec[1]==L and rec[0]>lastL) for rec in w['warps']),'lender warped after retirement'
    U=frame_at_B(w,L,first);S=basis(w['start_extra'][str(h)]);F1=basis(w['B'][first][-1])
    if E is None:E=S
    E=basis(E);assert len(E)==len(U) and contained(E,F1),(U,E,F1)
    G=make_G(U,E)
    for sec,start in (('B',first),('restore',0)):
        for i in range(start,len(w[sec])):
            e=w[sec][i]
            if e[0]=='add':
                if e[1]==h:e[1]=L
                if e[2]==h:e[2]=L
            elif e[1]==h:e[1]=L
    w['warps'].append([first,L,G,list(U),list(E)])
    del w['start_extra'][str(h)];w['removed']=w['removed']+[h]
    t=copy.deepcopy(w);t['A']=w['A'][w.get('prelude_events',0):]
    w['cleanup']=word_patch.derive_cleanup(t,rs)
    return w,dict(h=h,L=L,pos=first,U=list(U),E=list(E),G=G)
def profile(w):
    """recompute the paid profile and width inventory exactly as audit_local does (no algebra)"""
    v=112;n=2*v+w['report']['R'];h=9;full=basis([1<<i for i in range(h)])
    removed=set(w['removed']);live=[r for r in range(n) if r not in removed]
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*w['report']['R']
    for q,U in w['helper_final'].items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+w['report']['R'])
    for q,U in w['start_extra'].items():start[int(q)]=basis(U)
    cur=start.copy();paid=Counter()
    def climb(q,U):
        U=basis(U);assert contained(cur[q],U),('nonmonotone',q,cur[q],U)
        d=len(U)-len(cur[q])
        if d:paid[d]+=1
        cur[q]=U
    npre=w.get('prelude_events',0)
    for e in w['A'][:npre]:
        if e[0]=='warp':cur[e[1]]=basis(e[4])
        else:
            for q in registers(e):climb(q,e[-1])
    for e in w['A'][npre:]:
        for q in registers(e):climb(q,e[-1])
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for q,U in zip(w['centers'],w['center_frames']):
        U=basis(U);served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
        for T in sorted(served,key=lambda x:-len(x)):
            if T!=U:paid[len(U)-len(T)]+=1
            U=T
    byp={}
    for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append(op)
    for p in range(len(w['B'])+1):
        for op in byp.get(p,[]):
            rec=w['warps'][op-1];assert cur[rec[1]]==basis(rec[3]),('warp frame',op);cur[rec[1]]=basis(rec[4])
        if p<len(w['B']):
            for q in registers(w['B'][p]):climb(q,w['B'][p][-1])
    for e in w['restore']:
        for q in registers(e):climb(q,e[-1])
    for q in live:climb(q,end[q])
    inv=Counter(len(end[q])-len(start[q]) for q in range(2*v,n) if q in set(live))
    return {str(k):paid[k] for k in sorted(paid)},{str(k):inv[k] for k in sorted(inv)}
if __name__=='__main__':
    w0=load(sys.argv[1]);w=w0;recs=[]
    for spec in sys.argv[4:]:
        parts=spec.split(':');h,L=int(parts[0]),int(parts[1]);E=[int(x) for x in parts[2].split(',')] if len(parts)>2 else None
        w,r=alias(w,h,L,E);recs.append(r)
    lp,wi=profile(w);w['report']=dict(w['report'],local_profile=lp,width_inventory=wi)
    print('profile',lp,'widths',wi)
    open(sys.argv[2],'wb').write(gzip.compress(json.dumps(w,separators=(',',':')).encode()))
    patch=dict(kind='EXTRA_ALIASES_ON_ALIAS637',aliases=recs,fields={k:w[k] for k in ('start_extra','removed','B','restore','warps')},report=w['report'],prelude_events=w['prelude_events'],
               declared_gate_edit=word_patch.kernel_gate_edit(w0['B'],w['B']))
    open(sys.argv[3],'w').write(json.dumps(patch,separators=(',',':')))
