"""Independent mixed-width/source-extreme oracle for compact literal ADD.

Drives unchanged primitive directly, using only immutable checker hardware.
Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
from random import Random
import sys
from types import SimpleNamespace

PKG=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/scratch/a365d332d434/worker-compact-add/research/compact-rounded-add').resolve()
sys.path.insert(0,str(PKG))
from tables import compile_compact
from source_binding import vendor
H=vendor('lead_compact_physical','vendor/physical_fixture.py')

def encode(values,widths):
    out=[]
    for v,w in zip(values,widths):
        for s in [(v>>j)&1 for j in range(w)]+[2]:out.extend(((s>>2)&1,(s>>1)&1,s&1))
    return out
def decode(bits,widths):
    s=[4*bits[i]+2*bits[i+1]+bits[i+2] for i in range(0,len(bits),3)]
    out=[];offset=0
    for w in widths:
        b=s[offset:offset+w];assert len(b)==w and all(v in (0,1) for v in b) and s[offset+w]==2
        out.append(sum(v<<j for j,v in enumerate(b))-(b[-1]<<w));offset+=w+1
    assert offset==len(s)
    return out

def trial(table,receipt,x,y,widths):
    public=[H.Tape(encode(x,widths),101),H.Tape(encode(y,widths),1001,True)]
    work=[H.Tape((1,0)*41,2001),H.Tape((0,1)*73,3001)]
    work[0].pos+=67;work[1].pos+=146
    contexts=[H.Tape((1,0)*13,4001,True),H.Tape((0,1,1),5001,True)]
    contexts[0].pos+=21;contexts[1].pos+=3
    ports=public+work+contexts;before=[t.body() for t in public+contexts]
    A=sum(len(t.body()) for t in work);Qc=sum(len(t.body())+1 for t in contexts)
    rows=H.RowCounter(table)
    c=SimpleNamespace(payloads=tuple(ports),primitive_work=(2,3),primitive_context=(4,5),services={('lead',):rows})
    a,b=receipt['numerator'],receipt['denominator']
    expected=[xx+(a*yy+b//2)//b for xx,yy in zip(x,y)]
    fits=all(-(1<<(w-1))<=z<(1<<(w-1)) for z,w in zip(expected,widths))
    error=None
    try:H.M.Controller.primitive(c,('lead',),(0,1))
    except ValueError as exc:error=str(exc)
    assert (error is None)==fits,(receipt['coefficient'],widths,x,y,expected,error)
    assert public[1].body()==before[1] and [t.body() for t in contexts]==before[2:]
    assert all(t.protected() for t in ports)
    if fits:
        assert decode(public[0].body(),widths)==expected
        assert all(t.pos==t.origin for t in ports) and all(t.blank() for t in work)
    else:assert public[0].body()==before[0]
    S=sum(w+1 for w in widths);R=len(widths);U=1+S+(receipt['extra_width']+1)*R
    bound=512*(receipt['coefficient_bits']+8)*U+7*A+16*Qc
    used=rows.steps+sum(t.actions for t in ports)
    assert used<=bound,(used,bound)
    return fits,F(used,bound),expected

rng=Random(202611092029);cases=success=0;worst=F(0);inventory=[]
coefs=[F(-14729531,163840),F(-1379,250),F(1085645,393216),F(17,96),F(-31,80),F(65,128),F(-101,125),F(0),F(1)]
for q in coefs:
    table,receipt=compile_compact(q);inventory.append({k:receipt[k] for k in ('coefficient','rows','states','coefficient_bits','extra_width','odd_divisor')})
    for j in range(24):
        widths=[1,2,3,5,17,31] if j==0 else [rng.randrange(1,42) for _ in range(2 if j%2 else 4)]
        x=[];y=[]
        for w in widths:
            B=1<<(w-1);choices=[-B,B-1,0,rng.randrange(-B,B)]
            x.append(choices[j%4]);y.append(choices[(j+1)%4])
        ok,ratio,_=trial(table,receipt,x,y,widths);cases+=1;success+=ok;worst=max(worst,ratio)
    if q==F(-14729531,163840):
        ok,ratio,z=trial(table,receipt,[100,0],[2,0],[8,3]);assert ok and z==[-80,0];cases+=1;success+=1;worst=max(worst,ratio)
    if q==F(-1379,250):
        ok,ratio,z=trial(table,receipt,[7,0],[2,0],[4,1]);assert ok and z==[-4,0];cases+=1;success+=1;worst=max(worst,ratio)
    if q==F(1085645,393216):
        ok,ratio,z=trial(table,receipt,[-7,0],[3,0],[4,1]);assert ok and z==[1,0];cases+=1;success+=1;worst=max(worst,ratio)

result={'tables_sha256':hashlib.sha256((PKG/'tables.py').read_bytes()).hexdigest(),'proof_sha256':hashlib.sha256((PKG/'PROOF.md').read_bytes()).hexdigest(),'mixed_width_cases':cases,'successes':success,'correct_overflows':cases-success,'largest_cost_ratio':str(worst),'coefficient_inventory':inventory,'independent_source_cancellation_controls':3,'context_heads_started_inside_bodies':True,'no_changes_to_executor':True,'limits':['bounded additional literal execution; all-size proof separately reviewed','only three actual source tokens installed','no whole caller or tariff-cap claim','odd divisor<=125; no arbitrary logarithmic-divisor theorem','no new kappa']}
Path(__file__).with_name('compact-add-lead-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
