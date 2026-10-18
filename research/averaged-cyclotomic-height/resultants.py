"""Independent SymPy resultant identities and nonrationality counterexample."""
import importlib.util
import json
from math import gcd
from pathlib import Path
from sympy import Poly, QQ, Symbol, cyclotomic_poly
from sympy.polys.matrices import DomainMatrix

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'vendor/pr621/verify.py'
spec=importlib.util.spec_from_file_location('retained_pr621',SOURCE)
original=importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def need(ok,label):
    if not ok:
        raise ValueError(label)


def case(r):
    x,z=Symbol('x'),Symbol('z')
    field=QQ.alg_field_from_poly(Poly(cyclotomic_poly(r,x),x),alias='u')
    u=field([1,0])
    n=r-1
    def embed(a,k):
        result=field.zero
        for coefficient in a.to_list():
            result=result*u**(k%r)+field(coefficient)
        return result
    f=[field.one]*r
    for j in range(n-1,-1,-1):
        f[j]=f[j+1]*(field.one-u**(j+1))
    need(f[0]==field(r),'kernel constant coefficient')
    star=[embed(a,-1) for a in reversed(f)]
    fp=Poly.from_list(list(reversed(f)),z,domain=field)
    gp=Poly.from_list(list(reversed(star)),z,domain=field)
    R=field((-1)**n)*fp.rep.resultant(gp.rep)
    matrix=[[field.zero]*(2*n) for _ in range(2*n)]
    for poly,start in [(f,0),(star,n)]:
        for offset in range(n):
            for degree,a in enumerate(poly):
                matrix[degree+offset][start+offset]=a
    need(DomainMatrix(matrix,(2*n,2*n),field).det()==R,'determinant/resultant sign')
    need(R!=field.zero and embed(R,-1)==R,'nonzero real resultant')
    norm=field.one
    embeddings=[]
    for k in range(1,r):
        if gcd(k,r)!=1:
            continue
        value=embed(R,k)
        norm*=value
        embeddings.append([str(c) for c in value.to_list()])
    need(len(norm.to_list())==1 and norm.to_list()[0].denominator==1,'integer norm')
    retained=original.case(r,1)
    encoded=[str(c) for c in reversed(R.to_list())]
    encoded+=['0']*(field.mod.degree()-len(encoded))
    need(encoded==retained['resultant'],'independent exact field agreement')
    need(str(norm.to_list()[0])==retained['resultant_norm'],'independent norm agreement')
    if r==5:
        need(R!=embed(R,2) and len(R.to_list())>1,'reject rational-resultant shortcut')
        need(encoded==['98873','0','17859','17859'],'radix-five counterexample')
    return dict(r=r,resultant_ascending=encoded,norm=str(norm.to_list()[0]),
                embeddings_descending=embeddings,independent_field_agreement=True,
                rational_resultant=(len(R.to_list())==1),
                inherited_unit_root_control=retained['unit_root_negative_control'],
                inherited_missing_conjugation_control=retained['missing_conjugation_negative_control'])


def main():
    rows=[]
    for r in [3,4,5,7,8,9]:
        rows.append(case(r))
        print(r,'PASS independent exact resultant',flush=True)
    result={'status':'PASS_INDEPENDENT_EXACT_RESULTANTS','scope':__doc__,'cases':rows}
    return result


if __name__=='__main__':
    main()
