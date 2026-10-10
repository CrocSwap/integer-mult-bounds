from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Fresh literal PR325 banks, conditioned on hash-bound local source admission.
Independent code; immutable upstream files and sibling results are inert data.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from math import gcd,lcm
import json,gzip,hashlib,struct
if not __debug__:raise RuntimeError('Assertions required')
P=contract.BANK;I=contract.INERT;A=contract.SOURCE
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def write(n,obj):
 b=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode();(P/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
contract.verify_source()
admit=read(A/'RESULT.json');assert admit['status']=='PASS_ALL480_PR325_PARTNER_MIX_RETIMINGS_RAW_LOCAL_PROOF' and admit['admitted']==480 and admit['rejected']==0
for name,h in admit['artifacts'].items():assert sha(A/name)==h
assert not admit['prior_role_or_frame_selections_imported'] and not admit['upstream_programs_executed']
base=read(P/'BASE-LEDGER.json');w=read(I/'bitword__selected__bit__word_p10.json');F=read(I/'bitword__selected__bit__frames_p10.json')['frames'];K=read(I/'bitword__selected__bit__kchron_p10.json')['entries'];sel=read(A/'retiming-selection.json')['entries'];events=read(A/'source-events.json.gz');scalar=read(A/'scalar-events.json.gz');dim=lambda f:0 if f==-1 else F[str(f)]['dim']
assert len(sel)==len(K)==480 and len(events)==3840
assert sum(x['op']==1 for x in scalar)==admit['weighted_additions']==350640
assert sum(abs(x['c']) for x in scalar if x['op']==1)==admit['literal_unit_additions']==352560
assert sum(x['op']==2 for x in scalar)==sum(x['op']==3 for x in scalar)==20
# Recount actual retimed source paths, rather than applying a proposed delta.
source_paths=[[] for _ in range(960)];seen=set()
for e in events:
 i=e['event']; assert i not in seen;seen.add(i)
 old=scalar[i];assert all(e[k]==old[k] for k in ['op','a','b','c','semantic'])
 assert e['frame']==old['frame']
 if e['semantic'][0]=='partner_setup': assert e['frame']==K[e['semantic'][1]]['deliver_frame']
 for port in (e['a'],e['b']):
  if port<960:source_paths[port].append(e['frame'])
for j,s in enumerate(sel):
 old=K[j];assert s['pair']==j and (s['carrier'],s['passive'])==(old['carrier'],old['passive'])
 assert s['new_frame']==old['deliver_frame'] and s['old_frame']==old['mix_frame'] and dim(s['new_frame'])==18 and dim(s['old_frame'])==2
 assert scalar[s['setup_event']]['semantic']==['partner_setup',j,old['deliver_after_root']]
 for port,path in s['new_chains'].items():
  actual=[x for n,x in enumerate(source_paths[int(port)]) if n==0 or x!=source_paths[int(port)][n-1]]
  assert actual==path
source_hist=Counter()
for path in source_paths:
 ds=list(map(dim,path));assert ds[0]==1 and ds[-1]==20 and all(a<=b for a,b in zip(ds,ds[1:]));source_hist.update(b-a for a,b in zip(ds,ds[1:]) if b>a)
assert source_hist=={2:960,17:960}
helper=Counter({int(r):n for r,n in base['helper'].items()});oldsrc={int(r):n for r,n in base['source'].items()}
for r,n in oldsrc.items():helper[r]-=n
helper.update(source_hist);assert all(n>=0 for n in helper.values())
H=Counter({r:300*n for r,n in helper.items() if n});H.update({r:60*1920 for r in (4,19,38,42)})
assert sum(H.values())==14514000 and sum(r*n for r,n in H.items())==65757600
# Fresh physical roles and actual endpoint projectors from this exact word.
R=1+max(max(z[:2]) for z in w['ops']);roles=sorted(set(range(R))-{b for a,b in w['pairs']});gauges={g['role']:g['frame'] for g in w['gauges'] if g['role'] in roles};assert roles==base['physical_roles'] and len(roles)==8100
widths={r:20-dim(gauges[r]) if r in gauges else 20 for r in roles};assert Counter(widths.values())=={4:1200,20:6900}
def reduced(rows):
 a=[list(map(Q,row)) for row in rows];p=[];i=0
 for j in range(20):
  k=next((k for k in range(i,len(a)) if a[k][j]),None)
  if k is None:continue
  a[k],a[i]=a[i],a[k];d=a[i][j];a[i]=[x/d for x in a[i]]
  for k in range(len(a)):
   if k!=i and a[k][j]:d=a[k][j];a[k]=[x-d*y for x,y in zip(a[k],a[i])]
  p.append(j);i+=1
 return a[:i],p
def null(rows):
 a,p=reduced(rows);out=[]
 for j in range(20):
  if j in p:continue
  v=[Q(int(i==j)) for i in range(20)]
  for i,k in enumerate(p):v[k]=-a[i][j]
  d=lcm(*(x.denominator for x in v));v=[int(x*d) for x in v];d=gcd(*v);out.append([x//d for x in v])
 return out
def invert(B):
 a=[list(map(Q,row))+[Q(int(i==j)) for j in range(20)] for i,row in enumerate(B)];ops=[]
 for j in range(20):
  k=next(k for k in range(j,20) if a[k][j])
  if k!=j:a[j],a[k]=a[k],a[j];ops.append(['swap',j,k,None])
  d=a[j][j]
  if d!=1:a[j]=[x/d for x in a[j]];ops.append(['scale',j,j,str(1/d)])
  for i in range(20):
   if i!=j and a[i][j]:d=-a[i][j];a[i]=[x+d*y for x,y in zip(a[i],a[j])];ops.append(['add',i,j,str(d)])
 assert all(a[i][j]==int(i==j) for i in range(20) for j in range(20));return [row[20:] for row in a],ops
def mm(B,C):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*C)] for row in B]
identity=[[int(i==j) for j in range(20)] for i in range(20)];charts=[];maxops=maxnum=maxden=0
for frame,count in sorted(Counter(gauges.values()).items()):
 a=F[str(frame)]['a'];source=null(a);residual=[]
 for row in a:
  v=[11*x-sum(row) for x in row];d=gcd(*v);residual.append([x//d for x in v])
 assert len(source)==16 and len(residual)==4
 assert all(sum(x*y for x,y in zip(u,v))==0 for u in a for v in source)
 assert all(9*sum(x*y for x,y in zip(u,v))-sum(u)*sum(v)==0 for u in residual for v in source)
 B=list(map(list,zip(*(residual+source))));BI,ops=invert(B);assert mm(B,BI)==mm(BI,B)==identity
 project=[[sum(B[i][k]*BI[k][j] for k in range(4)) for j in range(20)] for i in range(20)]
 assert mm(project,project)==project and sum(project[i][i] for i in range(20))==4
 action=mm(project,B);assert action==[[B[i][j] if j<4 else 0 for j in range(20)] for i in range(20)]
 replay=[list(map(Q,row)) for row in B]
 for op,i,j,c in ops:
  if op=='swap':replay[i],replay[j]=replay[j],replay[i]
  elif op=='scale':replay[i]=[Q(c)*x for x in replay[i]]
  else:assert op=='add';replay[i]=[x+Q(c)*y for x,y in zip(replay[i],replay[j])]
 assert replay==identity
 nums=[abs(Q(c).numerator) for _,_,_,c in ops if c is not None];dens=[Q(c).denominator for _,_,_,c in ops if c is not None]+[x.denominator for row in BI for x in row]
 maxops=max(maxops,len(ops));maxnum=max(maxnum,*nums);maxden=max(maxden,*dens)
 charts.append({'frame':frame,'uses':count,'residual_rank':4,'basis_columns':residual+source,'inverse':[[str(x) for x in row] for row in BI],'factors':ops,'projector':[[str(x) for x in row] for row in project]})
assert len(charts)==120 and maxops<=400 and max(maxnum,maxden)<2**80
write('endpoint-charts.json.gz',{'charts':charts,'roles':roles,'gauge_frames':gauges})
# Two pure exact partitions. Every actual role x replica occurs once.
patterns=[{'widths':[4]*25,'count':2880},{'widths':[20]*5,'count':82800}];queues={width:iter([(r,t) for r in roles if widths[r]==width for t in range(60)]) for width in [4,20]};used=set();assign=bytearray();bank=0;norms=[];controls=[]
for pidx,p in enumerate(patterns):
 widths0=p['widths'];offsets=[];s=0
 for width in widths0:offsets.append(s);s+=width
 assert s==100
 def swaps(blocks):
  z=list(range(200))
  for o,width in blocks:
   for j in range(o,o+width):z[j],z[199-j]=z[199-j],z[j]
  return z
 blocks=list(zip(offsets,widths0));assert swaps(blocks)==list(range(199,-1,-1)) and swaps(blocks+blocks[::-1])==list(range(200))
 assert swaps(blocks[:-1])!=list(range(199,-1,-1));assert swaps(blocks+blocks[:1])!=list(range(199,-1,-1))
 controls+=['omitted_block_pattern_'+str(pidx),'duplicated_block_pattern_'+str(pidx)]
 for stage in range(5):
  permutation_programs=[]
  out=next(j for j in range(100) if not 20*stage<=j<20*(stage+1));witness=[]
  for block,(o,width) in enumerate(blocks):
   src=list(range(20*stage,20*stage+width));dest=list(range(o,o+width));pi=dict(zip(src+[j for j in range(100) if j not in src],dest+[j for j in range(100) if j not in dest]));assert sorted(pi.values())==list(range(100)) and [pi[j] for j in src]==dest
   scalar0=block+1;witness.append([pi[out],scalar0])
   images=list(range(100));sw=[]
   for original in range(100):
    current,target=images[original],pi[original]
    if current!=target:
     sw.append([current,target]);images=[target if v==current else current if v==target else v for v in images]
   assert images==[pi[j] for j in range(100)] and len(sw)<=99
   inverse_images=list(range(100))
   for i,j in reversed(sw):inverse_images=[j if v==i else i if v==j else v for v in inverse_images]
   assert all(inverse_images[pi[j]]==j for j in range(100))
   permutation_programs.append({'block':block,'chronological_coordinate_swaps':sw,'permutation':[pi[j] for j in range(100)]})
  assert len(set(map(tuple,witness)))==len(blocks);norms.append({'pattern':pidx,'stage':stage,'outside':out,'unit_column_witnesses':witness,'permutation_programs':permutation_programs})
 for _ in range(p['count']):
  replicas_in_bank=set()
  for block,(o,width) in enumerate(blocks):
   role,t=next(queues[width]);assert (role,t) not in used;used.add((role,t));assert t not in replicas_in_bank;replicas_in_bank.add(t)
   assign.extend(struct.pack('>6I',role,t,bank,o,width,block+1))
  bank+=1
assert bank==85680 and used=={(r,t) for r in roles for t in range(60)} and all(next(q,None)is None for q in queues.values())
(P/'literal-bank-assignments.bin.gz').write_bytes(gzip.compress(assign,mtime=0));rows=list(struct.iter_unpack('>6I',assign));digest=hashlib.sha256()
for stage in range(5):
 cover=bytearray(bank*100)
 for role,t,b,o,width,scale in rows:
  k=100*b+o;assert not any(cover[k:k+width]);cover[k:k+width]=b'\1'*width
  family=230400+stage*bank+b;assert 230400+stage*bank<=family<230400+(stage+1)*bank
  digest.update(struct.pack('>7I',stage,role,t,family,o,width,scale))
 assert cover.count(0)==0
S=230400+5*bank;E=sum(H.values());mass=sum(r*n for r,n in H.items());assert S==658800 and 100*S-mass==122400
# Every selector, route, ordinary scalar, recursive wrapper and matrix bill.
assert maxops<=150
factors=150+99+100;J=60*(24*960+10*8100);Kbill=2*5*60*((S-1)+8100*100*factors)
assert factors<=599 and Kbill<2**40
unit=60*(5*admit['literal_unit_additions']+6*960);weighted=60*(5*admit['weighted_additions']+6*960)
payload=64*admit['forward_norm']**3*admit['inverse_norm']**2;assert payload<2**104
terms={'unit_expanded_additions':unit,'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':Kbill,'constant':1};coefficient=sum(terms.values());assert coefficient<2**80
assert max(H)==42 and 2*max(H)<100 and S+20<2**80 and 6*200*199+3*200+6*199<320000
result={'status':'PASS_FRESH_LITERAL_BANKS_AND_FULL_INVOICE_CONDITIONAL_ON_RETAINED_FRAME_INVARIANT','source_admission_sha256':sha(A/'RESULT.json'),'base_ledger_sha256':sha(P/'BASE-LEDGER.json'),'selected_retimings':480,'source_histogram_from_actual_events':source_hist,'helper_histogram':helper,'literal_histogram':H,'literal_stock':S,'literal_children':E,'literal_rank_mass':mass,'deficit':122400,'physical_roles':len(roles),'inventory':Counter(widths.values()),'patterns':patterns,'banks_per_stage':bank,'completion_children':0,'actual_chart_count':len(charts),'chart_max_factors':maxops,'chart_billed_factor_bound':150,'chart_max_numerator':maxnum,'chart_max_denominator':maxden,'normalizer_factor_bound':factors,'normalizer_distinctness':norms,'zero_family_collisions_in_same_invocation':True,'assignment_count':5*len(rows),'assignment_sha256':hashlib.sha256(assign).hexdigest(),'five_stage_assignment_sha256':digest.hexdigest(),'all_coordinate_coverage':True,'bank_literal_universal_identity':'D_Q=[[I-Q,Q C100],[C100 Q,I-C100 Q C100]]; each disjoint coordinate block swaps exactly its paired coordinates, so product is D_I over Z and every coefficient ring. A common invertible ancestor conjugation preserves the identity.','weighted_additions':weighted,'unit_expanded_additions':unit,'forward_norm':admit['forward_norm'],'inverse_norm':admit['inverse_norm'],'payload_prefix_bound':payload,'payload_bits':payload.bit_length(),'route_families':J,'selector_calls':Kbill,'terms':terms,'coefficient':coefficient,'fallback_per_child':320000,'max_child_rank':42,'halving_degree':1,'row_reserve_coefficient':10001,'controls':controls,'artifacts':{n:sha(P/n) for n in ['endpoint-charts.json.gz','literal-bank-assignments.bin.gz']},'checker_sha256':sha(Path(__file__)),'scope':'Source retimings are hash-bound to fresh local admission. Fresh charts and every literal bank assignment/charge are checked here. Complete helper/target framed-word invariant and global IR binding remain separate gates; inherited compiler, prime, row, recovery and all-size analytic assumptions are unchanged.'}
write('BANK-RESULT.json',result);print(json.dumps({k:result[k] for k in ['status','literal_stock','literal_children','literal_rank_mass','chart_max_factors','normalizer_factor_bound','selector_calls','coefficient','payload_bits']},indent=2))
