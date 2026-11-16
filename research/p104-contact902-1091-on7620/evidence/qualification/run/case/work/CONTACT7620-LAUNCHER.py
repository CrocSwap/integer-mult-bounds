#!/usr/bin/env python3
"""Fresh #7620 composition application; preserve all predecessor source bytes."""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys,time,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
WORD='03da65fb97ffaf4d0e9756f3867df588b162975f6015d8458821d05b5fcb006b'
GZIP='4d742e0b6e915cc3c3d31d18d5d2703c1f943c695c25d7c5a24f04626c1f5235'
BASE='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
NATIVE='PASS_CONTACT7620_COMPLETE_NATIVE'
SIGNED='PASS_CONTACT7620_COMPLETE_SIGNED_APPLICATION'
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def pin_package(p):
    pins=read(p/'PINS.json')
    for rel,h in pins.items():
        f=p/rel;need(f.resolve().is_relative_to(p.resolve()) and f.is_file() and not f.is_symlink() and sha(f)==h,'package input mismatch '+str(f))
def prepare(root,work):
    need(not work.exists(),'fresh work directory required')
    source=root.parent/'kappa-research-20261115/inputs/pr7605'
    p=root/'inputs/pr7620';w2=root/'inputs/pr7616';pin_package(p);pin_package(w2)
    need(sha(source/'application.py')=='b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e','source7605 application pin')
    gate=root/'compose7620/run/case';need(read(gate/'RESULT.json')['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','positive fixed gate required')
    for rel,h in read(gate/'RESULT.json')['receipt_hashes'].items():need(sha(gate/rel)==h,'first gate receipt '+rel)
    need(sha(gate/'built/candidate-word.json.gz')==GZIP,'candidate bytes changed')
    temp=work.parent/'local-tmp';temp.mkdir(exist_ok=True)
    env=dict(os.environ,TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp),PYTHONPYCACHEPREFIX=str(work.parent/'pycache'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(work.parent/'pycache'),str(p/'reproduce.py'),'--w2',str(w2),'--source',str(source),'--work',str(work),'--stage','prepare'],env=env,check=True)
    frozen=work/'frozen-composition'
    copies={'7620-WORD.json.gz':p/'data/word.json.gz','7620-INVOICE.json':p/'data/invoice.json','7620-SIGNED.json':p/'evidence/SIGNED.json','7620-NATIVE.json':p/'evidence/FULL-NATIVE-RESULT.json','CONTACT7620-PRICE.json':gate/'price/PRICE.json','CONTACT7620-MANIFEST.json':gate/'built/edit-manifest.json'}
    for name,src in copies.items():
        dst=frozen/name;need(not dst.exists(),'new frozen copy exists '+name);shutil.copyfile(src,dst);need(sha(src)==sha(dst),'copy mismatch '+name)
    run_id=uuid.uuid4().hex;write(work/'QUALIFICATION-ID.json',{'run_id':run_id,'candidate_canonical_sha256':WORD,'source_canonical_sha256':BASE,'first_gate_result_sha256':sha(gate/'RESULT.json')})
    shutil.copyfile(HERE/'application.py',work/'CONTACT7620-LAUNCHER.py')
    nr=load('contact7620_adapt_native',HERE/'adapt_native.py').adapt(work,root)
    sr=load('contact7620_adapt_signed',HERE/'adapt_signed.py').adapt(work,root)
    for rel in ('producer54/validation_native/run.py','producer54/validation_signed/run.py'):
        f=work/rel;compile(f.read_text(),str(f),'exec')
    ledger={'schema':'contact7620-adapters/v1','run_id':run_id,'native':nr,'signed':sr,'candidate_canonical_sha256':WORD,'source_canonical_sha256':BASE,'launcher_sha256':sha(HERE/'application.py'),'common_U_sha256':sha(HERE/'COMMON-U.json'),'adapter_source_hashes':{n:sha(HERE/n) for n in ('adapt_native.py','adapt_signed.py')}}
    write(work/'CONTACT7620-ADAPTERS.json',ledger)
    write(work/'PREPARED.json',{'status':'PREPARED_NOT_EXECUTED','run_id':run_id,'ledger_sha256':sha(work/'CONTACT7620-ADAPTERS.json'),'candidate_canonical_sha256':WORD})
def validate_native(path,work):
    obj=read(path);need(obj['status']==NATIVE and obj['word_canonical_sha256']==WORD,'native result candidate/status')
    need(obj['native']['public']==1501 and obj['native']['lifetimes']==167 and obj['native']['owned_peak']==50 and not obj['native']['bad_inputs'],'native contract')
    need(obj['controls'] and all(obj['controls'].values()) and obj['controls']['wrong_902_1091_contact_source'] and obj['controls']['missing_902_paid_move'],'native rejection controls')
    need(obj['derived_grid']['odd_scale']==1125 and obj['derived_grid']['fractional_bits']==25,'native grid')
    pairs=obj['charts']['all_affected_pairs'];expected=read(work/'CONTACT7620-ADAPTERS.json')['native']['candidate_pair_count']
    need(len(pairs)==len({tuple(x['pair']) for x in pairs})==expected and obj['charts']['wrong_phase_rejected'],'native complete physical census')
    need(all(x['columns']==x['adjoint_columns']==512 and x['absolute_phase_verified'] for x in pairs),'native full physical columns')
    need(obj['physical_checks']==['verify_host3_odd.py','physical.py'],'native finite physical checks')
    need(obj['paired_ordinary']['source_7620']['conservative_total']<10**9 and obj['ordinary']['conservative_total']<10**9,'native paired ordinary')
    need(obj['paired_precision']['source_7620'] and obj['paired_precision']['candidate'],'native paired fresh precision')
    return obj
