"""Call the real recipe and exercise the new Gaussian origin at its actual first boundary."""
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import json,sys

runtime=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(runtime))
from upstream import install
install()
import grades
from grades import LOWER,UPPER_DIVISOR,WEIGHTS,numerical_recipe
from installations import ENTRY,TERMINAL,GAUSSIAN_C
from transport import Measure,ceil
from typed_transport import TypedPlan,NativeType,column_header
assert LOWER==1054 and UPPER_DIVISOR==1724 and WEIGHTS==(5,451)
contacts=[]
for tier in (ENTRY,TERMINAL):
    recipe=numerical_recipe(tier.complex_log)
    def inspect(n,types,cells,t,lower,upper,volume,ticks,rounds,**kw):
        assert n==1<<tier.complex_log and t==1-GAUSSIAN_C and lower==LOWER
        assert upper==2*(n//(1724*306))
        assert upper>516*lower and 4*258*(upper-6)<n
        assert len(cells)==88 and len(recipe.cells)==51
        assert tuple(w.multiplicity for w in types)==WEIGHTS
        assert (volume,ticks,rounds)==(n**6,n**82,n**2)
        assert kw=={'width':1<<(92*tier.complex_log),'delay_base':1<<19,'column_offset':6}
        needs=[]
        for a,r,b,k in cells:
            assert 2*r==int(2*r) and 2*k==int(2*k)
            needs.append(Q(2*r-gcd(int(2*r),int(2*k)),k-r))
        assert max(needs)==Q(94,17)<6
        return True
    actual=grades.TypedPlan
    try:
        grades.TypedPlan=inspect
        assert recipe.open()
    finally:grades.TypedPlan=actual
    contacts.append([tier.complex_log,len(recipe.typed_cells())])
for d,expected in ((LOWER,(1048,2096)),(LOWER+2,(1050,2100))):
    pair=tuple((column_header(d-6,kind)-kind)*(1+kind) for kind in (0,1))
    assert pair==expected
# Homogeneous small physical types use the exact extremal occupied r:k pair.
r,k=96,130
minimum=Q(94,17)
assert (2*r-gcd(2*r,2*k))==minimum*(k-r)
negative=None
for e in range(1450,1700,2):
    for d in range(max(LOWER,2*((e*r//k)//2)-2),2*((e*r//k)//2)+6,2):
        lo=max(e,Q(d*k,r));hi=min(e+2,Q((d+2)*k,r))
        if lo<hi and r*(e-4)-k*(d-4)<0:
            if negative is None or r*(e-4)-k*(d-4)<negative[-1]:
                negative=(e,d,lo,hi,r*(e-4)-k*(d-4))
assert negative is not None and negative[-1]==-52
e,d,lo,hi,_=negative
upper=e+4;n=1<<22
types=(NativeType((k,),(r,),5),NativeType((k,),(r,),451))
shares={(a,r,b,k):Q(w,456) for a in (0,1) for b,w in enumerate(WEIGHTS)}
args=(n,types,shares,1-GAUSSIAN_C,LOWER,upper,1<<36,3,n)
try:
    TypedPlan(*args,delay_base=3,padding=1,column_offset=4)
except ValueError as ex:assert 'prefix can exceed' in str(ex)
else:raise AssertionError('An unfunded four-column emitter was accepted')
plan=TypedPlan(*args,delay_base=3,padding=1,column_offset=6)
assert plan.column_offset==6 and plan.source_width>0
metrics=[]
for child in (0,1):
    actual=[z for z in plan.receive[d,child,0] if z.band==e]
    assert len(actual)==2 and all(z.count>0 for z in actual)
    for z in actual:
        assert r*(e-6)-k*(d-6)==16
        emitted_number=z.count
        m=Measure(1-GAUSSIAN_C,1<<36,64*n.bit_length())
        expected=int(WEIGHTS[z.kind]*m.mass(lo,hi)[0]*shares[z.kind,r,child,k])
        assert emitted_number==expected>0
        metrics.append([z.kind,child,emitted_number])
print('PASS_SHIFT_SIX_LOWER_BOUNDARY',json.dumps({'stages':contacts,'bad_shift_link':[e,d,-52],
    'validated_shift_six_suffix':16,'instantiated_typed_grants':metrics,'real_exterior_slots':plan.source_width}))
