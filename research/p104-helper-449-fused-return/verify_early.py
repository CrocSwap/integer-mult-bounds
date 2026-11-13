# SPDX-License-Identifier: Apache-2.0
"""Source-bound native adjoint and complete directed signed pricing."""
from pathlib import Path
from collections import Counter
import sys,json,gzip,copy,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import HERE,sources,load,read,canonical,sha256,need
from construct import construct

def run():
 with sources()as(vendor,audit,rank9,bundle,parent,old):
  word=construct(old);need(canonical(word)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Complete emitted word')
  ind=load('fused_ind',vendor/'independent.py');before,after=map(ind.native,(old,word));need(not before['bad_inputs']and not after['bad_inputs'],'Whole native arbitrary-input adjoints')
  need(json.loads(json.dumps(before))==read(parent/'NATIVE-RESULT.json')['native'],'Exact predecessor inventory')
  need(after['helpers']==before['helpers']and after['rises']==before['rises']and after['lifetimes']==before['lifetimes']+1 and after['owned_peak']==before['owned_peak']==50,'Stationary lifetime and full ownership census')
  need(word['owned_fields']==old['owned_fields']==68,'Declared owned labels')
  base=read(parent/'RESULT.json')['price'];engine=load('fused_gate',bundle/'gate.py')
  oldinvoice={k:({int(r):v for r,v in x.items()}if k in('T','P')else x)for k,x in base['after'].items()if k not in('raw_crossing','no_E_credit_crossing')}
  delta=Counter(after['paid']);delta.subtract(before['paid']);delta={r:v for r,v in delta.items()if v};invoice=copy.deepcopy(oldinvoice)
  for r,v in delta.items():invoice['P'][r]=invoice['P'].get(r,0)+17*v
  need(sum(r*v for r,v in delta.items())==0,'Unchanged rank mass')
  gate,price=engine.exact_price(vendor,audit,oldinvoice,invoice,{'gate':base['gate']})
  return json.loads(json.dumps(dict(status='PASS_SOURCE_BOUND_EXACT_NATIVE_AND_DIRECTED_PRICE',native=after,delta=delta,invoice=invoice,gate=gate,price=price,source_word_sha256=sha256(canonical(old)).hexdigest(),word_sha256=sha256(canonical(word)).hexdigest()),default=str))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=run()
 if a.out:
  with a.out.open('x')as f:json.dump(r,f,indent=2);f.write('\n')
 else:need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early field')
 print(r['status'],r['price']['claim_decimal'],flush=True)
