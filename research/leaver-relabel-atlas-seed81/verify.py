"""Complete local S6 atlas. New independent implementation, Apache-2.0."""
import argparse,copy,gzip,hashlib,itertools,json,tarfile
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='ba82555c64e1879e4b7decce28186f208fcb8262'
PATHS=('research/community-frontier1042-audit/selected-replay.tar.gz',
 'research/gauge44-leaver8/construction/leaver/CODED-CELLS-k8.json',
 'research/gauge44-slots-t16/construction/slots/SLOT-PINS-k8.json')
MEMBER='slots/local/FULL-WORD.json.gz'
def need(x,s):
 if not x:raise ValueError(s)
def pairs(p):
 d={}
 for k,v in p:
  need(k not in d,'duplicate JSON key');d[k]=v
 return d
def read(b):
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def basis(v):
 p={}
 for a in v:
  while a:
   k=a.bit_length()-1
   if k in p:a^=p[k]
   else:p[k]=a;break
 for k in sorted(p):
  for j in p:
   if j>k and p[j]>>k&1:p[j]^=p[k]
 return tuple(p[k] for k in sorted(p,reverse=True))
def inside(a,b):return basis(a+b)==b
def apply(e,rows):
 t=e[1]
 if e[0]=='scale':rows[t]={k:F(e[2],e[3])*v for k,v in rows[t].items()};return
 q=F(e[3],e[4]);s=e[2]
 for k,v in list(rows[s].items()):
  x=rows[t].get(k,F(0))+q*v
  if x:rows[t][k]=x
  else:rows[t].pop(k,None)
def index(s):return int(s[1:])+(6 if s[0]=='y' else 0)
def scaled(c,perm):
 C=[[F(q) for q in r] for r in c['coefficients']]
 # Independent gauge: c_1=1, recover every row then every column.
 r=[None]*6;r[0]=C[0][1]
 col=[None]*6
 for j in range(1,6):col[j]=C[0][j]/r[0]
 r[1]=C[1][2]/col[2];col[0]=C[1][0]/r[1]
 for i in range(2,6):r[i]=C[i][0]/col[0]
 need(all(C[i][j]==(0 if i==j else r[i]*col[j]) for i in range(6) for j in range(6)),'coefficient factorization')
 out=[]
 for tn,sn,q in c['unit']:
  need(type(q) is int and q==1,'unit coefficient')
  t=perm[int(tn[1:])]+(6 if tn[0]=='y' else 0)
  s=perm[int(sn[1:])]+(6 if sn[0]=='y' else 0)
  q=col[s]/col[t] if t<6 else r[t-6]/r[s-6] if s>=6 else r[t-6]*col[s]
  out.append(['add',t,s,q.numerator,q.denominator])
 return out
def locate(c,w):
 found=[]
 for i in range(len(w['B'])-20):
  mp={};ok=True
  for (tn,sn,q),e in zip(c['scaled'],w['B'][i:i+21]):
   if e[0]!='add' or F(q)!=F(e[3],e[4]):ok=False;break
   for name,z in ((tn,e[1]),(sn,e[2])):
    if (name in mp and mp[name]!=z) or (name[0]=='y' and z!=104+c['bindings'][name][1]):ok=False;break
    mp[name]=z
   if not ok:break
  if ok and len(set(mp.values()))==12:found.append((i,[mp['x'+str(j)] for j in range(6)]+[mp['y'+str(j)] for j in range(6)]))
 need(len(found)==1,'unique literal cell');return found[0]
