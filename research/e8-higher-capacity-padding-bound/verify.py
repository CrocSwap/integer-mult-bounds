"""Exact finite certificate for optimal residual padding at fixed width73.
Prepared with OpenAI Codex assistance. No floating-point computation required.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,sys
if not __debug__:
    raise SystemExit('Assertions enabled are required')
P=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
assert len(sys.argv)==2, 'Usage: python -B verify.py OUTPUT.json'
OUT=Path(sys.argv[1]).resolve()
assert P not in OUT.parents and not OUT.exists(), 'Use a fresh output file outside the package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (P/'MANIFEST.sha256').read_text().splitlines()}
def inventory():return {p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file() and p!=P/'MANIFEST.sha256'}
assert inventory()==manifest, 'Package inventory mismatch' 
RANKS=[9,8,7,5,4]
DUAL=[Q(1,8),-Q(1,64),-Q(5,32),-Q(7,16),-Q(37,64)]
counts=[36224,9472,1536,1152,1600]
patterns=[]
def enumerate_patterns(j,counts,left):
    if j==len(RANKS):
        patterns.append((counts,left));return
    for n in range(left//RANKS[j]+1):
        enumerate_patterns(j+1,counts+[n],left-n*RANKS[j])
enumerate_patterns(0,[],73)
assert len(patterns)==4765
# exp(5)>73, using only a positive initial segment of its Taylor series.
t=Q(1);partial=t
for k in range(1,6):
    t*=Q(5,k);partial+=t
assert partial>73
trace=hashlib.sha256();positive=0
for counts_per_bank,p in patterns:
    w=sum((n*y for n,y in zip(counts_per_bank,DUAL)),Q(0))
    trace.update((json.dumps([counts_per_bank,p,str(w)],separators=(',',':'))+'\n').encode())
    if w<=0:continue
    positive+=1
    if p==1:
        assert w<=1;continue
    assert 2<=p<=73
    exponent=64*(19*p-20*w)
    assert exponent.denominator==1 and exponent>=0
    # Equivalent to (19/20)*p*log(73/p) >= w*log(73).
    assert 73**int(exponent)>=p**(64*19*p)
packing=P/'patterns.json'
selected=json.loads(packing.read_bytes())
coverage=[0]*5;dual_total=Q(0);pads=0;banks=0
for bank in selected:
    x=[bank.get('r'+str(r),0) for r in RANKS]
    p=bank['padding'];n=bank['count'];assert sum(a*b for a,b in zip(x,RANKS))+p==73
    w=sum((a*y for a,y in zip(x,DUAL)),Q(0))
    assert p in (0,1) and w==p
    for j,a in enumerate(x):coverage[j]+=n*a
    dual_total+=n*w;pads+=n*p;banks+=n
assert coverage==counts and dual_total==pads==2711 and banks==5855
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(status='PASS_EXACT_FIXED_INVENTORY_RESIDUAL_PADDING_OPTIMUM',width=73,ranks=RANKS,counts=counts,dual=[str(x) for x in DUAL],alpha_interval='0 < alpha <= 1/100',patterns_exhausted=len(patterns),positive_dual_patterns=positive,pattern_enumeration_sha256=trace.hexdigest(),minimum_padding_moment='2711 * (73**alpha - 1)',attaining_banks=5855,attaining_rank_one_padding=2711,sources={'verify.py':sha(Path(__file__)),'PROOF.md':sha(P/'PROOF.md'),'T64-patterns.json':sha(packing)},scope='Optimality of padding moment only for this exact residual inventory and width73. Allows arbitrary partition of padding into positive-rank blocks; real-rank inventory, local construction, replication integrality, full costs and all-size assumptions are otherwise fixed. No global multiplication-score optimum claim.')
assert {k:v for k,v in result.items() if k!='sources'}==json.loads((P/'EXPECTED.json').read_bytes())
assert inventory()==manifest
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(result['status'],sha(OUT))
