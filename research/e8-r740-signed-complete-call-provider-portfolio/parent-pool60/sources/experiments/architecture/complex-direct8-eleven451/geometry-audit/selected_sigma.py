"""All actual direct8 m89 whole-host selectors, phases and owner injection."""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib
O=Path(__file__).resolve().parent;B=O.parent;P=B/'split-centres';H=B/'hosted'
load=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=load(H/'GLOBAL-TEMPLATE.json.gz');old=load(P/'GLOBAL-TEMPLATE.json.gz');ph=load(H/'DATA-PHASES.json');M=89
assert t['local_programs']==old['local_programs'] and t['m']==M and len(t['calls'])==88
idle={e['idx']:e for e in t['execution_schedule'] if e['kind']=='idle'}
dot=lambda x,y:(x&y).bit_count()%2
orth=lambda b:len(b)==M and all(dot(x,y)==int(i==j) for i,x in enumerate(b) for j,y in enumerate(b))
base={}
for r in ph['recipes']:
 b=[r['q']]+r['idle_children'][0]['orthogonal_axes'][:8]+[1<<i for i in range(9,M)]
 assert orth(b);base[r['port']]=b
used=defaultdict(list);seen=defaultdict(set);lookup={};routes=[]
for child,copy,off,w,s,h in t['hosting']['slots']:
 assert w==9;side,port=divmod(copy,120);e=idle[child];pi=e['phase_children'][side];recipe=ph['recipes'][port]['idle_children'][pi];axes=recipe['orthogonal_axes'];sel=axes[off:off+w]
 assert len(sel)==w and not set(sel)&set(used[child,copy]);used[child,copy]+=sel
 b=sel+[x for x in base[port] if x not in sel];assert orth(b)
 family=(s,e['pair'],side,port);assert tuple(b) not in seen[family];seen[family].add(tuple(b))
 assert (s,h)not in lookup;lookup[s,h]=(child,copy,off,w,b)
 routes.append([child,copy,off,w,s,h,b,recipe['translation_after']])
assert len(lookup)==6160
phasechecks=0
for e in t['idle_children']:
 child=e['idle'];copy=e['side']*120+e['port'];r=ph['recipes'][e['port']]['idle_children'][e['phase_child']];allaxes=r['orthogonal_axes'];taken=used[child,copy];rest=[x for x in allaxes if x not in taken]
 assert Counter(allaxes)==Counter(taken)+Counter(rest)
 assert len(rest)==e['rank'] and e['translation_after']==r['translation_after'];phasechecks+=1
for c in t['calls']:
 assert c['orientation']==('backward' if c['stage']%2 else 'forward')
 for h,(family,route) in enumerate(c['owners'][240:]):
  child,copy,off,w,b=lookup[c['stage'],h];side,port=divmod(copy,120);pair=idle[child]['pair']
  assert pair!=c['pair'];assert route==[3,child,off,w]
  assert family==c['replica']*1200+(2*pair+side)*120+port
r={'status':'PASS_ACTUAL_DIRECT8_ELEVEN_ALL_89_COLUMN_HOSTED_SIGMA_PHASE_OWNER_INJECTION','slots_per_replica':6160,'physical_slot_instances':49280,'all_sigma_columns':89,'sigma_orthogonality_and_inverse':'All89 column dot products exact; inverse transpose. Source local canonical9 helper endpoint retained; no cross-copy splitting.','full_character_phase_identity':'Exact multiset C_axis hosted+remainder equals originalchild, unchanged translation_after. Equality of Z4 Fourier multipliers on all2^89 characters, fixes globalphase since allfactorsfixuniformvector.','idle_phase_instances':phasechecks,'cover_injection':'Concrete sigma89 columns distinct within same stage/datafamily. Rightaction d*sigma^-1 bijective onO89 and distinct atfixedcoverd. All dataowners activepair, hostowners idleotherpair. Replicas/families disjoint.','reflection_inverse':'Sameselectedorthogonals invert bytranspose; exactinverse C_axis polynomials andtranslation persist under reversedchronology. Bothunchangedlocalorientations source800-column signedtheorem independently retained.','route_charge_requirement':'Retain allsourcecanonicalhelperchart factors; add actualorthogonal targetbasis/placement perhelper with paidphase/terminal/all-livecovercorrection. Finite factorbounds/primitive decomposition belongseparateinvoice gate, not inferredfreefromorthogonality.','sources':{str(p.relative_to(B)):sha(p) for p in [H/'GLOBAL-TEMPLATE.json.gz',H/'DATA-PHASES.json',P/'GLOBAL-TEMPLATE.json.gz',P/'LOCAL-CHECKS.json',P/'CLIFFORD-RECIPES.json']},'routes':routes,'scope':'Actualselectedwholehelper geometry/phase/owner and unchangedsignedlocalprogram binding; inheritedcompressedstream/Clifford/commongrid/compiler assumptions remainconditional. Thisdoesnotreplace literalallsizecompiler or finiteinvoice.'}
(O/'HOSTED-SIGMA.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(routes),phasechecks)
