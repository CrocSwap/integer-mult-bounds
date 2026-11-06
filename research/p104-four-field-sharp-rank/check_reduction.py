#!/usr/bin/env python3
"""Independent exact audit of the ordered three-sector reduction."""
import hashlib
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('rank21_audit_helpers',Path(__file__).with_name('check_rank21.py'))
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def block(a,ri,ci,q):
    return [[a[i*q+k][j*q+l] for j in ci for l in range(q)] for i in ri for k in range(q)]


def run():
    q=2; i=c.eye(q); z=c.zero(q); neg=lambda a:c.scale(-1,a)
    K=c.stack(c.beside(z,neg(i),neg(i),neg(i)),c.beside(i,z,neg(i),neg(i)),c.beside(i,i,z,neg(i)),c.beside(i,i,i,z))
    Ki=c.stack(c.beside(z,i,neg(i),i),c.beside(neg(i),z,i,neg(i)),c.beside(i,neg(i),z,i),c.beside(neg(i),i,neg(i),z))
    c.require(c.mul(K,Ki)==c.eye(4*q),'K inverse')
    J=c.stack(c.beside(z,i),c.beside(neg(i),z)); Ji=neg(J)
    F=c.stack(c.beside(z,neg(i)),c.beside(i,neg(i)))
    F2=c.mul(F,F); c.require(c.mul(F2,F)==c.eye(2*q),'F cubed')
    N=c.stack(c.beside(i,z),c.beside(i,z))
    T0=c.stack(c.beside(i,neg(i)),c.beside(z,i))
    far=c.stack(c.beside(neg(i),i),c.beside(i,neg(i)))
    supports=[[0,1],[1,2],[2,3]]
    c.require(block(Ki,supports[0],supports[1],q)==T0,'XY cross block')
    c.require(block(Ki,supports[1],supports[2],q)==T0,'YZ cross block')
    c.require(block(Ki,supports[0],supports[2],q)==far,'XZ cross block')
    c.require(c.mul(Ji,T0)==F,'adjacent forward factor')
    c.require(c.mul(Ji,block(Ki,supports[1],supports[0],q))==F2,'adjacent reverse factor')
    D=c.mul(Ji,far)
    c.require(c.mul(D,F)==N,'far forward multiplier')
    c.require(c.mul(F2,neg(D))==c.sub(c.eye(2*q),N),'far reverse multiplier')
    uu,vv,rr,pp,h,masks=c.fixture(); hi=c.inverse(h)
    U=c.beside(uu[0],uu[1],uu[3],uu[4]); Ui=c.inverse(U)
    V=c.stack(vv[0],vv[1],vv[3],vv[4]); c.require(c.mul(V,U)==K,'selected Gram')
    ms=[]; dimensions=[]
    for mask,support in zip([3,6,12],supports):
        emat=c.mul(c.mul(h,c.mat([[int(a==b and masks[a]==mask) for b in range(8)] for a in range(8)])),hi)
        e=c.mul(c.mul(Ui,emat),U)
        m=c.mul(K,e)
        c.require(c.mul(c.mul(m,Ki),m)==m,'sector idempotence')
        allowed={j*q+k for j in support for k in range(q)}
        c.require(all(m[a][b]==0 for a in range(8) for b in range(8) if a not in allowed or b not in allowed),'sector row and column support')
        mb=block(m,support,support,q); ms.append(mb); dimensions.append(c.rank(mb))
    px,py,pz=[c.mul(m,J) for m in ms]
    P=px; Q=c.mul(c.mul(F,py),F2); R=c.mul(c.mul(F2,pz),F)
    zero=c.zero(2*q)
    for a in [P,Q,R]: c.require(c.mul(a,a)==a,'reduced idempotent')
    for a,b in [(P,Q),(Q,P),(Q,R),(R,Q)]: c.require(c.mul(a,b)==zero,'adjacent orthogonality')
    c.require(c.mul(c.mul(P,N),R)==zero,'PNR')
    c.require(c.mul(c.mul(R,c.sub(c.eye(2*q),N)),P)==zero,'R(I-N)P')
    c.require(c.mul(P,R)!=zero,'control: replacing N by I fails')
    c.require(c.mul(R,P)!=zero,'control: replacing I-N by I fails')
    c.require(dimensions==[2,1,2],'equality dimensions')
    print(json.dumps({'status':'PASS_INDEPENDENT_ORDERED_REDUCTION','dimensions_xyz':dimensions,'q':q,'sum_capacity':sum(dimensions),'capacity_bound':'5q/2','controls':2,'scope':'Exact scalar-block identity audit and equality-fixture audit. Universal subspace argument reviewed separately.'},indent=2))

if __name__=='__main__': run()