def receipt_valid(work,supplied=None):
    r=read(work/'native.receipt.json') if supplied is None else supplied;p=work/'producer54/validation_native/NATIVE-RESULT.json';identity=read(work/'QUALIFICATION-ID.json')
    need(r['stage']=='native' and r['exit']==0 and r['run_id']==identity['run_id'],'fresh native attempt identity')
    need(r['candidate_canonical_sha256']==WORD and r['native_result_sha256']==sha(p),'fresh native result hash')
    need(r['adapter_sha256']==sha(work/'CONTACT7620-ADAPTERS.json') and r['launcher_sha256']==sha(HERE/'application.py')==sha(work/'CONTACT7620-LAUNCHER.py'),'fresh adapter/launcher binding')
    return r
def execute(stage,root,work):
    ledger=read(work/'CONTACT7620-ADAPTERS.json');identity=read(work/'QUALIFICATION-ID.json')
    need(ledger['run_id']==identity['run_id'] and ledger['launcher_sha256']==sha(HERE/'application.py') and ledger['common_U_sha256']==sha(HERE/'COMMON-U.json'),'prepared identity')
    for n,h in ledger['adapter_source_hashes'].items():need(sha(HERE/n)==h,'adapter source changed')
    native=work/'producer54/validation_native/NATIVE-RESULT.json'
    receipt_controls=[]
    if stage=='signed':
        validate_native(native,work);fresh=receipt_valid(work)
        for key in ('run_id','native_result_sha256','adapter_sha256','launcher_sha256'):
            bad=dict(fresh);bad[key]=fresh[key]+'-previous'
            try:receipt_valid(work,bad)
            except ValueError:receipt_controls.append(key)
            else:raise ValueError('stale native receipt binding accepted: '+key)
        # Actual predecessor receipts must fail candidate qualification.
        for stale in (root/'inputs/pr7620/evidence/FULL-NATIVE-RESULT.json',root/'inputs/pr7616/evidence/NATIVE.json'):
            try:validate_native(stale,work)
            except (ValueError,KeyError):pass
            else:raise ValueError('stale native receipt accepted')
    script=work/f'producer54/validation_{stage}/run.py';pin=ledger[stage]['adapted_runner_sha256' if stage=='native' else 'adapted_sha256']
    need(sha(script)==pin,'generated runner changed')
    start=time.monotonic();env=dict(os.environ,TMPDIR=str(work/'isolated'),TEMP=str(work/'isolated'),TMP=str(work/'isolated'),PYTHONPYCACHEPREFIX=str(work/'isolated/pycache'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    with (work/(stage+'.stdout')).open('x') as so,(work/(stage+'.stderr')).open('x') as se:
        p=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(work/'isolated/pycache'),str(root/'inputs/pr7620/windows_path_shim.py'),str(script)],cwd=work,env=env,stdout=so,stderr=se,check=False)
    r={'stage':stage,'exit':p.returncode,'wall_seconds':time.monotonic()-start,'run_id':identity['run_id'],'candidate_canonical_sha256':WORD,'adapter_sha256':sha(work/'CONTACT7620-ADAPTERS.json'),'launcher_sha256':sha(HERE/'application.py')}
    if p.returncode==0:
        if stage=='native':validate_native(native,work);r['native_result_sha256']=sha(native)
        else:
            obj=read(work/'producer54/validation_signed/RESULT.json');need(obj['status']==SIGNED,'signed success marker')
            catalogue=obj['catalogue'];need(catalogue and sum(x['checked_maps'] for x in catalogue)==catalogue[0]['catalogue_size'],'complete catalogue')
            cursor=0
            for row in catalogue:
                need(row['slice_start']==cursor and row['slice_stop']-row['slice_start']==row['checked_maps'] and row['word_sha256']==GZIP and row['phase_control_rejected'],'catalogue custody/coverage');cursor=row['slice_stop']
            need(cursor==catalogue[0]['catalogue_size'] and sum(x['main_boundary_pairs'] for x in catalogue)==104,'catalogue boundary closure')
            need(sum(obj['price']['after']['P'].values())==110111 and sum(obj['price']['after']['T'].values())==22461,'complete signed paid/target count')
            r['signed_result_sha256']=sha(work/'producer54/validation_signed/RESULT.json');r['stale_native_results_rejected']=2;r['stale_native_receipt_bindings_rejected']=receipt_controls
    write(work/(stage+'.receipt.json'),r);need(p.returncode==0,'complete '+stage+' application failed')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['prepare','native','signed'],required=True);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    need(__debug__ and sys.version_info[:2]==(3,12),'Python3.12 assertions enabled required')
    if a.stage=='prepare':prepare(a.root.resolve(),a.work.resolve())
    else:execute(a.stage,a.root.resolve(),a.work.resolve())
if __name__=='__main__':main()
