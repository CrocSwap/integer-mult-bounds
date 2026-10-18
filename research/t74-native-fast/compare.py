#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Compare all native mathematical outputs; only two elapsed fields are omitted.
Gzip container hashes are independently checked before semantic normalization.
"""
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import need
FILES = {
 'CANONICAL-WORD.json.gz', 'FULL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json', 'INDEPENDENT-LOCAL-REPLAY.json',
 'LOCAL-CHECKS.json', 'RESIDUAL-ADAPTERS.json', 'SCALAR-FRAME-AUDIT.json',
 'WARP-RECIPE-CHECKS.json', 'WRAPPER-CHECKS.json',
}
def sha(data):
 return hashlib.sha256(data).hexdigest()
def canonical(value):
 return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def normalized(directory):
 need({p.name for p in directory.iterdir()}==FILES, 'complete native output inventory')
 raw={n:(directory/n).read_bytes() for n in FILES}
 data={n:gzip.decompress(b) if n.endswith('.gz') else b for n,b in raw.items()}
 values={n:json.loads(b) for n,b in data.items()}
 # Preserve and validate every hash's binding. Only container-dependent hashes
 # are replaced by the digest of the actual decompressed artifact for comparison.
 for n in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WARP-RECIPE-CHECKS.json'):
  need(values[n]['canonical_word_sha256']==sha(raw['CANONICAL-WORD.json.gz']), 'canonical container binding '+n)
  values[n]['canonical_word_sha256']=sha(data['CANONICAL-WORD.json.gz'])
 for n in ('CLIFFORD-REVIEW.json','WARP-RECIPE-CHECKS.json'):
  need(values[n]['recipe_sha256']==sha(raw['CLIFFORD-RECIPES.json']), 'recipe byte binding '+n)
 need(values['INDEPENDENT-LOCAL-REPLAY.json']['local_programs_sha256']==sha(raw['LOCAL-PROGRAMS.json.gz']), 'program container binding')
 values['INDEPENDENT-LOCAL-REPLAY.json']['local_programs_sha256']=sha(data['LOCAL-PROGRAMS.json.gz'])
 audit=values['SCALAR-FRAME-AUDIT.json']
 need(audit['input_content_sha256']==sha(data['FULL-WORD.json.gz']), 'full word binding')
 need(audit['canonical_content_sha256']==sha(data['CANONICAL-WORD.json.gz']), 'canonical content binding')
 for n in ('SCALAR-FRAME-AUDIT.json','CLIFFORD-REVIEW.json'):
  seconds=values[n].pop('seconds')
  need(type(seconds) in (float,int) and seconds>=0, 'valid elapsed field '+n)
 return values

def compare(first,second):
 a,b=normalized(first),normalized(second)
 need(a==b,'native outputs differ: '+str([n for n in FILES if a[n]!=b[n]]))
 return {'status':'PASS_ALL_NATIVE_OUTPUTS_IDENTICAL','files':len(FILES),
         'normalized_sha256':sha(canonical(a)),
         'recipe_bytes_sha256':sha((first/'CLIFFORD-RECIPES.json').read_bytes())}

if __name__=='__main__':
 print(json.dumps(compare(Path(sys.argv[1]),Path(sys.argv[2])),indent=2))
