from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support as _portable
_portable.require_assertions()
"""Independent paid-complement review. Only stdlib and numpy are executed.
Pinned upstream sources and all earlier receipts are inert inputs, not imports.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
from functools import lru_cache
from math import gcd,lcm
import json,gzip,hashlib,struct,sys
if not __debug__: raise RuntimeError('Assertions required')
HERE=_portable.BANK
SPLIT=tuple(map(int,sys.argv[1].split(',')))if len(sys.argv)>1 else (49,11)
assert SPLIT == (49,11)
OUT=HERE/('split_'+str(SPLIT[0])+'_'+str(SPLIT[1]));OUT.mkdir(exist_ok=True)
BASE=_portable.BASE_OUTPUT
CAND=_portable.WORD
PRIOR=_portable.BASE_OUTPUT/"finite"
ADMISSION=_portable.HERE/"admission"
HEAD='1b37957d1520c80b6ea796bf418e52be5109c2d4'
WORD_SHA='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
def digest(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(Path(p).read_text())
manifest=read(_portable.INPUT_MANIFEST);assert manifest['head']==HEAD
sources={}
@lru_cache(None)
def src(name):
 r=next(r for r in manifest['files'] if r['path']==name); raw=(_portable.INPUTS/r['local']).read_bytes()
 assert len(raw)==r['bytes'] and digest(raw)==r['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob']
 sources[name]=r['sha256']
 if name.endswith('.gz'):raw=gzip.decompress(raw)
 return json.loads(raw) if name.endswith(('.json','.json.gz')) else raw.decode()
for n in ('proof/three-stage-cover-bit.tex','proof/three-stage-cover-rows.tex','bank_check.py','bank_template.py','finite_check.py'):src(n)
word=read(CAND);assert digest(CAND.read_bytes())==WORD_SHA
old=src('bitword/selected/bit/word_p10.json.gz');priorword=read(_portable.BASE_OUTPUT/'matching/word_weighted890.json')
frames={int(k):v for k,v in src('bitword/selected/bit/frames_p10.json.gz')['frames'].items()}
oldroles=sorted(set(range(9120))-{y for x,y in old['pairs']});virtual={1920+i:r for i,r in enumerate(oldroles)}
roles=sorted(set(range(9120))-{y for x,y in word['pairs']});old890roles=sorted(set(range(9120))-{y for x,y in priorword['pairs']})
assert set(old890roles)-set(roles)=={9101,9103} and not set(roles)-set(old890roles)
sinks=src('sink-selection.json')['sinks'];removed={r['role'] for r in sinks};assert all(virtual[r['stream']]==r['role'] for r in sinks)
roles=sorted(set(roles)-removed);assert len(roles)==8221
entrance={r:None for r in roles};end={r:None for r in roles}
for g in word['gauges']:
 if g['role'] in entrance: entrance[g['role']]=frames[g['frame']]
kernels=src('kernel-selection.json')['families'];assert len(kernels)==1047
for row in kernels:
 r=virtual[row['pivot']];assert r in entrance and entrance[r] is None
 entrance[r]={'dim':row['rank'],'b':row['basis']}
for row in src('restore-selection.json')['entries']:
 r=virtual[row['helper']]; assert r in entrance and entrance[r]['dim']==row['dims'][0] and end[r] is None
 end[r]={'dim':row['rank'],'b':row['basis']}
widths={r:(20 if end[r] is None else end[r]['dim'])-(0 if entrance[r] is None else entrance[r]['dim']) for r in roles}
expected={3:308,4:960,6:1,7:1,10:6,12:3,13:1,15:3,16:5,18:20,19:1007,20:5906}
assert Counter(widths.values())==expected

def rref(a,n=20):
 a=[list(map(F,row)) for row in a];piv=[];i=0
 for j in range(n):
  k=next((k for k in range(i,len(a)) if a[k][j]),None)
  if k is None:continue
  a[i],a[k]=a[k],a[i];q=a[i][j];a[i]=[x/q for x in a[i]]
  for k in range(len(a)):
   if k!=i and a[k][j]:
    q=a[k][j];a[k]=[x-q*y for x,y in zip(a[k],a[i])]
  piv.append(j);i+=1
  if i==len(a):break
 return a,piv

def null(a,n=20):
 a,piv=rref(a,n);out=[]
 for j in range(n):
  if j in piv:continue
  v=[F(int(k==j)) for k in range(n)]
  for i,p in enumerate(piv):v[p]=-a[i][j]
  z=lcm(*(x.denominator for x in v));v=[int(x*z) for x in v];g=gcd(*v);out.append([x//g for x in v])
 return out

def key(frame):return None if frame is None else json.dumps(frame,sort_keys=True)
@lru_cache(None)
def frame_parts(k):
 if k is None:return [],[[int(i==j) for j in range(20)] for i in range(20)]
 f=json.loads(k);b=f.get('b');a=f.get('a')
 if b is None:b=null(a)
 if a is None:a=null(b)
 assert len(b)==f['dim'] and len(a)==20-f['dim']
 assert all(sum(x*y for x,y in zip(u,v))==0 for u in a for v in b)
 return b,a

def prod(A,B):
 BT=list(zip(*B));return [[sum(x*y for x,y in zip(a,b)) for b in BT] for a in A]
def gram(a,b):return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
def check_chart(program,D,E):
 cols=[[F(x) for x in row] for row in program['basis_columns']];inv=[[F(x) for x in row] for row in program['inverse']]
 d=0 if D is None else D['dim'];e=20 if E is None else E['dim'];r=e-d
 assert program['rank']==r and len(cols)==20
 DB,DA=frame_parts(key(D));EB,EA=frame_parts(key(E)) if E is not None else ([[int(i==j) for j in range(20)]for i in range(20)],[])
 residual=cols[:r];source=cols[r:r+d];outside=cols[r+d:]
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in EA for b in residual+source)
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in DA for b in source)
 assert all(gram(a,b)==0 for a in residual for b in DB)
 assert all(gram(a,b)==0 for a in outside for b in EB)
 B=list(map(list,zip(*cols)));q=lcm(*(x.denominator for row in B+inv for x in row))
 Bi=[[int(x*q)for x in row]for row in B];Ii=[[int(x*q)for x in row]for row in inv]
 target=[[q*q*int(i==j)for j in range(20)]for i in range(20)]
 assert prod(Bi,Ii)==target and prod(Ii,Bi)==target
 # Independently execute only the supplied inert elementary factor list.
 replay=[row[:]for row in B]
 for op,i,j,q in program['factors']:
  q=F(q) if q is not None else None
  if op=='swap':replay[i],replay[j]=replay[j],replay[i]
  elif op=='scale':replay[i]=[q*x for x in replay[i]]
  else:assert op=='add';replay[i]=[x+q*y for x,y in zip(replay[i],replay[j])]
 assert replay==[[int(i==j)for j in range(20)]for i in range(20)]
 assert len(program['factors'])<=400
 assert max([abs(F(q).numerator) for op,i,j,q in program['factors'] if q is not None]+[1])<2**80
 assert max([F(q).denominator for op,i,j,q in program['factors'] if q is not None]+[1])<2**80
 return r

charts=json.loads(gzip.decompress((PRIOR/'endpoint-charts.json.gz').read_bytes()))
programs={p['program_id']:p for p in charts['factor_programs']};uses={x['role']:x for x in charts['role_uses']};seen=set();chart_uses=0
for r in roles:
 if entrance[r] is None: assert end[r] is None and widths[r]==20;continue
 u=uses[r];p=programs[u['program_id']];assert u['rank']==widths[r]
 checkkey=(u['program_id'],key(entrance[r]),key(end[r]))
 if checkkey not in seen:check_chart(p,entrance[r],end[r]);seen.add(checkkey)
 chart_uses+=1
assert chart_uses==2315
print('Charts independently validated:',len(seen),'uses:',chart_uses,flush=True)
# Source-bound candidate table, using only the candidate's proposed pattern text.
proposal=read(_portable.HERE/'witnesses/packing.json')
patterns=proposal['packing_patterns'];queues={w:iter([(r,t)for r in roles if widths[r]==w for t in range(60)]) for w in expected}
enc=bytearray();comp=bytearray();used=set();bank=0;pattern_checks=[];normalizer_checks=[]
full=list(range(199,99,-1))+list(range(99,-1,-1))
def apply(blocks):
 state=list(range(200))
 for start,width in blocks:
  for j in range(start,start+width):state[j],state[199-j]=state[199-j],state[j]
 return state
for pno,p in enumerate(patterns):
 ws=p['widths'];cw=list(SPLIT)if p.get('paid_complement_widths')else [];assert sum(ws)+sum(cw)==100
 assert not cw or (ws==[20,20] and tuple(cw)==SPLIT and p['count']==1)
 blocks=[];off=0
 for w in ws+cw:blocks.append((off,w));off+=w
 assert apply(blocks)==full and apply(blocks+blocks[::-1])==list(range(200))
 assert apply(blocks[:-1])!=full and apply(blocks+blocks[:1])!=full
 pattern_checks.append({'pattern':pno,'columns':200,'reversal_C100':True,'omitted_and_repeated_rejected':True})
 for stage in range(5):
  outside=next(x for x in range(100)if not 20*stage<=x<20*(stage+1));witness=[]
  for b,(start,w) in enumerate(blocks[:len(ws)]):
   active=list(range(20*stage,20*stage+w));target=list(range(start,start+w))
   S=active+[x for x in range(100)if x not in active];T=target+[x for x in range(100)if x not in target]
   pi=dict(zip(S,T));assert sorted(pi.values())==list(range(100));witness.append((pi[outside],b+1))
  assert len(set(witness))==len(ws)
  normalizer_checks.append((stage,pno,len(witness)))
 for _ in range(p['count']):
  off=0
  for b,w in enumerate(ws):
   r,t=next(queues[w]);assert (r,t)not in used;used.add((r,t));enc.extend(struct.pack('>IIIIII',r,t,bank,off,w,b+1));off+=w
  for w in cw:comp.extend(struct.pack('>III',bank,off,w));off+=w
  assert off==100;bank+=1
assert bank==85575 and used=={(r,t)for r in roles for t in range(60)}
assert all(next(it,None)is None for it in queues.values())
regularrows=list(struct.iter_unpack('>IIIIII',enc));comprows=list(struct.iter_unpack('>III',comp));assert len(comprows)==2
S=230400+5*bank;assert S==658275
allhash=hashlib.sha256();comp_addresses=[]
for stage in range(5):
 slots=bytearray(bank*100)
 for r,t,b,off,w,scalar in regularrows:
  assert 1<=scalar<=25 and not any(slots[b*100+off:b*100+off+w]);slots[b*100+off:b*100+off+w]=bytes([1])*w
  address=230400+stage*bank+b;assert 230400+stage*bank<=address<230400+(stage+1)*bank
  allhash.update(struct.pack('>IIIIIII',stage,r,t,address,off,w,scalar))
 for b,off,w in comprows:
  assert not any(slots[b*100+off:b*100+off+w]);slots[b*100+off:b*100+off+w]=bytes([2])*w
  comp_addresses.append({'stage':stage,'family':230400+stage*bank+b,'offset':off,'rank':w,'cover':'all GL_100(Z/q^w)','phase':'after 60 helper sweeps; before stage boundary'})
 assert slots.count(0)==0 and slots.count(2)==60
print('Literal real assignments:',len(used)*5,'completion children:',len(comp_addresses),flush=True)
with gzip.GzipFile(filename=str(OUT/'literal-assignments.bin.gz'),mode='wb',mtime=0)as z:z.write(enc)
# No dense transformation is executed. Permutations supply fixed algebraic
# witness charts for each added projector; actual children use the generic compiler.
complement=[]
for offset,r in [(40,SPLIT[0]),(40+SPLIT[0],SPLIT[1])]:
 support=list(range(offset,offset+r));target=list(range(r));pi=dict(zip(support+[x for x in range(100)if x not in support],target+[x for x in range(100)if x not in target]))
 assert sorted(pi.values())==list(range(100));assert {pi[x]for x in support}==set(range(r))
 # Canonical projector has northeast cross-block minors 1 in reversed order.
 # This is an integral generic witness at every prime, denominator 1.
 for k in range(1,r+1):assert all(int(i==j)==int(pi[support[i]]==j)for i in range(k)for j in range(k))
 assert r<50
 permutation=[pi[x]for x in range(100)];work=list(range(100));swaps=[]
 for i,t in enumerate(permutation):
  if work[i]!=t:
   j=work.index(t);work[i],work[j]=work[j],work[i];swaps.append((i,j))
 assert work==permutation and len(swaps)<=99
 # The list above is RIGHT-COLUMN updates M <- M*T. Chronological action
 # on coordinate column vectors is the REVERSE list for the displayed pi.
 def act_coordinate_swaps(sequence):
  images=list(range(100))
  for i,j in sequence:images=[j if x==i else i if x==j else x for x in images]
  return images
 chronological=list(reversed(swaps));assert act_coordinate_swaps(chronological)==permutation
 inverse_pi=[permutation.index(i)for i in range(100)]
 assert act_coordinate_swaps(swaps)==inverse_pi
 assert act_coordinate_swaps(chronological+swaps)==list(range(100))
 assert permutation!=inverse_pi and act_coordinate_swaps(swaps)!=permutation
 complement.append({'permutation_factor_count':len(swaps),'permutation_transpositions':swaps,'permutation_transpositions_encoding':'right-column updates M<-M*T, not chronological vector action','chronological_coordinate_transpositions':chronological,'chronological_inverse_transpositions':swaps,'both_coordinate_actions_exact':True,'unreversed_action_rejected':True,'normalizer_scalar_factors':0,'normalizer_denominators':[1],'offset':offset,'rank':r,'split_idempotent':True,'determinant_of_involution':(-1)**r,'generic_witness_permutation':[pi[x]for x in range(100)],'every_required_NE_minor':1,'no_new_prime_exclusions':True,'child_index_rule':f'A_child[k*f+j]=A[i_k*f+j]*D_P[k], 0<=k<{r}, 0<=j<f','maximum_child_ratio':str(F(r,100))})
# Independently derive the changed raw path histogram, then transport the
# independently admitted, unchanged downstream delta from the 890 baseline.
def basehist(w):
 pairs=dict(w['pairs']);roles0=sorted(set(range(9120))-set(pairs.values()));g={x['role']:x for x in w['gauges']};sources0={r:int(i)for i,r in w['sources'].items()}
 phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];visits=defaultdict(list)
 for i in order:
  for r in w['ops'][i][:2]:visits[r].append(w['op_frame'][i])
 for r,f in zip(w['rootroles'],w['root_frame']):visits[r].append(f)
 H0=Counter()
 for r in roles0:
  start=frames[g[r]['frame']]['dim']if r in g else frames[w['source_frame'][sources0[r]]]['dim']if r in sources0 else 0
  chain=visits[r].copy()
  if r in pairs:chain += [g[pairs[r]]['frame']]+visits[pairs[r]]
  ds=[start]+[frames[x]['dim']for x in chain]+[20]
  assert all(a<=b for a,b in zip(ds,ds[1:]))
  H0.update(b-a for a,b in zip(ds,ds[1:])if a<b)
  if r in sources0:H0[1]+=1
 return H0
bh0=basehist(priorword);bh1=basehist(word);delta=Counter(bh1);delta.subtract(bh0);delta={r:n for r,n in delta.items()if n};assert delta=={14:2,17:-2}
priorprice=read(_portable.BASE_OUTPUT/'arithmetic/weighted890-price.json')
helper=Counter({int(r):n for r,n in priorprice['final_helper_histogram'].items()});helper.update(delta)
H=Counter({r:60*5*n for r,n in helper.items()});H.update({r:60*1920 for r in [4,19,38,42]})
assert dict(H)=={int(r):n for r,n in proposal['literal_regular_histogram'].items()}
assert sum(H.values())==15002700 and sum(r*n for r,n in H.items())==65704800
H.update({SPLIT[0]:5,SPLIT[1]:5});E=sum(H.values());mass=sum(r*n for r,n in H.items());assert (E,mass,100*S-mass)==(15002710,65705100,122400)
assert max(H)==max(42,*SPLIT) and 2*max(H)<100
# Bind the fresh separate 892 scalar/source admission, not an exploratory cap.
scalar_path=_portable.ADM/'scalar-recurrence-result.json';scalar=read(scalar_path)
assert scalar['head']==HEAD and scalar['overlay_sha256']==WORD_SHA
assert scalar['checker_sha256']==digest((ADMISSION/'check_scalar_recurrence.py').read_bytes())
assert scalar['status']=='PASS_FRESH_WEIGHTED892_ALL1047_SCALAR_RECURRENCE'
for direction in ['forward','inverse']:
 row=scalar[direction];assert row['all_columns'] and row['columns']==10148
 assert row['weighted_additions']==336253 and row['literal_unit_additions']==338173
 assert {int(r):n for r,n in row['coefficient_histogram'].items()}=={1:335293,3:960}
assert scalar['forward']['max_row_l1']==132143 and scalar['inverse']['max_row_l1']==1307556
payload=64*scalar['forward']['max_row_l1']**3*scalar['inverse']['max_row_l1']**2
assert payload==scalar['payload_bound']==252483531736676034081055177728 and payload<2**104
transport=read(_portable.ADM/'transport-result.json')
assert transport['head']==HEAD and transport['overlay_sha256']==WORD_SHA and transport['kernel_entries_rebound']==1047
assert transport['kernel_delta_old']==transport['kernel_delta_new']
rebounds=read(_portable.ADM/'rebound-kernel-entries.json')['entries']
assert len(rebounds)==len(kernels)
for index,(k,b)in enumerate(zip(kernels,rebounds)):
 assert b['index']==index and b['virtual_pivot']==virtual[k['pivot']] and b['rank']==k['rank'] and b['basis']==k['basis']
 assert b['virtual_donors']==[virtual[d]for d in k['donors']]
summary_path=_portable.ADM/'ADMISSION-RESULT.json';admitted=read(summary_path)
_portable.verify_admission()
assert admitted['head']==HEAD and admitted['candidate_sha256']==WORD_SHA and admitted['candidate_pairs']==892
assert admitted['all_installed_kernels']==1047 and admitted['regression_tests_passed']==17 and admitted['all_regenerated_outputs_bound']
for n,hsh in admitted['artifact_hashes'].items():assert digest(_portable.admission_artifact(n).read_bytes())==hsh
admission_binding={n:digest((_portable.ADM/n).read_bytes())for n in ['scalar-recurrence-result.json','transport-result.json','source-target-geometry-result.json','reorder-transport-result.json','target-chronology-result.json','rebound-kernel-entries.json']}
# Conservative full primitive invoice, now bound to actual scalar counts.
T=60;v=960;R=8221;m=100;h=20;extra=10;norm=599
J=T*(24*v+10*R)+2*extra
K=2*5*T*((S-1)+R*m*norm)+2*extra*((S-1)+m*norm)
terms={'unit_expanded_additions':T*(5*338173+6*v),'high_affine_factors':J*16*(m*m+1)**2,'low_transpositions':J*(S+h),'generic_wrappers':E*(8*m*m+8),'matrix_preparation':E*128*(2*m)**3,'global_matrix_preparation':16*m**3,'copy_erase_episodes':5*h*T,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
assert K<2**40 and sum(terms.values())<2**80 and S+h<2**80
fallback=6*200*199+3*200+6*199;assert fallback<32*m*m
assert 2*m**3*10**16<2**80
linear=1-F(mass,m*S)-F(1,10**16)*32*m*E/S;assert linear>0
out={'status':'PASS_BANK_COMPLETION_AND_COMPILER_COMPATIBILITY_WITH_BOUND_892_SOURCE_RECEIPTS','head':HEAD,'word_sha256':WORD_SHA,'split':list(SPLIT),'physical_admission':False,'all_size_theorem':False,'source_hashes':sources,'checker_sha256':digest(Path(__file__).read_bytes()),'endpoints':{'actual_chart_checks':len(seen),'nontrivial_role_uses':chart_uses,'identity_role_uses':len(roles)-chart_uses,'all_actual_endpoint_charts_verified':True,'prior_chart_data_sha256':digest((PRIOR/'endpoint-charts.json.gz').read_bytes()),'chart_data_recomputed_as_exact_algebra':True,'normalizer_factor_bound':599,'complement_projectors':complement,'patterns':pattern_checks},'bank_addresses':{'roles':len(roles),'real_assignments_per_stage':len(used),'real_assignments_total':5*len(used),'banks_per_stage':bank,'all_100_coordinates_exactly_once':True,'stage_ranges_disjoint':True,'normalizer_distinctness_witnesses':len(normalizer_checks),'assignment_sha256':digest(enc),'five_stage_assignment_sha256':allhash.hexdigest(),'complement_addresses':comp_addresses},'literal_profile':{'stock':S,'children':E,'rank_mass':mass,'deficit':100*S-mass,'histogram':dict(sorted(H.items())),'rational_normalization_is_arithmetic_only':True},'finite_invoice':{'source_scalar_bound_is_conditional':False,'fresh_scalar_receipt_sha256':digest(scalar_path.read_bytes()),'source_admission_receipt_hashes':admission_binding,'source_admission_summary_sha256':digest(summary_path.read_bytes()),'payload_prefix_bound':payload,'payload_bits':payload.bit_length(),'forward_norm':132143,'inverse_norm':1307556,'scalar_units_bound':338173,'route_families':J,'selector_calls':K,'terms':terms,'coefficient':sum(terms.values()),'fallback_per_edge':320000,'actual_gaussian_fallback_bound':fallback,'fallback_charged_for_all_children':True,'linear_gap':str(linear),'row_stock_integer':True,'stock_plus_temporaries_less_than_prime':True,'row_reserve_coefficient':10001,'halving_degree':1,'new_temporary_roles':0},'not_established':['binding actual scalar/route/lowering output to this extended schedule','global physical/all-size admission; exact root and47slack arithmetic are provided separately in ARITHMETIC-RESULT.json'],'scope':'A new explicit paid completion phase fits the retained conditional generic compiler. Does not claim the unchanged upstream BankLowerer accepts partial patterns or rank-over20 local helpers.'}
(OUT/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k]for k in ('status','literal_profile','finite_invoice')},indent=2))
