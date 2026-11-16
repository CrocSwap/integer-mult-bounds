#!/usr/bin/env python3
"""Source-first #7624 candidate application; no execution occurs on import."""
import argparse, copy, gzip, hashlib, importlib.util, json, os, shutil, subprocess, sys, time, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = 'c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
BASE_GZIP = 'bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
PINS_SHA = '6a84e8ce4a23a9d60d388e2f42f583903d0a275b4be27e1c42738385b236a4a3'
SOURCE_TREE_SHA = '470052d3b0eafedaca9ffcd2a206f7974927287b0f36435af58e9336ab0e9c55'
NATIVE = 'PASS_CONTACT7624_COMPLETE_NATIVE'
SIGNED = 'PASS_CONTACT7624_COMPLETE_SIGNED_APPLICATION'
WORD = GZIP = None

def need(ok, message):
    if not ok: raise ValueError(message)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_bytes())
def write(path, obj): Path(path).write_text(json.dumps(obj, sort_keys=True, indent=2)+'\n')
def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def clean_env(**overrides):
    # -I protects the immediate child only. Its archived -B children must also
    # inherit an environment without optimization, path, or interpreter flags.
    env={k:v for k,v in os.environ.items() if not k.upper().startswith('PYTHON')}
    env.update(overrides)
    return env

def tree_sha(root):
    files=sorted(root.rglob('*'),key=lambda p:str(p.relative_to(root)))
    need(all(not p.is_symlink() for p in files),'tree contains symlink: '+str(root))
    listing=''.join(sha(p)+'  ./'+str(p.relative_to(root))+'\n' for p in files if p.is_file()).encode()
    return hashlib.sha256(listing).hexdigest()

def pin_package(p):
    need(sha(p/'PINS.json') == PINS_SHA, 'source package pins changed')
    pins = read(p/'PINS.json')
    need(len(pins) == 33, 'source package pin count')
    for rel, expected in pins.items():
        f = p/rel
        need(f.resolve().is_relative_to(p.resolve()) and f.is_file() and not f.is_symlink() and sha(f)==expected, 'package input mismatch '+rel)
    actual = {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}
    need(actual == set(pins)|{'PINS.json'}, 'source package file inventory')

def pin_source(source):
    need(source.is_dir(), 'missing #7605 source')
    # The digest is over the exact sorted sha256sum-format list, including paths.
    need(tree_sha(source)==SOURCE_TREE_SHA, '#7605 source closure changed')
    need(sha(source/'application.py')=='b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e', '#7605 application pin')
    retained=source/'retained/role902'; pins=read(retained/'PINS.json')
    for rel,h in pins.items():
        p=retained/rel
        need(p.resolve().is_relative_to(retained.resolve()) and p.is_file() and not p.is_symlink() and sha(p)==h, 'retained pin '+rel)

