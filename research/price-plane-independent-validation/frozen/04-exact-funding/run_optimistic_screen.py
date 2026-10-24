#!/usr/bin/env python3
"""Explicitly optimistic claim screen; must never be promoted to invoice evidence."""
from exact_engine import evaluate,MODEL
from pathlib import Path
import json,resource,hashlib
resource.setrlimit(resource.RLIMIT_AS,(500*1024*1024,500*1024*1024))
HERE=Path(__file__).resolve().parent
prior=HERE.parents[1]/'owned-relation-5377-cost-review-20261024/frozen/4610-round6-ARITHMETIC.json'
a=json.loads(prior.read_bytes());T={int(k):v for k,v in a['targets'].items()};P={int(k):v for k,v in a['paid'].items()}
T[9]-=128;P[1]-=128;P[8]-=128
config={'model':MODEL,'tuple':{'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'kappa':'.00302666','tested':'.00302667','reserve':'1/1000000000','root_bracket':['.00302667476807','.00302667476808'],'ordinary_BIT':a['ordinary_BIT']}
r=evaluate(T,P,config)
r.update(status='MODEL_ONLY_OPTIMISTIC_CLAIM_SCREEN',invoice_origin='Selected #4610 bill minus CLAIMED 128 H1,128 H8 paid and128 H9 targets. NOT independent #5383 census.',source_prior_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),config=config,independent_invoice_bound=False,source_capsule_bound=False,finite_template_gate_bound=False,endpoint_funded=False)
(HERE/'optimistic-screen-v1.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:r[k] for k in ['status','productive_count','paid_count','rank_mass_surplus','kappa','tested','H','j','seconds','endpoint_funded']}))
