"""One reversed child per actual projector in the verified minimal-V word.
Transplants icekylinx PR104's opposite-bank/stopped-product compiler only.
Rebuilds local ranks from the literal event stream, never from old widths.
"""
import gzip
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

P=Path(__file__).resolve().parent
wordpath=P/'round8-foundations-minimal-v-word.json.gz'
wordraw=wordpath.read_bytes();word=json.loads(gzip.decompress(wordraw))
ledgerpath=P/'round8-network-minimal-v-ledger/result.json'
ledger=json.loads(ledgerpath.read_text())
assert ledger['candidate_sha256']==hashlib.sha256(wordraw).hexdigest()
assert all(ledger[k] for k in ('complete_forward_F2','complete_reflected_F2',
    'actual_source_V_order_checked','all_scalar_gates_equal_frame_keys','histogram_matches_external'))
D=json.loads(gzip.decompress((P/'round7-public/tree/certificates/round7/deferred_23.json.gz').read_bytes()))
sigma=dict(zip(D['readout_order'],D['sigma']))
for s in word['removed_original_slots']:sigma.pop(s)
sigma.update({int(s):B for s,B in word['new_frames'].items()})
h=23;m=h*h;v=1771;N=v*v;R=D['R'];W=2*N+2*v*R
assert R==28866 and W==108516254
local={k:Counter() for k in ('auxiliary_steps','source_steps','target_steps','copied_centres')}
eventpath=P/'round8-network-minimal-v-ledger/forward-events.i32.gz'
events=gzip.decompress(eventpath.read_bytes());assert len(events)%20==0
for kind,a,b,c,r in struct.iter_unpack('<iiiii',events):
    if kind==0:
        assert 0<=r<=h
        if r:local['auxiliary_steps' if a>=2*v else 'source_steps' if a<v else 'target_steps'][r]+=1
    elif kind==2:
        assert r==h-1
        local['copied_centres'][r]+=1
    else:assert kind==1 and r==0
assert len(events)//20==ledger['events']
assert local['auxiliary_steps']==Counter({int(k):n for k,n in ledger['rank_histograms']['aux'].items()})
assert local['source_steps']+local['target_steps']==Counter({int(k):n for k,n in ledger['rank_histograms']['data'].items()})
assert local['copied_centres']==Counter({int(k):n for k,n in ledger['rank_histograms']['center'].items()})
parts={name:Counter({r:2*v*n for r,n in values.items()}) for name,values in local.items()}
parts['auxiliary_exteriors']=Counter()
for s in range(R):
    r=m-h+len(sigma.get(s,[]))
    assert 0<r<m
    parts['auxiliary_exteriors'][r]+=2*v
parts['data_bridges']=Counter({(h-1)**2:2*N})
parts['endpoint_copies']=Counter({1:N})
H=Counter()
for part in parts.values():H.update(part)
s=sum(r*n for r,n in H.items())
assert s==57403754177==word['histogram']['s']==W*m-N+2*v*h*(h-1)
assert all(0<r<m and n>0 for r,n in H.items())
out=dict(status='Complete profile rebuilt from locally replayed literal word; PR104 stopped interface applies conditionally',
    compiler_credit='icekylinx PR104',compiler_commit='948ce1510df750f4c18b96bdaef436a86f8bf834',
    word_sha256=hashlib.sha256(wordraw).hexdigest(),ledger_sha256=hashlib.sha256(ledgerpath.read_bytes()).hexdigest(),
    events_sha256=hashlib.sha256(eventpath.read_bytes()).hexdigest(),literal_forward_events=len(events)//20,
    h=h,m=m,v=v,R=R,W=W,N=N,s=s,deficit=W*m-s,maxchild=max(H),hist=dict(sorted(H.items())),
    classes={name:dict(calls=sum(values.values()),rank=sum(r*n for r,n in values.items()),hist=dict(sorted(values.items()))) for name,values in parts.items()},
    scope='Each nested residual, gauged auxiliary exterior, data bridge and endpoint copy is individually idempotent. One common generic basis plus opposite-bank conjugation preserves the complete operator; no local basis switches. No stopped saving or multiplication exponent certified in this file.')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('hist','classes')},indent=2))
