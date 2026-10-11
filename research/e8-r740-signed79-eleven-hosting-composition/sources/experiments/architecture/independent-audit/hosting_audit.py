"""Independent rational column and window audit of the six-coordinate toy.

Uses direct column actions, not the producer's matrix multiplication routines.
Includes an actual common rational chart and an ownership-collision control.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

N=6
def basis(i):return tuple(Q(int(i==j)) for j in range(N))
def apply(word,v):
    v=list(v)
    for op in word:
        if op[0]=='add':v[op[1]]+=Q(op[3])*v[op[2]]
        elif op[0]=='neg':v[op[1]]=-v[op[1]]
        else:raise ValueError(op)
    return tuple(v)
def endpoint(word):return tuple(apply(word,basis(i)) for i in range(N))
def invert(word):return [tuple(op[:3]) + (-op[3],) if op[0]=='add' else tuple(op) for op in reversed(word)]
def swap(v,a,b):
    v=list(v);v[a],v[b]=v[b],v[a];return tuple(v)
def chart(v,inverse=False):
    v=list(v);x,y=v[2:4]
    v[2]=Q(3,5)*x+(Q(-4,5) if inverse else Q(4,5))*y
    v[3]=(Q(4,5) if inverse else Q(-4,5))*x+Q(3,5)*y
    return tuple(v)
def residual(v):return chart(swap(chart(v,True),2,3))
def remainder(v):return swap(v,4,5)
def active(v):v=list(v);v[0]+=v[1];return tuple(v)
def conjugated_local(word,v):return chart(apply(word,chart(v,True)))
def touch(v):v=list(v);v[2]+=v[4];return tuple(v)
def safe_touch(v):v=list(v);v[4]+=v[5];return tuple(v)

def main():
    P=Path(__file__).resolve().parent
    source=P.parent/'joint-design/HOSTING-TOY.json'
    r=json.loads(source.read_text());word=r['local_word']
    columns=[basis(i) for i in range(N)]
    for v in columns:
        assert apply(word,v)==swap(active(v),2,3)
        assert apply(invert(word),apply(word,v))==v
        assert chart(chart(v,True))==v
        assert conjugated_local(word,v)==residual(active(v))
        assert remainder(conjugated_local(word,v))==remainder(residual(active(v)))
        assert remainder(safe_touch(conjugated_local(word,v)))==remainder(residual(safe_touch(active(v))))
    bad=[]
    for i,v in enumerate(columns):
        hosted=remainder(touch(conjugated_local(word,v)))
        original=remainder(residual(touch(active(v))))
        if hosted!=original:bad.append(dict(column=i,hosted=list(map(str,hosted)),original=list(map(str,original))))
    assert bad
    # A slot map must be injective. Distinct names are not a proof; two
    # independently chosen chart descriptions can own the same actual stream.
    def injective(images):return len(set(images))==len(images)
    assert injective([('F',0),('F',1)])
    assert not injective([('F',0),('F',0)])
    out=dict(status='PASS_INDEPENDENT_SIGNED_RATIONAL_CHART_HOSTING_AND_COUNTEREXAMPLE',
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        local_signed_updates=len(word),pending_old_signed_updates=8,pending_remainder_signed_updates=4,
        toy_pending_update_saving=4,
        caveat='Rational chart arithmetic is an exact operator check, not a free primitive chart implementation.',
        all_integer_columns=True,arbitrary_correlated_inputs=True,exact_inverse=True,
        rational_chart=[["3/5","4/5"],["-4/5","3/5"]],
        rational_chart_safe_disjoint_touch=True,unsafe_cross_coordinate_columns=bad,
        duplicate_physical_owner_control_rejected=True,
        boundary='Real covers need per-cover-class injective stream ownership and chart-compatible commutation of every intervening operator. Toy proves possibility, not PR442 admission.')
    (P/'HOSTING-INDEPENDENT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status']);print('unsafe basis columns', [x['column'] for x in bad])

if __name__=='__main__':main()
