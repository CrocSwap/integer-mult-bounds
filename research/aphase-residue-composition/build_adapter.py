#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Extend the exact PR2848 native/admission adapters to immutable PR2853."""
import argparse,ast,copy,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
for name in ('predecessor','source','out'):ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();P=a.predecessor.resolve();S=a.source.resolve();OUT=a.out.resolve()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
HEAD='d01045dfb67428679618027dff552f1d032fa999';MANIFEST='44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be';CLAIM='eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'
need(not OUT.exists() and not OUT.is_relative_to(S) and not OUT.is_relative_to(P),'fresh external output')
need(sha((S/'MANIFEST.json').read_bytes())==MANIFEST,'exact P53 manifest')
files=json.loads((S/'MANIFEST.json').read_bytes());need(len(files)==549,'549 source files')
need({p.relative_to(S).as_posix():sha(p.read_bytes()) for p in S.rglob('*') if p.is_file() and p!=S/'MANIFEST.json'}==files,'complete source inventory')
need(not list(S.rglob('__pycache__')) and not list(S.rglob('*.pyc')),'clean immutable source')
claimpath=S/'outer/OUTER-CLAIM.json';need(sha(claimpath.read_bytes())==CLAIM,'exact P53 full outer claim');claim=json.loads(claimpath.read_bytes());need(Q(claim['kappa_rational'])==Q(claim['kappa']),'full3046digit comparison exact')
source=(P/'admit_dirtentry_replica_latest.py').read_bytes();need(sha(source)=='b926725ea029c71979e48e785578aa4821ea7ea73c8e9139c4e2c71fa6bfc91b','P48 driver pin')
source_entry=f"    'pr2853': dict(commit='pr2853-dirtentry4', manifest='{MANIFEST}', helpers=408, source_file_count=549, upstream_head='{HEAD}'),\n"
comparison_entry=f"    'pr2853': dict(pr=2853, head='{HEAD}', sha256='{CLAIM}', field='kappa_rational'),\n    'pr2848': dict(pr=2848, head='c50d12e4720cd1fef2b5a65e337e37de9731879a', sha256='aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9', field='kappa'),\n"
old_transport="_part.with_suffix('.tmp').write_text(_j.dumps([_idx[0],_own]));_part.with_suffix('.tmp').replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)"
new_transport="_tmp=_part.with_name(_part.name+'.%d.%d.tmp'%(_AF_SHARD,os.getpid()));_tmp.write_text(_j.dumps([_idx[0],_own]));_tmp.replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)"
patch_call="    patch('audit_fast.py', [("+repr(old_transport)+", "+repr(new_transport)+")])\n"
anchor="    # PR2530's already checked correction: restored zero buffers occupy physical\n"
changes=[('SOURCE_PROFILES = {\n','SOURCE_PROFILES = {\n'+source_entry),('COMPARISONS = {\n','COMPARISONS = {\n'+comparison_entry),("choices=sorted(SOURCE_PROFILES), default='pr2833')","choices=sorted(SOURCE_PROFILES), default='pr2853')"),("choices=sorted(COMPARISONS), default='pr2843')","choices=sorted(COMPARISONS), default='pr2853')"),(anchor,"    # PR2843: exact per-shard/PID transport repair; predicates and merge unchanged.\n"+patch_call+anchor)]
def apply(original,changes):
 body=original.decode()
 for old,new in changes:need(body.count(old)==1,'unique exact preimage: '+old[:70]);body=body.replace(old,new)
 return body
body=apply(source,changes)
def check(text):
 old=ast.parse(source);new=ast.parse(text)
 def assignment(tree,name):return next(n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name)
 for name,extra in [('SOURCE_PROFILES',source_entry),('COMPARISONS',comparison_entry)]:
  expected=ast.parse('x={\n'+extra+'}').body[0].value;node=assignment(new,name).value
  for ek,ev in zip(expected.keys,expected.values):
   key=ast.literal_eval(ek);indices=[i for i,k in enumerate(node.keys) if ast.literal_eval(k)==key];need(len(indices)==1,'new key unique');i=indices[0]
   need(ast.dump(node.values[i])==ast.dump(ev),'exact typed record '+key);del node.keys[i];del node.values[i]
 for flag,prior in [('--source-profile','pr2833'),('--comparison-profile','pr2843')]:
  nodes=[n for n in ast.walk(new) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value==flag];need(len(nodes)==1,'unique CLI')
  k=next(k for k in nodes[0].keywords if k.arg=='default');need(ast.literal_eval(k.value)=='pr2853','exact new default');k.value=ast.Constant(prior)
 main=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='main');ex=ast.parse(patch_call.strip()).body[0];matches=[i for i,n in enumerate(main.body) if ast.dump(n)==ast.dump(ex)];need(len(matches)==1,'exact transport patch');del main.body[matches[0]]
 need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'unexpected executable change')
