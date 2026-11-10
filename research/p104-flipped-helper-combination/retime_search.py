"""Optional finite construction search; the verifier trusts no search result.

Revalidate frozen cut covectors after each exact split. Every accepted word
receives a complete rational replay. Float scores rank proposals only.
Ali Romman's helper mechanism, adapted by @CubeJerry with substantial OpenAI
assistance. Apache-2.0. See SEARCH.json for the completed finite domain.
"""
import sys,json,gzip,time,hashlib,copy,bisect
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from decimal import Decimal as D,getcontext
from construct import construct
from split import basis as basis_core

def basis(a,b,pivot,frame):
 return basis_core(a,b,pivot,frame,prefer_unit=True)
from linear import add,need,replay,read,HERE
import argparse
SRC=HERE/'retained/data/word.json.gz'
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--word',default=str(SRC));ap.add_argument('--hits',required=True)
ap.add_argument('--output',required=True);ap.add_argument('--prefix')
ap.add_argument('--max-new',type=int,default=80)
ap.add_argument('--prefix-steps',type=int)
args=ap.parse_args();OUT=Path(args.output);OUT.mkdir(parents=True,exist_ok=True)
getcontext().prec=50
base=json.loads(gzip.decompress(SRC.read_bytes()));cur=read(args.word)
hits=read(args.hits)
base_invoice=json.load(open(HERE/'BASELINE.json'));BT={int(k):v for k,v in base_invoice['T'].items()};BP={int(k):v for k,v in base_invoice['P'].items()}
main=set(base['live'])|{r+112 for r in base['live']}|set(base['hosted']['X2'])|set(base['hosted']['Y2']);dims=list(map(len,base['frames']))
def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encode(v)for v in x]
 return x
def raw(w):return json.dumps(w,sort_keys=True,separators=(',',':')).encode()
def digest(w):return hashlib.sha256(raw(w)).hexdigest()
def census(w):
 return Counter(dims[b]-dims[a]for r,(a,b)in enumerate(zip(w['initial'],w['final']))if r not in main),Counter(abs(dims[e[3]]-dims[e[2]])for e in w['program']if e[0]=='MOVE')
oldT,oldP=census(base)
def crossing(w):
 newT,newP=census(w);T=Counter(BT);P=Counter(BP)
 for r in set(newT)|set(oldT):T[r]+=18*(newT[r]-oldT[r])
 for r in set(newP)|set(oldP):P[r]+=18*(newP[r]-oldP[r])
 rs=sorted(set(T)|set(P));ls={r:D(r).ln()for r in rs};e=lambda c:sum(D(T[r]-P[r])*(ls[r]*(1-c)).exp()for r in rs)
 lo,hi=D('.003'),D('.005')
 for _ in range(150):
  m=(lo+hi)/2
  if e(m)>0:lo=m
  else:hi=m
 return str(lo),dict(T),dict(P)
def score(h):
 a,b,c,d=({int(k):Q(v)for k,v in h[y].items()}for y in('a','b','c','d'))
 return (round(-h['gain'],12),2*(len(basis(c,d,h['pivot'],3))+len(basis(a,b,h['pivot'],h['frame']))),h['cut'])
pending=[dict(copy.deepcopy(h),origin=i)for i,h in enumerate(hits)if all(sorted(x for x in q['old_paid']if x)==sorted(x for x in q['new_paid']if x) for q in h['paths'])];pending.sort(key=score)
def refresh(w,h):
 n=w['public'];N=n+w['owned_fields'];cut=h['cut'];f=h['frame'];at=w['initial']+[None]*w['owned_fields']
 a,b=({int(k):Q(v)for k,v in h[y].items()}for y in('a','b'))
 # Sparse reverse functional is only a search preflight. The constructor
 # separately checks the full forward prefix, suffix, and arbitrary-input word.
 from linear import load
 global directional_preflight
 if 'directional_preflight' not in globals():
  directional_preflight=load(HERE/'retained/6916/independent_directional.py','search_directional_preflight')
 for e in w['program'][:cut]:
  op,r=e[:2]
  if op=='MOVE':at[r]=e[3]
  elif op in('INIT','CLEAR'):at[r]=e[2]if op=='INIT'else None
 c=directional_preflight.prefix_dual(w['program'][:cut],a)
 d,_=directional_preflight.suffix_direction(w['program'][cut:],b)
 group={r for r in range(n)if r not in main and(w['initial'][r],w['final'][r])==(3,127)}
 need(set(c)|set(d)<=group,'same full helper boundary')
 need(sum(v*b.get(r,0)for r,v in a.items())==sum(v*d.get(r,0)for r,v in c.items())==1,'pairings')
 contacts=[[]for _ in range(N)];moves=[[]for _ in range(N)]
 for i,e in enumerate(w['program']):
  if e[0]=='MOVE':moves[e[1]].append(i)
  else:
   contacts[e[1]].append(i)
   if e[0]in('ADD','COPY'):contacts[e[2]].append(i)
 def path(r):
  if at[r]==f:return None
  if at[r]is None or r>=n:return False
  j=bisect.bisect_left(contacts[r],cut)
  lo=contacts[r][j-1]+1 if j else 0
  hi=contacts[r][j] if j<len(contacts[r]) else len(w['program'])
  mi=[i for i in moves[r]if lo<=i<hi]
  if len(mi)!=1:return False
  old,new=w['program'][mi[0]][2],w['program'][mi[-1]][3]
  if f not in (old,new):return False
  oldpaid=[abs(dims[w['program'][i][3]]-dims[w['program'][i][2]])for i in mi]
  newpaid=[abs(dims[old]-dims[f]),abs(dims[new]-dims[f])]
  if sorted(oldpaid)!=sorted(x for x in newpaid if x):return False
  return dict(role=r,lo=lo,hi=hi,frame=f,old=old,new=new,moves=mi,old_paid=oldpaid,new_paid=newpaid,cost=0,private=r>=n)
 support=set(a)|set(b);paths={r:path(r)for r in support}
 need(all(x is not False for x in paths.values()),'zero-added-paid support retiming')
 pivots={r for r in group if (r in support and paths[r]is not False)or(r not in support and path(r)is not False)}
 need(pivots,'coframed or zero-retimed full helper')
 p=min(pivots,key=lambda p:len(basis(c,d,p,3))+len(basis(a,b,p,f)))
 if p not in paths:paths[p]=path(p)
 out=copy.deepcopy(h);out.update(pivot=p,a=a,b=b,c=c,d=d,paths=[paths[r]for r in sorted(paths)if paths[r]],basis_version='dyadic-unit-v1')
 return encode(out)
