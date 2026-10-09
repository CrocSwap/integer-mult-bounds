#!/usr/bin/env python3
"""Exact Gaussian-dyadic schedule and endpoint controls; not a final theorem.
Zhihao Chen / Codex. Pinned producer: Swapnil Jain, Apache-2.0.
"""
import sys,json,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'swapnil-round7/independent/complex-twostage'))
from producer import NStar3,compile_roles

def word(h):
    c=NStar3(h);k=compile_roles(c);v=len(c.triples);R=k['size'];off=2*v
    # Each event is dst += (numerator/denominator)*src.
    L=[];V=[];J=[];C=[]
    for n,ins,outs in k['gates']:
        if len(ins)==2:L.append((off+ins[0],off+ins[1],1,1))
        L.extend((off+o,off+outs[0],1,1) for o in outs[1:])
    V=[(off+s,c.tid[t],1,1) for t,s in k['src'].items()]
    J=[(v+c.tid[t],off+k['pout'][i],cf,2) for i,(t,n,cf) in enumerate(c.pieces)]
    ret=k['rout'];star=off+ret[('*',)]
    for j,T in enumerate(c.triples):
        if h-1 not in T:
            C.append((v+j,star,2,2));C.extend((v+j,off+ret[('E',i)],-1,2) for i in T)
        else:
            C.append((v+j,star,5-h,2));C.extend((v+j,off+ret[('E',i)],1,2) for i in range(h-1) if i not in T)
    inv=lambda a:[(t,s,-n,d) for t,s,n,d in reversed(a)]
    ops=L+inv(C)+inv(J)+inv(L)+V+L+C+J+inv(L)+inv(V)
    bank=lambda s:s+v if s<v else s-v if s<2*v else s
    reverse=[(bank(t),bank(s),n,d) for t,s,n,d in inv(ops)]
    return c,k,ops,reverse

def replay(v,R,ops,reverse=False):
    # Signed base encoding: an L1 bound below the base proves injectivity.
    # All registers initially represent twice a formal basis vector.
    width=64;size=2*v+R;vals=[2<<(width*i) for i in range(size)];bound=[2]*size
    peak=2
    for t,s,n,d in ops:
        assert n*vals[s]%d==0
        vals[t]+=n*vals[s]//d
        bound[t]+=(abs(n)*bound[s]+d-1)//d;peak=max(peak,bound[t])
    assert peak+4 < 1<<width
    expected=[2<<(width*i) for i in range(size)]
    for i in range(v):
        if reverse:expected[i]-=2<<(width*(i+v))
        else:expected[i+v]+=2<<(width*i)
    return vals==expected,peak

def phases():
    # All 2^16 Fourier addresses for two distinct weight-three tensor lines.
    h=4;m=16;p=7;q=14;U=sum(1<<(i*h+j) for i in range(h) for j in range(h) if p>>i&1 and q>>j&1)
    def parity(a):return a.bit_count()&1
    def tq(z):return sum(q<<(i*h) for i in range(h) if parity((z>>(i*h))&q))
    def pi(z):
        col=0
        for j in range(h):
            if parity(sum(((z>>(i*h+j))&1)<<i for i in range(h))&p):col|=1<<j
        return sum(col<<(i*h) for i in range(h) if p>>i&1)
    bad_no_inverse=bad_no_wrapper=0
    # Fourth roots represented exactly as Gaussian integer pairs.
    units=((1,0),(0,1),(-1,0),(0,-1))
    def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    add=lambda a,b:(a[0]+b[0],a[1]+b[1])
    neg=lambda a:(-a[0],-a[1])
    for z in range(1<<m):
        uz=U if parity(z&U) else 0;T=tq(z);P=pi(z);B=z^P
        X2=B^uz;Y1=T^uz;C=B^tq(B)
        assert X2^T==B^Y1==C
        wt=z.bit_count()%4;u=uz.bit_count()%4
        assert (X2.bit_count()-T.bit_count()-C.bit_count())%4==0
        assert (B.bit_count()-Y1.bit_count()-C.bit_count())%4==0
        assert ((z^uz).bit_count()+u-wt)%4==0
        assert u%2==parity(z&U)  # P_U*1=U, so residual is an address translation.
        # Source phase q_U; after forward and inverse opposite shear:
        # X=-i^wt*y; Y=i^(wt-2u)*x+i^(wt-u)*y.
        # Pre-translate x by (-1)^u; copy X through C_U^-1 into Y.
        Xy=neg(units[wt]);Yx=mul(units[(wt-2*u)%4],units[(2*u)%4]);Yy=units[(wt-u)%4]
        assert Yx==units[wt] and add(Yy,mul(units[-u%4],Xy))==(0,0)
        if add(Yy,mul(units[u],Xy))!=(0,0):bad_no_inverse+=1
        if units[(wt-2*u)%4]!=units[wt]:bad_no_wrapper+=1
    assert bad_no_inverse and bad_no_wrapper
    return dict(addresses=1<<m,connector_and_endpoint_identities=True,
                wrong_forward_correction_failures=bad_no_inverse,omitted_translation_failures=bad_no_wrapper)

def main():
    st=time.monotonic();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('120s')));signal.alarm(120)
    rows=[]
    for h in (8,10):
        c,k,ops,rev=word(h);v=len(c.triples)
        a,ba=replay(v,k['size'],ops);b,bb=replay(v,k['size'],rev,True);assert a and b
        # Wrong inverse sign and omitted first cancellation are actual word mutations.
        wrong=[(t,s,-n,d) for t,s,n,d in rev];assert not replay(v,k['size'],wrong,True)[0]
        omitted=ops[:];idx=next(i for i,(t,s,n,d) in enumerate(ops) if t>=v and t<2*v and d==2);del omitted[idx]
        assert not replay(v,k['size'],omitted)[0]
        rows.append(dict(h=h,roles=k['size'],formal_basis=2*v+k['size'],events=len(ops),forward=True,inverse_opposite=True,coefficient_bound=max(ba,bb),negative_controls=2))
    out=dict(rows=rows,phase=phases(),elapsed=time.monotonic()-st,limit_seconds=120,
             scope='Complete exact dyadic small scalar words and all-address tensor phase controls. General commutator/phase argument in report. No h24 physical trace, precision/tape or final assembly certification.',new_multiplication_bound=False)
    (HERE/'round6-complex-interface-controls.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));signal.alarm(0)
if __name__=='__main__':main()