def contexts(cells,w):
 n=224+w['report']['R'];enter=sorted(map(int,w['start_extra']))
 rows=[{i:F(1)} if i in enter else {} for i in range(n)]
 cur=[(p,) for p in w['ports']]+[()]*(n-112)
 for k,v in w['start_extra'].items():cur[int(k)]=basis(v)
 loc={locate(c,w)[0]:(c,locate(c,w)[1]) for c in cells};out={}
 for e in w['A']:
  apply(e,rows)
  for z in e[1:3] if e[0]=='add' else e[1:2]:cur[z]=basis(e[-1])
 for e in w['cut']:apply(e,rows)
 for i,e in enumerate(w['B']):
  if i in loc:
   c,rs=loc[i];out[c['cell']]={'index':i,'registers':rs,'entry':[cur[z] for z in rs],'dirt':[rows[z].copy() for z in rs]}
  apply(e,rows)
  for z in e[1:3] if e[0]=='add' else e[1:2]:cur[z]=basis(e[-1])
  if i-20 in loc:
   c,rs=loc[i-20];out[c['cell']]['exit']=[cur[z] for z in rs]
 need(all(not row for row in rows[112:224]),'selected final entering-target response')
 return out,enter
def rows_matrix(ops):
 rows=[{i:F(1)} for i in range(12)]
 for e in ops:apply(e,rows)
 return rows
def classify(ops,ctx):
 rows=rows_matrix(ops)
 dirty=copy.deepcopy(ctx['dirt'])
 for e in ops:apply(e,dirty)
 # The source rows intentionally mutate; target response must be unchanged.
 dirt_ok=dirty[6:]==ctx['reference_dirt']
 cur=ctx['entry'].copy();frames=[];fail=None;paid=Counter()
 for i,e in enumerate(ops):
  t,s=e[1:3];u=basis(cur[t]+cur[s]);frames.append(u)
  for z in (t,s):
   if not inside(u,ctx['exit'][z]) and fail is None:fail=[i,z,list(u),list(ctx['exit'][z])]
   d=len(u)-len(cur[z])
   if d:paid[d]+=1
   cur[z]=u
 if fail is None:
  for z in range(12):
   d=len(ctx['exit'][z])-len(cur[z])
   if d:paid[d]+=1
 return rows,dirt_ok,fail is None,fail,dict(sorted(paid.items()))
def inputs():
 s=read((HERE/'SOURCES.json').read_bytes());need(set(s)=={'base','files'} and s['base']==BASE and set(s['files'])==set(PATHS),'exact source inventory')
 for p in PATHS:need(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==s['files'][p],'source pin '+p)
 with tarfile.open(ROOT/PATHS[0]) as t:
  hits=[x for x in t.getmembers() if x.name==MEMBER];need(len(hits)==1 and hits[0].isfile(),'unique tar member')
  raw=gzip.decompress(t.extractfile(hits[0]).read());w=read(raw)
 pins=read((ROOT/PATHS[2]).read_bytes())
 need(hashlib.sha256(enc(w).encode()).hexdigest()==pins['word_sha256']=='c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8','selected word pin')
 need((w['report']['v'],w['report']['R'],w['report']['h'])==(112,480,9),'geometry')
 return read((ROOT/PATHS[1]).read_bytes()),w
