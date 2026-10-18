"""Exact pooled-hosting dual bound for the fixed PR544 static44 word.

Prepared for chafreaky with OpenAI Codex assistance, Apache-2.0.
Standard library only. This is a scoped upper bound, not a new supplier.
"""
import argparse,copy,hashlib,importlib.util,itertools,json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:raise SystemExit('Assertions must remain enabled')
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('out',type=Path);a=ap.parse_args()
out=a.out.resolve();assert not out.exists() and not out.is_relative_to(ROOT)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
assert actual==read(ROOT/'MANIFEST.json')
for entry in read(ROOT/'SOURCES.json')['files']:
    blob=(ROOT/entry['local']).read_bytes()
    assert sha(ROOT/entry['local'])==entry['sha256']
    assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==entry['git_blob']

def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'engines'/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
M,Other=load('moment'),load('base_two_moment')
plan=read(ROOT/'inputs/PR544-PLAN.json');published=read(ROOT/'inputs/PR544-RESULT.json');composition=read(ROOT/'inputs/PR547-EXPECTED.json');cert=read(ROOT/'CERTIFICATE.json')
for key,value in read(ROOT/'inputs/PR544-EXPECTED.json').items():assert published[key]==value
m,W,calls,ports,deficit=73,7168,72,112,2560
assert published['complex_live']==W and published['complex_deficit']==deficit
assert composition['complex_lower']==published['complex_lower']
stock=Counter()
for rank,times in plan['windows'].values():stock[rank]+=ports
ranks=sorted(stock);widths=Counter(plan['baseline_widths']);ws=sorted(widths)
assert widths=={5:56,8:156,9:292}
demand={w:calls*widths[w] for w in ws}
H={int(r):calls*n for r,n in published['complex_local_profile'].items()}
assert len(plan['order'])==calls and len(set(map(tuple,plan['order'])))==calls
mass=sum(r*n for r,n in H.items())+sum(r*n for r,n in stock.items())-sum(w*n for w,n in demand.items())
assert m*W-mass==deficit
patterns=[]
for r in ranks:
    for counts in itertools.product(*(range(r//w+1) for w in ws)):
        left=r-sum(w*n for w,n in zip(ws,counts))
        if left>=0:patterns.append((r,counts,left))
used_ranks=sorted(({left for r,counts,left in patterns}|set(H))-{0})

def prove(certificate):
    b=Q(certificate['excluded_b']);dual=list(map(Q,certificate['dual']))
    assert 0<b<Q(1,32) and len(dual)==len(ranks)+len(ws)
    theta=dict(zip(ranks,dual));mu=dict(zip(ws,dual[len(ranks):]))
    terms={'mercator':{0:(Q(0),Q(0))},'base_two':{0:(Q(0),Q(0))}}
    for r in used_ranks:
        lo,hi=M.moment({r:1},m,1,b,True)
        x,y=Other.moment(m,1,[(r,1)],b)
        fl,fu=Other.moment(m,1,[(1,32*m*m)],b)
        x+=fl/10**16;y+=fu/10**16
        assert max(lo,x)<=min(hi,y),'independent moment intervals disagree'
        for name,l,u in [('mercator',lo,hi),('base_two',x,y)]:
            terms[name][r]=((m*l-r)/b,(m*u-r)/b)
    receipts={}
    for name,values in terms.items():
        slacks=[values[left][0]-theta[r]-sum(mu[w]*n for w,n in zip(ws,counts)) for r,counts,left in patterns]
        assert min(slacks)>=0,(name,'dual infeasible')
        local=sum(n*values[r][0] for r,n in H.items())
        dual_objective=sum(stock[r]*theta[r] for r in ranks)+sum(demand[w]*mu[w] for w in ws)
        gap=local+dual_objective-Q(deficit)/b
        assert gap>0,(name,'no strict exclusion')
        receipts[name]=dict(minimum_pattern_slack=str(min(slacks)),local_excess_lower=str(local),dual_objective=str(dual_objective),strict_excess_lower=str(gap),moment_minus_one_lower=str(b*gap/(m*W)))
    return b,receipts

b,receipts=prove(cert)
controls=[]
for name,changed in [('current_admitted_b',dict(cert,excluded_b=published['complex_lower'])),('inflated_stock_dual',copy.deepcopy(cert))]:
    if name=='inflated_stock_dual':changed['dual'][0]=str(Q(changed['dual'][0])+1)
    try:prove(changed)
    except AssertionError:controls.append(name)
    else:raise AssertionError('invalid certificate accepted: '+name)
current=Q(published['complex_lower']);k=Q(composition['kappa']);limit=b/(1+b)
assert current<b and k<limit
result=dict(status='PASS_EXACT_STATIC44_POOLED_HOSTING_CEILING',excluded_b=str(b),current_admitted_b=str(current),strict_kappa_ceiling=str(limit),current_composed_kappa=str(k),kappa_headroom_upper=str(limit-k),relative_kappa_headroom_percent_upper=str(100*(limit/k-1)),stock=dict(stock),helper_widths=dict(widths),demands=demand,patterns_checked=len(patterns),moment_engines=receipts,negative_controls=controls,manifest_sha256=sha(ROOT/'MANIFEST.json'),scope='All fractional pooled whole-helper packings of this fixed local word, idle-child stock, nine-stage chain, eight replicas and helper widths. Chronology, owner identity and integer restrictions are relaxed. Other local words, stage chains, widths or compiler/outer architectures are not bounded.')
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],'b <',str(b),'kappa headroom <',float(limit-k),flush=True)
