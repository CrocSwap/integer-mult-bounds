"""OpenAI Codex whole-owner cross-replica derivative of pinned PR484.
CLI: SOURCE484_PACKAGE VERIFIED_VARIANT COLORED_OWNERS.json.gz OUT
No optimizer or unpublished word builder runs. The frozen map explicitly names
one whole helper per family per complete invocation, plus borrowed spectators.
"""
import sys,json,gzip,hashlib,copy
from pathlib import Path
from collections import Counter,defaultdict
SOURCE,BASE,MAP,OUT=map(lambda p:Path(p).resolve(),sys.argv[1:5]);assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(SOURCE/'code'));import onehost_gk as OH
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
parent=read(BASE/'split-centres/GLOBAL-TEMPLATE.json.gz');t=copy.deepcopy(parent);canon=read(BASE/'split-centres/CANONICAL-WORD.json.gz');checks=read(BASE/'split-centres/LOCAL-CHECKS.json');ph=read(BASE/'work/complex-nine-native/DATA-PHASES.json');roles=read(MAP);DATA=7680;T=8;V=120;M=73;R=560
assert(len(roles),len(canon['start']),len(ph['recipes']))==(40320,800,120)
widths=[9-len(canon['frames'][canon['start'][240+h]])for h in range(R)];assert Counter(widths)==Counter({9:438,8:104,7:14,5:4})
rank={z['child']:z['rank']for z in parent['idle_children']};side={};pairs={}
for e in parent['execution_schedule']:
 if e['kind']=='idle_cover_sweep':
  for sd,ch in enumerate(e['child_indices']):side[ch]=sd;pairs[ch]=e['pair']
bycall=defaultdict(dict);used=defaultdict(set);sigmas={};digest=hashlib.sha256();entering=0
for z in roles:
 s,rep,h=z['stage'],z['replica'],z['helper'];i,cp,off,w,f=z['child'],z['copy'],z['offset'],z['width'],z['family'];orp,port=divmod(cp,V)
 assert 0<=s<9 and 0<=rep<T and 0<=h<R and w==widths[h] and 0<=orp<T
 assert f==orp*960+(2*pairs[i]+side[i])*120+port and pairs[i]!=max(0,(s-1)//2)
 assert(h not in bycall[s,rep])and off>=0 and off+w<=rank[i]
 B=OH.idle_basis(canon['ports'][port]);pending=list(map(int,ph['recipes'][port]['idle_children'][i]['orthogonal_axes']));assert len(pending)==rank[i]
 occ=[B.index(v)for v in pending[off:off+w]];sp=OH.spectators(canon['ports'][port],pending,off,w)if w<9 else[]
 order=occ+sp+[j for j in range(M)if j not in occ and j not in sp];assert len(order)==len(set(order))==M
 sigma=[B[j]for j in order];sigmahash=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigmas[sigmahash]=sigma
 route=[4,i,off,w,sp]if w<9 else[3,i,off];bycall[s,rep][h]=[f,route];entering+=w<9
 cells=set(range(off,off+w));assert not used[i,orp,port]&cells;used[i,orp,port]|=cells
 digest.update(json.dumps([s,rep,h,f,sigmahash],separators=(',',':')).encode()+b'\n')
for c in t['calls']:
 k=(c['stage'],c['replica']);assert set(bycall[k])==set(range(R))
 c['owners']=c['owners'][:240]+[bycall[k][h]for h in range(R)];assert len({f for f,r in c['owners']})==800 and all(f<DATA for f,r in c['owners'])
newidle=[];paid=Counter()
for c in t['calls']:
 for r,n in checks[c['orientation']]['paid_profile'].items():paid[int(r)]+=n
for old in parent['idle_children']:
 i,port=old['child'],old['port']
 for rep in range(T):
  u=used[i,rep,port];assert u==set(range(len(u)));left=old['rank']-len(u)
  if left:
   f=rep*960+(2*pairs[i]+side[i])*120+port;newidle.append(dict(child=i,port=port,replica=rep,replicas=1,family=f,rank=left,hosted=len(u),pending_offset=len(u)));paid[left]+=1
assert M*DATA-sum(r*n for r,n in paid.items())==2496
C=len(canon['centers']);physical=DATA+C+R+2
assert parent['physical']-parent['live']==C+R+2
# Local circuits, exact phase recipes, normalized wrappers and data routes stay
# byte-identical; only full-family helper placement and idle remainders change.
t.update(version='complex484-cross-replica-whole-owner-v1',live=DATA,physical=physical,idle_children=newidle,private_namespace={'centers':[DATA,DATA+C],'reserved_tableau':[DATA+C,DATA+C+R],'coefficient':[physical-2,physical]})
t['hosting']=dict(rule='one-helper-per-physical-family-per-complete-invocation',max_helpers_per_physical_family_per_call=1,scope='all eight physical data replicas pooled; each whole helper occurs once per(stage,invocation replica)',pooled_slots=roles,banks=[0]*9,owner_map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),idle_remainder_semantics='Each idle_children item acts once, on its explicit replica/family, at pending_offset with the stated rank; replicas=1.')
t['route_semantics']['helper']='Whole physical family may belong to another replica; actual orthogonal port basis followed by residual/spectator coordinate permutation. Entering helpers have paid wrappers around the complete invocation; at most one helper and no active data wire uses that family in that invocation. Route[4,child,offset,width,spectators], width9 route[3,child,offset].'
t['bank_padding']['families']=[];t['cover_final_correction']['families']=[0,DATA];t['cover_final_correction']['charged_calls_per_cover']=DATA
for e in t['execution_schedule']:
 if e['kind']=='bank_padding_cover_sweep':e['families']=[DATA,DATA]
 elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
assert t['loop_order']==parent['loop_order'] and 'each local invocation completes before the next' in t['loop_order']
assert t['local_programs']==parent['local_programs']
raw=json.dumps(t,sort_keys=True,separators=(',',':')).encode();(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
res=dict(status='EMITTED_CROSS_REPLICA_WHOLE_OWNER_COMPLEX_TEMPLATE',template_sha256=hashlib.sha256(raw).hexdigest(),parent_template_sha256=hashlib.sha256(gzip.decompress((BASE/'split-centres/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(),live=DATA,physical=physical,global_profile=dict(sorted(paid.items())),rank_mass=sum(r*n for r,n in paid.items()),deficit=2496,maxchild=max(paid),hosted_residuals=len(roles),banks_per_stage=[0]*9,entering_helper_roles=entering,unique_actual_73column_sigmas=len(sigmas),sigma_stream_sha256=digest.hexdigest(),cross_replica_helper_roles=sum(z['replica']!=z['owner_replica']for z in roles),source_artifacts={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [BASE/'split-centres/CANONICAL-WORD.json.gz',BASE/'split-centres/LOCAL-PROGRAMS.json.gz',BASE/'split-centres/LOCAL-CHECKS.json',BASE/'split-centres/RESIDUAL-ADAPTERS.json',BASE/'work/complex-nine-native/DATA-PHASES.json']},scope='New emitted complete-invocation placement; independent controller/spectator/normalization and complete finite invoice admission required.')
(OUT/'HOSTED.json').write_text(json.dumps(res,indent=2)+'\n');(OUT/'ACTUAL-SIGMAS.json.gz').write_bytes(gzip.compress(json.dumps(sigmas,separators=(',',':')).encode(),mtime=0));print(json.dumps(res,indent=2))