def gate_control(root):
    base=root/'compose7624_completion'; control=base/'control'; run=base/'run'
    final=read(control/'RESULT.json'); guard=read(control/'GUARD-VERIFIED.json')
    resource=read(run/'RESOURCE.json'); allow=read(control/'ALLOW.json'); ready=read(control/'READY.json')
    freeze=base/'FREEZE.json'; freeze_check=read(base/'FREEZE-CHECK.json')
    need(final['differential_case_completed'] is True and final['group_empty'] is True and final['verified_before_release'] is True and final['source_released'] is True and final['guard_only'] is False and type(final['returncode']) is int and final['returncode']==0, 'first gate final controller incomplete')
    need(guard['verified_before_release'] is True and guard['guard_only'] is False and guard['source_released'] is False, 'first gate pre-release guard incomplete')
    need(resource['differential_case_completed'] is True and resource['source_executed'] is True and len(resource['stages'])==1 and resource['stages'][0]['name']=='differential' and type(resource['stages'][0]['exit_code']) is int and resource['stages'][0]['exit_code']==0, 'first gate resource receipt incomplete')
    need(allow['guard_only'] is False and allow['unit']==guard['unit']==final['unit'] and ready['cgroup']==guard['properties']['ControlGroup']==final['properties']['ControlGroup'], 'first gate service binding')
    expected={'cpu.max':'10000 10000','cpu.max.burst':'0','memory.max':'2147483648','memory.swap.max':'0','memory.oom.group':'1','pids.max':'16'}
    need(all(guard['kernel_controls'].get(k)==v and final['kernel_controls'].get(k)==v for k,v in expected.items()), 'first gate kernel limits')
    props=guard['properties']; need(props['MemoryMax']=='2147483648' and props['MemorySwapMax']=='0' and props['CPUQuotaPerSecUSec']=='1s' and props['CPUAffinity']=='0' and props['TasksMax']=='16', 'first gate service limits')
    need(allow['freeze_sha256']==sha(freeze)==freeze_check['freeze_sha256']=='f004a64716370ae9185b7b7ca8f06eb35b3566223e2b01309e8d2f1d7c7449df', 'completion freeze binding')
    need(freeze_check['original_failure_preserved'] is True and freeze_check['physical_cap']==75 and freeze_check['bounds']=={'service':600,'stage':595,'inner':580,'memory':2147483648,'cpu':1,'swap':0}, 'completion fixed bounds')
    spec=read(freeze); need(spec['schema']=='fixed-source-research-freeze/v1' and len(spec['files'])==freeze_check['files']==104, 'completion frozen inventory')
    for row in spec['files']:
        p=Path(row['path']); need(p.is_file() and not p.is_symlink() and sha(p)==row['sha256'], 'first gate frozen source changed '+str(p))
    return {name:sha(path) for name,path in {'controller_result':control/'RESULT.json','guard':control/'GUARD-VERIFIED.json','resource':run/'RESOURCE.json','allow':control/'ALLOW.json','ready':control/'READY.json','freeze':freeze,'freeze_check':base/'FREEZE-CHECK.json'}.items()}

