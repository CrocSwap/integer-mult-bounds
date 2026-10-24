#!/usr/bin/env python3
"""Independent literal #5392 invoice; standard library, no submitted imports.

Complete source/transposed chronology, recursive ranks, helper ownership,
scalar macros and conservative route reservation. Physical transpose/phase
and expanded-template applicability are independent external prerequisites.
Substantial OpenAI Codex assistance; preserve Ali Romman and all source credit.
"""
from pathlib import Path
from hashlib import sha256,sha1
from fractions import Fraction as Q
from collections import Counter
import gzip,json
H=Path(__file__).resolve().parent;W=H.parent;ROOT=H.parents[2]
CAP=W/'source-capsule';PKG='research/native-transpose-owned';HEAD='329b2ff35d2994b11abbb59f770d12da75c494ac';BASE='1ec1119972c9aefe42525172d07b332fcff81cb4'
OLD=ROOT/'outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot'
NEEDED=['research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','research/joint-helper-lattice/CONTROLLER.json','research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','research/query-thinned-controllers/RESULT.json']
def need(x,s):
 if not x:raise ValueError(s)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def checked(row,b):
 need(sha256(b).hexdigest()==row['sha256'],'source SHA '+row['path']);need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'source Git blob '+row['path'])
def hist(x):return {str(k):v for k,v in sorted(x.items()) if v}
def scalar(g):
 if g[0] in ('copy','clear'):return 2
 q=Q(*(g[3:] if g[0]=='add' else g[2:]));n,d=abs(q.numerator),q.denominator
 need(n>0 and d&(d-1)==0,'dyadic scalar required')
 if g[0]=='scale':need(n&(n-1)==0,'dyadic unit SCALE');return 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
 need(g[0]=='add','scalar opcode');return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def authenticate():
 root=read(CAP/'ROOT-MANIFEST.json');need(root['head']==HEAD,'candidate head')
 for row in root['rows']:checked(row,(CAP/row['path']).read_bytes())
 source=read(CAP/PKG/'SOURCES.json');need(source['base_commit']==BASE,'source base')
 rows={r['path']:r for r in source['files']};bindings={}
 for name in NEEDED:
  data=(OLD/name).read_bytes();checked(rows[name],data);dest=H/'frozen-canonical'/name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():need(dest.read_bytes()==data,'immutable canonical bytes changed')
  else:dest.write_bytes(data);dest.chmod(0o444)
  bindings[name]={'sha256':sha256(data).hexdigest(),'git_blob':rows[name]['git_blob'],'path':str(dest),'source_commit':BASE}
 oldword=OLD/'research/kappa-joint-relations-20261023/WORD.json.gz';need(sha(oldword)=='7883ba0faefc96505bb61ca7312d588fa22dfe2164050c817c1718b8fa28693a','independent #5383 literal source changed')
 dest=H/'frozen-owned-source-WORD.json.gz'
 if dest.exists():need(dest.read_bytes()==oldword.read_bytes(),'frozen source word changed')
 else:dest.write_bytes(oldword.read_bytes());dest.chmod(0o444)
 return {'root_manifest_sha256':sha(CAP/'ROOT-MANIFEST.json'),'candidate_rows_rechecked':len(root['rows']),'canonical':bindings,'source_owned_word_sha256':sha(dest),'source_owned_word_payload_sha256':sha256(gzip.decompress(dest.read_bytes())).hexdigest()}
def paid_rank(e,c):
 need(e[0] in ('climb','center'),'paid opcode');r=e[-1];a,b=e[-3:-1]
 need(type(r) is int and r>0 and abs(len(c['frames'][a])-len(c['frames'][b]))==r,'paid rank not frame dimensional delta');return r
def transpose_records(b,c):
 out=[]
 for i in reversed(range(len(b))):
  e=b[i];kind=e[0]
  if kind=='scalar':
   g=e[1]
   if g[0]=='add':out.append(['scalar',['add',g[2],g[1],*g[3:]],e[2]])
   elif g[0]=='copy':out.extend([['scalar',['add',g[2],g[1],1,1],e[2]],['scalar',['clear',g[1]],e[2]]])
   else:need(g[0] in ('clear','scale'),'scalar transpose alphabet');out.append(e)
  elif kind=='warp':out.append(['warp',e[1],-e[2],e[4],e[3]])
  elif kind in ('climb','center'):out.append(['transpose_paid_source',i,paid_rank(e,c)])
  elif kind=='zero_retag':pass # Source and transposed physical identities; no zero assertion on reverse rows.
  else:need(kind in ('phase','adapter'),'source grammar');out.append(['transpose_marker',i])
 return out
