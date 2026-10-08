"""Summarize local frozen-input proposals and independent finite certificates."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
rows=[]
for path in sorted(HERE.glob('*/h*/compiled.json')):
 d=json.loads(path.read_text());c=d['compiled'];stats=c['stats']
 row=dict(strategy=d['strategy'],axis=d['axis'],roles=c['roles'],xors=c['elementary_xors'],clearing_xors=stats.get('clearing_xors'),reclaimed=stats.get('reclaimed'),
   one_edge_exchanges=stats.get('local_moment_exchanges',0),two_edge_cycles=stats.get('local_two_edge_cycles',0),word_sha256=d['word_sha256'],record=str(path.relative_to(HERE)),
   missing_discovery_profile_pairs=d.get('missing_local_profile_pairs'),record_sha256=sha256(path.read_bytes()).hexdigest(),source_pin=d['frozen_source_commit'])
 rows.append(row)
certificates=[]
for path in sorted((HERE.parent/'verification').rglob('candidate-certificate.json')):
 d=json.loads(path.read_text())
 if d.get('status','').startswith('PASS')or 'kappa'in d:
  certificates.append(dict(case=str(path.parent.relative_to(HERE.parent/'verification')),kappa=d['kappa'],kappa_decimal=float(Fraction(d['kappa'])),bit_saving=d['bit_saving'],
    certificate=str(path.relative_to(HERE.parent)),certificate_sha256=sha256(path.read_bytes()).hexdigest(),scope=d['scope'],fresh_word_receipts=d['fresh_word_receipts']))
result=dict(frozen_source='PR62',source_pin='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',no_later_external_source=True,proposals=rows,independent_certificates=certificates,
 no_global_matching_or_schedule_optimality_claim=True)
(HERE/'search-ledger.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(proposals=len(rows),certificates=len(certificates),best=max(certificates,key=lambda x:x['kappa_decimal'])['case']if certificates else None)),flush=True)
