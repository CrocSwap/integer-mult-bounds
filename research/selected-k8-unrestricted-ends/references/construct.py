# SPDX-License-Identifier: Apache-2.0
# Prepared for 1337isnot1337 with substantial OpenAI Codex assistance.
"""Twelve literal frame edits; scalar program and every other field preserved."""
import argparse,copy,gzip,hashlib,importlib.util,json
from collections import Counter
from pathlib import Path
BASE='c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8'
TARGET='f64e0942edc5eb2d45b0a3b068ba942436f35ba9a077ff53d7e4424d1617b2cd'
HERE=Path(__file__).resolve().parent

def build(path,promotion):
 raw=gzip.decompress(path.read_bytes())
 if hashlib.sha256(raw).hexdigest()!=BASE:raise ValueError('source content pin')
 w=json.loads(raw);base=copy.deepcopy(w);recipe=json.loads((HERE/'data/END-RECIPE.json').read_bytes())
 if [x[0] for x in recipe['ends']]!=[574,575]:raise ValueError('end sites')
 for q,old,new in recipe['ends']:
  if w['helper_final'][str(q)]!=old:raise ValueError('old end')
  w['helper_final'][str(q)]=new
 for i,old,new in recipe['B_frames']:
  if w['B'][i][-1]!=old:raise ValueError('old B frame')
  w['B'][i][-1]=new
 for i,k,old,new in recipe['early_cleanup']:
  if w['early_cleanup'][i]!=[k,old]:raise ValueError('old early tail')
  w['early_cleanup'][i][1]=new
 s=importlib.util.spec_from_file_location('credited_promotion',promotion);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 H=Counter({int(k):v for k,v in base['report']['local_profile'].items()});H.subtract(m.chain_profile(base));H.update(m.chain_profile(w));H=+H
 w['report'].update(local_profile={str(k):v for k,v in sorted(H.items())},local_rank_mass=sum(k*v for k,v in H.items()),width_inventory={str(k):v for k,v in sorted(m.widths(w).items())})
 data=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
 if hashlib.sha256(data).hexdigest()!=TARGET:raise ValueError('constructed word pin')
 for section in ('A','cut','B','precondition','cleanup'):
  if [e[:-1] for e in w[section]]!=[e[:-1] for e in base[section]]:raise ValueError('scalar changed')
 return data

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--promotion',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 if a.output.exists():raise ValueError('output exists')
 data=build(a.input,a.promotion);a.output.write_bytes(gzip.compress(data,mtime=0));print('PASS_K8_RANK7_TWELVE_FRAME_CONSTRUCTION')