def local_paid(program,c,source=None):
 p=Counter();sc=0;ops=Counter();kinds=Counter()
 for e in program:
  k=e[0];kinds[k]+=1
  if k in ('climb','center'):p[paid_rank(e,c)]+=1
  elif k=='transpose_paid_source':
   need(source is not None and 0<=e[1]<len(source),'paid source occurrence');rank=paid_rank(source[e[1]],c);need(e[2]==rank,'transpose paid rank');p[rank]+=1
  elif k=='scalar':sc+=scalar(e[1]);ops[e[1][0]]+=1
 return p,sc,ops,kinds
def assemble(controller,locals_,helpers):
 P=Counter();T=Counter();counts=Counter();main=Counter();idle=Counter();chron=[]
 fullstages={e[1] for e in controller['physical_events'] if e[0]=='LOCAL'}
 for i,e in enumerate(controller['physical_events']):
  ep=Counter();et=Counter();k=e[0];counts[k]+=1
  if k=='LOCAL':
   d='backward' if e[3] else 'forward';counts[d]+=1;ep.update(locals_[d]);et.update(helpers[d])
  elif k=='QUERY_SHEAR':ep[1]+=112
  elif k=='IDLE':
   need(len(set(e[2]))==len(e[2]) and all(type(j) is int and j in fullstages for j in e[2]),'literal idle stage list');ep[8*len(e[2])]+=224;idle.update(ep)
  else:need(k in ('ADD','SIGNED_SWAP'),'controller event')
  P.update(ep);T.update(et);chron.append({'index':i,'event':e,'paid':hist(ep),'helpers':hist(et)})
 for term in controller['diagonal']:
  need(abs(term[0])==1 and all(x in (0,1) for x in term[1:]) and all(not q or j in fullstages for j,q in enumerate(term[1:])), 'main target term');main[1+8*sum(term[1:])]+=112
 T.update(main);return P,T,counts,main,idle,chron
