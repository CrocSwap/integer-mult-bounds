#!/usr/bin/env python3
"""Independent host-integer evidence audit; no Tensor/cohort/factory imports."""
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent/'real-packed-outer-consumer-20261023'
def need(x,m):
    if not x:raise ValueError(m)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def bits_hash(bits):
    need(all(type(b) is int and b in (0,1) for b in bits),'literal bit array')
    return sha256(bytes(bits)).hexdigest()
def words(bits,width,count):
    need(len(bits)==width*count,'exact full signed record length')
    bits_hash(bits);out=[]
    for i in range(count):
        row=bits[i*width:(i+1)*width]
        x=sum(b<<j for j,b in enumerate(row))
        out.append(x-(1<<width) if row[-1] else x)
    return out
def complex_words(bits):
    values=words(bits,50,70)
    return list(zip(values[::2],values[1::2]))
def encode_words(values,width):
    need(all(-(1<<(width-1))<=v<(1<<(width-1)) for v in values),'signed word headroom')
    return [(v>>j)&1 for v in values for j in range(width)]
def encode_complex(values):return encode_words([v for pair in values for v in pair],50)
def crt(v):
    out=[None]*35
    for k,x in enumerate(v):out[(k%5)*7+(3*k%7)]=x
    return out
def inverse_crt(v):return [v[(k%5)*7+(3*k%7)] for k in range(35)]
def truncate(v,shift):return (-1 if v<0 else 1)*(abs(v)>>shift)
def nearest(v,shift):return (-1 if v<0 else 1)*((abs(v)+(1<<(shift-1)))>>shift)

freeze=json.loads((AUTHOR/'FULL-ATTEMPT2-FREEZE.json').read_text())
for name,h in freeze['files'].items():need(digest(AUTHOR/name)==h,'frozen postrun evidence '+name)
receipt_path=AUTHOR/'FULL-PACKED-ATTEMPT2-RESULT.json'
r=json.loads(receipt_path.read_text())
c=json.loads((AUTHOR/'FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json').read_text())
need(r['status']=='PASS_ACTUAL_TWO_TENSOR_STAGED_PACKED_CALLER','actual successful staged endpoint')
need(r['before_hashes']==r['after_hashes'],'recorded source/candidate hashes unchanged')
for path,h in r['before_hashes'].items():need(digest(AUTHOR/path)==h,'current scientific bytes '+path)
need(r['harness_sha256']==r['harness_after_sha256']==digest(AUTHOR/'run_full_packed_attempt2_DRAFT.py')=='c7bb6a705f42469709995f7d8a4c29ab0c12764d744546508a443151ec0345dc','exact reviewed executed harness')
need(r['source_and_candidate_unchanged'] and r['harness_unchanged'],'integrity flags')
need(r['Tensor_calls']==2 and r['Converter_calls']==3 and r['injected_child_dispatches']==1,'exact dispatch counts')
ts,cs=r['actual_Tensor_observations'],r['actual_Converter_observations']
need(len(ts)==2 and len(cs)==3,'durable completed return counts')
need(c['actual_Tensor_observations']==ts and c['actual_Converter_observations']==cs,'durable checkpoint/receipt child equality')
need(c['actual_pointwise_bits']==r['arrays']['actual_pointwise_bits'],'durable checkpoint/receipt product equality')
need(c['harness_sha256']==r['harness_sha256'] and c['candidate_sha256']==r['before_hashes']['packed_sandwich_DRAFT.py'],'checkpoint identity')
stage_hashes=[]
for item in ts+cs:
    need(bits_hash(item['raw_bits'])==item['return_sha256'],'actual return hash')
    if 'input_raw_bits' in item:need(bits_hash(item['input_raw_bits'])==item['input_sha256'],'actual CRT input hash')
    stage_hashes.append(item['return_sha256'])
need([x['opposite'] for x in ts]==[False,True],'forward/opposite flags')
need([x['inverse'] for x in cs]==[False,False,True],'two forward CRT/one inverse')
digits1,digits2=r['independent_digit_streams']
need(digits1==[255,0,3,17] and digits2==[1,254,0,9],'frozen independent fixture')
naturals=[]
for digits,observation in zip((digits1,digits2),cs):
    ingress=[(v<<(48-8-2),0) for v in digits]+[(0,0)]*31
    need(complex_words(observation['input_raw_bits'])==ingress,'actual physical ingress records')
    natural=complex_words(observation['raw_bits'])
    need(natural==crt(ingress),'independent exact CRT orientation')
    need(all(im==0 for _,im in natural),'real converted input')
    naturals.append(natural)
packed=[(u[0],v[0]) for u,v in zip(*naturals)]
need(bits_hash(encode_complex(packed))==ts[0]['input_sha256'],'actual packed Tensor input from actual CRT returns')
need(all(a*a+b*b<(1<<94) for a,b in packed),'strict packed half-disk input')
forward=complex_words(ts[0]['raw_bits'])
need([list(x) for x in forward]==r['arrays']['expected_forward'],'all35 actual forward records match frozen staged target')
reflected=[forward[((-i)%5)*7+((-j)%7)] for i in range(5) for j in range(7)]
need([list(x) for x in reflected]==r['arrays']['expected_J'],'J of captured actual H matches target')
product=[]
for (a,b),(c0,d) in zip(forward,reflected):
    ar,ai,br,bi=a+c0,b-d,b+d,c0-a
    need(all(-(1<<50)<=v<(1<<50) for v in (ar,ai,br,bi)),'widened51bit raw split headroom')
    # Four-split-product formula is independent of the author's squared formula.
    rr,ii=ar*br-ai*bi,ar*bi+ai*br
    need(rr==2*a*b+2*c0*d and ii==-a*a+b*b+c0*c0-d*d,'exact split-product identity')
    product.append((truncate(rr,50),truncate(ii,50)))
