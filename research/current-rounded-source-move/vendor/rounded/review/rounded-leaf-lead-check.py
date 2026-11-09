"""Independent signed-tail/drop tests for the dynamic rounded native wrapper.

Only physical fixture hardware is reused. Integer generation, decoding, exact
rounding and width/radius bounds below are independent of worker oracles.
Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from contextlib import ExitStack
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
from random import Random
import sys

PKG=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/scratch/a365d332d434/native-w6-rounded-leaf/research/current-rounded-positive-leaf').resolve()
sys.path.insert(0,str(PKG))
from rounded_leaf import Provider,RoundedOverflow,A,C,Count
from check_rounded import Tape

def body(t):
    data=bytes(t.cells[t.origin:]);end=data.find(bytes([A.BLANK]))
    if end<0:end=len(data)
    assert all(v==A.BLANK for v in data[end:])
    return data[:end]
def encode(values,width):
    out=[]
    for v in values:
        assert -(1<<(width-1))<=v<(1<<(width-1))
        for s in [(v>>j)&1 for j in range(width)]+[2]:out.extend((s>>2,(s>>1)&1,s&1))
    return bytes(out)
def decode(data,width):
    assert len(data)%(3*(width+1))==0
    s=[4*data[j]+2*data[j+1]+data[j+2] for j in range(0,len(data),3)];out=[]
    for j in range(0,len(s),width+1):
        z=s[j:j+width];assert s[j+width]==2 and all(b in (0,1) for b in z)
        out.append(sum(b<<k for k,b in enumerate(z))-(z[-1]<<width))
    return out
def trial(h,g,values):
    margin=(g+2)//2+1;wide=h+g+margin
    p=Provider(1);work=[Tape(3+j%5) for j in range(p.port_count)];context=Tape(13)
    p.bind(work,A.BinaryContextPort(context));work[0].cells[work[0].origin:]=encode(values,wide)
    expected=[(z+(1<<(g-1)))//(1<<g) for z in values]
    admitted=all(-(1<<(h-1))<=z<(1<<(h-1)) for z in expected)
    p.cohort.start();cleanup=ExitStack();caught=False
    try:
        with C.execution(),p.scope.installed():
            args=[]
            for value in (h,g,margin,len(values)):
                c=Count.literal(value);cleanup.callback(c.close);args.append(c)
            try:p.drop(*args)
            except RoundedOverflow:caught=True
        assert caught!=admitted,(h,g,values,expected)
        if admitted:assert decode(body(work[1]),h)==expected
    finally:
        with C.execution(),p.scope.installed():cleanup.close();p.pool.empty()
        p.cohort.finish()
        for t in work[:3]:A.retire(t)
    assert all(not body(t) and t.head==t.origin for t in work)
    assert context.head==context.origin and not body(context)
    return admitted,len(values),sum(t.actions() for t in work)

rng=Random(20261109);accepted=rejected=components=actions=0
for h in (2,3,5,9,17):
    for g in (1,2,4,9,31,65):
        Q=1<<g;B=1<<(h-1);low=-B*Q-Q//2;high=B*Q-Q//2-1
        good=[low,low+1,high-1,high,-Q//2,Q//2,-3*Q//2,0]
        good += [rng.randrange(low,high+1) for _ in range(8)]
        ok,n,a=trial(h,g,good);assert ok;accepted+=1;components+=n;actions+=a
        wide=h+g+(g+2)//2+1
        for bad in (low-1,high+1,-(1<<(wide-1)),(1<<(wide-1))-1):
            ok,n,a=trial(h,g,[0,bad]);assert not ok;rejected+=1;components+=n;actions+=a

width_checks=0
for h in range(2,201):
    for g in range(1,301):
        w=h+g+(g+2)//2+1
        assert 2*h+3*g-1 <= 2*(w-2)
        if g<=h:assert w+1<=3*(h+1)
        width_checks+=1
result={'production_sha256':hashlib.sha256((PKG/'rounded_leaf.py').read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256((PKG/'PROOF.md').read_bytes()).hexdigest(),'accepted_field_cases':accepted,'correct_late_overflow_fields':rejected,'signed_components':components,'runtime_g_range':'1,2,4,9,31,65','h_range':'2,3,5,9,17','literal_codec_actions':actions,'independent_internal_width_checks':width_checks,'cleanup_all_private_roles':True,'limits':['dynamic drop codec and proof obligations independently checked','worker full small-native fixtures are separate evidence','no full selected producer or whole MOVE','no new kappa']}
Path(__file__).with_name('rounded-leaf-lead-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