def gate_values(root):
    gate_control(root)
    gate=root/'compose7624_completion/run/case'; result=read(gate/'RESULT.json')
    need(result['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U', 'positive first gate required')
    required={'RETAINED-PASSED.json','built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/status.json','price/PRICE.json','price/invoice-new.json'}
    receipts=result['receipt_hashes']; need(required<=set(receipts), 'incomplete first gate receipt set')
    for rel,h in receipts.items():
        p=gate/rel
        need(p.resolve().is_relative_to(gate.resolve()) and p.is_file() and not p.is_symlink() and sha(p)==h, 'first gate receipt '+rel)
    retained=read(gate/'RETAINED-PASSED.json'); failed=root/'compose7624/control/RESULT.json'
    need(result['qualified_kappa'] is False and result['original_failed_controller_sha256']==retained['original_failed_controller_sha256']==sha(failed), 'original failed gate retained')
    need(read(failed)['differential_case_completed'] is False, 'original failure must remain visible')
    for item in retained['evidence']:
        original=Path(item['path']); need(original.is_file() and not original.is_symlink() and sha(original)==item['sha256'], 'retained predecessor evidence changed')
        if 'destination' in item: need(sha(gate/item['destination'])==item['sha256'], 'retained passed copy changed')
    m=read(gate/'built/edit-manifest.json'); compressed=(gate/'built/candidate-word.json.gz').read_bytes()
    need(m['source_canonical_sha256']==BASE and m['source_gzip_sha256']==BASE_GZIP, 'source manifest binding')
    need(hashlib.sha256(compressed).hexdigest()==m['candidate_gzip_sha256'] and hashlib.sha256(canonical(json.loads(gzip.decompress(compressed)))).hexdigest()==m['candidate_canonical_sha256'], 'candidate byte and canonical binding')
    price=read(gate/'price/PRICE.json')
    need(price['status']=='PROVISIONAL_UNDER_COMMON_U' and price['bindings']['candidate_canonical_sha256']==m['candidate_canonical_sha256'] and price['bindings']['original_word_canonical_sha256']==BASE, 'price binding')
    return gate,m,price

def prepare(root, work):
    need(not work.exists(), 'fresh work directory required')
    package=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass'
    source=root.parent/'kappa-research-20261115/inputs/pr7605'
    pin_package(package); pin_source(source); gate,m,price=gate_values(root)
    temp=work.parent/'local-tmp'; temp.mkdir(exist_ok=True)
    cache=work.parent/'pycache'
    env=clean_env(TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp),PYTHONPYCACHEPREFIX=str(cache),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(package/'reproduce.py'),'--source',str(source),'--work',str(work),'--stage','prepare'],env=env,check=True)
    frozen=work/'frozen-composition'
    copies={'7624-WORD.json.gz':package/'data/word.json.gz', '7624-INVOICE.json':package/'evidence/invoice-step1.json',
      '7624-NATIVE.json':package/'evidence/NATIVE.json', '7624-SIGNED.json':package/'evidence/SIGNED.json',
      '7624-CERTS.json':package/'evidence/certs-step1.json', 'CONTACT7624-PRICE.json':gate/'price/PRICE.json',
      'CONTACT7624-MANIFEST.json':gate/'built/edit-manifest.json'}
    copy_hashes={}
    for name,src in copies.items():
        dst=frozen/name; need(not dst.exists(), 'new frozen copy exists '+name); shutil.copyfile(src,dst)
        need(sha(src)==sha(dst), 'frozen copy mismatch '+name); copy_hashes[name]=sha(dst)
    helper=work/'producer54/validation_signed/w2_adapt.py'
    original_helper=sha(helper)
    need(helper.read_bytes().count(b'(life, peak, owned_count) == (204, 50, 68)')==1,'prepared 204 helper')
    run_id=uuid.uuid4().hex
    gate_control_hashes=gate_control(root)
    write(work/'QUALIFICATION-ID.json',{'run_id':run_id,'candidate_canonical_sha256':WORD,'candidate_gzip_sha256':GZIP,'source_canonical_sha256':BASE,'first_gate_result_sha256':sha(gate/'RESULT.json'),'first_gate_control_hashes':gate_control_hashes})
    shutil.copyfile(HERE/'application.py',work/'CONTACT7624-LAUNCHER.py')
    nr=load('contact7624_adapt_native',HERE/'adapt_native.py').adapt(work,root)
    sr=load('contact7624_adapt_signed',HERE/'adapt_signed.py').adapt(work,root)
    need(sha(helper)==original_helper and sr['helper_sha256']==original_helper and sr['helper_original_sha256']==original_helper,'prepared 204 helper changed')
    for n in ('CANDIDATE-WORD.json.gz','CANDIDATE-INVOICE.json','CONTACT7624-PAIRS.json'):
        copy_hashes[n]=sha(frozen/n)
    need(copy_hashes['CANDIDATE-WORD.json.gz']==GZIP and sha(work/'producer54/reroute/WORD.json.gz')==GZIP, 'candidate overlay bytes')
    for rel in ('producer54/validation_native/run.py','producer54/validation_signed/run.py'):
        f=work/rel; compile(f.read_text(),str(f),'exec')
    ledger={'schema':'contact7624-adapters/v1','run_id':run_id,'native':nr,'signed':sr,'candidate_canonical_sha256':WORD,'candidate_gzip_sha256':GZIP,'source_canonical_sha256':BASE,'launcher_sha256':sha(HERE/'application.py'),'common_U_sha256':sha(HERE/'COMMON-U.json'),'first_gate_result_sha256':sha(gate/'RESULT.json'),'first_gate_control_hashes':gate_control_hashes,'frozen_hashes':copy_hashes,'prepared_inputs_tree_sha256':tree_sha(work/'inputs'),'source_7605_tree_sha256':SOURCE_TREE_SHA,'source_7624_pins_sha256':PINS_SHA,'source_204_helper_sha256':original_helper,'adapted_204_helper_sha256':sha(helper),'adapter_source_hashes':{n:sha(HERE/n) for n in ('adapt_native.py','adapt_signed.py')}}
    write(work/'CONTACT7624-ADAPTERS.json',ledger)
    write(work/'PREPARED.json',{'status':'PREPARED_NOT_EXECUTED','run_id':run_id,'ledger_sha256':sha(work/'CONTACT7624-ADAPTERS.json'),'candidate_canonical_sha256':WORD})

