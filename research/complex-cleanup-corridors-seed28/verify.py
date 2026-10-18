"""All-length repeated-operand/read-barrier certificate, Apache-2.0."""
import argparse,gzip,hashlib,importlib.util,itertools,json,sys,tarfile
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import independent
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
def census(ops):
 locations=defaultdict(list)
 for i,e in enumerate(ops):
  if e[0]=='add':locations[tuple(e[1:3])].append(i)
 records=[];unblocked=[]
 for (a,b),indices in sorted(locations.items()):
  for i,j in itertools.combinations(indices,2):
   witnesses=[k for k in range(i+1,j) if ops[k][0]=='add' and ops[k][2]==a]
   rec={'target':a,'source':b,'first':i,'second':j,'interior_length':j-i-1,
    'first_read':witnesses[0] if witnesses else None,'last_read':witnesses[-1] if witnesses else None,
    'read_count':len(witnesses)}
   records.append(rec)
   if not witnesses:unblocked.append([i,j])
 return records,unblocked,locations
def validate(records,ops):
 expected,unblocked,_=census(ops);need(not unblocked,'unblocked corridor')
 need(enc(records)==enc(expected),'complete barrier certificate')
 for r in records:
  for k in (r['first_read'],r['last_read']):
   need(r['first']<k<r['second'] and ops[k][0]=='add' and ops[k][2]==r['target'],'literal read witness')
def add(t,s,q):q=F(q);return ['add',t,s,q.numerator,q.denominator]
def controls(ops,records):
 import copy
 count=0
 for mutate in ('missing','wrong_barrier','wrong_count'):
  bad=copy.deepcopy(records)
  if mutate=='missing':bad.pop()
  elif mutate=='wrong_barrier':bad[0]['first_read']=bad[0]['first']
  else:bad[0]['read_count']+=1
  try:validate(bad,ops)
  except ValueError:count+=1
  else:raise ValueError('accepted broken barrier certificate')
 # Three profitable unrestricted-input examples in the declared rewrite class.
 examples=[]
 for q,p,r in [(F(1),F(-1),F(1)),(F(3,2),F(1,2),None),(F(1,2),F(-1,2),F(2))]:
  old=[add(0,1,q)]
  if r is not None:old.append(add(1,2,r))
  old.append(add(0,1,p));new=[]
  if r is not None:new.extend([add(1,2,r),add(0,2,-q*r)])
  if q+p:new.append(add(0,1,q+p))
  need(independent.replay(old,3)==independent.replay(new,3),'planted exact rewrite')
  need(census(old)[1]==[[0,len(old)-1]],'planted corridor discovery')
  need(sum(map(cost,new))<sum(map(cost,old)),'planted paid gain')
  try:list(independent.barriers(old))
  except ValueError:pass
  else:raise ValueError('backwards oracle missed planted opportunity')
  examples.append({'original':old,'replacement':new,'old_real_primitives':sum(map(cost,old)),'new_real_primitives':sum(map(cost,new))});count+=1
 # Dropping endpoint additions across a read loses its contribution to a third wire.
 old=[add(0,1,1),add(2,0,1),add(0,1,-1)];bad=[add(2,0,1)]
 need(independent.replay(old,3)!=independent.replay(bad,3),'read barrier scalar counterexample');count+=1
 return count,examples,{'original':old,'invalid_replacement':bad,'input':[0,1,0],'original_output':[0,1,1],'invalid_output':[0,1,0]}
def compute():
 w=source();ops=w['cleanup'];need(all(w['frames'][e[-1]]==[256,128,64,32,16,8,4,2,1] for e in ops),'all cleanup operations at FULL')
 need(all(e[0] in ('add','scale') and (e[0]!='add' or e[1]!=e[2]) for e in ops),'literal distinct-operand macro model')
 records,unblocked,loc=census(ops);validate(records,ops)
 need(max(map(len,loc.values()))==2,'frozen pair multiplicity')
 backward=list(independent.barriers(ops));got={(i,j):k for i,j,k in backward}
 need(len(got)==len(records) and all(got[r['first'],r['second']]==r['first_read'] for r in records),'independent backwards witnesses')
 spec=importlib.util.spec_from_file_location('pinned_pr696_lower',ROOT/PATHS[2]);lower=importlib.util.module_from_spec(spec);spec.loader.exec_module(lower)
 total=0
 for e in ops:
  z=e[:-1].copy();z[1]=('R',z[1])
  if z[0]=='add':z[2]=('R',z[2])
  actual=len(lower.lower(z));need(actual==cost(e),'independent paid primitive tally');total+=actual
 k,examples,bad=controls(ops,records)
 return {'base':BASE,'selected_local_word':'PR1094 reuses PR1042 seven-slot R480 word','macro_counts':dict(sorted(Counter(e[0] for e in ops).items())),
 'cleanup_macros':len(ops),'distinct_ordered_pairs':len(loc),'repeated_pairs':len(records),'maximum_pair_multiplicity':max(map(len,loc.values())),
 'unblocked_pairs':len(unblocked),'all_lengths_covered':True,'baseline_real_component_primitives':total,'baseline_complex_primitives':2*total,
 'read_barriers':records,'controls':k,'planted_profitable_rewrites':examples,'read_barrier_counterexample':bad,
 'scope':'No repeated-operand target-unread corridor exists in this fixed cleanup; not arbitrary cleanup optimality','native_executed':False,'new_kappa':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=compute()
 if a.write:(HERE/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 else:need(enc(r)==enc(read((HERE/'RESULT.json').read_bytes())),'typed canonical result mismatch')
 print('PASS_CLEANUP_CORRIDOR_BARRIER macros='+str(r['cleanup_macros'])+' repeated=111 blocked=111 controls='+str(r['controls'])+' no_new_kappa')
 print('real_component_primitives',r['baseline_real_component_primitives'])
if __name__=='__main__':main()
