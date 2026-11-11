"""Independent set-valued causal slots, exact column kernel and receiver rank gaps."""
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

root,receipt=map(Path,sys.argv[1:])
r=json.loads(receipt.read_bytes())
pins={}
for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
    key,digest,_=line.split('\t')
    assert key not in pins
    pins[key]=digest
assert pins==r['pins']


def read(key):
    raw=(root/key).read_bytes()
    assert sha256(raw).hexdigest()==pins[key]
    return raw


def basis(rows):
    pivots={}
    for row in rows:
        while row:
            i=min(row)
            if i not in pivots:
                pivots[i]=row
                break
            row^=pivots[i]
    return pivots


def agree(a,b):
    x=basis(a)
    y=basis(b)
    assert len(x)==len(y)==len(basis([*x.values(),*y.values()]))


w=json.loads(gzip.decompress(read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')))
R22=json.loads(read('round22/RESULT.json'))
R24=json.loads(read('round24/RESULT.json'))
R25=json.loads(read('round25/RESULT.json'))
prior={a['event']:a for a in R25['carriers']}
marks=[p for p in R24['incidence'] if p['marked']]
mark_events=[p['event'] for p in marks]
variants=json.loads(read('pr7209/RESULT.json'))['bank_maps']
singletons=[b['banks'][0] for b in R22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
actual={}
for carrier,record in prior.items():
    owner=record['owner']
    program=w['program']
    assert program[carrier]==['MOVE',owner,record['source_chart'],record['target_chart']]
    e=next(k for k in range(carrier+1,len(program))
           if program[k][1]==owner or (program[k][0] in ('ADD','SWAP') and program[k][2]==owner))
    op,i,j,f=program[e]
    assert op=='ADD' and j==owner and f==record['target_chart']
    actual[carrier]=[('paid',owner,record['source_chart'])]
    actual[e]=[('ordinary',i,f),('ordinary',j,f)]
slots=defaultdict(list)
for i,s in enumerate(r['sources']):
    assert s['index']==i
    assert s['cut']==s['event']+(s['kind']=='ordinary')
    slots[s['event']].append(s)
assert {e:[(a['kind'],a['owner'],a['chart']) for a in s] for e,s in slots.items()}==actual
assert len(actual)==120 and len(r['sources'])==180
N=w['public']
frames=w['start']+[None]*w['owned_fields']
old=[frozenset([j]) for j in range(N)]+[frozenset()]*w['owned_fields']
state=[frozenset()]*len(old)
observations=defaultdict(set)
terminal={}
terminal_markers={}
paid={}
source_bases=[]


def bind(event,slots):
    chart=slots[0]['chart']
    assert all(frames[s['owner']]==chart for s in slots)
    rows={i:(old[i],state[i]) for i,f in enumerate(frames) if f==chart}
    raw=set(a for a,_ in rows.values())
    for _,mask in rows.values():
        for i in mask:
            raw.update(source_bases[i])
    for s in slots:
        given={x['owner']:(frozenset(x['old_row']),frozenset(x['earlier_slots'])) for x in s['source_rows']}
        assert given==rows and s['index']==len(source_bases)
        b=[frozenset(x) for x in s['causal_source_basis']]
        agree(raw,b)
        assert len(b)==len(basis(b))
        source_bases.append(b)


def observe(i,c):
    if state[i]:
        observations[frames[i]].add((c,i,state[i]))


for t,(op,i,*a) in enumerate(w['program']):
    allowed=slots.get(t,[])
    if op=='MOVE':
        f,g=a
        assert frames[i]==f and f!=1
        if g==1:
            terminal[t]=old[i]
            terminal_markers[t]=(i,state[i])
        elif not allowed:
            paid[t]=state[i]
        if allowed:
            bind(t,allowed)
            s,=allowed
            assert s['cut']==t and s['target_chart']==g
            assert frozenset(s['old_row'])==old[i]
            state[i]^=frozenset([s['index']])
        frames[i]=g
    elif op=='ADD':
        j,f=a
        assert frames[i]==frames[j]==f
        old[i]^=old[j]
        state[i]^=state[j]
        observe(i,t+1)
        if allowed:
            bind(t,allowed)
            for s in allowed:
                assert s['cut']==t+1
                k=s['owner']
                state[k]^=frozenset([s['index']])
                observe(k,t+1)
    elif op=='SWAP':
        j=a[0]
        frames[i],frames[j]=frames[j],frames[i]
        old[i],old[j]=old[j],old[i]
        state[i],state[j]=state[j],state[i]
        observe(j,t+1)
    else:
        assert op in ('INIT','CLEAR') and a[0]!=1
        assert frames[i]==(None if op=='INIT' else a[0])
        frames[i]=a[0] if op=='INIT' else None
        old[i]=state[i]=frozenset()
    observe(i,t+1)
assert frames==w['final']+[None]*w['owned_fields']
assert old==[frozenset([j-111,j]) if 111<=j<222 else frozenset([j]) for j in range(N)]+[frozenset()]*w['owned_fields']
ext={j:state[j] for j,f in enumerate(frames[:N]) if f!=1}
assert len(paid)==2266 and len(ext)==114 and len(terminal)==545
assert {str(t):sorted(m) for t,m in paid.items() if m}==r['nonzero_protected_markers']
assert {str(j):sorted(m) for j,m in ext.items() if m}==r['nonzero_exterior_markers']


response=defaultdict(set)
for k,table in enumerate((paid,ext)):
    for event,mask in table.items():
        for slot in mask:
            response[slot].add((k,event))
variables=[(i,v) for i,rows in enumerate(source_bases) for v in rows]
columns={}
null=[]
for j,(slot,v) in enumerate(variables):
    column=frozenset((k,t,a) for k,t in response[slot] for a in v)
    coeff=frozenset([j])
    while column:
        p=min(column)
        if p not in columns:
            columns[p]=(column,coeff)
            break
        a,b=columns[p]
        column^=a
        coeff^=b
    if not column:
        null.append(coeff)
assert len(variables)==1036 and len(columns)==148 and len(null)==888


def exposed(mask,nullbasis):
    rows=set()
    for v in nullbasis:
        row=frozenset()
        for k in v:
            slot,a=variables[k]
            if slot in mask:
                row^=a
        if row:
            rows.add(row)
    return rows


U=[v for t,v in terminal.items() if t not in mark_events]
W=[v for f,v in zip(frames,old) if f==1]
assert len(basis(U))==523 and len(basis(W))==len(basis(terminal.values()))==545
assert len(basis(W+list(terminal.values())))==545
window={p['event']:p['quiet_window'] for p in R24['incidence']}
price=next(x['price'] for x in R25['scopes'][0]['recipients'] if 'price' in x)
summary=[]
for mode,s in enumerate(r['scopes']):
    chosen=null if not mode else [frozenset([j]) for j in range(len(variables))]
    agree(chosen,[frozenset(v) for v in s['null_basis']])
    assert s['rank']==(148 if not mode else 0) and s['nullity']==len(chosen)
    for cm,clock in enumerate(s['clocks']):
        assert clock['price']==price
        assert all(Fraction(a['net_upper'][1])<0 for b in price.values() for a in b)
        assert clock['expanded_singleton_upper']==0
        for j,p in zip(singletons,clock['recipients'],strict=True):
            mark=marks[j]
            lim=mark['quiet_window'][1] if cm else mark['event']
            charts={mark['source_chart'],*mark['compatible_literal_charts']}
            paths={(c,i,f,m) for f in charts for c,i,m in observations[f] if c<=lim}
            for var in variants[j]['variants']:
                for e in var['virtual_bank_events']:
                    owner,mm=terminal_markers[e]
                    if mm and (window[e][0] if cm else e)<=lim:
                        paths.add((e,owner,var['literal_chart'],mm))
            masks={v[3] for v in paths}
            assert masks=={frozenset(a['slots']) for a in p['observed_markers']}
            for a in p['observed_markers']:
                c,i,f,_=a['witness']
                assert (c,i,f,frozenset(a['slots'])) in paths
            raw=set().union(*(exposed(m,chosen) for m in masks))
            assert len(basis(raw))==p['exposed_response_rank']
            oldlib={frozenset(a['row']) for a in R22['scope'][1]['banks'][j]['source_witnesses']}
            S=list(oldlib|raw)
            lower=U+[terminal[mark['event']]]
            # Compute the dimension gap by two sum ranks, independently of
            # the marked coordinate map used by the primary implementation.
            expansion=21-len(basis(S+W))+len(basis(S+lower))
            assert expansion==len(p['new_quotient_basis'])==0
    summary.append({'scope':s['scope'],'coefficient_rank':s['rank'],'kernel_dimension':s['nullity'],
                    'recipient_modes':2,'expanded_singletons':0})
print(json.dumps({'status':'PASS','causal_slots':180,'coefficients':len(variables),'protected_contacts':2266,
                  'exterior_outputs':114,'scopes':summary},sort_keys=True))
