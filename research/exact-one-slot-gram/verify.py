"""Integer annihilation and matching modular degree certificates.

No discovery routine or python-flint call is used. Substantial OpenAI Codex
assistance; Krzysztof Wojt; Apache-2.0. Not a proof-kernel verification.
"""
import argparse
from hashlib import shake_256, sha256
import json
from math import isqrt
from pathlib import Path
import sys
import time

import numpy as np
import sympy as sp

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import (PACKAGE, SOURCE_SHA256, REPRESENTATIVES, require, read_query,
                   symmetries, label_orbits, stabilizer, sector, coordinate_orbits,
                   apply, polynomial_action, zero_matrices)

PRIME = 2147483647
X = sp.Symbol('x')
EXPECTED_ORBITS = ((0,2), (1,224), (3,224), (7,16), (30,14), (128,32))
EXPECTED_COORDINATE_ORBITS = {1:(26,22),3:(26,26),7:(16,8),30:(11,11),128:(8,8)}


def polynomial(coefficients, modulus=None):
    require(isinstance(coefficients,list) and len(coefficients)>1,'polynomial list')
    require(all(type(x) is int for x in coefficients) and coefficients[-1]==1,'monic integer polynomial')
    if modulus is None:
        return sp.Poly.from_list(list(reversed(coefficients)),X,domain=sp.ZZ)
    return sp.Poly.from_list(list(reversed(coefficients)),X,modulus=modulus)


def seeded_values(name, shape):
    size=int(np.prod(shape))
    data=shake_256(('exact-one-slot-gram/v1/'+name).encode()).digest(4*size)
    return (np.frombuffer(data,dtype='<u4').astype(np.int64)%PRIME).reshape(shape)


def determinant_mod(matrix):
    a=np.array(matrix,dtype=np.int64,copy=True)%PRIME
    determinant=1
    for j in range(len(a)):
        positions=np.flatnonzero(a[j:,j])
        if not len(positions):
            return 0
        pivot=j+int(positions[0])
        if pivot!=j:
            a[[j,pivot]]=a[[pivot,j]]
            determinant=-determinant
        value=int(a[j,j])
        determinant=determinant*value%PRIME
        if j+1<len(a):
            factors=a[j+1:,j]*pow(value,-1,PRIME)%PRIME
            a[j+1:,j:]=(a[j+1:,j:]-factors[:,None]*a[j,j:])%PRIME
    return determinant%PRIME


def determinant_condensed(matrix):
    """Modular Bareiss condensation, separate from Gaussian elimination."""
    a=np.array(matrix,dtype=np.int64,copy=True)%PRIME
    sign,previous=1,1
    while len(a)>1:
        positions=np.flatnonzero(a[:,0])
        if not len(positions):
            return 0
        pivot=int(positions[0])
        if pivot:
            a[[0,pivot]]=a[[pivot,0]]
            sign=-sign
        value=int(a[0,0])
        a=((a[1:,1:]*value-a[1:,0,None]*a[None,0,1:])%PRIME)*pow(previous,-1,PRIME)%PRIME
        previous=value
    return sign*int(a[0,0])%PRIME


def hankel_certificate(degree,name,shape,action):
    value=seeded_values(name+'/input',shape)
    observer=seeded_values(name+'/output',shape)
    moments=[]
    for k in range(2*degree-1):
        # Products < PRIME^2 < 2^62; reduce before summing <=4096 entries.
        moments.append(int(np.sum((value*observer)%PRIME)%PRIME))
        if k+1<2*degree-1:
            value=action(value)
    hankel=np.array([[moments[i+j] for j in range(degree)] for i in range(degree)],dtype=np.int64)
    first=determinant_mod(hankel)
    second=determinant_condensed(hankel)
    require(first==second and first!=0,'matching nonzero Hankel determinants')
    return {'degree':degree,'determinant':first,'moment_sha256':sha256(json.dumps(moments,separators=(',',':')).encode()).hexdigest()}


