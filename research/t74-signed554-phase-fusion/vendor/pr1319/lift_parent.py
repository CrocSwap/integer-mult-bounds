import argparse,copy,gzip,hashlib,importlib.util,json,shutil
from pathlib import Path
F=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--owners',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();P=a.owners.resolve();D=a.out.resolve();D.mkdir(exist_ok=False)
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def dump(p,v):
 b=json.dumps(v,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
src=F/'inputs';plan=rd(src/'PLAN.json');parent=rd(src/'GLOBAL-TEMPLATE.json.gz');original=copy.deepcopy(parent);copies=2;T=plan['T'];olddata=plan['live'];bank=parent['live']-olddata;newdata=copies*olddata;newlive=copies*parent['live'];delta=newlive-parent['live'];private=parent['physical']-parent['live']
def family(f,g):return f+g*olddata if f<olddata else newdata+g*bank+f-olddata
parent['calls']=[]
for c in original['calls']:
 for g in range(copies):
  z=copy.deepcopy(c);z['replica']+=g*T;z['owners']=[[family(f,g),r] for f,r in c['owners']];assert len({f for f,r in z['owners']})==len(z['owners']);parent['calls'].append(z)
for c in parent['idle_children']:assert c['replicas']==T;c['replicas']*=copies
for e in parent['execution_schedule']:
 if 'replicas' in e:assert e['replicas']==list(range(T));e['replicas']=list(range(copies*T))
 if e['kind']=='bank_padding_cover_sweep':e['families']=[newdata,newlive]
 elif e['kind']=='translate_every_live_family':e['families']=[0,newlive];e['charged_calls_per_cover']=newlive
parent['bank_padding']['families']=[family(f,g) for g in range(copies) for f in original['bank_padding']['families']];parent['bank_padding']['children']=[]
for g in range(copies):
 for c in original['bank_padding']['children']:
  z=copy.deepcopy(c);z['family']=family(z['family'],g);parent['bank_padding']['children'].append(z)
parent['cover_final_correction'].update(families=[0,newlive],charged_calls_per_cover=newlive)
parent['private_namespace']={k:[i+delta for i in v] for k,v in parent['private_namespace'].items()};parent.update(live=newlive,physical=newlive+private,version='direct-sum-pinned-t37-envelope')
parent['replica_lift']=dict(replicas=copies*T,data_stock=newdata,bank_stock=copies*bank,groups=original['replica_lift']['groups']*copies,source_template_content_sha256=identity(original),phase_recipe_unchanged=True)
assert parent['local_programs']==original['local_programs'] and parent['recipe']==original['recipe']
assert len(parent['calls'])==copies*len(original['calls'])
for c in parent['calls']:
 g,r=divmod(c['replica'],T);old=next(x for x in original['calls'] if (x['stage'],x['replica'])==(c['stage'],r));assert [route for f,route in c['owners']]==[route for f,route in old['owners']];assert c['window']==old['window']
dump(D/'GLOBAL-TEMPLATE.json.gz',parent)
source=F/'vendor/build_parent.py';sp=importlib.util.spec_from_file_location('windows',source);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
order=rd(P/'ORDER.json');windows,schedule=mod.actual_windows(parent,order);dispatch={(s,r):pid for s,r,pid in rd(P/'DISPATCH.json')};oldcalls={(x['stage'],x['replica']):x for x in plan['provider_calls']};plan['provider_calls']=[];plan['per_call_widths']=[]
for time,(s,r) in enumerate(order):
 pid=dispatch[s,r];desc=plan['provider_registry'][pid];z=copy.deepcopy(oldcalls[s,r%T]);z.update(replica=r,time=time,provider=pid,local_program_sha256=desc['orientation_program_sha256'][z['orientation']]);plan['provider_calls'].append(z);plan['per_call_widths'].append(dict(stage=s,replica=r,time=time,widths=desc['widths']))
for n in ['OWNERS.json.gz','DISPATCH.json','PROFILE.json']:shutil.copy2(P/n,D/n)
plan.update(T=copies*T,live=copies*plan['live'],deficit=copies*plan['deficit'],order=order,windows=windows,profile=rd(P/'PROFILE.json'),assignment_sha256=sha(D/'OWNERS.json.gz'),assignment_content_sha256=identity(rd(D/'OWNERS.json.gz')),status='EXPLICIT_T74_ALTERNATING_PATH_EXACT_FILL',mode='mixed-t74-exact-fill',solver_status='exact alternating paths on frozen legal bins')
plan['replica_lift']=dict(replicas=copies*T,parent_template_content_sha256=identity(parent),owners_file_sha256=sha(D/'OWNERS.json.gz'),schedule_content_sha256=identity(schedule),source_replicas=T,copies=copies,phase_recipe_unchanged=True)
dump(D/'PLAN.json',plan);construction=rd(P/'RESULT.json');dump(D/'CONSTRUCTION.json',construction)
spec=rd(src/'SPEC.json');spec.update(name='mixed-t74-exact-fill',call_order=order,dispatch=rd(P/'DISPATCH.json'),providers={},expected={'gain_baseline_kappa':rd(F/'vendor/pr1297/CLAIM.json')['kappa']},data={'plan_sha256':sha(D/'PLAN.json'),'owners_sha256':sha(D/'OWNERS.json.gz')})
spec['geometry']=dict(replicas=plan['T'],stages=plan['L'],pairs=plan['K'],dimension=plan['M'],charged_prefix_bits=1<<(192+37+2*len(order)+4).bit_length(),parent_live=parent['live'],parent_physical=parent['physical'],parent_idle=sum(c['replicas'] for c in parent['idle_children']),parent_helpers=private-8-2)
dump(D/'SPEC.json',spec);dump(P/'PARENT-LIFT-RECEIPT.json',dict(status='PASS_EXACT_DIRECT_SUM_PARENT_AND_WINDOW_LIFT',source_sha256=sha(src/'GLOBAL-TEMPLATE.json.gz'),new_sha256=sha(D/'GLOBAL-TEMPLATE.json.gz'),calls=len(parent['calls']),roles=len(rd(D/'OWNERS.json.gz')),old_replicas=T,new_replicas=plan['T'],private_work_shared=private,geometry=spec['geometry']));print('PREPARED',spec['geometry'])
