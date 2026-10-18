import sys,pickle;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pipeline import *
TPLA=[('y1','a3'),('y2','a4'),('h1','a0'),('h0','a2'),('a2','a0'),('y3','a1'),('a1','a3'),('h0','a4'),('y0','a1'),('y3','h0'),('h1','a1'),('y2','h1'),('y1','a2'),('a2','a1'),('y1','a4'),('y0','h0'),('y3','a0')]
TPLB=[('h0','a0'),('h1','a1'),('y3','a2'),('y2','a3'),('a2','a3'),('y0','a4'),('y1','a2'),('h1','a2'),('a0','a1'),('y0','h1'),('h0','a4'),('y3','a0'),('a2','a0'),('y3','a4'),('y2','h0'),('y1','h0'),('y2','a1')]
TPL2=[('y1','a3'),('y0','a2'),('y3','a0'),('h','a1'),('y2','a4'),('y0','a4'),('a1','a3'),('y2','h'),('y2','a3'),('y3','a2'),('y0','h'),('y1','a0'),('a1','a0'),('y1','a2'),('a2','a1'),('y3','a4'),('y2','a0'),('y1','a4'),('y3','h'),('y0','a3')]
TPL=[('y1','a0'),('y0','a1'),('h','a4'),('y2','a3'),('y3','a2'),('a1','a0'),('y2','y0'),('y1','y3'),('y2','a4'),('y3','a1'),('a2','a3'),('y0','a2'),('y2','a0'),('y1','h'),('y0','a4'),('a1','a2'),('y3','h'),('y1','a3')]
def zcopy(W,K):
    z=K['atoms'][4]
    for c in K['copies']:
        if any(e[0]=='add' and e[1]==c and e[2]==z for e in W):return c
OWN=None
import os as _os
LATE=bool(_os.environ.get('PCELL_LATE'))
def instantiate(W,K,tpl):
    a=K['atoms'];h=zcopy(W,K)
    own={t:OWN[t][0] for t in K['targets']}
    want=[a[1],a[0],a[3],a[2]]
    y=[v+next(t for t in K['targets'] if own[t]==w) for w in want]
    nm={'a%d'%i:a[i] for i in range(5)};nm.update({'y%d'%i:y[i] for i in range(4)});nm['h']=h
    return [(nm[t],nm[s]) for t,s in tpl],h
def apply_key(W,d,P,n,key,tpl,host=None):
    host=host or _os.environ.get('PCELL_HOST','a1')
    tpl=globals()[_os.environ['PCELL_TPL']] if _os.environ.get('PCELL_TPL') else tpl
    global OWN;OWN=d['own_rows']
    K=key_parts(d,W,key);dele=segment(d,W,K);sym,bad=symbolic(W,K,dele,n)
    if bad:return None,'window %s'%bad[:2],K
    if LATE:K['own']={t:OWN[t][0] for t in K['targets']}
    sol,h=instantiate(W,K,tpl)
    hreg={'a%d'%i:K['atoms'][i] for i in range(5)}[host]
    NW=build(W,K,sym,dele,sol,hreg,newh=[h])
    return NW,'ok',K
if __name__=='__main__':
    d,P,W,n=load(__import__('os').environ['PC_CENSUS'],__import__('os').environ['PC_PROTO'])
    H0,_=replay(W,P,n);OWN=d['own_rows']
    keys=[((0,2),-1),((0,2),1),((0,3),-1),((0,3),1),((1,2),-1),((1,2),1),((1,3),-1),((1,3),1),((4,6),-1),((4,6),1),((4,7),-1),((4,7),1),((5,6),-1),((5,6),1),((5,7),-1),((5,7),1)]
    for key in keys:
        NW,st,K=apply_key(W,d,P,n,key,TPL)
        if NW is None:print(key,st);continue
        bad,fb,dH=check(W,NW,K,K['atoms'][1],n,P,H0)
        bad=[x for x in bad if x!=('host',K['atoms'][1]) or K['M']==K['atoms'][1]]
        print(key,'rows',bad[:4],'frames',fb[:3],'dH',sorted(dH.items()),'fee %.4f'%fee(dH))
def joint(W,d,P,n,keys,tpl):
    W0=W;H0,_=replay(W,P,n);R0=rows_of(W,n)
    for key in keys:
        NW,st,K=apply_key(W,d,P,n,key,tpl)
        assert NW is not None,(key,st)
        W=NW
    R=rows_of(W,n);H,fb=replay(W,P,n)
    rm=set()
    for key in keys:
        K=key_parts(d,W0,key);rm|=set(K['copies'])-{zcopy(W0,K)}
    badrows=[x for x in range(n) if x not in rm and R[x]!=R0[x] and not any(x in key_parts(d,W0,k)['atoms'] for k in keys)]
    dH=Counter(H);dH.subtract(H0);dH={a:b for a,b in dH.items() if b}
    return W,badrows,fb,dH,rm
