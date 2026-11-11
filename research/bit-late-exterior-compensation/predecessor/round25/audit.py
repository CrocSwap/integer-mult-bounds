"""Independent single-carrier impulse replay and column-rank proof."""
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
    path,digest,_=line.split('\t')
    assert path not in pins
    pins[path]=digest
assert pins==r['pins']


def read(path):
    raw=(root/path).read_bytes()
    assert sha256(raw).hexdigest()==pins[path]
    return raw


def span(seq):
    pivot={}
    for v in seq:
        while v:
            i=min(v)
            if i not in pivot:
                pivot[i]=v
                break
            v^=pivot[i]
    return pivot


def agree(actual,given):
    a=span(actual)
    b=span(given)
    assert len(a)==len(b)==len(span([*a.values(),*b.values()]))


w=json.loads(gzip.decompress(read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')))
R24=json.loads(read('round24/RESULT.json'))
R22=json.loads(read('round22/RESULT.json'))
price=json.loads(read('bit-price/RESULT.json'))
singletons=[b['banks'][0] for b in R22['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks'])==1]
marked=[x for x in R24['incidence'] if x['marked']]
spec={v['event']:(v['owner'],v['source_chart'],c['chart'],frozenset(v['row']),j)
      for j in singletons for c in marked[j]['clocks'][1]['compatible_charts'] for v in c['paid_ingress']}
carriers={a['event']:a for a in r['carriers']}
events=sorted(spec)
assert list(carriers)==events and len(events)==60
for e,(owner,source,target,row,j) in spec.items():
    a=carriers[e]
    assert (a['owner'],a['source_chart'],a['target_chart'],frozenset(a['old_row']),a['recipient'])==(owner,source,target,row,j)
    assert a['index']==events.index(e) and a['after_cut']==e+1
n=w['public']
size=n+w['owned_fields']
state=[frozenset([i]) for i in range(n)]+[frozenset()]*w['owned_fields']
frames=w['start']+[None]*w['owned_fields']
protected,terminal={},{}
source_rows={}
for t,item in enumerate(w['program']):
    op,i=item[:2]
    if op=='MOVE':
        a,b=item[2:]
        assert frames[i]==a and a!=1
        if t in spec:
            assert spec[t][:4]==(i,a,b,state[i])
            source_rows[t]={j:state[j] for j,f in enumerate(frames) if j!=i and f==a}
            assert source_rows[t]=={x['owner']:frozenset(x['row']) for x in carriers[t]['live_other_coframed_sources']}
        elif b!=1:
            protected[t]=i
        if b==1:
            terminal[t]=i
        frames[i]=b
    elif op=='ADD':
        j,a=item[2:]
        assert frames[i]==frames[j]==a
        state[i]^=state[j]
    elif op=='SWAP':
        j=item[2]
        state[i],state[j]=state[j],state[i]
        frames[i],frames[j]=frames[j],frames[i]
    else:
        assert op in ('INIT','CLEAR') and item[2]!=1
        assert frames[i]==(None if op=='INIT' else item[2])
        frames[i]=item[2] if op=='INIT' else None
        state[i]=frozenset()
assert frames==w['final']+[None]*w['owned_fields']
assert state==[frozenset([i-111,i]) if 111<=i<222 else frozenset([i]) for i in range(n)]+[frozenset()]*w['owned_fields']
outside=[j for j,f in enumerate(frames[:n]) if f!=1]
assert len(outside)==r['protected_exterior_output_count']==114
assert len(protected)==r['protected_paid_contact_count']==2266
assert len(terminal)==r['terminal_arrival_inputs_deferred']==545


def impulse(e):
    v=[0]*size
    p=[]
    peer_changes={}
    for t,item in enumerate(w['program']):
        op,j=item[:2]
        if op=='MOVE':
            if t in protected and v[j]:
                p.append(t)
            if t in spec:
                peer_changes[t]=[k for k in source_rows[t] if v[k]]
            if t==e:
                v[j]^=1
        elif op=='ADD':
            v[j]^=v[item[2]]
        elif op=='SWAP':
            k=item[2]
            v[j],v[k]=v[k],v[j]
        else:
            v[j]=0
    return p,[j for j in outside if v[j]],peer_changes


paid_marks={}
exterior_marks={}
paid_columns=[]
exterior_columns=[]
carriers_with_other_old_rows=0
for k,e in enumerate(events):
    p,q,peers=impulse(e)
    assert not any(peers.values())
    for j in p:
        paid_marks.setdefault(j,[]).append(k)
    for j in q:
        exterior_marks.setdefault(j,[]).append(k)
    paid_columns.append(frozenset(p))
    exterior_columns.append(frozenset(q))
    carriers_with_other_old_rows+=bool(span(source_rows[e].values()))
assert {str(k):v for k,v in paid_marks.items()}==r['nonzero_protected_contact_markers']
assert {str(k):v for k,v in exterior_marks.items()}==r['nonzero_exterior_markers']
assert all(not peer['earlier_carriers'] for a in carriers.values() for peer in a['live_other_coframed_sources'])
assert carriers_with_other_old_rows==60
summary=[]
for s in r['scopes']:
    p,q,joint,witness=[],[],[],[]
    variables=0
    subset=set(s['exterior_basis_roles'])
    for k,(e,rows) in enumerate(zip(events,s['carrier_source_bases'],strict=True)):
        assert e==rows['event']
        terms=[frozenset(v) for v in rows['rows']]
        other=list(source_rows[e].values())
        if s['source_scope']=='arbitrary current coframed replacement':
            other.append(spec[e][3])
        agree(other,terms)
        assert len(span(terms))==len(terms)
        variables+=len(terms)
        for delta in terms:
            x=frozenset((0,t,a) for t in paid_columns[k] for a in delta)
            y=frozenset((1,t,a) for t in exterior_columns[k] for a in delta)
            p.append(x)
            q.append(y)
            joint.append(x|y)
            witness.append(frozenset(k for k in y if k[1] in subset))
    expected=148 if s['source_scope']=='arbitrary current coframed replacement' else 88
    assert variables==s['variables']==expected
    assert len(span(p))==s['protected_only_coefficient_rank']
    assert len(span(q))==s['exterior_only_coefficient_rank']==expected
    assert len(span(joint))==s['equation_rank']==expected
    assert len(span(witness))==expected
    assert len(span(frozenset(v) for v in exterior_marks.values()))==s['exterior_scalar_marker_rank']==20
    assert len(subset)==20 and subset<=set(outside)
    assert s['joint_kernel_dimension']==0 and not s['kernel_coefficients'] and not s['joint_live_carrier_events']
    for d in s['recipients']:
        if 'bank_index' in d:
            j=d['bank_index']
            old=R22['scope'][1]['banks'][j]
            assert old['quotient_basis']==[[j]]
            assert not d['nonzero_joint_response_rows'] and not d['new_quotient_basis']
        else:
            assert d['expanded_singleton_upper']==d['independent_recipient_direction_upper']==0
            for trial,entries in d['price'].items():
                for item,threshold in zip(entries,price[trial],strict=True):
                    h=item['h']
                    old=R24['scopes'][1]['paid_refinement_price'][h]['directed'][trial]
                    assert item['stock_upper']==14+2*h
                    assert item['net_upper']==old['charged_net_upper'] and Fraction(item['net_upper'][1])<0
                    assert item['required_expansions']==threshold.get('needed_singleton_expansions')
                    assert not item['affordable_upper']
    summary.append({'source_scope':s['source_scope'],'variables':variables,'joint_rank':len(span(joint)),
                    'exterior_rank':len(span(q)),'paid_only_rank':len(span(p)),
                    'zero_leak_kernel_dimension':variables-len(span(joint)), 'singleton_expansions':0})
print(json.dumps({'status':'PASS','carrier_impulses':len(events),'protected_paid_contacts':len(protected),
                  'exterior_outputs':len(outside),'scopes':summary},sort_keys=True))
