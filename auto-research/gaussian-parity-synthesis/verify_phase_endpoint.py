"""Independent exact audit of the PR36/46 paid phase endpoint.

Uses arbitrary Gaussian dyadics, independently controlled by Fraction.
The weight-nine mask is the actual tensor-triple line in PR46. Full tensors
are finite controls at D=9,10,11, not an execution at the physical D=784.
"""
from fractions import Fraction as Q
from itertools import product
from random import Random
import json
from pi_exact import Gaussian as G, butterfly, tensor, translation_phase, z_phase


def fadd(z, w): return z[0]+w[0], z[1]+w[1]
def fphase(z): return -z[1], z[0]
def fpi(z): return (z[0]+z[1])/2, (z[1]-z[0])/2
def fpair(u, v, inverse=False):
    if inverse:
        return fpi(fadd(u,fphase(v))),fpi(fadd(fphase(u),v))
    return fpi(fadd(fphase(u),v)),fpi(fadd(u,fphase(v)))


def audit():
    if not __debug__: raise RuntimeError('run this exact audit without Python -O')
    count = dict(canonical_cases=0, heterogeneous_pair_cases=0,
                 operation_cases=0, endpoint_cases=0, endpoint_values=0,
                 restoration_values=0)
    rng = Random(46045)
    candidates = [G(a,b,e) for a,b,e in product(range(-3,4),range(-3,4),range(7))]
    for a,b,e in product(range(-4,5),range(-4,5),range(9)):
        z=G(a,b,e)
        # Independent multiply-back equality for the original representation.
        original=(Q(a),Q(b))
        for _ in range(e): original=fpi(original)
        assert z.fractions()==original
        assert z.exponent==0 or (z.re+z.im)%2==1
        assert G(z.re,z.im,z.exponent)==z
        if z.exponent:
            # Odd residue prohibits a representation at exponent e-1.
            assert (z.re-z.im)%2==1
        count['canonical_cases']+=1
    for trial in range(5000):
        u,v=rng.sample(candidates,2)
        uf,vf=u.fractions(),v.fractions()
        assert (u+v).fractions()==fadd(uf,vf)
        assert (u*v).fractions()==(uf[0]*vf[0]-uf[1]*vf[1],uf[0]*vf[1]+uf[1]*vf[0])
        assert u.over_two(3).fractions()==(uf[0]/8,uf[1]/8)
        for inverse in (False,True):
            a,b=butterfly(u,v,inverse)
            assert (a.fractions(),b.fractions())==fpair(uf,vf,inverse)
            assert butterfly(a,b,not inverse)==(u,v)
            count['heterogeneous_pair_cases']+=1
        count['operation_cases']+=3
    mask=(1<<9)-1
    for d in (9,10,11):
        for trial in range(3):
            n=1<<d
            x=[G(rng.randint(-20,20),rng.randint(-20,20),rng.randrange(5)) for _ in range(n)]
            y=[G(rng.randint(-20,20),rng.randint(-20,20),rng.randrange(7)) for _ in range(n)]
            # A=-F y, B=F T^-2 x+E y; all denominator tags arbitrary.
            fx=tensor(x,d)
            fy=tensor(y,d)
            a=[-v for v in fy]
            ti2x=translation_phase(translation_phase(x,mask,True),mask,True)
            first=tensor(ti2x,d)
            ey=tensor(translation_phase(y,mask,True),d)
            b=[u+v for u,v in zip(first,ey)]
            correction=translation_phase(a,mask,True)
            corrected=[u+v for u,v in zip(b,correction)]
            assert corrected==first
            # i^9 Z_u F T^-2 Z_u=F: include actual weight-nine wrappers.
            phased_x=z_phase(x,mask)
            squared=translation_phase(translation_phase(phased_x,mask,True),mask,True)
            restored=[v.phase(9) for v in z_phase(tensor(squared,d),mask)]
            assert restored==fx
            # Every copy is erased by exact subtraction, with dirty original retained.
            assert [u-v for u,v in zip(correction,correction)]==[G()]*n
            assert tensor(fy,d,True)==y
            assert translation_phase(translation_phase(y,mask),mask,True)==y
            count['endpoint_cases']+=1
            count['endpoint_values']+=n
            count['restoration_values']+=n
    # Sharp C grid and the normalized-H0 boundary must remain distinct.
    c=tensor([G(1)]+[G()]*511,9)
    assert max(v.exponent for v in c)==9
    assert any(v.over_two(0).exponent for v in c)
    # Component box norm differs from complex-modulus norm at odd depth.
    assert butterfly(G(1,-1),G(1,1))==(G(2),G())
    rejected=False
    try: translation_phase([G()]*4,3)
    except ValueError: rejected=True
    assert rejected
    return dict(status='passed',counts=count,
        source_commit='71b6c960c89295e952522dd44111df9cfc51ae90',
        source='notes/copied-centers-complex.tex: Two-stage phase endpoint and its paid correction',
        controls=['noncanonical input tags','heterogeneous arbitrary dirty scratch',
                  'weight-nine input/output phase wrappers','paid endpoint correction',
                  'inverse restoration','even-norm physical line rejected',
                  'component box norm distinguished from complex-modulus norm'],
        scope='Finite exact scalar phase controls, not full framed/tape execution or exponent improvement')


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