if __name__=='__main__' and len(sys.argv)>1:
    keys=[((0,2),-1),((0,2),1),((0,3),-1),((0,3),1),((1,2),-1),((1,2),1),((1,3),-1),((1,3),1)]
    if sys.argv[1]=='all':keys+=[((4,6),-1),((4,6),1),((4,7),-1),((4,7),1),((5,6),-1),((5,6),1),((5,7),-1),((5,7),1)]
    W2,br,fb,dH,rm=joint(W,d,P,n,keys,TPL)
    print('JOINT rows',br[:5],'frames',fb[:5],'dH',sorted(dH.items()),'removed',len(rm))
    pickle.dump(dict(W=W2,rm=sorted(rm)),open(__import__('os').environ.get('PC_OUT','.')+'/joint.pkl','wb'))

def apply_key2(W,d,n,key):
    """two-helper templates: class by third block; kept helpers = z copy (h0) and the copy read by role R (h1)."""
    global OWN;OWN=d['own_rows']
    K=key_parts(d,W,key);dele=segment(d,W,K);sym,bad=symbolic(W,K,dele,n)
    if bad:return None,'window %s'%bad[:2],K,None
    K['own']={t:OWN[t][0] for t in K['targets']}
    a=K['atoms'];own=K['own']
    want=[a[1],a[0],a[3],a[2]];order=[next(t for t in K['targets'] if own[t]==w) for w in want]
    y=[v+t for t in order]
    zc=zcopy(W,K)
    zr={i for i in range(4) if any(e[0]=='add' and e[1]==y[i] and e[2]==zc for e in W)}
    SIG={'a0':'a1','a1':'a0','a2':'a3','a3':'a2','y0':'y1','y1':'y0','y2':'y3','y3':'y2','a4':'a4','h0':'h0','h1':'h1'}
    base={(0,3):(TPLA,2),(1,2):(TPLB,0)}
    if K['c3']==(0,1,2,3):tpl,role,zb=TPLA,2,{0,3}
    else:tpl,role,zb=TPLB,0,{1,2}
    if zr!=zb:
        assert zr=={ {0:1,1:0,2:3,3:2}[i] for i in zb},(key,zr)
        tpl=[(SIG[t],SIG[s_]) for t,s_ in tpl];role={0:1,1:0,2:3,3:2}[role]
    h1=next(c for c in K['copies'] if c!=zc and any(e[0]=='add' and e[1]==y[role] and e[2]==c for e in W))
    nm={'a%d'%i:a[i] for i in range(5)};nm.update({'y%d'%i:y[i] for i in range(4)});nm['h0']=zc;nm['h1']=h1
    sol=[(nm[t],nm[s]) for t,s in tpl]
    # host = atom whose final set is M
    sets={r:{i} for i,r in enumerate(a)};sets.update({zc:set(),h1:set()});sets.update({r:set() for r in y})
    for t,s_ in sol:sets[t]=sets[t]|sets[s_]
    host=next(r for r in a if sets[r]==set(sym[K['M']]))
    r_,c_,mu=coeffs(K,sym);alpha={x:1/c_[i] for i,x in enumerate(a)}
    src=lambda h:next(e[2] for e in W if e[0]=='add' and e[1]==h and e[2] in a)
    halpha={zc:alpha[src(zc)],h1:alpha[src(h1)]}
    NW=build(W,K,sym,dele,sol,host,newh=[zc,h1],halpha=halpha)
    return NW,'ok',K,dict(host=host,kept=[zc,h1],removed=sorted(set(K['copies'])-{zc,h1}))

def apply_key3(W,d,n,key,newreg):
    """TPL2 (one helper, no Y+=Y, own rows inside) with a FRESH helper register newreg (no entrance)."""
    global OWN;OWN=d['own_rows']
    K=key_parts(d,W,key);dele=segment(d,W,K);sym,bad=symbolic(W,K,dele,n)
    if bad:return None,'window %s'%bad[:2],K,None
    K['own']={t:OWN[t][0] for t in K['targets']}
    a=K['atoms'];own=K['own']
    want=[a[1],a[0],a[3],a[2]];order=[next(t for t in K['targets'] if own[t]==w) for w in want]
    y=[v+t for t in order]
    nm={'a%d'%i:a[i] for i in range(5)};nm.update({'y%d'%i:y[i] for i in range(4)});nm['h']=newreg
    sol=[(nm[t],nm[s_]) for t,s_ in TPL2]
    sets={r:{i} for i,r in enumerate(a)};sets[newreg]=set();sets.update({r:set() for r in y})
    for t,s_ in sol:sets[t]=sets[t]|sets[s_]
    host=next(r for r in a if sets[r]==set(sym[K['M']]))
    NW=build(W,K,sym,dele,sol,host,newh=[newreg])
    return NW,'ok',K,dict(host=host,removed=sorted(K['copies']))