def run():
 need(not (H/'INVOICE-v1.json').exists(),'immutable invoice exists')
 auth=authenticate();x=read(CAP/PKG/'WORD.json.gz');base=read(H/'frozen-canonical'/NEEDED[0]);old=read(H/'frozen-owned-source-WORD.json.gz');c=base['canonical'];ctl=read(H/'frozen-canonical'/NEEDED[1])
 need(x['schema']=='owned-transpose-word/v1' and x['source_word_sha256']==auth['source_owned_word_payload_sha256'],'source physical word binding')
 need(x['backward']==old['programs']['backward'] and all(v==c[k] for k,v in old['canonical'].items()) and set(c)-set(old['canonical'])=={'local_profile'},'literal backward source differs')
 need(x['forward_body']==transpose_records(x['backward'],c),'literal transpose event/charge sequence differs')
 owned=set(map(tuple,x['owned_roles']));need(owned==set(map(tuple,old['owned']['backward'])),'owned inventory changed')
 local={};scalars={};ops={};kinds={}
 for d,program in [('backward',x['backward']),('forward',x['forward_body'])]:local[d],scalars[d],ops[d],kinds[d]=local_paid(program,c,x['backward'] if d=='forward' else None)
 helper_roles=[r for r in range(224,len(c['start'])) if ('L',r) not in owned]
 helpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in helper_roles)
 boundary=x['forward_boundary'];need(boundary['both_ends']=={'X':'Q_squared_native','Y':'scalar_minus_one'},'unpriced interface correction')
 need(boundary['main_Q_squared_offsets']==c['ports'],'complete main Q-squared offset list')
 expected=[{'role':r,'rank':len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]),'offset':2**(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]))-1} for r in helper_roles]
 need(boundary['helper_post_translations']==expected,'complete helper translation pass')
 main_native=2*len(c['ports']);main_scalar=2*len(c['ports'])*scalar(['scale',['L',0],-1,1]);helper_native=len(expected)
 scalar_before=dict(scalars);scalars['forward']+=main_scalar
 P,T,counts,main,idle,chron=assemble(ctl,local,{'forward':helpers,'backward':helpers})
 basepaid={};basehelpers={}
 for d in ['forward','backward']:
  basepaid[d]=local_paid(base['programs'][d],c)[0];basehelpers[d]=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,len(c['start'])))
 BP,BT,*_=assemble(ctl,basepaid,basehelpers)
 # Conservative fresh route cap: both source/transpose bodies, every phase,
 # old helper wrappers and owned lifetimes, plus all newly emitted corrections.
 sourcepaid=max(sum(v.values()) for v in basepaid.values());sourcehelpers=max(sum(v.values()) for v in basehelpers.values())
 warps=kinds['backward']['warp'];adapters=kinds['backward']['adapter'];phases=kinds['backward']['phase'];extraowned=len(owned)-1
 route_terms={'source_paid':sourcepaid,'two_helper_wrappers':2*sourcehelpers,'warps':warps,'adapters':adapters,'explicit_phase_groups':phases,'two_routes_per_added_owned_lifetime':2*extraowned}
 routes=2*sum(route_terms.values())+main_native+helper_native
 # Boundary/controller ordinary programs are explicitly charged within32/port.
 bcounts={}
 for side in ['left','right']:
  prog=ctl['boundaries'][side+'_program'];cost=0
  for e in prog:
   if e[0]=='SWAP':units=26
   elif e[0]=='SCALE':
    q=Q(e[2]);units=scalar(['scale',['L',0],q.numerator,q.denominator])
   else:need(e[0]=='ADD','boundary opcode');q=Q(e[3]);units=scalar(['add',['L',0],['L',1],q.numerator,q.denominator])
   need(units<=32,'boundary record tariff');cost+=112*units
  bcounts[side]={'events':len(prog),'explicit_scalar_units':cost,'charged_32_per_port':True}
 raw=counts['LOCAL']*2*10**7+counts['QUERY_SHEAR']*1792+32*112*(len(ctl['physical_events'])+sum(v['events'] for v in bcounts.values()))
 need(max(scalars.values())+routes*1000<2*10**7 and raw<10**9,'unfunded ordinary allowance')
 need(counts['backward']==16 and counts['forward']==2 and counts['QUERY_SHEAR']==15,'full controller incidence')
 need(len(owned)==17 and len(helper_roles)==400,'ownership/productive helper census')
 chronp=H/'CHRONOLOGY-v1.json';chronp.write_text(json.dumps({'controller':chron,'local_kinds':{d:dict(k) for d,k in kinds.items()},'boundary':bcounts},sort_keys=True,indent=2)+'\n');chronp.chmod(0o444)
 out={'schema':'independent-literal-transpose-invoice/1','candidate':{'pr':5392,'head':HEAD,'canonical_base':BASE,'package':PKG},'status':'LITERAL_CENSUS_AND_CONSTRUCTIVE_ORDINARY_INVOICE_READY','authentication':auth,'word_sha256':sha(CAP/PKG/'WORD.json.gz'),'histograms':{'paid':hist(P),'productive':hist(T)},'local':{d:{'paid':hist(local[d]),'productive_helpers':hist(helpers),'body_scalar_units':scalar_before[d],'complete_scalar_units':scalars[d],'scalar_ops':dict(ops[d]),'event_kinds':dict(kinds[d])} for d in ['forward','backward']},'totals':{'paid':sum(P.values()),'productive':sum(T.values()),'paid_rank_mass':sum(r*n for r,n in P.items()),'productive_rank_mass':sum(r*n for r,n in T.items()),'rank_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())},'controller':{'counts':dict(counts),'main':hist(main),'idle':hist(idle),'raw_owned_banks':counts['LOCAL']*len(owned)},'delta_from_literal_selected':{'paid':hist(Counter({r:P[r]-BP[r] for r in P.keys()|BP.keys()})),'productive':hist(Counter({r:T[r]-BT[r] for r in T.keys()|BT.keys()}))},'ordinary':{'classification':'constructively_upper_bounded','source_route_terms':route_terms,'both_directions_route_multiplier':2,'main_Q_squared_native_passes':main_native,'main_scalar_minus_one_units':main_scalar,'helper_native_passes':helper_native,'route_groups_upper':routes,'route_unit_multiplier':1000,'route_units_upper':routes*1000,'local_scalar_max':max(scalars.values()),'local_units_upper':max(scalars.values())+routes*1000,'local_budget':2*10**7,'raw_units_upper':raw,'raw_budget':10**9,'explicit_new_phase_groups_charged':2*phases,'no_scalar_count_inserted_in_rank_moment':True,'unknown_charges_are_zero':False,'tariff_applicability':'requires role03 source physical primitive/whole-job/native translation applicability; one1000record cap per fixed9axis route group'},'chronology_sha256':sha(chronp),'physical_gate':'PENDING_ROLE01_FULL_TRANSPOSE_PHASE_ALL_COLUMN_REVIEW','precision_gate':'PENDING_ROLE03_NEW_WORD_EXPANDED_COUNT_STOCK_TAPE_APPLICABILITY','not_established':['physical transpose/native phases','expanded constants and fixed tape theorem','exact numerical funding'],'method':'Literal JSON and exact Fraction only. No candidate RESULT/price/native/verifier code imported; emitted paid_profiles/helper_profiles not used.'}
 outp=H/'INVOICE-v1.json';outp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');outp.chmod(0o444)
 print(json.dumps({'invoice_sha256':sha(outp),'totals':out['totals'],'scalar':scalars,'route_upper':routes*1000,'local_upper':out['ordinary']['local_units_upper'],'raw':raw,'raw_owned_banks':out['controller']['raw_owned_banks']}))
if __name__=='__main__':run()