def compute(cells,w,independent=True):
 contexts_,enter=contexts(cells,w);results=[];controls=0
 if independent:
  import sys
  sys.path.insert(0,str(HERE));import independent as other
  other.verify_contexts(w,contexts_,enter)
 for c in cells:
  ctx=contexts_[c['cell']];original=scaled(c,tuple(range(6)))
  need(not any(set(ctx['registers'][:6]) & set(e[1:3] if e[0]=='add' else e[1:2]) for e in w['B'][ctx['index']+21:]),'leaver post-cell touch')
  need([[('y' if e[1]>=6 else 'x')+str(e[1]%6),('y' if e[2]>=6 else 'x')+str(e[2]%6),str(F(e[3],e[4]))] for e in original]==c['scaled'],'rescaling selected cell')
  raw=copy.deepcopy(ctx['dirt'])
  for e in original:apply(e,raw)
  ctx['reference_dirt']=raw[6:];need(raw[6:]==ctx['dirt'][6:],'selected target dirt invariant')
  need(classify(original,ctx)[1:3]==(True,True),'selected labeling admissible')
  buckets=Counter();records=[];witness={};accepted=[]
  C=[[F(q) for q in row] for row in c['coefficients']]
  for perm in itertools.permutations(range(6)):
   ops=scaled(c,perm);rows,dirty,frame,fail,paid=classify(ops,ctx)
   need(all([rows[i+6].get(j,F(0)) for j in range(6)]==C[i] for i in range(6)),'clean transfer')
   if independent:
    d2,f2=other.check(ops,ctx,C)
    need((dirty,frame)==(d2,f2),'independent oracle disagreement')
   key=('dirt_ok' if dirty else 'dirt_fail')+'_'+('span_ok' if frame else 'span_fail')
   buckets[key]+=1
   rec={'permutation':list(perm),'dirt':dirty,'frames':frame,'failure':fail,'rank_increment_tally':{str(k):v for k,v in paid.items()} if frame else None}
   if not dirty:
    delta=copy.deepcopy(ctx['dirt'])
    for e in ops:apply(e,delta)
    differences=[(i,k,delta[i+6].get(k,F(0))-ctx['reference_dirt'][i].get(k,F(0)))
      for i in range(6) for k in sorted(set(delta[i+6])|set(ctx['reference_dirt'][i]))
      if delta[i+6].get(k,F(0))!=ctx['reference_dirt'][i].get(k,F(0))]
    i,k,q=differences[0];rec['dirt_witness']={'target':ctx['registers'][i+6],'entering_helper':k,'delta':str(q)}
   if dirty and frame:accepted.append(list(perm))
   records.append(rec);witness.setdefault(key,rec)
  # A dropped read must fail the independent endpoint, not just a receipt hash.
  bad=original[:1]+original[2:]
  need(any([rows_matrix(bad)[i+6].get(j,F(0)) for j in range(6)]!=C[i] for i in range(6)),'dropped read control');controls+=1
  need('dirt_fail_span_ok' in witness and 'dirt_ok_span_fail' in witness,'both distinct rejection mechanisms');controls+=2
  empty=copy.deepcopy(ctx);empty['exit']=[()]*12
  need(not classify(original,empty)[2],'empty cap control');controls+=1
  # The source-read criterion is necessary here, not only sufficient: target
  # additions have distinct destinations, sources and no chained dependency.
  yy=[(e[1]-6,e[2]-6) for e in original if e[2]>=6]
  need(len(yy)==3 and len(set(x for e in yy for x in e))==6,'disjoint target matching')
  clean=[j for j in range(6) if not ctx['dirt'][j+6]]
  need(len(clean)==3 and all(not r for r in ctx['dirt'][:6]),'three clean target rows and clean leavers')
  need(sum(v for k,v in buckets.items() if k.startswith('dirt_ok'))==36,'exact dirt kernel count')
  results.append({'cell':c['cell'],'B_start':ctx['index'],'registers':ctx['registers'],
    'entry_frames':[list(x) for x in ctx['entry']],'exit_caps':[list(x) for x in ctx['exit']],
    'target_dirt_rows':[{str(k):str(v) for k,v in sorted(r.items())} for r in ctx['dirt'][6:]],
    'counts':dict(sorted(buckets.items())),'clean_target_labels':clean,'accepted_permutations':accepted,
    'examples':witness,'atlas_sha256':hashlib.sha256(enc(records).encode()).hexdigest()})
 return {'base':BASE,'word_sha256':'c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8',
  'model':'individual S6 cell relabelings; exact monotone GF(2) label-span containment within fixed entry and exit caps; target entering-dirt equality; no Gram or residual-legality test',
  'cells':results,'entering_helpers':enter,'independent_entry_columns':len(enter),'trials':5760,'clean_transfers_checked':5760,'controls':controls,'gram_or_residual_legality_checked':False,'primitive_cost_invoice':False,'native_executed':False,'new_kappa':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 cells,w=inputs();out=compute(cells,w)
 if a.write:(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
 else:need(enc(out)==enc(read((HERE/'RESULT.json').read_bytes())),'typed canonical result mismatch')
 print('PASS_LEAVER_RELABEL_ATLAS cells=8 trials=5760 controls='+str(out['controls'])+' no_new_kappa')
 for c in out['cells']:print(c['cell'],c['counts'])
if __name__=='__main__':main()