def typed_pairs(rows):
    need(type(rows) is list and len(rows)>0, 'pair inventory must be nonempty list')
    out=[]
    for pair in rows:
        need(type(pair) is list and len(pair)==2 and all(type(v) is int and v>=0 for v in pair), 'malformed physical pair')
        out.append(tuple(pair))
    need(len(out)==len(set(out)), 'duplicate physical pair')
    return set(out)

def validate_native_obj(obj, work):
    need(obj['status']==NATIVE and obj['word_canonical_sha256']==WORD,'native result candidate/status')
    need(obj['native']['public']==1501 and obj['native']['lifetimes']==204 and obj['native']['owned_peak']==50 and not obj['native']['bad_inputs'],'native contract')
    need(obj['controls'] and all(obj['controls'].values()) and obj['controls']['wrong_902_1091_contact_source'] and obj['controls']['missing_902_paid_move'],'native rejection controls')
    need(obj['derived_grid']['odd_scale']==1125 and obj['derived_grid']['fractional_bits']==25,'native grid')
    manifest=read(work/'frozen-composition/CONTACT7624-PAIRS.json'); ledger=read(work/'CONTACT7624-ADAPTERS.json')
    need(sha(work/'frozen-composition/CONTACT7624-PAIRS.json')==ledger['native']['candidate_pair_manifest_sha256'] and manifest['source_canonical_sha256']==BASE and manifest['candidate_canonical_sha256']==WORD,'physical pair manifest binding')
    expected=typed_pairs(manifest['full_validation_pairs']); source=typed_pairs(manifest['pinned_source_pairs'])
    need(len(source)==1075==manifest['source_affected_count'] and source<=expected and len(expected)==ledger['native']['candidate_pair_count'] and ledger['native']['source_pair_count']==1075,'fixed source and complete pair inventories')
    pairs=obj['charts']['all_affected_pairs']; need(type(pairs) is list and all(type(x) is dict and 'pair' in x for x in pairs),'malformed native pair rows')
    need(typed_pairs([x['pair'] for x in pairs])==expected and obj['charts']['wrong_phase_rejected'] is True,'native exact physical census')
    need(all(type(x.get('columns')) is int and x['columns']==512 and type(x.get('adjoint_columns')) is int and x['adjoint_columns']==512 and x.get('absolute_phase_verified') is True for x in pairs),'native full physical columns')
    need(obj['physical_checks']==['verify_host3_odd.py','physical.py'],'native finite physical checks')
    need(obj['paired_ordinary']['source_7624']['conservative_total']<10**9 and obj['paired_ordinary']['candidate']['conservative_total']<10**9,'paired ordinary')
    need(obj['paired_precision']['source_7624'] and obj['paired_precision']['candidate'],'paired fresh precision')
    return obj

def validate_native(path,work): return validate_native_obj(read(path),work)

def native_inventory_controls(obj,work):
    # Exercise the actual consumer against the populated fresh result and fixed
    # manifest, preserving its denominator rather than re-deriving it from rows.
    rows=obj['charts']['all_affected_pairs']; need(len(rows)>=2,'positive fixed inventory needed for controls')
    mutations={}
    for name in ('missing_pair','substituted_pair','duplicate_pair','empty_pairs','boolean_pair','malformed_row'):
        bad=copy.deepcopy(obj); r=bad['charts']['all_affected_pairs']
        if name=='missing_pair': r.pop()
        elif name=='substituted_pair': r[0]['pair']=[2**63,0]
        elif name=='duplicate_pair': r[-1]['pair']=list(r[0]['pair'])
        elif name=='empty_pairs': r.clear()
        elif name=='boolean_pair': r[0]['pair'][0]=True
        else: r[0]['columns']=True
        try: validate_native_obj(bad,work)
        except (ValueError,KeyError,TypeError,IndexError): mutations[name]=True
        else: raise ValueError('native inventory consumer accepted '+name)
    return mutations

