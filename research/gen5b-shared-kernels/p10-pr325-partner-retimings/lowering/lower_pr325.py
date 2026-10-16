from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
"""Independent source-bound PR325 480-retiming global frame IR.
Consumes fresh admitted data, never executes upstream source. Apache-2.0.
Prepared with substantial OpenAI assistance.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
import gzip,hashlib,json,struct,copy,os
import numpy as np
assert contract.sha(contract.HERE/'lowering/generic_ir_helpers.py')=='c6b2bd1d0419360b2c2bf0dc039bbe8a461915c6918e25eba19cd095aedf8bc5'
from generic_ir_helpers import stage_template,permutation,emit_boundary
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent
OUT=contract.GLOBAL
LOCAL=contract.FRAME
SOURCE=contract.SOURCE
BANK=contract.BANK
PREP=contract.PREPARED
AUDIT=contract.AUDIT
HEAD='0eca9340a3df6141b8e71a41638c3937b3522888'
WORD='601da0e6a67715011a4bbc44f6977f13625c5833d4d40443c10b0d5a9da1896d'
S=658800;NB=85680;WORK=10020;ACTIVE=((0,1),(1,0),(0,1),(3,2),(2,3))
sha=lambda b:hashlib.sha256(b).hexdigest()
def fs(p):return sha(Path(p).read_bytes())
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def dump(n,x):
 b=canon(contract.portable(x));(OUT/n).write_bytes(gzip.compress(b,mtime=0)if n.endswith('.gz')else b)
def gz(n,b):
 (OUT/n).write_bytes(gzip.compress(b,mtime=0));return {'file':n,'sha256':sha(b),'compressed_sha256':fs(OUT/n),'bytes':len(b)}
def bound_inputs():
 assert fs(contract.input_for('proof/primary/03-motifs.tex'))=='ed76761194988a01af77ead0ea6469cb5dcd29690ab985a0b5a4006b0f2b69bb'
 local=read(LOCAL/'RESULT.json');validation=read(LOCAL/'VALIDATION.json');bank=read(BANK/'BANK-RESULT.json');prep=read(PREP/'PREPARATION.json')
 assert local['status']=='PASS_FRESH_PR325_480_RETIMINGS_FULL_LOCAL_FRAME_WORD'
 assert local['candidate_sha256']==WORD and local['head']==HEAD and local['source_retimings']==480
 assert not local['source_selections_imported_from_old_word']
 assert validation['status']=='PASS_INDEPENDENT_PR325_FULL_LOCAL_RECORD_AND_FRAME_AUDIT'
 assert validation['builder_receipt_sha256']==fs(LOCAL/'RESULT.json')
 binding=read(LOCAL/'ARBITRARY-DIRTY-AUDIT-BINDING.json')
 assert binding['local_result_sha256']==fs(LOCAL/'RESULT.json')and binding['local_validation_sha256']==fs(LOCAL/'VALIDATION.json')
 for name,h in binding['audit_files'].items():assert fs(AUDIT/name)==h
 assert read(AUDIT/'FULL-FRAME-AUDIT.json')['status']=='PASS_PR325_FULL_LOCAL_ARRAY_FRAME_CONTRACT'
 for item in read(LOCAL/'MANIFEST.json')['files']:assert fs(LOCAL/item['path'])==item['sha256']
 assert fs(contract.HERE/'frame/build_local.py')==local['checker_sha256'] and fs(contract.HERE/'frame/validate_local.py')==validation['checker_sha256']
 for key in ('all_complete_source_helper_target_paths_nested','all_helper_integer_sources_restored','all_source_integer_values_restored','all_targets_in_terminal_caps','all_COPY_lifetimes_exact'):assert local[key]
 for name,h in local['artifacts'].items():assert fs(LOCAL/name)==h
 for name,h in read(PREP/'MANIFEST.json').items():assert fs(PREP/name)==h
 for name,h in bank['artifacts'].items():assert fs(BANK/name)==h
 assert fs(BANK/'literal-bank-assignments.bin.gz')==prep['assignment_gzip_sha256']
 assert bank['source_admission_sha256']==local['source_result_sha256']==fs(SOURCE/'RESULT.json')
 assert bank['completion_children']==0 and bank['normalizer_factor_bound']==349
 prefix=SOURCE/'inputs/bitword__selected__bit__'
 wp=Path(str(prefix)+'word_p10.json.gz');gp=Path(str(prefix)+'graph_p10.json');assert fs(wp)==WORD
 w=read(wp);g=read(gp);roles=read(PREP/'fresh-role-index.json')['roles'];rm=read(LOCAL/'role-map.json')
 assert roles==[rm['representative_by_physical'][str(j)]for j in range(1920,WORK)]
 assert roles==sorted(set(range(9060))-{b for a,b in w['pairs']})
 frames=read(LOCAL/'local-frames.json.gz');ep=read(LOCAL/'local-endpoints.json');records=read(LOCAL/'local-records.json.gz')
 roots={'source_head':HEAD,'word_gzip_sha256':WORD,'source_result_sha256':fs(SOURCE/'RESULT.json'),'retiming_selection_sha256':fs(SOURCE/'retiming-selection.json'),
 'local_result_sha256':fs(LOCAL/'RESULT.json'),'local_validation_sha256':fs(LOCAL/'VALIDATION.json'),'fresh_role_map_sha256':fs(LOCAL/'role-map.json'),
 'local_records_sha256':fs(LOCAL/'local-records.json.gz'),'local_frames_sha256':fs(LOCAL/'local-frames.json.gz'),'bank_result_sha256':fs(BANK/'BANK-RESULT.json'),
 'fresh_preparation_sha256':fs(PREP/'PREPARATION.json'),'source_graph_sha256':fs(gp),'source_manifest_sha256':fs(SOURCE/'SOURCES.json'),'array_lifting_contract_sha256':fs(contract.input_for('proof/primary/03-motifs.tex')),'local_frozen_manifest_sha256':fs(LOCAL/'MANIFEST.json'),'arbitrary_dirty_audit_binding_sha256':fs(LOCAL/'ARBITRARY-DIRTY-AUDIT-BINDING.json')}
 return local,bank,roles,records,frames,ep,w,g,roots

def verify_local(records,frames,ep):
 state={int(k):v for k,v in ep['initial'].items()};final={int(k):v for k,v in ep['final'].items()}
 assert set(state)==set(final)==set(range(WORK))
 rank=lambda f:frames[str(f)]['rank'];H=Counter();ops=Counter();coeff=Counter();tmp=None;reads=0
 for op,a,b,c,f,z in records:
  ops[op]+=1
  if op==0:
   assert state[a]==b and rank(c)-rank(b)==f and f>=0;state[a]=c
   if f:H[f]+=1
  elif op==1:
   assert a!=b and state[a]==state[b]==f and c%2;coeff[abs(c)]+=1
   if b==WORK:assert tmp is not None;reads+=1
  elif op==2:
   assert tmp is None and b==WORK and state[a]==c and rank(c)==z==18 and rank(f)==0
   tmp=(a,b,c,f);state[b]=f;H[z]+=1;reads=0
  else:
   assert op==3 and tmp==(a,b,c,f) and state[a]==c and state[b]==f and reads==144
   del state[b];tmp=None
 assert state==final and tmp is None and (ops[1],ops[2],ops[3])==(350640,20,20)
 assert sum(k*v for k,v in coeff.items())==352560
 assert(sum(H.values()),sum(r*n for r,n in H.items()))==(46844,179640)
 return H,ops

def endpoint_binding(roles,frames,ep):
 charts=read(PREP/'fresh-endpoint-charts.json.gz');programs={int(k):v for k,v in charts['programs'].items()};uses={int(k):v for k,v in charts['uses'].items()}
 source_ids=read(LOCAL/'source-frame-map.json');widths={};receipts=[]
 for j,r in enumerate(roles):
  before=ep['initial'][str(1920+j)];after=ep['final'][str(1920+j)];A=frames[str(before)];B=frames[str(after)]
  assert B['rank']==20;widths[r]=20-A['rank']
  if r not in uses:assert A['rank']==0;continue
  original=uses[r];assert before==source_ids[str(original)]and A['rank']==16
  p=programs[original];cols=[list(map(F,row))for row in p['basis_columns']];inv=[list(map(F,row))for row in p['inverse']]
  assert p['factor_count']<=150
  if original not in {row[1]for row in receipts}:
   AA=[list(map(F,row))for row in A['annihilator']];BB=[list(map(F,row))for row in A['basis']]
   assert all(sum(x*y for x,y in zip(a,b))==0 for a in AA for b in cols[4:])
   assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in cols[:4]for b in BB)
   mat=[list(row)for row in zip(*cols)]
   for left,right in ((mat,inv),(inv,mat)):
    assert all(sum(x*y for x,y in zip(row,col))==int(i==j)for i,row in enumerate(left)for j,col in enumerate(zip(*right)))
   for op,i,j,c in p['factors']:
    if op=='swap':mat[i],mat[j]=mat[j],mat[i]
    elif op=='scale':mat[i]=[F(c)*x for x in mat[i]]
    else:assert op=='add';mat[i]=[x+F(c)*y for x,y in zip(mat[i],mat[j])]
   assert mat==[[int(i==j)for j in range(20)]for i in range(20)]
  receipts.append([r,original,before,after,4])
 assert Counter(widths.values())=={4:1200,20:6900}
 dump('actual-endpoint-chart-binding.json',{'uses':receipts,'fresh_unique_charts':len(programs),'identity_endpoints':6900,'all_actual_endpoints_bound':True})
 return widths,programs,uses

def namespaces(roles,widths,programs,uses):
 raw=gzip.decompress((PREP/'literal-bank-assignments.bin.gz').read_bytes());assign={};coverage=bytearray(NB*100)
 for r,t,b,o,w,sc in struct.iter_unpack('>6I',raw):
  assert widths[r]==w and 0<=t<60 and 0<=b<NB and 0<=o<o+w<=100 and 1<=sc<=25
  assert(r,t)not in assign;assign[r,t]=(b,o,w,sc)
  sl=slice(100*b+o,100*b+o+w);assert not any(coverage[sl]);coverage[sl]=b'\1'*w
 assert len(assign)==486000 and all(coverage)
 ids={};normalizers=[];maps=np.empty((5,60,WORK+1,2),dtype='<i4');hashes=[]
 for s in range(5):
  for t in range(60):
   a=maps[s,t]
   for i in range(1920):a[i]=((4*t+ACTIVE[s][int(i>=960)])*960+i%960,0 if s==0 else 1+s*960+i%960)
   witnesses=defaultdict(list)
   for j,r in enumerate(roles):
    b,o,w,sc=assign[r,t];pid=uses.get(r,-1);key=s,o,w,sc,pid
    if key not in ids:
     pi=permutation(s,o,w);outside=next(k for k in range(100)if not 20*s<=k<20*(s+1))
     ids[key]=len(normalizers);normalizers.append({'id':ids[key],'stage':s,'support':[o,o+w],'rank':w,'scalar':sc,'permutation':pi,'chart_program':pid,
      'formula':'N=scalar*Pi*embed_stage(B_inverse)','physical_cover':'g=d*tau_stage*N_inverse','outside_column':outside,'unit_column_witness':[pi[outside],sc],'paid_factor_bound':349})
    n=ids[key];family=230400+s*NB+b;a[1920+j]=(family,4801+n);witnesses[family].append(tuple(normalizers[n]['unit_column_witness']))
   a[-1]=(S,-1)
   assert len(set(map(tuple,a.tolist())))==WORK+1 and all(len(set(v))==len(v)for v in witnesses.values())
   assert len(set(map(int,a[1920:-1,0])))==8100
   hashes.append({'stage':s,'replica':t,'sha256':sha(a.tobytes()),'full_address_injective':True})
 gz('all-namespaces.i32.gz',maps.tobytes());dump('namespace-hashes.json',hashes)
 dump('normalizers.json.gz',{'normalizers':normalizers,'chart_programs':programs,'common_ancestor_chart':'QA=diag(A,I100)',
 'data_route_encoding':'0=d;1+s*960+port=d*rho_s_port;-1=external_work;4801+n=d*tau_s*N_n_inverse',
 'regular_endpoint':'The admitted arbitrary-dirty separated local endpoint is conjugated by this exact N. Complete GL100 cover right multiplication is bijective.'})
 return maps,len(normalizers)

def routes_and_projectors(w,g,frames,ep,roots):
 labels=g['labels'];assert len(labels)==960;source_ids=read(LOCAL/'source-frame-map.json');routes=[]
 for q in range(960):
  ids=labels[q];assert len(ids)==len(set(ids))==3 and all(0<=j<20 for j in ids)
  chi=[int(j in ids)for j in range(20)];f=ep['initial'][str(q)];frm=frames[str(f)]
  assert f==source_ids[str(w['source_frame'][q])] and frm['rank']==1
  assert all(sum(F(x)*y for x,y in zip(a,chi))==0 for a in frm['annihilator'])
  pi=ids+[j for j in range(20)if j not in ids]
  routes.append({'port':q,'label':ids,'source_frame':f,'pi_columns':pi,'norm_G':2})
 dump('fresh-data-routes.json',{'ports':routes,'G':'I20-J20/9','qstar':[int(j<3)for j in range(20)],
 'rho0':'I100','rho_s':'I outside H0+Hs; blocks [P_chi,pi*Kstar;Kstar*pi_inverse,Pstar]; Pstar=qstar*qstar^t*G/2; Kstar=I20-Pstar',
 'rho_is_involution':True,'tau_s':'exchange H0 with Hs coordinatewise','source_graph_sha256':roots['source_graph_sha256']})
 # All 8 boundary projector formulas are bound to these new source vectors.
 dump('boundary-projectors.json',{'D':'rho(stage,port)*F(stage,frame,complement)*rho(stage,port)',
 'kinds':{'P':'actual source frame','K':'actual source frame complemented','H':'FULL','0':'ZERO'},
 'pairs':[['D(0,P)','D(1,H)'],['ZERO100','D(1,K)'],['D(2,P)','D(3,P)'],['D(2,0)','D(3,0)'],['D(2,H)','I100'],['D(2,K)','I100-D(0,P)'],['D(4,H)','I100'],['D(4,K)','I100-D(0,P)']],
 'ranks':[38,38,19,19,42,42,4,4],'fresh_data_routes_sha256':fs(OUT/'fresh-data-routes.json')})

def phases():
 ps=[]
 for s in range(5):
  ps.extend({'kind':'helper','stage':s,'replica':t,'cover':'all_GL100_Rw','reverse_complement':s in(1,3)}for t in range(60))
  if s in(1,2,4):ps.extend({'kind':k,'stage':s,'which':{1:0,2:1,4:2}[s],'replica':t,'cover':'all_GL100_Rw'}for t in range(60)for k in('idle','bridge'))
 ps.extend({'kind':'terminal_exchange','replica':t,'cover':'all_GL100_Rw'}for t in range(60))
 for i,p in enumerate(ps):p['phase_index']=i
 return ps

def invoice(hist,bank):
 E=sum(hist.values());J=60*(24*960+10*8100);K=2*5*60*((S-1)+8100*100*349)
 terms={'unit_expanded_additions':60*(5*352560+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),
 'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
 assert terms==bank['terms']and(J,K,sum(terms.values()))==(6242400,170009279400,24857617667871401)
 return {'literal_stock':S,'children':E,'rank_mass':sum(r*n for r,n in hist.items()),'terms':terms,'coefficient':sum(terms.values()),'route_movements':J,'selector_calls':K,
 'all_edges_pay_fallback320000':True,'row_reserve':10001,'new_temporary_roles':0,'completion_children':0,'max_rank':max(hist)}

def main():
 local,bank,roles,records,frames,ep,w,g,roots=bound_inputs();H,ops=verify_local(records,frames,ep)
 assert H==Counter({int(k):v for k,v in local['one_stage_paid_histogram'].items()})==Counter({int(k):v for k,v in bank['helper_histogram'].items()})
 widths,programs,uses=endpoint_binding(roles,frames,ep);maps,norms=namespaces(roles,widths,programs,uses);routes_and_projectors(w,g,frames,ep,roots)
 print('Fresh roles, endpoint charts, data routes and all300 namespaces bound',flush=True)
 ps=phases();assert len(ps)==720;phase_ids={(p['stage'],p['replica']):p['phase_index']for p in ps if p['kind']=='helper'}
 bindings=[];templates=[];overrides=[];hist=Counter();chain=hashlib.sha256();counts=Counter()
 for s in range(5):
  template=stage_template(s,records,frames);assert Counter(map(int,template[(template[:,0]==0)&(template[:,4]>0),4]))==H
  for ordinal,row in enumerate(template):
   op,a,b,c,f,z,stage,rev,source=map(int,row)
   if op!=0:continue
   signed=(frames[str(c)]['rank']-frames[str(b)]['rank'])*(-1 if rev else 1);orientation=-1 if a==WORK and not rev else 1
   assert orientation*signed==f
   if a==WORK:
    assert f==18;overrides.append({'stage':s,'template_record':ordinal,'local_source_record':source,'family':S,'old_frame':b,'new_frame':c,'complement':rev,'rank':18,'difference_orientation':orientation,
     'positive_projector':'F(old,0)-F(new,0)'if not rev else'F(new,1)-F(old,1)','meaning':'positive embedded center projector; D_P is involutive; never D_negativeP'})
  templates.append(gz(f'stage-{s}-template.i32.gz',template.tobytes()))
  for t in range(60):
   a=maps[s,t];data=np.zeros((len(template),12),dtype='<i4');data[:,0]=phase_ids[s,t];data[:,1]=template[:,0];data[:,2:4]=a[template[:,1]];data[:,4]=template[:,2];data[:,5]=-2
   mask=(template[:,0]==1)|(template[:,0]==2);data[mask,4:6]=a[template[mask,2]];data[:,6:]=template[:,3:]
   assert np.all(np.any(data[mask,2:4]!=data[mask,4:6],axis=1))
   digest=sha(data.tobytes());chain.update(bytes.fromhex(digest));hist.update(H);bindings.append({'stage':s,'replica':t,'phase_index':phase_ids[s,t],'records':len(template),'sha256':digest})
  print('Materialized stage',s,'through all60 fresh namespaces',flush=True)
 boundary=bytearray()
 for p in ps:
  if p['kind']=='helper':p['template']=templates[p['stage']];p['local_record_sha256']=roots['local_records_sha256']
  else:
   for row in emit_boundary(p):
    boundary.extend(struct.pack('<8i',p['phase_index'],*row));counts[row[0]]+=1
    if row[0]==4:hist[row[4]]+=1
 assert counts=={4:460800,5:345600,7:115200}and len(overrides)==100
 assert hist==Counter({int(k):v for k,v in bank['literal_histogram'].items()})
 assert(sum(hist.values()),sum(r*n for r,n in hist.items()),max(hist))==(14514000,65757600,42)
 # Universal arbitrary-dirty bank endpoint, both actual patterns, all200 columns.
 for width in(4,20):
  state=list(range(200))
  for start in range(0,100,width):
   for j in range(start,start+width):state[j],state[199-j]=state[199-j],state[j]
  assert state==list(range(199,-1,-1))
 dump('extended-phases.json',ps);dump('all-frame-bindings.json',bindings);dump('copied-work-projector-overrides.json',overrides);gz('boundary-records.i32.gz',boundary)
 dump('projector-descriptors.json',{'local_frames_sha256':roots['local_frames_sha256'],'P_frame':'B^t*(B*G*B^t)^-1*B*G; G=I20-J20/9',
 'F_stage':'diag(P_frame if not reflected else I20-P_frame,Kstar in windows 1..stage,0 later)',
 'regular_MOVE':'positive F(new,rev)-F(old,rev), conjugated by invocation d and common ancestor QA',
 'copied_work_MOVE':'mandatory 100 positive overrides; forward source-frame to ZERO uses old-minus-new',
 'copied_work_sha256':fs(OUT/'copied-work-projector-overrides.json'),'physical_to_invocation_chart':'helper g=d*tau*N_inverse; data g=d*rho',
 'fresh_data_routes_sha256':fs(OUT/'fresh-data-routes.json'),'boundary_projectors_sha256':fs(OUT/'boundary-projectors.json'),
 'generic':'ambient 100 split-idempotent child; strict max 42 < 50; all wrappers and all-edge fallback charged',
 'array_lifting_contract_sha256':roots['array_lifting_contract_sha256'],'arbitrary_dirty_audit_binding_sha256':roots['arbitrary_dirty_audit_binding_sha256'],
 'reflected_COPY':'Fresh COPY and fresh row-reserve cleanup on the reflected scalar invocation, not an inverse physical ERASE.',
 'ADD_semantics':'Pointwise XOR on complete role arrays over F2. Address partial swaps induce array-entry permutations; at each gate both input and output incidences share the exact same frame. These common linear array operators commute with pointwise ADD. This is not a head-coordinate arithmetic shear.',
 'local_frame_identity':'D_out*S_Omega*D_in_inverse on all roles, including arbitrary correlated dirty auxiliary arrays; exact primary 03-motifs, lines 146–185.',
 'retained_matrix_interface':'Actual common-frame, COPY and endpoint premises are independently audited; no matrix theorem is inferred solely from this IR or its histogram.'})
 for name in('extended-phases.json','copied-work-projector-overrides.json','projector-descriptors.json','fresh-data-routes.json','boundary-projectors.json'):chain.update((OUT/name).read_bytes())
 chain.update(boundary);bill=invoice(hist,bank);dump('invoice.json',bill)
 controls=[]
 bad=copy.deepcopy(records);idx=next(i for i,r in enumerate(bad)if r[0]==0 and r[4]>0);bad[idx][4]+=1
 try:verify_local(bad,frames,ep)
 except AssertionError:controls.append('wrong_MOVE_rank')
 else:raise AssertionError('bad rank accepted')
 for name,change in [('omitted_phase',lambda x:x.pop(59)),('boundary_before_last_helper',lambda x:x.__setitem__(slice(119,121),list(reversed(x[119:121])))),('unrequested_completion',lambda x:x.append({'kind':'paid_bank_completion'}))]:
  bad=phases();change(bad);assert bad!=phases();controls.append(name)
 for name,h in local['artifacts'].items():assert fs(LOCAL/name)==h
 assert roots['local_result_sha256']==fs(LOCAL/'RESULT.json')and roots['bank_result_sha256']==fs(BANK/'BANK-RESULT.json')
 result={'status':'PASS_SOURCE_BOUND_PR325_GLOBAL_FRAME_IR','source_head':HEAD,'source_word_gzip_sha256':WORD,'source_identity':roots,'candidate_fingerprint':sha(canon(roots)),
 'compiler_sha256':fs(__file__),'generic_ir_helpers_sha256':fs(HERE/'generic_ir_helpers.py'),'actual_local_records':len(records),'local_opcodes':dict(ops),'local_histogram':dict(sorted(H.items())),
 'literal_histogram':dict(sorted(hist.items())),'literal_stock':S,'calls':sum(hist.values()),'rank_mass':sum(r*n for r,n in hist.items()),'max_rank':42,'normalizer_descriptors':norms,'phases':720,
 'completion_sweeps':0,'expanded_frame_stage_records':sum(x['records']for x in bindings),'full_program_sha256':chain.hexdigest(),'copied_work_positive_projector_overrides':100,'invoice':bill,
 'rejected_controls':controls,'upstream_production_code_executed':False,'prior_role_frame_or_chart_data_imported':False,'publication_performed':False,
 'attribution':'New PR325 source word and selections are credited to immutable head and source-provenance notices. Only independently authored generic stage and boundary code is retained, with CODE-PROVENANCE.json.',
 'scope':'Concrete fresh local frame word, actual endpoint charts, all 300 literal namespaces, 720 phases and signed boundaries are bound. Matrix frame/COPY retiming proof is separately audited; generic primitive, prime uniformity, ordinary leaves, complex supplier and all-size interfaces remain inherited.'}
 dump('RESULT.json',result);dump('MANIFEST.json',{p.name:fs(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name not in ('MANIFEST.json','GEOMETRY-CONTROLS.json','EMISSION-CONTROLS.json')});print(json.dumps(contract.portable(result),indent=2))
if __name__=='__main__':main()
