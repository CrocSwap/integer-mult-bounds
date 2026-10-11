"""Isolated source-bound R822 B3 unsplit-idle construction. Apache-2.0.
Uses unchanged PR373 projectors, records, banks, native columns and route bill.
Changes paid idle decomposition; proves exact depth2 and doubles INTERNAL rows.
Prepared with OpenAI Codex assistance. Inherited conditional interfaces remain.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,importlib.util,json,os,subprocess,sys,time
assert __debug__
import argparse
ap=argparse.ArgumentParser();ap.add_argument('parent',type=Path);ap.add_argument('bit_replay',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
BASE=args.parent.resolve();CHECK=BASE/'code/bit/checkers';OLD=args.bit_replay.resolve();WORD=OLD/'word.json.gz';REC=OLD/'records';OUT=args.output.resolve();assert not OUT.exists() and OUT!=BASE and BASE not in OUT.parents;OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert sha(BASE/'MANIFEST.sha256')=='c945d6c1fa1a469ef73e48519921589926f7c7a9cf19eb51842255d2c0ef2d8e'
for line in (BASE/'MANIFEST.sha256').read_text().splitlines():
 digest,name=line.split(None,1);assert sha(BASE/name)==digest,name
parent_receipt=json.loads((OLD/'RECEIPT.json').read_text());assert parent_receipt['status']=='PASS_SOURCE_BOUND_CONDITIONAL_E8_HELPER_REUSE_AND_ASSEMBLY'
assert hashlib.sha256(gzip.decompress(WORD.read_bytes())).hexdigest()==parent_receipt['word_sha256']
assert {n:sha(REC/n)for n in parent_receipt['records']}==parent_receipt['records']
paths={**{'parent/'+str(p.relative_to(BASE)):p for p in [BASE/'MANIFEST.sha256',CHECK/'geometry_k.py',CHECK/'finite_k.py',CHECK/'tile_k.py',CHECK/'columns_k.cpp',BASE/'code/complex/code/bridged.py',BASE/'code/pricing/moment.py',BASE/'code/pricing/base_two_moment.py']},**{'bit/'+n:OLD/n for n in ['word.json.gz','records/249-records.bin','records/249-states.json','records/frames.json','cout/legality.json','columns-k3-r822','RECEIPT.json']}}
sources={label:sha(path)for label,path in paths.items()};dump(OUT/'SOURCES.json',sources)
sys.path.insert(0,str(CHECK));sys.path.insert(0,str(BASE/'code/complex/code'))
import cost as C,bridged
geo=load('geo_unsplit',CHECK/'geometry_k.py');sp=geo.sp
c=json.load(gzip.open(WORD,'rt'));assert (c['h'],c['v'],c['R'],len(c['ret']))==(8,120,822,9)
s,fr,d,rec=C.load_snapshot(str(REC));H,resid,v=C.local_profile(rec,s,d,h=8);lay=bridged.check(3,8)
prof=Counter({r:49*n for r,n in H.items()})
for r in lay['blocks_per_role_pair']:prof[r]+=1680
m=56;W=10794;T=7;rank=max(prof);assert rank==34 and m*m>2*rank*rank and m<=2*rank
assert sum(r*n for r,n in prof.items())==m*W-1512
moment=load('moment',BASE/'code/pricing/moment.py');other=load('other',BASE/'code/pricing/base_two_moment.py')
root=moment.certify(dict(prof),m,W,True);saving=Q(int(Q(root['lower'])*10**18),10**18);bounds=[]
for a in [saving,saving+Q(1,10**18)]:
 e1=moment.moment(prof,m,W,a,True);lo,hi=other.moment(m,W,list(prof.items()),a);fl,fh=other.moment(m,W,[(1,32*m*m*sum(prof.values()))],a);e2=[lo+Q(1,10**16)*fl,hi+Q(1,10**16)*fh]
 assert max(e1[1],e2[1])<1 if a==saving else min(e1[0],e2[0])>1
 bounds.append(dict(saving=str(a),engine1=list(map(str,e1)),engine2=list(map(str,e2))))
priced=dict(word=str(REC),K=3,stages=7,idle_blocks_per_role_pair=lay['blocks_per_role_pair'],h=8,T=T,maxchild=rank,bit_moment_interval=bounds[0]['engine1'],normalized_histogram=dict(prof),W=W,m=m,bit_coarse=str(saving),complex_coarse='999240641319551/1000000000000000000',bounds=bounds,halving_degree=2)
dump(OUT/'kappa-input.json',priced);print('PASS dual exact moment',saving,float(saving),flush=True)
# Exact rational construction: retain one full commuting projector gap per idle transition.
h=8;G=sp.eye(h)/2;L=[sp.Matrix(x)for x in c['lines']];ip=lambda a,b:(a.T*G*b)[0]
def refl(r):return sp.eye(h)-r*(r.T*G)*2/ip(r,r)
isom={0:(sp.eye(h),[])};frontier=[0]
while frontier:
 nxt=[]
 for a in frontier:
  for b in range(v):
   if b in isom or abs(ip(L[a],L[b]))!=1:continue
   z=L[a]-L[b]if ip(L[a],L[b])==1 else L[a]+L[b];isom[b]=(refl(z)*isom[a][0],isom[a][1]+[z]);nxt.append(b)
 frontier=nxt
assert len(isom)==120
GEO=geo.Geo(h,G,L[0],7);want=geo.expected(3,h);allports=[];start=time.monotonic();denoms=set();matrix_hash=hashlib.sha256();matrix_count=0
def dyadic(A,label):
 global matrix_count
 matrix_count+=1;matrix_hash.update((label+':'+str(A.shape)+';').encode())
 for i,x in enumerate(A):
  if not x:continue
  q=sp.Rational(x);d=int(q.q);assert d&(d-1)==0,('non-dyadic',label,d);denoms.add(d);matrix_hash.update((str(i)+':'+str(q)+';').encode())
# No intermediate Q is used: split=m is a threshold larger than every proper gap.
for t in range(v):
 g,word=isom[t];gi=g.inv();ranks,children=GEO.check_port(3,L[t],g,gi,m,L)
 dyadic(g,f'g{t}');dyadic(gi,f'ginv{t}');rho=[GEO.rho(j,g,gi)for j in range(7)]
 P=GEO.frame_projector(L[t].T);Ph={'P':P,'K':sp.eye(h)-P,'H':sp.eye(h),'0':sp.zeros(h)};data={}
 for j in range(7):
  dyadic(rho[j],f'rho{t}/{j}')
  for kind,F in Ph.items():
   endpoint=GEO.stage_projector(j,F);dyadic(endpoint,f'stage{t}/{j}/{kind}');data[j,kind]=rho[j]*endpoint*rho[j];dyadic(data[j,kind],f'data{t}/{j}/{kind}')
 pairs=[];I=sp.eye(m);Z=sp.zeros(m);p=data[0,'P']
 for q in (2,3):pairs.extend([(p,data[2*q-3,'H']),(Z,data[2*q-3,'K']),(data[2*q-2,'P'],data[2*q-1,'P']),(data[2*q-2,'0'],data[2*q-1,'0'])])
 pairs.extend([(data[2,'H'],I),(data[2,'K'],I-p)])
 for q in (2,3):pairs.extend([(data[2*q,'H'],I),(data[2*q,'K'],I-p)])
 for j,(a,b)in enumerate(pairs):
  gap=b-a;dyadic(gap,f'gap{t}/{j}');assert gap*gap==gap and gap.T*GEO.GG==GEO.GG*gap and int(gap.trace())==want[j]

 assert ranks==children==want and sorted(children)==sorted(lay['blocks_per_role_pair']*2)
 assert max(children)==34 and all(0<r<m for r in children)
 assert m*m>2*max(children)**2
 allports.append(dict(port=t,reflection_count=len(word),ranks=ranks))
 if t%30==0:print('geometry',t+1,120,round(time.monotonic()-start,1),flush=True)
assert {c['start'][r]for r in range(240,1062)}=={c['start'][120]} and len(c['frames'][c['start'][120]])==0
GEO.check_entrance(sp.zeros(h))
dump(OUT/'geometry.json',dict(status='PASS_EXACT_UNSPLIT_ALL_PORT_PROJECTORS',ports=allports,stage_boundaries=6,halving_degree=2,m=56,maxchild=34,matrix_count=matrix_count,matrix_sha256=matrix_hash.hexdigest(),computed_denominators=sorted(denoms),child_denominator_basis='All actual g,g^-1,rho,stage/data endpoints and full idle gaps checked entrywise; self-adjoint idempotent gaps checked exactly',entrance_zero_helpers=822,duplicate_window_rejected=True))
print('PASS unsplit exact geometry',flush=True)
def run(cmd,name):
 with (OUT/(name+'.log')).open('w')as f:subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT,check=True)
# Fresh native full1542-column check and12 omitted-bridge controls, same scalar word.
run([OLD/'columns-k3-r822',REC/'249-records.bin',OUT/'columns.json'],'columns')
cols=json.loads((OUT/'columns.json').read_text());assert cols['formal_columns_checked']==1542 and len(cols['negative_controls'])==12
cols.pop('seconds');cols.pop('local_scalar_stream');dump(OUT/'columns.json',cols)
run([sys.executable,'-B',CHECK/'tile_k.py',REC,3,8,7],'banks')
# Reconstruct the finite input from this run's histogram, immutable word/native evidence.
run([sys.executable,'-B',BASE/'code/bit/receipts_k.py',WORD,REC,OLD/'cout/legality.json',OUT/'columns.json',OUT/'kappa-input.json',OUT/'finite-input.json'],'finite-input')
# Auditable finite adapter. Keep the source route/invoice/normalizer/finite-cutoff checks.
# Replace only obsolete half-shrink guard, and explicitly charge least halving depth.
text=(CHECK/'finite_k.py').read_text();old='assert m==S*h and Q(max(literal),m)<Q(1,2)';new='assert m==S*h and 0<max(literal)<m\n    depth=1\n    while m**depth<=2*max(literal)**depth:depth+=1\n    assert depth==2 and m==56 and max(literal)==34'
assert text.count(old)==1;text=text.replace(old,new)
old="row_reserve=dict(internal_coefficient=d+1,external_complex_coefficient=20161)";new="row_reserve=dict(internal_coefficient=depth*(d+1),halving_degree=depth,per_level_coefficient=d+1,bound='6274*w*ceil(log2(max(2,n))) plus inherited ordinary-leaf reserve',restored=True,physical_stock_less_than_prime=True,external_complex_coefficient=20161)"
assert text.count(old)==1;text=text.replace(old,new)
# Preserve dependency resolution to unchanged source modules without mutating primary source.
text=text.replace('HERE=os.path.dirname(os.path.abspath(__file__))','HERE='+repr(str(CHECK)))
(OUT/'finite_unsplit.py').write_text(text)
run([sys.executable,'-B',OUT/'finite_unsplit.py','e8',OUT/'finite-input.json',OUT/'finite.json'],'finite')
f=json.loads((OUT/'finite.json').read_text());assert f['row_reserve']['internal_coefficient']==6274 and f['coefficient']<2**80
assert f['positive_rank_children']==sum(prof.values()) and f['rank_mass']==56*10794-1512
for label,digest in sources.items():assert sha(paths[label])==digest,label
controls={}
for name,valid in [('halving_degree_one',m>2*rank),('missing_internal_depth_charge',3137>=6274),('dropped_rank34_child',sum(r*n for r,n in prof.items())-34*1680==m*W-1512)]:assert not valid;controls[name]=True
result=dict(status='PASS_EXACT_R822_UNSPLIT_B3_BIT_CONSTRUCTION_FINITE',word_sha256=sha(WORD),records_sha256=sha(REC/'249-records.bin'),bit_coarse=str(saving),m=m,W=W,T=T,maxchild=rank,halving_degree=2,depth_check=[56**2,2*34**2],finite_coefficient=f['coefficient'],internal_row_coefficient=6274,geometry_sha256=sha(OUT/'geometry.json'),columns_sha256=sha(OUT/'columns.json'),finite_sha256=sha(OUT/'finite.json'),source_parent_manifest_sha256=sha(BASE/'MANIFEST.sha256'),arithmetic_sanity_controls=controls,scope='Conditional inherited PR373/370 generalized E8 bit geometry/compiler/9totals and completed ordinary restored-row interfaces. The degree2 row extension follows the pinned general restored-row argument; no new unconditional theorem or Lean build.')
dump(OUT/'RECEIPT.json',result);print(json.dumps(result,indent=2),flush=True)