def receipt_valid(work, supplied=None):
    r=read(work/'native.receipt.json') if supplied is None else supplied
    p=work/'producer54/validation_native/NATIVE-RESULT.json'; identity=read(work/'QUALIFICATION-ID.json')
    need(r['stage']=='native' and r['exit']==0 and r['run_id']==identity['run_id'],'fresh native attempt identity')
    need(r['candidate_canonical_sha256']==WORD and r['native_result_sha256']==sha(p),'fresh native result hash')
    need(r['adapter_sha256']==sha(work/'CONTACT7624-ADAPTERS.json') and r['launcher_sha256']==sha(HERE/'application.py')==sha(work/'CONTACT7624-LAUNCHER.py'),'fresh adapter/launcher binding')
    return r

def execute(stage,root,work):
    ledger=read(work/'CONTACT7624-ADAPTERS.json'); identity=read(work/'QUALIFICATION-ID.json'); gate,m,price=gate_values(root)
    pin_package(root/'inputs/pr7624/research/p104-w2-primal-dual-bypass')
    need(tree_sha(work/'inputs')==ledger['prepared_inputs_tree_sha256'],'prepared source closure changed')
    need(ledger['run_id']==identity['run_id'] and ledger['candidate_canonical_sha256']==WORD and identity['candidate_canonical_sha256']==WORD and identity['candidate_gzip_sha256']==GZIP and identity['first_gate_result_sha256']==sha(gate/'RESULT.json')==ledger['first_gate_result_sha256'],'prepared identity and gate')
    need(identity['first_gate_control_hashes']==ledger['first_gate_control_hashes']==gate_control(root),'finalized first gate receipt custody')
    need(ledger['launcher_sha256']==sha(HERE/'application.py')==sha(work/'CONTACT7624-LAUNCHER.py') and ledger['common_U_sha256']==sha(HERE/'COMMON-U.json'),'prepared launcher and common U')
    need(read(work/'PREPARED.json')['ledger_sha256']==sha(work/'CONTACT7624-ADAPTERS.json'),'ledger binding')
    for n,h in ledger['adapter_source_hashes'].items(): need(sha(HERE/n)==h,'adapter source changed')
    for n,h in ledger['frozen_hashes'].items(): need(sha(work/'frozen-composition'/n)==h,'frozen input changed '+n)
    need(sha(work/'producer54/reroute/WORD.json.gz')==GZIP,'reroute candidate changed')
    helper=work/'producer54/validation_signed/w2_adapt.py'
    need(sha(helper)==ledger['source_204_helper_sha256']==ledger['adapted_204_helper_sha256']==ledger['signed']['helper_sha256'],'prepared helper binding')
    for kind,key in (('native','adapted_runner_sha256'),('signed','adapted_sha256')):
        need(sha(work/f'producer54/validation_{kind}/run.py')==ledger[kind][key],'generated runner changed '+kind)
    native=work/'producer54/validation_native/NATIVE-RESULT.json'; receipt_controls=[]; stale_count=0
    if stage=='signed':
        native_obj=validate_native(native,work); inventory_controls=native_inventory_controls(native_obj,work); fresh=receipt_valid(work)
        for key in ('run_id','native_result_sha256','adapter_sha256','launcher_sha256'):
            bad=dict(fresh); bad[key]=fresh[key]+'-previous'
            try: receipt_valid(work,bad)
            except ValueError: receipt_controls.append(key)
            else: raise ValueError('stale native receipt binding accepted: '+key)
        stale_paths=(root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/evidence/NATIVE.json',root.parent/'kappa-research-20261115b/inputs/pr7620/evidence/FULL-NATIVE-RESULT.json',root.parent/'kappa-research-20261115b/inputs/pr7616/evidence/NATIVE.json')
        for stale in stale_paths:
            try: validate_native(stale,work)
            except (ValueError,KeyError): stale_count+=1
            else: raise ValueError('stale native result accepted: '+str(stale))
    script=work/f'producer54/validation_{stage}/run.py'; start=time.monotonic(); cache=work/'isolated/pycache'
    env=clean_env(TMPDIR=str(work/'isolated'),TEMP=str(work/'isolated'),TMP=str(work/'isolated'),PYTHONPYCACHEPREFIX=str(cache),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    shim=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/windows_path_shim.py'
    with (work/(stage+'.stdout')).open('x') as so,(work/(stage+'.stderr')).open('x') as se:
        p=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(cache),str(shim),str(script)],cwd=work,env=env,stdout=so,stderr=se,check=False)
    r={'stage':stage,'exit':p.returncode,'wall_seconds':time.monotonic()-start,'run_id':identity['run_id'],'candidate_canonical_sha256':WORD,'adapter_sha256':sha(work/'CONTACT7624-ADAPTERS.json'),'launcher_sha256':sha(HERE/'application.py')}
    if p.returncode==0:
        if stage=='native': validate_native(native,work); r['native_result_sha256']=sha(native)
        else:
            obj=read(work/'producer54/validation_signed/RESULT.json'); need(obj['status']==SIGNED,'signed success marker')
            catalogue=obj['catalogue']; size=obj['catalogue_size']; generator=work/'producer54/validation_signed/adapted/short_native_catalogue.py'
            need(type(size) is int and size>0 and sha(generator)==obj['catalogue_generator_sha256'],'fresh catalogue generator size and custody')
            need(type(catalogue) is list and catalogue and sum(x['checked_maps'] for x in catalogue)==size,'complete catalogue')
            cursor=0
            for row in catalogue:
                need(all(type(row[k]) is int for k in ('catalogue_size','slice_start','slice_stop','checked_maps','main_boundary_pairs')) and row['catalogue_size']==size and row['slice_start']==cursor and row['slice_stop']>row['slice_start'] and row['slice_stop']-row['slice_start']==row['checked_maps'] and row['word_sha256']==GZIP and row['phase_control_rejected'] is True,'catalogue custody/coverage'); cursor=row['slice_stop']
            need(cursor==size and sum(x['main_boundary_pairs'] for x in catalogue)==104,'catalogue boundary closure')
            after=obj['price']['after']; need(sum(after['P'].values())==110043 and sum(after['T'].values())==22461 and after['S']==1424,'complete signed paid/target count')
            before=obj['price']['baseline_7624']; need(sum(before['P'].values())==110060 and sum(before['T'].values())==22461 and before['S']==1424,'source invoice count')
            outer=obj['price']['public_claim_gate']['outer']; need(outer['strict_count']==54 and outer['functional_count']==4,'58 outer predicates')
            tape=obj['checks']['ODD-FIXED-TAPE-COUNTS.json']; need(tape['native_invocations']==17,'17 caller invocations')
            need(obj['price']['first_gate_claim']==price['claim'] and obj['price']['first_gate_probe']==price['tested'],'first gate claim binding')
            r['signed_result_sha256']=sha(work/'producer54/validation_signed/RESULT.json'); r['stale_native_results_rejected']=stale_count; r['stale_native_receipt_bindings_rejected']=receipt_controls; r['native_inventory_consumer_controls']=inventory_controls
    write(work/(stage+'.receipt.json'),r); need(p.returncode==0,'complete '+stage+' application failed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--stage',choices=['prepare','native','signed'],required=True); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--work',type=Path,required=True); a=ap.parse_args()
    need(__debug__ and sys.version_info[:2]==(3,12),'Python 3.12 assertions enabled required')
    global WORD,GZIP
    root=a.root.resolve(); gate,m,price=gate_values(root); WORD=m['candidate_canonical_sha256']; GZIP=m['candidate_gzip_sha256']
    if a.stage=='prepare': prepare(root,a.work.resolve())
    else: execute(a.stage,root,a.work.resolve())
if __name__=='__main__': main()