actual_product=complex_words(r['arrays']['actual_pointwise_bits'])
need(product==actual_product,'host exact raw-split/shift50 result equals physical product')
need([list(x) for x in product]==r['arrays']['expected_product'],'all35 product target records')
need(bits_hash(encode_complex(product))==ts[1]['input_sha256'],'actual opposite input is actual once-truncated product')
need(all(a*a+b*b<=(1<<94) for a,b in product),'actual opposite half-disk input')
opposite=complex_words(ts[1]['raw_bits'])
need([list(x) for x in opposite]==r['arrays']['expected_opposite'],'all35 actual opposite target records')
need(all(pair==(0,0) for pair in opposite),'observed opposite result is zero')
recovered=[nearest(a*35*35*(1<<20),48) for a,_ in opposite]
need(words(cs[2]['input_raw_bits'],86,35)==recovered,'host twoS/shift20/nearest recovery from captured opposite')
ordinary=inverse_crt(recovered)
need(words(cs[2]['raw_bits'],86,35)==ordinary,'actual inverse CRT of recovered records')
need(ordinary==r['arrays']['expected_coefficients'],'all35 ordinary coefficient target')
diagnostic=sum(v*256**i for i,v in enumerate(ordinary))
expected_bits=[(diagnostic>>i)&1 for i in reversed(range(64))]
need(r['output_bits']==expected_bits and len(expected_bits)==64,'exact prescribed carry bits')
need(bits_hash(expected_bits)==r['output_sha256'],'actual output hash')
true=sum(v*256**i for i,v in enumerate(digits1))*sum(v*256**i for i,v in enumerate(digits2))
need(diagnostic==r['staged_integer']==0 and true==r['true_integer']==43113955509404415,'prominent diagnostic versus true values')
need(r['diagnostic_difference']==diagnostic-true==-43113955509404415 and not r['diagnostic_equals_true_product'],'mismatch retained')
need(not r['require_recovery'] and not r['production_recovery_claim'],'no production admission')
need(r['actual_counts']==dict(conversions=3,transforms=2,pointwise_products=1,packed_records=35,J_axis_passes=2,split_records=35,split_exact_adds=140,pointwise_real_products=140),'finite parent counters')
tensor_counts=dict(natural_padding=4,gathers=4,halos=4,expansion_axes=2,compression_axes=2,assembled_axes=2,chirps=1)
need(all(t['complete_child_counts']==tensor_counts for t in ts),'perTensor complete stage counters')
for ob in cs:
    counts=ob['complete_child_counts']
    need(counts==dict(global_routes=1,triangular_shifts=2,padding_passes=2,router=dict(batches=1,edges=3,involutions=2,literal=1)),'perCRT stage counters')
for name in ('pending_end_head_rejected','consume_and_reuse_policy_checked','borrowed_values_heads_restored','metadata_values_heads_restored','resident_empty_origin_checks'):
    need(r[name] is True,'executed lifecycle assertion '+name)
need(r['injected_failure_cut']=='first Converter dispatch before original child operation','limited injected failure cut')
log=(AUTHOR/'FULL-PACKED-ATTEMPT2.log').read_text()
need(all(log.count(s)==1 for s in ('NUMERICAL_TENSOR_START 0 False','NUMERICAL_TENSOR_FINISH 0','NUMERICAL_TENSOR_START 1 True','NUMERICAL_TENSOR_FINISH 1')),'log confirms two numerical starts/finishes')
backup=json.loads((AUTHOR/'full-attempt1-frozen/SHA256SUMS.json').read_text())
for name,h in backup.items():
    need(digest(AUTHOR/name)==h and digest(AUTHOR/'full-attempt1-frozen'/name)==h,'earlier failure unchanged '+name)
nonzero=lambda values:sum(a!=0 or b!=0 for a,b in values)
need((nonzero(forward),nonzero(product),nonzero(opposite))==(28,35,0),'nonzero stage census')
result={'status':'PASS_INDEPENDENT_POSTRUN_STAGED_EVIDENCE_REVIEW',
 'no_numeric_replay_or_cohort_import':True,'observed_integer':diagnostic,'staged_integer':r['staged_integer'],
 'true_integer':true,'observed_minus_true':diagnostic-true,'accurate_integer_recovery_claim':False,
 'receipt_sha256':digest(receipt_path),'checkpoint_sha256':digest(AUTHOR/'FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json'),
 'completed_Tensor_returns':2,'completed_CRT_returns':3,'records_each':35,
 'signed_component_bits':50,'inverse_CRT_record_bits':86,'output_bits':64,
 'raw_return_lengths':[len(x['raw_bits']) for x in ts+cs],
 'raw_return_hashes':stage_hashes,'independent_physical_product_sha256':bits_hash(encode_complex(product)),
 'source_and_candidate_current_hashes_checked':len(r['before_hashes']),
 'nonzero_records':{'forward':28,'product':35,'opposite':0},
 'product_max_squared_norm_numerator':max(a*a+b*b for a,b in product),'squared_norm_denominator':1<<96,
 'normal_lifecycle_flags_and_exact_harness_assertions_verified':True,
 'failure_cut':'pre-firstConverter dispatch only; earlier deadline numerical-child cleanup failure remains',
 'seconds_reported':r['seconds'],'all_prior_failure_artifacts_preserved':True,
 'limits':['No production accuracy/admission','Zero opposite makes recovery normalization check degenerate','Four full-stage mutations unrun','No full priced tariff or matched speedup','No recursive moment/compiler reserve/kappa claim']}
(HERE/'POSTRUN-CHECK-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],'observed=0 true=43113955509404415 difference=-43113955509404415')
