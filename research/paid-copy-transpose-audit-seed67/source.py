"""Paid overwrite-copy transpose audit, Apache-2.0."""
import argparse,gzip,hashlib,importlib.util,itertools,json,sys,tarfile
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

BASE='ce7ad1b6ab09452c3478723a2e96ed5ff212dc08'
PATHS=('research/community-frontier1042-audit/selected-replay.tar.gz',
 'research/gauge44-slots-t16/construction/slots/SLOT-PINS-k8.json',
 'research/complex-dyadic-lowering/lower.py',
 'research/community-frontier1094-audit/SELECTED-SOURCE.json')
MEMBER='slots/local/CANONICAL-WORD.json.gz'
def need(x,s):
 if not x:raise ValueError(s)
def pairs(ps):
 d={}
 for k,v in ps:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def read(b):return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def cost(e):
 if e[0]=='add':
  q=F(e[3],e[4]);need(q!=0 and q.denominator&(q.denominator-1)==0,'dyadic addition')
  if abs(q)==1:return 2
  return 3+abs(q.numerator).bit_length()-1+abs(q.numerator).bit_count()-1+q.denominator.bit_length()-1
 q=F(e[2],e[3]);need(q!=0 and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0,'unit scale')
 return abs(abs(q.numerator).bit_length()-q.denominator.bit_length())+int(q<0)
def source():
 p=read((HERE/'SOURCES.json').read_bytes());need(set(p)=={'base','files'} and p['base']==BASE and set(p['files'])==set(PATHS),'exact source inventory')
 for x in PATHS:need(sha((ROOT/x).read_bytes())==p['files'][x],'source pin '+x)
 selected=read((ROOT/PATHS[3]).read_bytes())
 need(selected['files'][PATHS[1]]==p['files'][PATHS[1]],'PR1094 selected slot binding')
 with tarfile.open(ROOT/PATHS[0]) as t:
  hits=[m for m in t.getmembers() if m.name==MEMBER];need(len(hits)==1 and hits[0].isfile(),'named archive member')
  raw=gzip.decompress(t.extractfile(hits[0]).read())
 w=read(raw);pins=read((ROOT/PATHS[1]).read_bytes())
 need(sha(raw)==pins['canonical_sha256']=='4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c','canonical word')
 need((w['h'],w['v'],w['R'])==(9,112,480),'selected local shape')
 return w