def translate(h,oldn,p,cut,B,M,removed,before,after):
 hc=h['cut'];later=hc>=cut
 h['cut']=B+hc-sum(i<hc for i in removed)+(before+after+2*M if later else 0)
 for key in('a','b'):
  old={int(r):q for r,q in h[key].items()};new={}
  for r,q in old.items():
   nr=r+1 if r>=oldn else(oldn if later and r==p else r)
   new[str(nr)]=q
  h[key]=new
 if h['pivot']>=oldn:h['pivot']+=1
 elif later and h['pivot']==p:h['pivot']=oldn
start=time.time();seq=read(args.prefix)if args.prefix else[];seq=seq[:args.prefix_steps]if args.prefix_steps is not None else seq;need(not seq or seq[-1]['payload_sha256']==digest(cur),'Prefix matches source word');start_count=len(seq);rejected=[];attempt=0;free_count=len(pending);start_payload=digest(cur)
while pending and len(seq)-start_count<args.max_new and time.time()-start<900:
 h=pending.pop(0);attempt+=1
 try:
  h=refresh(cur,h);out,sw=construct(cur,h);rc=replay(out,base)
  from pricing import ordinary_bound
  need(ordinary_bound(out,read(HERE/'retained/data/caller.json'),rc)['full_ordinary_upper']<1000000000,'Complete ordinary headroom including full mixed-port LAMBDA debit')
 except Exception as exc:
  rejected.append({'origin':h.get('origin'),'error':str(exc)});continue
 a,b,c,d=({int(k):Q(v)for k,v in h[y].items()}for y in('a','b','c','d'));B=len(basis(c,d,h['pivot'],3));M=len(basis(a,b,h['pivot'],h['frame']))
 need(census(out)[1]==oldP,'no added paid jobs')
 removed={i for q in h['paths']for i in q['moves']};before=sum(q['old']!=q['frame']for q in h['paths']);after=sum(q['new']!=q['frame']for q in h['paths'])
 for hh in pending:translate(hh,cur['public'],h['pivot'],h['cut'],B,M,removed,before,after)
 j=len(seq)+1;k,T,P=crossing(out);op=OUT/('word-%02d.json.gz'%j);op.write_bytes(gzip.compress(raw(out),mtime=0))
 rec={'iteration':j,'source_payload_sha256':digest(cur),'screen_count':len(hits),'screen_hit_index':h['origin'],'witness':h,'prepared_split':sw,'receipt':rc,'payload_sha256':digest(out),'diagnostic_crossing':k,'complete_T':T,'complete_P':P,'rejected_candidates':[]}
 seq.append(rec);(OUT/'SEQUENCE.json').write_text(json.dumps(seq,sort_keys=True,indent=2)+'\n');cur=out
 print('ACCEPTED',j,'origin',h['origin'],'frame',h['frame'],'pivot',h['pivot'],'ranks',h['ranks'],'public',out['public'],'events',len(out['program']),'raw',k,'attempt',attempt,'elapsed',time.time()-start,flush=True)
(OUT/'SEARCH.json').write_text(json.dumps({'initial_hits':len(hits),'unchanged_paid_templates':free_count,'source_payload_sha256':start_payload,'initial_splits':start_count,'maximum_new_splits':args.max_new,'attempted':attempt,'accepted':len(seq)-start_count,'remaining':len(pending),'rejected':rejected},sort_keys=True,indent=2)+'\n')
print('DONE',len(seq),'attempted',attempt,'elapsed',time.time()-start,flush=True)
