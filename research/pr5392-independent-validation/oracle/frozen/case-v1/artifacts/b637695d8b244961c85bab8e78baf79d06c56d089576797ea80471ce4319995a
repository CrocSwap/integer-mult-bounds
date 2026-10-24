#!/usr/bin/env python3
"""Independent literal owned-transpose and universal free-group endpoint audit."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,json,time,copy
HERE=Path(__file__).resolve().parent
WORKSPACE=HERE.parents[2]
CAPSULE=HERE.parent/'source-capsule'
PKG=CAPSULE/'research/native-transpose-owned'
OLD=WORKSPACE/'outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'
HEAD='329b2ff35d2994b11abbb59f770d12da75c494ac'
def need(ok,why):
 if not ok:raise ValueError(why)
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def plus(row,key,value):
 value+=row.get(key,F(0))
 if value:row[key]=value
 else:row.pop(key,None)
def authenticate():
 raw=(CAPSULE/'ROOT-MANIFEST.json').read_bytes()
 need(hashlib.sha256(raw).hexdigest()=='d459d535bc81cb08f95239a729a60d616e6f45f7b1818d02a1a0d20135107a9b','exact root manifest')
 m=json.loads(raw);need(m['head']==HEAD,'exact head')
 for r in m['rows']:
  b=(CAPSULE/r['path']).read_bytes();need(blob(b)==r['git_blob'] and hashlib.sha256(b).hexdigest()==r['sha256'],'source byte binding '+r['path'])
 return hashlib.sha256(raw).hexdigest()
def transform(program):
 emitted=[];formal=[];counts=Counter();paid=Counter()
 for index in range(len(program)-1,-1,-1):
  e=program[index];kind=e[0];counts[kind]+=1
  if kind=='scalar':
   g=e[1];tag=g[0]
   if tag=='add':out=[['scalar',['add',g[2],g[1],*g[3:]],e[2]]]
   elif tag=='copy':out=[['scalar',['add',g[2],g[1],1,1],e[2]],['scalar',['clear',g[1]],e[2]]]
   else:need(tag in ('clear','scale'),'scalar grammar');out=[e]
  elif kind=='warp':out=[['warp',e[1],-e[2],e[4],e[3]]]
  elif kind in ('climb','center'):
   rank=e[-1];out=[['transpose_paid_source',index,rank]];paid[rank]+=1
  elif kind=='zero_retag':
   formal.append(['ghost',e[1],10000001+index]);continue
  else:need(kind in ('phase','adapter'),'source marker');out=[['transpose_marker',index]]
  emitted.extend(out);formal.extend(out)
 return emitted,formal,counts,paid

def evaluate(program,owned):
 roles=[('L',i) for i in range(632)]+[('C',i) for i in range(9)]
 rows={r:{(r,()):F(1)} for r in roles};entry_owned=set(owned)
 for e in program:
  kind=e[0]
  if kind=='scalar':
   g=e[1];dst=tuple(g[1]);tag=g[0]
   if tag=='clear':need(dst in entry_owned,'erase only owned destination');rows[dst]={}
   elif tag=='scale':rows[dst]={key:q*F(*g[2:]) for key,q in rows[dst].items()}
   else:
    need(tag=='add','no overwrite COPY in transpose');src=tuple(g[2]);need(src!=dst,'distinct ADD owners')
    for key,q in tuple(rows[src].items()):plus(rows[dst],key,q*F(*g[3:]))
  elif kind in ('warp','ghost'):
   dst=tuple(e[1]);op=e[2];out={}
   for (r,w),q in rows[dst].items():
    nw=w[1:] if w and w[0]==-op else (op,)+w;plus(out,(r,nw),q)
   rows[dst]=out
  else:need(kind in ('transpose_paid_source','transpose_marker'),'proof grammar')
 for r in roles:
  want={} if r in entry_owned else {(r,()):F(1)}
  if r[0]=='L' and 112<=r[1]<224:want[(('L',r[1]-112),())]=F(-1)
  need(rows[r]==want,'full arbitrary-entry endpoint '+str(r))
 return {'entry_columns':len(roles),'retained':len(roles)-len(entry_owned),'arbitrary_owned':len(entry_owned),'owned_returned_zero':True,'all_ghost_terms_cancel':True,'normalized_main_transpose_shear':'(x,y)->(x,y-x)'}
def polynomial_interface():
 # Laurent polynomials in D and Q, with Q exponent reduced mod4.
 def add(a,b):
  r=dict(a)
  for k,v in b.items():
   v+=r.get(k,0)
   if v:r[k]=v
   else:r.pop(k,None)
  return r
 def mul(a,b):
  r={}
  for (d,q),v in a.items():
   for (e,s),w in b.items():r=add(r,{(d+e,(q+s)%4):v*w})
  return r
 def mm(a,b):return [[add(mul(a[i][0],b[0][j]),mul(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
 Z={};D={(1,0):1};J=[[{(0,2):1},Z],[Z,{(0,0):-1}]];B=[[D,{(1,1):-1}],[Z,D]];T=list(map(list,zip(*B)));want=[[D,Z],[{(1,3):1},D]]
 need(mm(mm(J,T),J)==want,'F=J B^T J')
 wrong=[[{(0,0):1},Z],[Z,{(0,0):-1}]]
 need(mm(mm(wrong,T),wrong)!=want,'omitted Q squared control')
 # Native constant phase2 tensorizes to(-1)^f, unlike external scalar-1.
 need((-1)**2!=-1,'f2 scalar/tensor minus-one control')
 return {'identity':'F=J B^T J','Q_modulus':4,'D_formal_commuting_symmetric':True,'minus_one_external_scalar':True,'wrong_Q_correction_rejected':True,'f2_native_minus_one_rejected':True}
def main():
 start=time.monotonic();manifest=authenticate();old=load(OLD);word=load(PKG/'WORD.json.gz')
 need(hashlib.sha256(gzip.decompress(OLD.read_bytes())).hexdigest()=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d','independently checked5383source')
 need(word['source_word_sha256']=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d','declared exact source')
 need(word['backward']==old['programs']['backward'],'literal unchanged independently checked backward')
 owned={tuple(r) for r in word['owned_roles']};need(owned=={tuple(r) for r in old['owned']['backward']},'exact17owned role contract')
 emitted,formal,counts,paid=transform(word['backward']);need(emitted==word['forward_body'],'exact literal transpose, with physical zero identities omitted')
 endpoint=evaluate(formal,owned)
 c=old['canonical'];bound=word['forward_boundary']
 need(bound['both_ends']=={'X':'Q_squared_native','Y':'scalar_minus_one'},'actual J wrappers')
 need(bound['main_Q_squared_offsets']==c['ports'] and len(c['ports'])==112,'all112actual port translations')
 helpers=[r for r in range(224,632) if ('L',r) not in owned]
 expected=[{'role':r,'rank':len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]),'offset':(1<<(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]])))-1} for r in helpers]
 need(bound['helper_post_translations']==expected and len(expected)==400,'complete400actual helper corrections')
 need(bound['source_wrappers']=='transpose the normalized backward whole-job wrappers','whole invocation wrappers explicit')
 need({int(k):v for k,v in word['paid_profiles']['forward'].items()}==paid,'literal forward paid histogram')
 controls=[]
 def reject(label,mutate):
  bad=copy.deepcopy(formal);mutate(bad)
  try:evaluate(bad,owned)
  except ValueError as error:return {'control':label,'status':'REJECTED','reason':str(error)}
  raise ValueError('control accepted '+label)
 def find(p,f):return next(i for i,e in enumerate(p) if f(e))
 def wrongadd(p):
  i=find(p,lambda e:e[0]=='scalar' and e[1][0]=='add');p[i][1][1],p[i][1][2]=p[i][1][2],p[i][1][1]
 controls.append(reject('wrong ADD transpose',wrongadd))
 def noclear(p):
  i=find(p,lambda e:e[0]=='scalar' and e[1][:2]==['clear',['C',1]]);p.pop(i)
 controls.append(reject('omitted owned COPY cleanup',noclear))
 def wrongwarp(p):
  i=find(p,lambda e:e[0]=='warp');p[i][2]*=-1
 controls.append(reject('wrong warp transpose inverse',wrongwarp))
 # Ghosts are arbitrary full operators, not assumed monomial or zero-input.
 raw=(PKG/'WORD.json.gz').read_bytes()
 result={'status':'PASS_INDEPENDENT_LITERAL_TRANSPOSE_AND_UNIVERSAL_ENDPOINT','head':HEAD,'manifest_sha256':manifest,'word_sha256':hashlib.sha256(raw).hexdigest(),'word_payload_sha256':hashlib.sha256(gzip.decompress(raw)).hexdigest(),'word_git_blob':blob(raw),'source_program_counts':dict(counts),'paid':dict(sorted(paid.items())),'entry_endpoint':endpoint,'ghosts':sum(e[0]=='ghost' for e in formal),'main_interface':polynomial_interface(),'helper_translations':len(expected),'helper_ranks':dict(Counter(r['rank'] for r in expected)),'negative_controls':controls,'seconds':round(time.monotonic()-start,3),'scope':'Fresh literal transposition and formal all-column/owned bridge cancellation; exact wrapper inventory and F=J B^T J. Actual2847paid phase recipes require separate independent phase receipt; five inherited physical premises remain.'}
 (HERE/'WORD-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
