"""Exact hash-chain validation with two named discovery-root differences.

No producer mathematics is changed. Raw fresh hashes are verified first.
Only record.numerical_complex_root and flow.numerical_local_root are allowed
the same diagnostic rounding already used by upstream PR193. Every other
record/flow value and the full exact program payload retain frozen identity.
"""
import copy,gzip,hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
PREFIX='research/source-assisted-v4/.work/'
RECORD=PREFIX+'aligned/cache/record.json'
FLOW=PREFIX+'flow.json'
PAYLOAD_SHA256='6d5aa89e0a06c449ee60611d95d1e535a76c42a09b274d021e4001238ca20c45'
RECORD_SHA256='2065cbaa22c87198a4d535119534e05fab4a258445ecda00cf3cbb9151cfcc30'
FLOW_SHA256='ecc1b61843c40303516f05721d708e3f8183ba9c7fea2551da45028d557f7af3'
PROGRAM_SHA256='3b4e671d7c6630570b04788bb2c81629e2c52f8dc2fcc5805952f0b403921027'
WITNESS_SHA256='51da02c6cd844276ca26608f1b714ab07d476ec25634ad1a9b461ccda2fbe457'
def digest(b):return hashlib.sha256(b).hexdigest()
def compact(x):return (json.dumps(x,separators=(',',':'))+'\n').encode()
def pretty(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def canon(x):
    if isinstance(x,float):return format(x,'.12e')
    if isinstance(x,dict):return {k:canon(v) for k,v in x.items()}
    if isinstance(x,list):return [canon(v) for v in x]
    return x
def unique(pairs):
    d={}
    for k,v in pairs:
        assert k not in d,'Duplicate JSON key';d[k]=v
    return d
def decode(b):return json.loads(b,object_pairs_hook=unique)
def root_equal(x,y):
    assert type(x) is float and math.isfinite(x) and x>0
    assert format(x,'.12e')==format(y,'.12e'),'Discovery root changed beyond upstream precision'
def normalized(result):
    x=copy.deepcopy(result)
    x['flow']['cache_sha256']['record.json']=RECORD_SHA256
    x['lift_certificate_sha256']=PAYLOAD_SHA256
    x['lift']['certificate_sha256']=PAYLOAD_SHA256
    cp=x['complex_profile'];cp['exact_lift_certificate_sha256']=PAYLOAD_SHA256
    chain=cp['proof_chain_sha256'];chain[RECORD]=RECORD_SHA256;chain[FLOW]=FLOW_SHA256
    chain[PREFIX+'lift.certificate.json.gz']=PAYLOAD_SHA256
    chain[PREFIX+'lift.json']=digest(json.dumps(x['lift'],sort_keys=True,separators=(',',':')).encode())
    x['assembly']['construction_receipts']['complex_lift_certificate_sha256']=PAYLOAD_SHA256
    x['assembly']['source_sha256']['complex']=digest(json.dumps(cp,sort_keys=True,separators=(',',':')).encode())
    return x
def validate(actual,published,repo,read_bytes=None):
    repo=Path(repo);read_bytes=read_bytes or (lambda p:p.read_bytes())
    raw=lambda rel:read_bytes(repo/rel)
    obj=lambda rel:decode(raw(rel))
    # The same golden record/flow byte boundaries, without shipping cache fixtures.
    # These two values are diagnostic representatives; all other bytes stay exact.
    expected_record_root=0.0005471133463770652
    expected_flow_root=0.0007009184438593611
    assert published['flow']['cache_sha256']['record.json']==RECORD_SHA256
    assert published['complex_profile']['proof_chain_sha256'][FLOW]==FLOW_SHA256
    record,flow=obj(RECORD),obj(FLOW)
    assert compact(record)==raw(RECORD) and pretty(flow)==raw(FLOW),'Unexpected upstream serialization'
    root_equal(record['numerical_complex_root'],expected_record_root)
    root_equal(flow['numerical_local_root'],expected_flow_root)
    assert set(flow['cache_sha256'])==set(published['flow']['cache_sha256']),'Missing or additional cache binding'
    for name,h in flow['cache_sha256'].items():
        assert name in ('graph.json','frames.json','selection.json','record.json')
        assert digest(raw(PREFIX+'aligned/cache/'+name))==h,'Actual flow/cache binding changed'
    rr=copy.deepcopy(record);rr['numerical_complex_root']=expected_record_root
    assert digest(compact(rr))==RECORD_SHA256,'An exact record field changed'
    ff=copy.deepcopy(flow);ff['numerical_local_root']=expected_flow_root;ff['cache_sha256']['record.json']=RECORD_SHA256
    assert digest(pretty(ff))==FLOW_SHA256,'An unapproved flow field changed'
    proof=raw(PREFIX+'lift.certificate.json.gz');payload=gzip.decompress(proof);cert=decode(payload)
    assert compact(cert)==payload,'Unexpected proof serialization'
    assert set(cert)=={'signature','schema','input_witness_sha256','input_profile_sha256','maps','topological_order','kernel_pairs'}
    assert cert['input_profile_sha256']==digest(raw(FLOW)), 'Actual embedded flow hash mismatch'
    assert cert['input_witness_sha256']==digest(raw(PREFIX+'flow.witness.json'))==WITNESS_SHA256
    binding={k:cert[k] for k in ('maps','topological_order','kernel_pairs')}
    assert digest(json.dumps(binding,separators=(',',':')).encode())==PROGRAM_SHA256
    fixed=copy.deepcopy(cert);fixed['input_profile_sha256']=FLOW_SHA256
    assert digest(compact(fixed))==PAYLOAD_SHA256,'Exact proof changed beyond its bound diagnostic-profile hash'
    proof_hash=digest(proof);lift=obj(PREFIX+'lift.json');cp=obj(PREFIX+'complex-profile.json');glob=obj(PREFIX+'global.json')
    for branch in ('complex','bit'):glob[branch].pop('numerical_root_for_discovery_only',None)
    assert actual['lift']==canon(lift) and actual['complex_profile']==canon(cp)
    assert actual['flow']==canon(flow) and actual['assembly']==canon(glob)
    assert actual['witness_sha256']==WITNESS_SHA256
    assert lift['exact_scalar_program_sha256']==cp['exact_scalar_program_sha256']==PROGRAM_SHA256
    assert actual['lift_certificate_sha256']==lift['certificate_sha256']==cp['exact_lift_certificate_sha256']==proof_hash
    assert glob['construction_receipts']['complex_lift_certificate_sha256']==proof_hash
    assert glob['source_sha256']['complex']==digest(raw(PREFIX+'complex-profile.json'))
    assert glob['source_sha256']['bit']==digest(raw('research/source-assisted/bit/source_aligned_profile.json'))
    assert set(cp['proof_chain_sha256'])==set(published['complex_profile']['proof_chain_sha256']),'Missing or additional proof-chain binding'
    for rel,h in cp['proof_chain_sha256'].items():
        p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
        assert digest(raw(rel))==h,'Actual proof-chain mismatch: '+rel
    assert normalized(actual)==normalized(published),'Unexplained canonical result difference'
    return dict(status='PASS exact program with two bound discovery-root diagnostics',
      actual_record_sha256=digest(raw(RECORD)),actual_flow_sha256=digest(raw(FLOW)),
      actual_payload_sha256=digest(payload),normalized_full_payload_sha256=PAYLOAD_SHA256,
      exact_scalar_program_sha256=PROGRAM_SHA256,witness_sha256=WITNESS_SHA256,
      actual_compressed_sha256=proof_hash,upstream_canonical_equality=(actual==published),
      permitted_root_fields=['aligned/cache/record.json:numerical_complex_root','flow.json:numerical_local_root'],
      root_values=dict(record_actual=record['numerical_complex_root'],record_cloud=expected_record_root,flow_actual=flow['numerical_local_root'],flow_cloud=expected_flow_root),
      scope='Every actual hash edge checked before normalization. All other record/flow bytes and full maps/topology/kernel proof bytes retain frozen identity after the explicitly bound hash substitution. Fresh caller records upstream direct canonical equality separately; no historical execution record is required.')