def check_sector_interface(c,t,s,addresses,targets,signs,ports):
    """Compare every compressed port column with its two-term embedding."""
    for q,target,sign in zip(ports,targets,signs):
        require(np.array_equal(target[target],np.arange(len(addresses))),
                "port permutation is an involution")
        require(np.array_equal(sign[target],sign),"port signs are symmetric")
        for j,a in enumerate(addresses):
            output={}
            for b,weight in ((a,1),(a^c,s)):
                if (q&c).bit_count()%2:
                    dest,coefficient=b^q,weight
                else:
                    dest,coefficient=b,weight*(1-2*((q&b).bit_count()%2))
                output[dest]=output.get(dest,0)+coefficient
            dest=addresses[int(target[j])]
            expected={dest:int(sign[j]),dest^c:s*int(sign[j])}
            require(output==expected,'literal/compressed port embedding')
            require((dest&(c^511)).bit_count()%2==t,'parity sector preservation')
    return len(ports)*len(addresses)


def check_zero(record,roots,ports):
    p=polynomial(record['coefficients'])
    matrices=zero_matrices(roots,ports)
    require(np.array_equal(matrices,matrices.transpose(0,2,1)),'zero-block symmetry')
    identities=np.broadcast_to(np.eye(8,dtype=object),(512,8,8)).copy()
    current=identities.copy()
    for coefficient in reversed(record['coefficients'][:-1]):
        current=np.matmul(matrices.astype(object),current)+coefficient*identities
    require(np.all(current==0),'zero-block integer annihilation on every column')
    action=lambda value:np.einsum('aij,aj->ai',matrices,value)%PRIME
    lower=hankel_certificate(p.degree(),'zero',(512,8),action)
    return p,lower


def check_sector(record,roots,ports,generators):
    c,t,s=(record[key] for key in ('c','t','s'))
    p=polynomial(record['coefficients'])
    addresses,targets,signs=sector(c,t,s,ports)
    columns=check_sector_interface(c,t,s,addresses,targets,signs,ports)
    orbits=coordinate_orbits(c,addresses,stabilizer(c,generators))
    require(len(orbits)==EXPECTED_COORDINATE_ORBITS[c][t] and sum(map(len,orbits))==1024,'complete coordinate orbit cover')
    seeds=np.zeros((8,128,len(orbits)),dtype=object)
    for k,orbit in enumerate(orbits):
        i,j=divmod(orbit[0],128)
        seeds[i,j,k]=1
    residual=polynomial_action(record['coefficients'],seeds,roots,targets,signs)
    require(np.all(residual==0),'sector integer annihilation on orbit representatives')
    lower=hankel_certificate(p.degree(),f'{c}/{t}/{s}',(8,128),lambda v:apply(v,roots,targets,signs,PRIME))
    lower.update({'c':c,'t':t,'s':s,'orbit_seeds':len(orbits),'embedded_port_columns':columns})
    return p,lower


