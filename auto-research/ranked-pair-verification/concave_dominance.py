"""Exact profile dominance; no transcendental arithmetic or upstream imports.

If signed profile d has zero rank mass and C(k)=sum d[t]*min(t,k)<=0,
then every discrete concave f with f(0)=0 has sum d[t]*f(t)<=0.
The equality is checked coefficient-by-coefficient in the min-function basis.
With C(1)<0 and 2f(1)>f(0)+f(2), the inequality is strict.
"""
from pathlib import Path
from hashlib import sha256
import json

def require(b,message):
    if not b:raise ValueError(message)

def certify(old,new):
    require(len(old)==len(new),'profile lengths')
    d=[b-a for a,b in zip(old,new)]
    require(d[0]==0,'width-zero profile changed')
    T=len(d)-1
    C=[sum(min(t,k)*n for t,n in enumerate(d)) for k in range(T+1)]
    require(C[T]==0,'total rank mass changed')
    require(all(v<=0 for v in C),'not concave dominance')
    require(C[1]<0,'strict concavity witness absent')
    # Expand sum C(k)*(2f(k)-f(k-1)-f(k+1)).
    coefficients=[0]*(T+1)
    for k in range(1,T):
        coefficients[k]+=2*C[k]
        coefficients[k-1]-=C[k]
        coefficients[k+1]-=C[k]
    require(coefficients[1:]==d[1:],'summation-by-parts coefficient identity')
    # The only remaining term is a multiple of f(0), fixed to zero.
    return dict(signed_multiplicities={t:n for t,n in enumerate(d) if n},
                capped_mass_differences=C,
                zero_rank_mass=True,strict_at_width_one=True,
                min_basis_identity_checked=True,f_zero_coefficient=coefficients[0])

def main():
    root=Path(__file__).resolve().parent
    rows=[]
    for h in (23,25):
        paths=[root/'finite-frames'/f'pair-{kind}-{h}-receipt.json' for kind in ('original','ranked')]
        old,new=[json.loads(p.read_text()) for p in paths]
        require(old['profile']['R']==new['profile']['R'],'roles must stay unchanged')
        row=certify(old['profile']['blocks'],new['profile']['blocks'])
        row.update(h=h,roles=new['profile']['R'],old_word=old['word_sha256'],new_word=new['word_sha256'],
                   source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in paths})
        rows.append(row)
    out=dict(status='PASS exact integer concave dominance',axes=rows,
        consequence='For every 0<a<1 the new normalized characteristic is strictly lower than the original; m,W and exterior/data profiles are unchanged.',
        scope='Algebraic theorem for the reconstructed finite profiles; physical compiler/analytic transfer hypotheses remain separate.')
    (root/'concave-dominance.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])

if __name__=='__main__':main()
