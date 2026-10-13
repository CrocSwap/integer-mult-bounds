"""OpenAI Codex: apply a frozen frame-only retiming to verified PR484.
Usage: python -B apply_retime.py BASE_FULL-WORD.json.gz RETIME-FRAMES.json.gz OUT_FULL-WORD.json.gz
Source PR433/PR484 notices remain inherited. Frame accounting follows their
nested-frame contract, implemented here for independent frozen-map replay.
No optimizer runs; scalar gates, selected entrances and boundaries are fixed.
"""
import copy,gzip,hashlib,json,sys
from pathlib import Path
from collections import Counter

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def basis(vs):
 b={}
 for x in vs:
  for p in sorted(b,reverse=True):
   if x>>p&1:x^=b[p]
  if x:
   p=x.bit_length()-1
   for q in b:
    if b[q]>>p&1:b[q]^=x
   b[p]=x
 return tuple(b[p]for p in sorted(b,reverse=True))
def inside(a,b):return basis(list(a)+list(b))==basis(b)
def registers(e):return [e[1],e[2]]if e[0]=='add'else[e[1]]
def profile(w):
 v=120;n=240+w['report']['R'];full=basis([1<<i for i in range(9)])
 cur=[basis([p])for p in w['ports']]+[()]*v+[basis(w.get('start_extra',{}).get(str(r),[]))for r in range(240,n)];paid=Counter()
 def climb(r,F):
  F=basis(F);assert inside(cur[r],F),('non-nested frame',r,cur[r],F)
  if cur[r]!=F:paid[len(F)-len(cur[r])]+=1;cur[r]=F
 lev={int(t):basis(E)for t,E in w.get('target_levels',{}).items()}
 for part in ['A','B']:
  if part=='B':
   assert all(cur[v+t]==lev.get(t,())for t in range(v))
   for r,F in zip(w['centers'],w['center_frames']):
    old=basis(F);assert cur[r]==old
    for E in sorted({lev.get(e[1]-v,())for e in w['cut']if e[2]==r},key=lambda E:-len(E)):
     assert inside(E,old)
     if old!=E:paid[len(old)-len(E)]+=1;old=E
  for e in w[part]:
   for r in registers(e):climb(r,e[-1])
 for r in range(n):climb(r,basis([x for x in range(1,512)if not(x&w['ports'][r-v]).bit_count()%2])if v<=r<2*v else full)
 return dict(sorted(paid.items()))

def main(src,mapfile,out):
 assert not out.exists();w=json.loads(gzip.decompress(src.read_bytes()));p=json.loads(gzip.decompress(mapfile.read_bytes()));assert hashlib.sha256(canonical(w)).hexdigest()==p['source_word_json_sha256'];z=copy.deepcopy(w)
 for part in ['A','B']:
  seen=set()
  for i,old,new in p[part]:
   assert i not in seen and z[part][i][-1]==old;seen.add(i);z[part][i][-1]=new
  assert [e[:-1]for e in w[part]]==[e[:-1]for e in z[part]]
 assert w['A'][:531]==z['A'][:531]
 local=profile(z);assert local=={int(r):k for r,k in p['expected_local_profile'].items()}
 oldlocal={int(r):k for r,k in w['report']['local_profile'].items()};globalpaid=Counter({int(r):k for r,k in w['report']['global_profile'].items()})
 for r in set(local)|set(oldlocal):globalpaid[r]+=72*(local.get(r,0)-oldlocal.get(r,0))
 assert all(k>=0 for k in globalpaid.values());globalpaid={r:k for r,k in sorted(globalpaid.items())if k};assert globalpaid=={int(r):k for r,k in p['expected_global_profile'].items()}
 z['report']['local_profile']={str(r):k for r,k in local.items()};z['report']['global_profile']={str(r):k for r,k in globalpaid.items()}
 assert hashlib.sha256(canonical(z)).hexdigest()==p['candidate_word_json_sha256']
 out.write_bytes(gzip.compress(canonical(z),mtime=0));print(json.dumps(dict(status='PASS_FROZEN_FRAME_ONLY_RETIME_APPLICATION',changed_A_frames=len(p['A']),changed_B_frames=len(p['B']),local_profile=local,output_json_sha256=hashlib.sha256(canonical(z)).hexdigest(),output_gzip_sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
if __name__=='__main__':main(*map(Path,sys.argv[1:4]))