def failure_controls(certificate,roots,ports,generators):
    checks=[]
    def rejects(name,operation):
        try:
            operation()
        except (ValueError,KeyError):
            checks.append(name)
        else:
            raise ValueError('control was accepted: '+name)
    rejects('nonmonic polynomial',lambda:polynomial([1,2]))
    rejects('noninteger polynomial',lambda:polynomial([0.5,1]))
    rejects('degenerate sector',lambda:sector(0,0,1,ports))
    altered=roots.copy();altered[0,0]+=3
    rejects('changed root covariance',lambda:symmetries(altered,ports))
    require(determinant_mod([[1,2],[2,4]])==0,'dependent Hankel control')
    require(determinant_mod([[0,1],[1,0]])==PRIME-1,'row-swap determinant control')
    require(determinant_condensed([[0,1],[1,0]])==PRIME-1,'row-swap condensation control')
    checks.extend(('dependent Hankel','Gaussian row swap','condensation row swap'))
    rec=certificate['sectors'][0]
    c,t,s=(rec[key] for key in ('c','t','s'))
    aa,tt,ss=sector(c,t,s,ports)
    source=np.zeros((8,128),dtype=np.int64)
    source[int(np.flatnonzero(roots[0])[0]),0]=1
    require(not np.array_equal(apply(source,roots,tt,ss),
                               apply(source,roots[1:],tt[1:],ss[1:])),
            'dropped source port control')
    checks.append('dropped source port')
    bad_signs=ss.copy();bad_signs[0,0]*=-1
    rejects('port phase mutation',lambda:check_sector_interface(c,t,s,aa,tt,bad_signs,ports))
    # The already verified p(B)=0 changes to exactly I if its constant gains 1.
    seeds=np.zeros((8,128,1),dtype=object);seeds[0,0,0]=1
    changed=rec['coefficients'][:];changed[0]+=1
    require(np.array_equal(polynomial_action(changed,seeds,roots,tt,ss),seeds),'changed polynomial constant control')
    checks.append('polynomial constant mutation')
    return checks


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--certificate',default=str(PACKAGE/'CERTIFICATE.json'))
    parser.add_argument('--emit-receipt',action='store_true')
    parser.add_argument('--only-c',type=int,default=None,help='partial development check; never emits full PASS')
    args=parser.parse_args()
    start=time.monotonic()
    require(all(PRIME%d for d in range(3,isqrt(PRIME)+1,2)),'prime trial-division certificate')
    with open(args.certificate,encoding='utf-8') as handle:
        certificate=json.load(handle)
    roots,ports=read_query()
    generators=symmetries(roots,ports)
    orbits=label_orbits(generators)
    require(tuple((v[0],len(v)) for v in orbits)==EXPECTED_ORBITS,'complete Bell orbit cover')
    require(certificate['source_sha256']==SOURCE_SHA256 and certificate['operator']=='B=4*A_1','certificate source/operator binding')
    entries=certificate['sectors']
    expected={(c,t,s) for c in REPRESENTATIVES if c for t in (0,1) for s in (-1,1)}
    require(len(entries)==len(expected) and {(x['c'],x['t'],x['s']) for x in entries}==expected,'exact sector inventory')
    receipt={'source_sha256':SOURCE_SHA256,'prime':PRIME,'bell_orbits':EXPECTED_ORBITS,'sectors':[]}
    polynomials=[]
    if args.only_c in (None,0):
        p,record=check_zero(certificate['zero'],roots,ports)
        polynomials.append(p);receipt['zero']=record
        print('checked zero degree',p.degree(),file=sys.stderr,flush=True)
    for entry in sorted(entries,key=lambda x:(x['c'],x['t'],-x['s'])):
        if args.only_c is not None and entry['c']!=args.only_c:
            continue
        p,record=check_sector(entry,roots,ports,generators)
        polynomials.append(p);receipt['sectors'].append(record)
        print('checked sector',entry['c'],entry['t'],entry['s'],'degree',p.degree(),file=sys.stderr,flush=True)
    if args.only_c is not None:
        print('PARTIAL_CHECK_ONLY',args.only_c,'seconds',round(time.monotonic()-start,2))
        return
    upper=sp.Poly(1,X,domain=sp.ZZ)
    lower=sp.Poly(1,X,modulus=PRIME)
    for p in polynomials:
        upper=sp.lcm(upper,p)
        lower=sp.lcm(lower,sp.Poly(p.as_expr(),X,modulus=PRIME))
    require(upper.degree()==lower.degree()==certificate['degree'],'matching global upper/lower degrees')
    require(sp.Poly(upper.as_expr(),X,modulus=PRIME)==lower,'global polynomial reduction')
    receipt['degree']=upper.degree()
    receipt['polynomial_sha256']=sha256(json.dumps([int(x) for x in reversed(upper.all_coeffs())],separators=(',',':')).encode()).hexdigest()
    require(receipt['polynomial_sha256']==certificate['polynomial_sha256'],'declared global polynomial hash')
    receipt['controls']=failure_controls(certificate,roots,ports,generators)
    receipt['status']='PASS_EXACT_ONE_SLOT_GRAM'
    if args.emit_receipt:
        print(json.dumps(receipt,indent=2))
    print('PASS_EXACT_ONE_SLOT_GRAM','degree='+str(upper.degree()),'seconds='+str(round(time.monotonic()-start,2)))


if __name__=='__main__':
    main()
