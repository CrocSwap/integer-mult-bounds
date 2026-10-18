#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the frozen shared-kernel integration derivation without executing candidate code.

--old/--new contain admit.py, source/{MANIFEST.json,new/rebuild_borrow.py,verify.py},
and runtime/geometry_controls.py (original versus exact runtime control patch).
--derivation contains DERIVATION.json,build_overlay.py,prepare_shared_native.py,reproduce.py.
The minimal fixture proof authenticates complete manifest inventories and the two
changed validator scripts. Optional full-source paths additionally rehash every file.
Prepared for Yiyang (@Lyy-iiis) with substantial OpenAI Codex assistance.
"""
import argparse,ast,copy,hashlib,json,tempfile
from pathlib import Path,PurePosixPath

BASE_ADMIT='b926725ea029c71979e48e785578aa4821ea7ea73c8e9139c4e2c71fa6bfc91b'
OLD_MANIFEST='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
NEW_MANIFEST='54dc42f25c1d8b85adcf593c4bf6c0f83f7351388af857812790b8a0b4c3d869'
DERIVATION_SHA='da6024f182a95a5b39cfbc24638aff14a104c2e7cf3037aa5840ef4fc6395eb7'
SCRIPT_PINS={'build_overlay.py':'4c83a251a03045144608456e6b3bdbcced9255ce7c2d89f7039e766972100666','prepare_shared_native.py':'9d86bf49f6aec1d4f671a5d060815e97cb470151221a29fba736e91f06c74b07','reproduce.py':'7fc4cd1277f42ba0a25a1eae72c6290878fefd5bab7053f4e548c15d95d914c5'}
CHANGED={'new/BORROW-PROVIDERS.json','new/borrow/inputs/PR2833-WORD-base.json.gz','new/borrow/inputs/PR2833-WORD-extra.json.gz','new/borrow/inputs/shared_kernel_43base.json','new/borrow/inputs/shared_kernel_43extra.json','new/borrow/shared_kernel.py','new/borrow/shared_kernel_review.py','new/borrow/words/BORROW-WORD-43base.json.gz','new/borrow/words/BORROW-WORD-43extra.json.gz','new/rebuild_borrow.py','verify.py'}
ADDITIONS={
 'SOURCE_PROFILES':{'shared-four':{'commit':'shared-four-kernel-pr2833','manifest':NEW_MANIFEST,'helpers':408,'source_file_count':547,'upstream_head':'e9307b48d7d1b690939935ecef0f8e524e6d92f4'}},
 'COMPARISONS':{'pr2848':{'pr':2848,'head':'c50d12e4720cd1fef2b5a65e337e37de9731879a','sha256':'aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9','field':'kappa'}},
}
DEFAULTS={'--source-profile':('pr2833','shared-four'),'--comparison-profile':('pr2843','pr2848')}
ANCHORS={'new/rebuild_borrow.py':'    final=json.loads(gzip.decompress(shipped.read_bytes()))','verify.py':"run('rebuild-borrow-words',P/'new/rebuild_borrow.py')"}
def need(ok,reason):
 if not ok:raise ValueError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def jdata(data):return json.loads(data)
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'))
def assignment(tree,name):
 nodes=[x for x in tree.body if isinstance(x,ast.Assign) and len(x.targets)==1 and isinstance(x.targets[0],ast.Name) and x.targets[0].id==name]
 need(len(nodes)==1,'one assignment: '+name);return nodes[0]
def literal_records(node):
 need(isinstance(node.value,ast.Dict),'literal outer dict')
 keys=[ast.literal_eval(k) for k in node.value.keys];need(all(type(k)is str for k in keys) and len(keys)==len(set(keys)),'distinct literal record keys')
 out={}
 for k,v in zip(keys,node.value.values):
  need(isinstance(v,ast.Call) and isinstance(v.func,ast.Name) and v.func.id=='dict' and not v.args,'literal dict keyword record')
  names=[x.arg for x in v.keywords];need(None not in names and len(names)==len(set(names)),'distinct explicit record fields')
  out[k]={q.arg:ast.literal_eval(q.value) for q in v.keywords}
 return out
def default_node(tree,flag):
 calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value==flag]
 need(len(calls)==1,'one CLI option: '+flag);kw=[k for k in calls[0].keywords if k.arg=='default'];need(len(kw)==1,'one CLI default: '+flag);return kw[0]
GEOMETRY_REPLACEMENTS=[
 (" i['complete_invocation_sweeps']=i['bridge_sweeps']=333", " i['complete_invocation_sweeps']-=1;i['bridge_sweeps']-=1"),
 (" o,i=copy.deepcopy(owner),copy.deepcopy(invoice);fn(o,i);oh=digest(o);i['owner_audit_sha256']=oh", " o,i=copy.deepcopy(owner),copy.deepcopy(invoice);fn(o,i);assert (o,i)!=(owner,invoice), 'geometry mutant must change actual receipts';oh=digest(o);i['owner_audit_sha256']=oh"),
]
def remove_exact_geometry_patch(tree):
 mains=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main'];need(len(mains)==1,'one admission main')
 body=mains[0].body;matches=[]
 for i,n in enumerate(body):
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
   c=n.value
   if isinstance(c.func,ast.Name) and c.func.id=='patch' and c.args and isinstance(c.args[0],ast.Constant) and c.args[0].value=='geometry_controls.py':matches.append((i,c))
 need(len(matches)==1,'exactly one geometry control patch call');i,c=matches[0]
 need(len(c.args)==2 and not c.keywords and ast.literal_eval(c.args[1])==GEOMETRY_REPLACEMENTS,'only exact undercharge and non-vacuity geometry edits')
 def patch_target(n):
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='patch' and n.value.args and isinstance(n.value.args[0],ast.Constant):return n.value.args[0].value
 need(i>0 and i+1<len(body) and patch_target(body[i-1])=='new/rebind.py' and patch_target(body[i+1])=='verify_release.py','geometry patch occurs only at approved location')
 body.pop(i)

def check_adapter(olddata,newdata):
 need(sha(olddata)==BASE_ADMIT,'immutable PR2848 predecessor adapter SHA')
 old,new=ast.parse(olddata),ast.parse(newdata)
 remove_exact_geometry_patch(new)
 for name,add in ADDITIONS.items():
  a,b=assignment(old,name),assignment(new,name);before=literal_records(a)
  need(not(before.keys()&add.keys()),'new records cannot overwrite existing record')
  need(canon(literal_records(b))==canon(before|add),'exact record extension: '+name)
  b.value=copy.deepcopy(a.value)
 for flag,(a,b) in DEFAULTS.items():
  on,nn=default_node(old,flag),default_node(new,flag)
  need(ast.literal_eval(on.value)==a and ast.literal_eval(nn.value)==b,'exact CLI default change: '+flag)
  nn.value=copy.deepcopy(on.value)
 need(ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),'all executable AST and docstring unchanged outside four profile/default edits and exact added geometry-control patch')
def manifest(data,expected,count):
 need(sha(data)==expected,'immutable manifest SHA');m=jdata(data);need(type(m)is dict and len(m)==count,'manifest file count')
 for p,h in m.items():
  need(type(p)is str and not PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts and p!='MANIFEST.json','safe manifest path')
  need(type(h)is str and len(h)==64 and all(c in '0123456789abcdef' for c in h),'SHA256 manifest value')
 return m

def check_bundle(bundle):
 old,new,d=bundle['old'],bundle['new'],bundle['derivation'];checks=[]
 check_adapter(old['admit.py'],new['admit.py']);checks.append('adapter_exact_AST_guard_preservation')
 before=manifest(old['source/MANIFEST.json'],OLD_MANIFEST,541);after=manifest(new['source/MANIFEST.json'],NEW_MANIFEST,547);checks.append('pinned_before_after_manifests_541_to547')
 change={p:{'before_sha256':before.get(p),'after_sha256':after.get(p)} for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)}
 need(set(change)==CHANGED,'exact eleven-path overlay allowlist');need(sum(p in before for p in change)==5 and sum(p not in before for p in change)==6,'exact five modified six added zero deleted');checks.append('eleven_changes_five_modified_six_added_no_deletions')
 need(set(before)<=set(after),'no source deletion');need(all(before[p]==after[p] for p in before.keys()-CHANGED),'all other536manifest_entries_unchanged');checks.append('all_536_other_source_hashes_unchanged')
 need(sha(d['DERIVATION.json'])==DERIVATION_SHA,'immutable derivation receipt SHA');receipt=jdata(d['DERIVATION.json'])
 need(receipt['status']=='PASS_SOURCE_BOUND_FOUR_KERNEL_OVERLAY_DERIVATION' and receipt['upstream_manifest_sha256']==OLD_MANIFEST and receipt['derived_manifest_sha256']==NEW_MANIFEST and receipt['source_file_count']==547,'derivation manifest/status bindings')
 need(receipt['changes']==change,'receipt exact manifest delta');checks.append('derivation_receipt_manifest_delta_binding')
 for name,h in SCRIPT_PINS.items():need(sha(d[name])==h,'frozen integration script SHA: '+name)
 need(receipt['builder_sha256']==SCRIPT_PINS['build_overlay.py'],'receipt builder pin');checks.append('builder_native_preparer_executed_wrapper_pins')
 patches=receipt['patches'];need(len(patches)==2 and {p['path'] for p in patches}==set(ANCHORS),'exact two patch records')
 for p in patches:
  name=p['path'];ob,nb=old['source/'+name],new['source/'+name]
  need(sha(ob)==before[name]==p['before_sha256'] and sha(nb)==after[name]==p['after_sha256'],'altered script bound to both manifests: '+name)
  a,b=p['old'],p['new'];need(a==ANCHORS[name] and ob.decode().count(a)==1,'exact unique old anchor: '+name)
  need(b.count(a)==1 and b!=a,'nonempty strictly additive patch: '+name)
  if name=='new/rebuild_borrow.py':need(b.endswith(a),'rebuild addition precedes retained anchor')
  else:need(b.startswith(a+'\n'),'independent review follows retained verify call')
  need(ob.decode().replace(a,b).encode()==nb,'entire modified script equals exact declared additive patch: '+name)
  need(nb.decode().replace(b,a).encode()==ob,'inverse patch recovers all original bytes: '+name)
  ast.parse(nb)
  checks.append('exact_additive_patch_'+name)
 # New identities are not accepted merely because the manifest names them.
 need(after['new/borrow/shared_kernel.py']=='b3241527e6c136dc4b54975ef401c49d452bd6159fb99030accaf095c8fbd3ed','production generator pin')
 need(after['new/borrow/shared_kernel_review.py']=='5b323e50fb5a10ac088472b3e085b54d7d2ae3a29f8552ff44b788a984eb97d1','independent review pin')
 for tag in ['base','extra']:
  r=receipt['words'][tag];source_path='new/borrow/words/BORROW-WORD-43'+tag+'.json.gz';snapshot_path='new/borrow/inputs/PR2833-WORD-'+tag+'.json.gz'
  need(r['groups']==[478,460,462,480] and r['source_word_sha256']==before[source_path]==after[snapshot_path] and r['candidate_word_sha256']==after[source_path],'word and retained snapshot bindings '+tag)
  need(r['generator_sha256']==after['new/borrow/shared_kernel.py'],'word generation pin '+tag)
 checks.append('two_word_snapshots_and_generator_review_bound')
 # Parse only; none of these fixture scripts is imported or executed.
 for name in SCRIPT_PINS:ast.parse(d[name])
 wrap=ast.parse(d['reproduce.py']);pins=ast.literal_eval(assignment(wrap,'SCRIPT_PINS').value)
 need(pins['admit_shared_replica.py']==sha(new['admit.py']) and pins['build_overlay.py']==SCRIPT_PINS['build_overlay.py'] and pins['prepare_shared_native.py']==SCRIPT_PINS['prepare_shared_native.py'],'executed wrapper pins checked adapter/builder/preparer')
 need(ast.literal_eval(assignment(wrap,'SOURCE_SHA').value)==OLD_MANIFEST and ast.literal_eval(assignment(wrap,'OVERLAY_SHA').value)==NEW_MANIFEST,'executed wrapper manifests')
 checks.append('executed_wrapper_pins_derivation_and_adapter')
 original=old['runtime/geometry_controls.py'];derived=new['runtime/geometry_controls.py']
 need(sha(original)==before['geometry_controls.py']==after['geometry_controls.py'],'original geometry runtime fixture is unchanged source')
 text=original.decode()
 for a,b in GEOMETRY_REPLACEMENTS:
  need(text.count(a)==1,'geometry runtime exact unique preimage');text=text.replace(a,b)
 need(text.encode()==derived,'runtime geometry changes exactly undercharge and non-vacuity checks')
 gt=ast.parse(derived);fn=next(n for n in gt.body if isinstance(n,ast.FunctionDef) and n.name=='old_call_count')
 need(len(fn.body)==2 and all(isinstance(n,ast.AugAssign) and isinstance(n.op,ast.Sub) and isinstance(n.value,ast.Constant) and type(n.value.value)is int and n.value.value==1 for n in fn.body),'actual charges each decrease exactly one')
 need([n.target.slice.value for n in fn.body]==['complete_invocation_sweeps','bridge_sweeps'],'both actual sweep charges mutated')
 loops=[n for n in gt.body if isinstance(n,ast.For)]
 need(len(loops)==1 and isinstance(loops[0].iter,ast.List) and [n.id for n in loops[0].iter.elts]==['old_prefix','old_call_count','old_parent_idle','old_stock','missing_call','low_row'],'all six geometry controls retained')
 guard=[n for n in loops[0].body if isinstance(n,ast.Assert)]
 need(len(guard)==1 and ast.dump(guard[0].test,include_attributes=False)==ast.dump(ast.parse('(o,i)!=(owner,invoice)',mode='eval').body,include_attributes=False),'every mutant must differ before unchanged assembly')
 checks.append('runtime_geometry_exact_undercharge_nonvacuity_six_controls_retained')
 return checks

def read_bundle(old,new,derivation):
 bundle={}
 layouts={'old':(old,['admit.py','source/MANIFEST.json','source/new/rebuild_borrow.py','source/verify.py','runtime/geometry_controls.py']),'new':(new,['admit.py','source/MANIFEST.json','source/new/rebuild_borrow.py','source/verify.py','runtime/geometry_controls.py']),'derivation':(derivation,['DERIVATION.json',*SCRIPT_PINS])}
 for group,(root,names) in layouts.items():
  need(root.is_dir() and not root.is_symlink(),'fixture directory required');bundle[group]={}
  for name in names:
   p=root/name;need(p.is_file() and not any(q.is_symlink() for q in [p,*p.parents] if q.is_relative_to(root)),'fixture is regular non-symlink file')
   bundle[group][name]=p.read_bytes()
 return bundle

def full_tree(path,expected):
 need(path.is_dir() and not path.is_symlink(),'full source directory');actual={}
 for p in sorted(path.rglob('*')):
  need(not p.is_symlink(),'no source symlink')
  need(p.name!='__pycache__' and p.suffix!='.pyc','no source bytecode or cache directory')
  if p.is_file() and p!=path/'MANIFEST.json':actual[p.relative_to(path).as_posix()]=sha(p.read_bytes())
 need(actual==expected,'whole source tree equals manifest');return len(actual)

def controls(bundle):
 rejected=[]
 def reject(name,group,path,transform):
  bad=copy.deepcopy(bundle);old=bad[group][path];bad[group][path]=transform(old);need(bad[group][path]!=old,'control changes bytes: '+name)
  try:check_bundle(bad)
  except (ValueError,TypeError,KeyError,SyntaxError):rejected.append(name)
  else:raise RuntimeError('accepted invalid control: '+name)
 def substitute(a,b):
  def apply(data):need(a.encode() in data,'control preimage');return data.replace(a.encode(),b.encode(),1)
  return apply
 reject('weakened_stage_exit_guard','new','admit.py',substitute('need(result.returncode == 0,','need(True,'))
 reject('wrong_source_manifest','new','admit.py',substitute(NEW_MANIFEST,'0'*64))
 reject('wrong_comparison_field','new','admit.py',substitute("field='kappa'),","field='kappa_decimal'),"))
 reject('float_helper_count','new','admit.py',substitute('helpers=408, source_file_count=547','helpers=408.0, source_file_count=547'))
 reject('wrong_default','new','admit.py',substitute("default='pr2848')","default='pr2843')"))
 reject('weakened_final_source_guard','new','admit.py',substitute("need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST\n","need(True\n"))
 reject('zero_decrement_geometry_mutant','new','admit.py',substitute("i['complete_invocation_sweeps']-=1","i['complete_invocation_sweeps']-=0"))
 reject('geometry_control_waiver','new','runtime/geometry_controls.py',substitute("else:raise AssertionError('accepted '+fn.__name__)","else:pass"))
 reject('weakened_assemble_predicate','new','admit.py',substitute("assert bn['status']=='PASS_TENSOR_BLOCK_NORM_CERTIFICATE'","assert True"))
 reject('removed_geometry_nonvacuity_check','new','runtime/geometry_controls.py',substitute("assert (o,i)!=(owner,invoice)","assert True"))
 reject('altered_predecessor_bytes','old','admit.py',lambda x:x+b'\n')
 reject('unlisted_source_change','new','source/MANIFEST.json',lambda x:canon(jdata(x)|{'undeclared.py':'0'*64}).encode())
 reject('removed_inherited_verify_guard','new','source/verify.py',lambda x:x+b'\nraise RuntimeError("changed guard")\n')
 reject('removed_kernel_chain_stage','new','source/new/rebuild_borrow.py',substitute("chain.append(shared_word);steps.append('shared-four-kernel')","pass"))
 reject('altered_derivation_receipt','derivation','DERIVATION.json',lambda x:x+b'\n')
 reject('weakened_cache_binding','derivation','prepare_shared_native.py',substitute("tree(oldcache)==oldreceipt['cache_files']","True"))
 reject('weakened_secondary_comparison','derivation','reproduce.py',substitute("Q(result['kappa'])>Q(latest['kappa_rational'])","True"))
 for name,kind in [('empty_source_cache_directory','cache'),('source_bytecode_file','bytecode'),('source_symlink','symlink')]:
  with tempfile.TemporaryDirectory(prefix='integration-derivation-control-') as temp:
   p=Path(temp)
   if kind=='cache':(p/'__pycache__').mkdir()
   elif kind=='bytecode':(p/'unexpected.pyc').write_bytes(b'not executable')
   else:(p/'link').symlink_to('absent-target')
   try:full_tree(p,{})
   except ValueError:rejected.append(name)
   else:raise RuntimeError('accepted invalid full-source control: '+name)
 return rejected

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ['old','new','derivation','out']:ap.add_argument('--'+n,type=Path,required=True)
 ap.add_argument('--controls',action='store_true');ap.add_argument('--full-old-source',type=Path);ap.add_argument('--full-new-source',type=Path);a=ap.parse_args()
 b=read_bundle(a.old,a.new,a.derivation);checks=check_bundle(b);extra={}
 for tag,path in [('old',a.full_old_source),('new',a.full_new_source)]:
  if path is not None:
   expected=jdata(b[tag]['source/MANIFEST.json']);need((path/'MANIFEST.json').read_bytes()==b[tag]['source/MANIFEST.json'],'full source manifest bytes');extra[tag]=full_tree(path,expected)
 rejected=controls(b) if a.controls else []
 result=dict(status='PASS_EXACT_SHARED_KERNEL_INTEGRATION_DERIVATION',checks=checks,check_count=len(checks),rejected_controls=rejected,adapter_sha256=sha(b['new']['admit.py']),predecessor_adapter_sha256=BASE_ADMIT,source_manifest_sha256=OLD_MANIFEST,overlay_manifest_sha256=NEW_MANIFEST,overlay_change_count=11,modified_paths=5,added_paths=6,source_file_counts={'old':541,'new':547},full_source_trees_rehashed=extra,wrapper_sha256=SCRIPT_PINS['reproduce.py'],derivation_sha256=DERIVATION_SHA,checker_sha256=sha(Path(__file__).read_bytes()),fixture_sha256={g:{p:sha(v) for p,v in files.items()} for g,files in b.items()},candidate_code_executed=False,scope='Exact adapter AST guard preservation except the approved non-vacuous geometry mutant patch, authenticated unchanged overlay manifest delta, two additive supplier validator patches, frozen wrapper/preparer pins. Minimal fixtures do not prove omitted file bytes or full runtime admission; optional whole-source rehashes and full release evidence are reported separately.')
 a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['status','check_count','rejected_controls','full_source_trees_rehashed']},sort_keys=True))
if __name__=='__main__':main()
