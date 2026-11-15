from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import sys,json,gzip,hashlib,importlib.util
P=Path('pr378-donor-screen');sys.path.insert(0,'pr378-complex-screen/package/code');import cxkernel as C
sys.path.insert(0,'pr378-complex-screen/package/complex/gx');import gx
old=json.load(gzip.open('pr378-complex-screen/package/data/gcert1-e8-r783-far.json.gz'));c=json.load(gzip.open(P/'signed25.json.gz'));a=json.load(open(P/'best-local-audit.json'))
assert c['R']==old['R'] and c['h']==old['h'] and c['ports']==old['ports'];chosen=[]
for r in a['relations']:
 p=r['pivot'];chosen.append((a['frame'],p,{int(d):Q(q) for d,q in r['donors'].items()}))
# Never transplant a frame ID without exact basis binding and actual first-use containment.
assert c['frames'][a['frame']]==old['frames'][a['frame']]
first={}
for phase in ('A','B'):
 for g in c[phase]:
  for r in [g[2]]+[x[0] for x in g[3]]+(g[4] if g[0]=='out' else []):first.setdefault(r,g[1])
for E,p,co in chosen:
 for r in [p]+list(co):assert C.inside(c['frames'][E],c['frames'][first[r]])
# Full raw rational operator from all 1023 dirty columns, independently replayed.
def matrix(c):
 n=2*c['v']+c['R'];reg=[{i:Q(1)} for i in range(n)]
 def ax(t,s,q):
  for k,v in list(s.items()):
   z=reg[t].get(k,0)+q*v
   if z:reg[t][k]=z
   else:reg[t].pop(k,None)
 for phase in ('A','B'):
  if phase=='B':
   totals={k:dict(reg[r]) for k,r,f in c['ret']}
   for t,row in enumerate(c['scat']['table']):
    for k,x,y in row:ax(c['v']+t,totals[k],Q(x,y))
  for g in c[phase]:
   for r,x,y in g[3]:
    t,s=(r,g[2]) if g[0]=='out' else (g[2],r);ax(t,reg[s],Q(x,y))
 return reg
orig=matrix(old);prefix=matrix(c);assert orig==prefix
w=C.rehist(C.apply(c,chosen));stats={};gx.check1(w,scalar=True,stats=stats)
blob=gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0);(P/'signed25-donor-candidate.json.gz').write_bytes(blob)
H=Counter()
for block in w['blocks'].values():H.update({int(r):72*n for r,n in block.items()})
H.update({int(r):9*n for r,n in a['padding'].items()})
for r in [16,8,32,8,48,8,48,32,16]:H[r]+=1920
W=a['live'];assert 73*W-sum(r*n for r,n in H.items())==2496
modules=[]
for name in ['moment','base_two_moment']:
 sp=importlib.util.spec_from_file_location(name,'pr370-e8-screen/code/pricing/'+name+'.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);modules.append(mod)
M,B=modules;root=M.certify(H,73,W,True);b=Q(int(Q(root['lower'])*10**18),10**18);step=Q(1,10**18);assert M.moment(H,73,W,b,True)[1]<1<M.moment(H,73,W,b+step,True)[0]
fb=32*73**2*sum(H.values());_,u=B.moment(73,W,list(H.items()),b);_,fu=B.moment(73,W,[(1,fb)],b);lo,_=B.moment(73,W,list(H.items()),b+step);flo,_=B.moment(73,W,[(1,fb)],b+step);assert u+Q(1,10**16)*fu<1<lo+Q(1,10**16)*flo
out=dict(status='PASS_LOCAL_PREFIX_DONOR_COMPATIBILITY_AND_CONDITIONAL_BANK_PRICE',source_head395='dcebad83e4d7e6a5643ba8edfb432b0ba0dd1826',prefix_sha256=hashlib.sha256((P/'signed25.json.gz').read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(blob).hexdigest(),all_raw_columns=1023,full_prefix_operator_equals378=True,actual_first_use_cap_containment=True,local_gx=stats,pivots=a['pivots'],profile=dict(sorted(H.items())),live=W,conditional_component_coarse=str(b),reported395_component='250523357922707/250000000000000000',difference_from_reported395_component=str(b-Q(250523357922707,250000000000000000)),two_engines=True,full_fallback=True,next_grid_rejected=True,scope='Source-bound local full-operator prefix compatibility and fresh emitted recount, using prior explicit bank geometry. No composition with PR390 early-restoration/preconditioning; no native Gaussian entrance/global splice/finite admission, final kappa or publication.')
(P/'signed25-donor-screen.json').write_text(json.dumps(out,indent=2));print(out)
