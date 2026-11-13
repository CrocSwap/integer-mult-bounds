"""Assemble a concise result from successful fresh native and signed receipts."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from collections import Counter
import gzip,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
read=lambda p:json.loads(Path(p).read_text())
n=read(HERE/'validation_native/NATIVE-RESULT.json')
s=read(HERE/'validation_signed/RESULT.json')
b=read(HERE/'reroute/RESULT.json')
assert n['status']=='PASS_CHANGED_485_1455_PRODUCER_COMPLETE_NATIVE'
assert s['status']=='PASS_CHANGED_485_1455_PRODUCER_COMPLETE_SIGNED_APPLICATION'
word_hash=sha256(gzip.decompress((HERE/'reroute/WORD.json.gz').read_bytes())).hexdigest()
assert word_hash==n['word_canonical_sha256']==b['candidate_canonical_sha256']=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
assert s['caller_sha256']=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
claim=Q(s['claim']);threshold=Q('0.003646777872835');assert claim>threshold
before=s['price']['before'];after=s['price']['after']
paid_delta={k:after['P'].get(k,0)-before['P'].get(k,0)for k in sorted(set(before['P'])|set(after['P']),key=int)if after['P'].get(k,0)!=before['P'].get(k,0)}
assert paid_delta=={'1':17,'3':-17,'4':-17,'6':17}
assert after['T']==before['T']and after['S']==before['S']==1424
assert after['empty_root_credits']==before['empty_root_credits']==0
assert sum(after['P'].values())==110519 and sum(after['T'].values())==22461
assert s['price']['gate']['outer']['strict_count']==54
assert s['price']['gate']['outer']['functional_count']==4
partial=s['checks']['ODD-ADMISSION-PARTIAL.json']
precision=s['checks']['ODD-PRECISION.json']
tape=s['checks']['ODD-FIXED-TAPE-COUNTS.json']
result={'status':'PASS_COMPLETE_CONDITIONAL_CHANGED_PRODUCER',
 'source_head':'58a9d052143f5d85295ed2d0163591c47f89a331',
 'canonical_main_pin':'e54523517d0f03e58352e647c403a5af3e525a57',
 'caller_head':'07a76c5e2738882c0cb322278e56f6cae3c9885d',
 'caller_sha256':s['caller_sha256'],'candidate_canonical_sha256':word_hash,
 'candidate_gzip_sha256':sha256((HERE/'reroute/WORD.json.gz').read_bytes()).hexdigest(),
 'conditional_claim':str(claim),'claim_decimal':s['price']['price']['claim_decimal'],
 'comparison_claim':str(threshold),'exact_claim_improvement':str(claim-threshold),
 'directed_crossing_bracket':s['price']['gate']['raw_bracket'],
 'native_paid_delta':b['paid_delta'],'native_productive_delta':{},
 'signed_paid_delta':paid_delta,'signed_productive_delta':{},
 'paid_calls':110519,'productive_calls':22461,'surplus':1424,'empty_credit':0,
 'native_events':76475,'added_operations':{'ADD':3},'owned_labels':68,'owned_lifetimes':74,'owned_peak':50,
 'grid':{'odd_scale':1125,'fractional_bits':25},
 'ordinary_bound':partial['ordinary']['conservative_total'],
 'ordinary_increase':partial['ordinary']['conservative_total']-782784552,
 'precision_coefficient':precision['context_c'],
 'fixed_tape':{k:tape[k]for k in('native_invocations','monomial_map_slots','elementary_records_upper','scalar_services_upper','context_c')},
 'outer':s['price']['gate']['outer'],
 'assumptions':['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
 'receipt_sha256':{str(p.relative_to(HERE)):sha256(p.read_bytes()).hexdigest()for p in[HERE/'validation_native/NATIVE-RESULT.json',HERE/'validation_signed/RESULT.json',HERE/'reroute/INDEPENDENT-RESULT.json',HERE/'reroute/ADVERSARIAL.json']},
 'scope':'Fresh source-aware local replay under the five retained assumptions. No maintainer selection or canonical edit is made.'}
(HERE/'APPLICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