check(body)
mutations={'wrong_source_manifest':(MANIFEST,'0'*64),'wrong_source_count':('source_file_count=549','source_file_count=548'),'wrong_comparison':(CLAIM,'f'*64),'wrong_source_default':("default='pr2853')","default='pr2833')"),'removed_native_exit_guard':('need(result.returncode == 0,','need(True,'),'removed_gain_guard':('and kappa > previous','and kappa >= previous'),'shared_shard_temporary':(repr(new_transport),repr(old_transport))}
rejected=[]
for name,(old,new) in mutations.items():
 need(old in body,'mutant acts')
 try:check(body.replace(old,new,1))
 except (RuntimeError,ValueError,SyntaxError):rejected.append(name)
 else:raise RuntimeError('accepted mutant '+name)
# Execute no native chain here; only authenticate every exact runtime patch preimage against P53.
patches=[]
tree=ast.parse(body)
for n in ast.walk(tree):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='patch' and len(n.args)==2:
  name=ast.literal_eval(n.args[0]);repls=eval(compile(ast.Expression(n.args[1]),'<literal-patch>','eval'),{'__builtins__':{}},{'DISCOVERY_APPEND_OLD':next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='DISCOVERY_APPEND_OLD'),'DISCOVERY_APPEND_NEW':next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name) and x.targets[0].id=='DISCOVERY_APPEND_NEW')})
  patches.append((n.lineno,name,repls))
runtime={};runtime_records=[]
for _,name,repls in sorted(patches):
 text=runtime.get(name,(S/name).read_text());before=sha(text.encode())
 for old,new in repls:need(text.count(old)==1,'P53 runtime preimage '+name+': '+old[:60]);text=text.replace(old,new)
 compile(text,name,'exec');runtime[name]=text;runtime_records.append({'path':name,'before_normalized_sha256':before,'after_sha256':sha(text.encode()),'replacement_count':len(repls)})
preparer=(P/'prepare_dirtentry_native_portable.py').read_bytes();need(sha(preparer)=='2962be17ee23d9c7953490e2d2919539b22b0ae2a29a10d89fddb6cfd3600431','P48 portable native preparer')
prep_changes=[("SOURCE_SHA='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'",f"SOURCE_SHA='{MANIFEST}'"),("SOURCE_COMMIT='pr2833-dirtentry'","SOURCE_COMMIT='pr2853-dirtentry4'"),("len(pins)==541","len(pins)==549"),("source_file_count=541","source_file_count=549"),("status='PASS_PR2833_FRESH_NATIVE_PREPARATION'","status='PASS_PR2853_FRESH_NATIVE_PREPARATION'"),("print('PASS_PR2833_FRESH_NATIVE_PREPARATION',flush=True)","print('PASS_PR2853_FRESH_NATIVE_PREPARATION',flush=True)")]
prep=apply(preparer,prep_changes);compile(prep,'prepare_native.py','exec');compile(body,'admit.py','exec')
OUT.mkdir(parents=True)
records=[]
for filename,original,new,cs in [('admit_aphase_residue.py',source,body,changes),('prepare_aphase_native.py',preparer,prep,prep_changes)]:
 (OUT/filename).write_text(new);records.append({'source_path':'research/t248-dirtentry-residue/'+('admit_dirtentry_replica_latest.py' if filename.startswith('admit') else 'prepare_dirtentry_native_portable.py'),'source_sha256':sha(original),'target_path':filename,'target_sha256':sha(new.encode()),'exact_preimages':[{'old':x,'new':y} for x,y in cs]})
record={'status':'PASS_PR2853_SOURCE_PROFILE_AND_COMPARATOR_DERIVATION','head':HEAD,'source_manifest_sha256':MANIFEST,'source_file_count':549,'comparison_claim_sha256':CLAIM,'comparison_field':'kappa_rational','comparison_decimal_digits':len(claim['kappa'].split('.')[1]),'comparison_kappa':claim['kappa_rational'],'files':records,'admission_AST':'Exact PR2848 executable AST after undoing only declared source/comparison records, defaults and inherited shard transport repair.','runtime_patch_groups':runtime_records,'rejected_controls':rejected,'scope':'All old native/rebuild/phase/blocknorm/admission/release predicates retained. P53 dirtentry4 stage and5 rejecting mutants per provider are untouched. Native maxima and final candidate admission must still be executed.'}
(OUT/'DERIVATION.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':record['status'],'files':[{k:x[k] for k in ('target_path','target_sha256')} for x in records],'runtime_patch_groups':len(runtime_records),'rejected_controls':rejected},indent=2))
