#!/usr/bin/env python3
"""Compose Dumitrean's PR2733 refit with Tekalign's PR2751 joint-twelve word.
Does not certify native/global/outer admission. Outputs an exact word delta.
"""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
SOURCE_HEAD='4cfbb0cc8314d7fb4e8e754545a49a42eb590a69'
REFIT_HEAD='a63c55ff56aaa8645d64d1162d1f017b59ded42a'
PINS={'base':'ae8b6b4d62a9da29331062fae1bd68b0341edf83152f5a5ef50c5109ba578f9a','extra':'1bb44a73d5841afb954b49ae94dba2e0c536b1eea9436ae5d89de87d8a04e127'}
OLD=['add',393,515,1,1,[259,132,66,36,16,9]]
NEW=['add',393,515,1,1,[259,148,66,36,9]]
EXPECTED={'1':2366,'2':646,'3':297,'4':120,'5':26,'8':8}
def need(x,m):
 if not x:raise ValueError(m)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def patch(w):
 need(w['report']['local_profile']==EXPECTED,'Exact source local profile')
 sites=[i for i,g in enumerate(w['B']) if g==OLD]
 need(sites==[1151],'Exact unique source B1151')
 out=copy.deepcopy(w);out['B'][1151]=copy.deepcopy(NEW)
 out['report']['local_profile']['1']-=2;out['report']['local_profile']['2']+=1
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 need(not a.out.exists(),'Output directory must be fresh')
 outputs={};receipts={}
 for tag,pin in PINS.items():
  raw=(a.source/f'inputs/WORD-{tag}.json.gz').read_bytes();need(hashlib.sha256(raw).hexdigest()==pin,'Source bytes '+tag)
  before=json.loads(gzip.decompress(raw));after=patch(before)
  outputs[tag]=canonical(after)
  receipts[tag]={'source_sha256':pin,'canonical_source_sha256':hashlib.sha256(canonical(before)).hexdigest(),'canonical_result_sha256':hashlib.sha256(outputs[tag]).hexdigest(),'section':'B','index':1151,'old':OLD,'new':NEW,'local_profile':after['report']['local_profile']}
 sourceprofile=json.loads((a.source/'PROFILE.json').read_bytes());newprofile=sourceprofile.copy();newprofile['1']-=1332;newprofile['2']+=666
 need(sum(int(r)*n for r,n in newprofile.items())==4816512,'Preserved full paid mass')
 a.out.mkdir()
 for tag,data in outputs.items():(a.out/f'WORD-{tag}.json.gz').write_bytes(gzip.compress(data,mtime=0))
 receipt={'status':'EXACT_CREDITED_FRAME_REFIT_COMPOSITION','source_head':SOURCE_HEAD,'refit_head':REFIT_HEAD,'providers':receipts,'global_delta':{'1':-1332,'2':666},'global_profile':newprofile,'source_refit_authorship':'Marius-Paul Dumitrean PR2733; joint twelve-source recovery Tekalign PR2751','scope':'Generator only; independent algebra/frame checks and native/global/outer replay remain separate.'}
 (a.out/'PATCH.json').write_text(json.dumps(receipt,indent=2)+'\n')
 (a.out/'PROFILE.json').write_text(json.dumps(newprofile,indent=2)+'\n')
 print(receipt['status'])
