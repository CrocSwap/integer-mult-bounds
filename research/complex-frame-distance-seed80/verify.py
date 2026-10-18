"""Exact geometric frame-distance proof certificate and source-bound replay."""
import argparse,gzip,hashlib,json,sys,tarfile
from collections import Counter
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));import literal
BASE='ba82555c64e1879e4b7decce28186f208fcb8262'
COMPILER='research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'
OBLIGATION='research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/code/phases_full.py'
PATHS=('research/community-frontier1042-audit/selected-replay.tar.gz',COMPILER,OBLIGATION,'research/gauge44-slots-t16/construction/slots/SLOT-PINS-k8.json')
MEMBERS=('slots/local/CANONICAL-WORD.json.gz','slots/local/CLIFFORD-RECIPES.json','slots/local/CLIFFORD-REVIEW.json')
def need(b,s):
 if not b:raise ValueError(s)
def pairs(ps):
 d={}
 for k,v in ps:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def read(b):return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
@lru_cache(None)
def span(U):
 a={0}
 for u in U:a|={x^u for x in tuple(a)}
 return frozenset(a)
def dim(S):
 k=len(S);need(k>0 and k&(k-1)==0,'subspace cardinality');return k.bit_length()-1
def lagrangian(n,U):
 S=span(tuple(U));perp=[z for z in range(1<<n) if all((u&z).bit_count()%2==0 for u in U)]
 return frozenset(u|((u^z)<<n) for u in S for z in perp)
def source():
 pins=read((HERE/'SOURCES.json').read_bytes());need(set(pins)=={'base','files'} and pins['base']==BASE and set(pins['files'])==set(PATHS),'exact source inventory')
 for p in PATHS:need(sha((ROOT/p).read_bytes())==pins['files'][p],'source pin '+p)
 data={}
 with tarfile.open(ROOT/PATHS[0]) as t:
  for name in MEMBERS:
   match=[m for m in t.getmembers() if m.name==name];need(len(match)==1 and match[0].isfile(),'unique named member')
   b=t.extractfile(match[0]).read();data[name]=gzip.decompress(b) if name.endswith('.gz') else b
 c,recipes,review=[read(data[name]) for name in MEMBERS]
 slot=read((ROOT/PATHS[3]).read_bytes())
 need(sha(data[MEMBERS[0]])==slot['canonical_sha256']=='4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c','canonical word')
 need(sha(data[MEMBERS[1]])==slot['clifford_recipes_sha256']==review['recipe_sha256'],'recipe identity')
 need((c['h'],c['v'],c['R'])==(9,112,480),'source geometry')
 return c,recipes,review
def matrices(n,frames):
 M=[];I=[]
 for U in frames:
  need(len(span(tuple(U)))==1<<len(U),'independent basis')
  a=literal.frame(n,U);need(literal.symplectic(a,n),'symplectic frame');b=literal.inverse_columns(a)
  pre=span(tuple(b[n:]));need(pre==lagrangian(n,U),'literal canonical preimage Lagrangian')
  M.append(a);I.append(b)
 return M,I
def selected(c,recipes,review,precomputed=None):
 n=c['h'];frames=c['frames'];M,I=precomputed if precomputed is not None else matrices(n,frames);spaces=[span(tuple(u)) for u in frames]
 edges=set(map(tuple,c['edges']))|{e for f in c['center_frames'] for e in ((f,0),(0,f))}
 recs=recipes['children'];keys=[(r['old'],r['new']) for r in recs]
 need(len(keys)==len(set(keys)) and set(keys)==edges,'exact child edge inventory')
 hist=Counter();rows=[]
 for rec in sorted(recs,key=lambda r:(r['old'],r['new'])):
  a,b=rec['old'],rec['new'];d=len(frames[a])+len(frames[b])-2*dim(spaces[a]&spaces[b])
  r=literal.transition_rank(n,I[a],M[b]);need(r==d,'literal versus intersection rank')
  need(type(rec['rank']) is int and rec['rank']==r,'stored child rank')
  need(spaces[a]<=spaces[b] or spaces[b]<=spaces[a],'selected edge nested')
  need(r==abs(len(frames[a])-len(frames[b])),'nested corollary')
  hist[r]+=1;rows.append([a,b,r])
 need({str(k):v for k,v in sorted(hist.items())}==review['ranks'],'stored rank histogram')
 adapters=recipes['endpoint_adapters'];keys=[(r['role'],r['port']) for r in adapters]
 need(len(keys)==len(set(keys)) and set(keys)=={(role,p) for role in ('source','target') for p in range(c['v'])},'exact adapter inventory')
 for rec in adapters:
  target=rec['role']=='target';p=rec['port'];q=c['ports'][p]
  f=c['final'][c['v']+p] if target else c['start'][p]
  need(rec['frame']==f,'adapter frame identity')
  old=literal.port_frame(n,q,target);r=literal.transition_rank(n,literal.inverse_columns(old),M[f])
  need(type(rec['rank']) is int and rec['rank']==r==0,'endpoint adapter rank')
 return {'frames':len(frames),'edges':len(edges),'endpoint_adapters':len(adapters),'rank_histogram':{str(k):v for k,v in sorted(hist.items())},'edge_digest':sha(enc(rows).encode()),'all_nested':True},(M,I)
