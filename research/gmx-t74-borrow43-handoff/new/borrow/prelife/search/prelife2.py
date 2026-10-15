"""prelife2.py WORD gapb.json out.json : pre-life gap borrowing (borrower L hosted on retired cold lender h) with
forward join-lifting frame repair (expBP edit.repair), all warp images E (dim |Uh|) tried; screened by price_root."""
import json,gzip,sys,copy,itertools
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..')]   # this directory and new/borrow (audit_local, word_patch, alias_build)
from audit_local import basis,contained,registers
import word_patch
from alias_build import make_G,profile
from fractions import Fraction as F
import edit
from chains import price_root
def load(p):return json.loads(gzip.decompress(open(p,'rb').read()))
def build(w,L,h,E,extra_warp_ok=False):
    w=copy.deepcopy(w);rs=word_patch.restored_of(w)
    assert str(h) in w['helper_final'] and h in rs,'lender not cold'
    assert str(L) not in w['helper_final'] and str(L) not in w['start_extra'] and L not in rs,'L cold/entering'
    for sec in ('precondition','A','cut','restore'):
        assert not any(L in registers(e) for e in w[sec] if e[0]!='warp'),'L touched in '+sec
    assert not any(h in registers(e) for e in w['restore'] if e[0]!='warp'),'h in restore'
    assert not any(rec[1]==h for rec in w['warps']),'h lender already'
    Lpos=[p for p,e in enumerate(w['B']) if L in registers(e)];first=Lpos[0]
    lasth=max([p for p,e in enumerate(w['B']) if h in registers(e)],default=-1)
    assert lasth<first,'lender not retired'
    assert not any(rec[1]==L and rec[0]<first for rec in w['warps'])
    Uh=basis(w['helper_final'][str(h)]);E=basis(E);assert len(E)==len(Uh)
    for p in Lpos:
        U=basis(w['B'][p][-1])
        if contained(E,U):break
        w['B'][p][-1]=list(basis(list(U)+list(E)))
    for i in range(first,len(w['B'])):
        e=w['B'][i]
        if e[0]=='add':
            if e[1]==L:e[1]=h
            if e[2]==L:e[2]=h
        elif e[1]==L:e[1]=h
    for rec in w['warps']:
        if rec[1]==L:rec[1]=h
    op=len(w['warps'])+1
    w['warps'].append([first,h,make_G(Uh,E),list(Uh),list(E)])
    # NB: the warp list order defines op ids; warps at the same position are applied in op order
    vec={};keep=[]
    for e in w['compensation']:
        if e[0]=='add' and e[2]==L:vec[e[1]]=vec.get(e[1],F(0))+F(e[3],e[4])
        else:keep.append(e)
    # corrections run BEFORE the (target-only, linear) precondition: pull the compensation vector back through it
    for g in reversed(w['precondition']):
        if g[0]=='add':
            if vec.get(g[2]):vec[g[1]]=vec.get(g[1],F(0))-F(g[3],g[4])*vec[g[2]]
        else:
            if g[1] in vec:vec[g[1]]=vec[g[1]]/F(g[2],g[3])
    corr=[dict(target=t,source=h,operator_word=[op],coefficient=str(c)) for t,c in sorted(vec.items()) if c]
    assert all(F(x['coefficient']).denominator&(F(x['coefficient']).denominator-1)==0 for x in corr),'non-dyadic correction'
    w['compensation']=keep;w['initial_corrections']=w['initial_corrections']+corr
    del w['helper_final'][str(h)];w['removed']=w['removed']+[L]
    import repair2
    try:repair2.run(w,TRACE,'taint')
    except AssertionError as e:raise AssertionError('repair:'+str(e))
    t=copy.deepcopy(w);t['A']=w['A'][w.get('prelude_events',0):]
    w['cleanup']=word_patch.derive_cleanup(t,rs-{h})
    lp,wi=profile(w);w['report']=dict(w['report'],local_profile=lp,width_inventory=wi)
    return w
def Es_for(w,L,h):
    """dim-d E with U0 <= E <= (first L frame of dim >= d), U0 = L's first gate frame; at most 64"""
    Uh=basis(w['helper_final'][str(h)]);d=len(Uh)
    Lpos=[p for p,e in enumerate(w['B']) if L in registers(e)]
    fr=[basis(w['B'][p][-1]) for p in Lpos];U0=fr[0]
    Fs=[f for f in fr if len(f)>=d][0]
    if len(U0)>d:return []
    vecs=[x for x in range(1,512) if len(basis(list(Fs)+[x]))==len(Fs)]
    out=set()
    for vs in itertools.combinations(vecs,d-len(U0)):
        B_=basis(list(U0)+list(vs))
        if len(B_)==d:out.add(B_)
        if len(out)>=64:break
    return sorted(out)
if __name__=='__main__':
    import repair2
    w=load(sys.argv[1]);TRACE=None
    TRACE,_=repair2.run(copy.deepcopy(w),None)
    base=w['report']['local_profile'];pairs=json.load(open(sys.argv[2]))
    b0={int(k):v for k,v in base.items()}
    res=[]
    from collections import Counter;why=Counter()
    seen=set()
    for x in pairs:
        if not x['loose'] or x['w']!=4 or (x['h'],x['L']) in seen:continue
        seen.add((x['h'],x['L']))
        try:Es=Es_for(w,x['L'],x['h'])
        except Exception as e:why['Es '+str(e)[:40]]+=1;continue
        best=None;n=0
        for E in Es:
            try:w2=build(w,x['L'],x['h'],E)
            except AssertionError as e:why[str(e)[:40]]+=1;continue
            n+=1
            lp={int(k):v for k,v in w2['report']['local_profile'].items()}
            k=price_root(b0,lp)['kappa']
            if best is None or k>best[0]:best=(k,list(E),lp,w2['report']['width_inventory'])
        if best:
            res.append(dict(h=x['h'],L=x['L'],nE=len(Es),nok=n,kappa=best[0],E=best[1],lp=best[2],wi=best[3]));print(res[-1],flush=True)
    print('base',price_root(b0,b0)['kappa']);print(why.most_common(12))
    json.dump(res,open(sys.argv[3],'w'))