def all_subspaces(n):
 # Closure under adjoining any ambient vector reaches every finite subspace.
 spaces={frozenset({0}):()};todo=[frozenset({0})]
 for S in todo:
  for x in range(1,1<<n):
   if x in S:continue
   T=S|frozenset(y^x for y in S)
   if T not in spaces:spaces[T]=spaces[S]+(x,);todo.append(T)
 return sorted(spaces.items(),key=lambda z:(len(z[0]),sorted(z[0])))
def exhaustive():
 n=5;items=all_subspaces(n);spaces,frames=zip(*items)
 need(Counter(map(dim,spaces))=={0:1,1:31,2:155,3:155,4:31,5:1},'all F2^5 subspaces')
 M,I=matrices(n,frames);hist=Counter();shortcut=0;first=None;digest=hashlib.sha256()
 for i,S in enumerate(spaces):
  for j,T in enumerate(spaces):
   d=dim(S)+dim(T)-2*dim(S&T);r=literal.transition_rank(n,I[i],M[j])
   need(r==d,'exhaustive geometric/literal agreement');hist[r]+=1
   if d!=abs(dim(S)-dim(T)):
    shortcut+=1
    if first is None:first={'U':list(frames[i]),'V':list(frames[j]),'true_rank':r,'absolute_dimension_difference':abs(dim(S)-dim(T))}
   digest.update(bytes((r,)))
 return {'ambient_dimension':n,'subspaces':len(items),'ordered_pairs':len(items)**2,'rank_histogram':{str(k):v for k,v in sorted(hist.items())},'rank_stream_sha256':digest.hexdigest(),'dimension_difference_failures':shortcut,'first_counterexample':first}
def controls(c,recipes,review):
 import copy
 count=0
 # These validation cases reuse source matrices, so do not re-run frame setup.
 frames=c['frames'];M,I=matrices(c['h'],frames)
 def reject(r,v,message):
  try:selected(c,r,v,(M,I))
  except ValueError as e:need(message in str(e),'wrong rejection reason');return
  raise ValueError('accepted corrupted recipe')
 bad=copy.deepcopy(recipes);bad['children'][0]['rank']+=1
 reject(bad,review,'stored child rank');count+=1
 bad=copy.deepcopy(recipes);bad['children'].pop()
 reject(bad,review,'exact child edge inventory');count+=1
 bad=copy.deepcopy(recipes);bad['children'].append(bad['children'][0])
 reject(bad,review,'exact child edge inventory');count+=1
 bad=copy.deepcopy(review);bad['ranks'][next(iter(bad['ranks']))]+=1
 reject(recipes,bad,'stored rank histogram');count+=1
 bad=copy.deepcopy(recipes);bad['endpoint_adapters'].pop()
 reject(bad,review,'exact adapter inventory');count+=1
 bad=copy.deepcopy(recipes);bad['endpoint_adapters'][0]['rank']=1
 reject(bad,review,'endpoint adapter rank');count+=1
 # Non-nested equal-size spaces show that the shortcut can miss positive rank.
 for U,V in [((1,),(2,)),((1,2),(2,4)),((1,2),(4,8))]:
  mats,invs=matrices(5,[U,V]);rank=literal.transition_rank(5,invs[0],mats[1]);need(rank>0 and len(U)==len(V),'nonnested shortcut control');count+=1
 # Gate convention errors must violate the geometric preimage, not just a pin.
 for n,U in [(3,(3,)),(4,(3,5)),(5,(3,5,9))]:
  a=literal.frame(n,U);bad=list(a);bad[n]^=1
  try:b=literal.inverse_columns(bad);ok=literal.symplectic(bad,n) and span(tuple(b[n:]))==lagrangian(n,U)
  except ValueError:ok=False
  need(not ok,'corrupted primitive action');count+=1
  dropped=literal.frame(n,U,omit_diagonal=True)
  need(literal.symplectic(dropped,n),'diagonal omission remains symplectic')
  need(span(tuple(literal.inverse_columns(dropped)[n:]))!=lagrangian(n,U),'diagonal omission must change preimage');count+=1
 # A scalar global phase is deliberately invisible to this rank-only checker.
 bad=copy.deepcopy(recipes);bad['children'][0]['left']['phase']=(bad['children'][0]['left']['phase']+1)%4
 need(enc(selected(c,bad,review,(M,I))[0])==enc(selected(c,recipes,review,(M,I))[0]),'documented phase blind spot')
 return count
def compute():
 c,r,v=source();s,_=selected(c,r,v);e=exhaustive();k=controls(c,r,v)
 return {'base':BASE,'source_checkpoint':'historical PR1042 R480; current frontier not modified','identity':'rank(B(F_V F_U^-1)) = dim(U)+dim(V)-2dim(U intersect V)',
 'selected':s,'exhaustive':e,'controls':k,'phase_blind_spot_demonstrated':True,'phase_checked':False,'operator_equality_checked':False,'new_kappa':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();r=compute()
 if args.write:(HERE/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
 else:need(enc(r)==enc(read((HERE/'RESULT.json').read_bytes())),'typed canonical result mismatch')
 print('PASS_COMPLEX_FRAME_DISTANCE frames='+str(r['selected']['frames'])+' edges='+str(r['selected']['edges'])+' pairs=139876 controls='+str(r['controls'])+' no_phase_claim')
 print(json.dumps(r['exhaustive'],sort_keys=True))
if __name__=='__main__':main()
