# SPDX-License-Identifier: Apache-2.0
"""Offline native and signed replay for the original-74 #7657 word with the #7643 contact."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
A=SimpleNamespace(**runpy.run_path(str(HERE/'adapt.py')))
CANDIDATE='5ab1da9cae4ffb118ce79270108f879e50365c8adcb89d02d78158ffb0908d8c'
P7645='6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
CALLER='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'


def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)


def write(p,data):
    with p.open('x') as out:
        json.dump(data,out,indent=2,sort_keys=True)
        out.write('\n')


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def digest(x):
    return sha256(x).hexdigest()


def execute(script):
    subprocess.run([sys.executable,'-I','-B',str(script)],cwd=script.parent,check=True)


def prepare(pkg,work):
    src=pkg/'sources'
    for name,pin in read(HERE/'source-pins.json').items():
        assert digest((src/name).read_bytes())==pin,name
    p44=src/'7647/closure/pr7644';p57=src/'7657'; scientific=src/'7647/application/source'
    p05=p44/'retained/pr7605'
    word_path=pkg/'inputs/candidate.json.gz'
    word=read(word_path)
    assert digest(canonical(word))==CANDIDATE
    work.mkdir(parents=True,exist_ok=False)
    b=work/'reconstruction';b.mkdir()
    for name in ('build_candidate.py','combined.py','word_checks.py','generate.py','compose_edits.py'):
        shutil.copyfile(p57/'src'/name,b/name)
    # Only these four original inputs are read by the upstream construction scripts.
    for name in ('data/word.json.gz','data/invoice.json','data/peer7611.json','retained/pr7605/data/word.json.gz'):
        out=b/'source7644'/name
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p44/name,out)
    execute(b/'build_candidate.py')
    execute(b/'combined.py')
    for old,new in [('candidate.json.gz','baseline.json.gz'),('combined-edits.json','baseline-edits.json'),('candidate-invoice.json','baseline-invoice.json')]:
        (b/old).rename(b/new)
    base=read(b/'baseline.json.gz')
    assert digest(canonical(base))==P7645 and base==read(pkg/'inputs/base7645.json.gz')
    assert digest((b/'baseline-invoice.json').read_bytes())=='7d54c1ec036d4c096526dd95e06892ca99210812d51a503b22f6d78243330ca9'
    execute(b/'generate.py')
    execute(b/'compose_edits.py')
    prior=read(b/'candidate.json.gz')
    assert digest(canonical(prior))==A.BASE and prior==read(pkg/'inputs/peer7657.json.gz')
    contact=SimpleNamespace(**runpy.run_path(str(HERE/'contact_word.py')))
    local=contact.splice(prior,read(scientific/'7612-CONTACT.json'))
    assert word==dict(prior,program=[e for _,e in local])
    legacy=SimpleNamespace(**runpy.run_path(str(p57/'src/run.py')))
    caller=p05/'retained/role902/upstream/inputs/pr7113' # signed caller supplied by the package
    caller_path=pkg/'inputs/caller.json'
    assert digest(caller_path.read_bytes())==CALLER
    recount=runpy.run_path(str(scientific/'recount.py'))
    invoice=recount['invoice']; diff=recount['difference']
    caller=read(caller_path)
    r45,r57,after=[invoice(w,caller) for w in (base,prior,word)]
    for c in (r45,r57,after):
        assert c['calls']==17 and c['life']==74 and c['peak']==50
        for field in ('targets','native_targets','owned_rise','caller_paid','caller_targets'):
            assert c[field]==after[field]
    assert diff(after['events'],r57['events'])=={'MOVE':-1}
    assert diff(after['native_paid'],r57['native_paid'])==A.FEE
    assert diff(after['paid'],r57['paid'])=={r:17*n for r,n in A.FEE.items()}
    def bill(x):
        return {**read(b/'baseline-invoice.json'),'targets':{str(k):v for k,v in x['targets'].items()},
                'paid':{str(k):v for k,v in x['paid'].items()}}
    assert bill(r45)==read(b/'baseline-invoice.json')
    for label,raw in (('7645',r45),('7657',r57)):
        observed=read(src/label/'evidence/SIGNED-RESULT.json')['price']['after']
        assert (observed['T'],observed['P'])==(bill(raw)['targets'],bill(raw)['paid'])
    write(b/'candidate-invoice.json',bill(r57))
    assert digest((b/'candidate-invoice.json').read_bytes())=='fa0c37a9e67d0a82850c4fcfd5cbdb3bd88e1f8db329176e5669da6c7788f6a2'
    assert after['scalar_upper']==r57['scalar_upper']
    ordinary=read(p57/'evidence/FINAL.json')['ordinary_bound']-17*1000
    appdir=work/'application'
    legacy.prepare(SimpleNamespace(package=p05,word=b/'candidate.json.gz',edits=b/'combined-edits.json',sha=A.BASE,
                                   invoice=b/'candidate-invoice.json',incumbent=b/'baseline-invoice.json',claim=A.OLD_CLAIM),appdir)
    f=appdir/'frozen-composition'
    for label in ('7645','7657'):
        for old,new in [('FINAL','FINAL'),('SIGNED-RESULT','SIGNED')]:
            shutil.copyfile(src/label/'evidence'/(old+'.json'),f/(label+'-'+new+'.json'))
    shutil.copyfile(p57/'evidence/NATIVE-RESULT.json',f/'7657-NATIVE.json')
    shutil.copyfile(b/'candidate.json.gz',f/'7657-WORD.json.gz')
    shutil.copyfile(b/'candidate-invoice.json',f/'7657-INVOICE.json')
    shutil.copyfile(scientific/'7612-CONTACT.json',f/'CONTACT.json')
    shutil.copyfile(HERE/'contact_word.py',appdir/'contact_word.py')
    shutil.copyfile(word_path,appdir/'producer54/reroute/WORD.json.gz')
    shutil.copyfile(word_path,f/'CANDIDATE-WORD.json.gz')
    bill_out=f/'CANDIDATE-INVOICE.json'
    bill_out.write_text(json.dumps(bill(after),sort_keys=True,indent=2)+'\n')
    write(appdir/'DERIVATION.json',dict(ordinary=ordinary,scalar_delta=0,native_move_delta=-1,
                                       prior_events=len(prior['program']),candidate_events=len(word['program'])))
    original=read(appdir/'FROZEN.json')
    old_fee={int(r):17*n for r,n in original['delta'].items()}
    history={}
    for stage in ('native','signed','final'):
        path=appdir/'final_application.py' if stage=='final' else appdir/f'producer54/validation_{stage}/run.py'
        previous=path.read_text()
        edits=[]
        if stage=='native': code=A.native(previous,CANDIDATE,(scientific/'7643-native.py').read_text(),edits)
        elif stage=='signed': code=A.signed(previous,CANDIDATE,old_fee,edits)
        else: code=A.final(previous,edits)
        path.write_text(code)
        history[stage]=dict(source=digest(previous.encode()),adapted=digest(code.encode()),edits=edits)
    write(appdir/'APPLICATION-ADAPTATIONS.json',history)
    pins={str(p.relative_to(appdir)):digest(p.read_bytes()) for p in sorted(appdir.rglob('*')) if p.is_file()}
    write(work/'CUSTODY.json',dict(candidate=CANDIDATE,prepared=pins))
    print('PASS_CONTACT7657_PREPARED',CANDIDATE,A.CLAIM,ordinary,flush=True)


def price(pkg,work,appdir):
    f=appdir/'frozen-composition'
    old=pkg/'sources/7647/closure/pr7644/retained/pr7605'
    e=runpy.run_path(str(old/'retained/pricing/evaluate_recursive_power.py'))
    interval=runpy.run_path(str(old/'retained/role902/engines/interval_gate.py'))
    claim=Q(A.CLAIM)
    signed=read(appdir/'producer54/validation_signed/RESULT.json')
    lo,hi=map(Q,signed['price']['gate']['raw_bracket'])
    probes=[('candidate_claim','CANDIDATE',claim,1),('candidate_guard','CANDIDATE',claim+Q(7,10**14),1),
            ('candidate_raw_lower','CANDIDATE',lo,1),('candidate_raw_upper','CANDIDATE',hi,-1)]
    for label in ('7645','7657'):
        prior=read(f/(label+'-FINAL.json'))
        assert Q(prior['raw_crossing'][1])<claim
        probes.extend([(label+'_at_new_claim',label,claim,-1),(label+'_raw_upper',label,Q(prior['raw_crossing'][1]),-1)])
    result={}
    for name,which,k,sign in probes:
        inv,_=e['load_invoice'](f/(which+'-INVOICE.json'))
        bound=e['evaluate'](dict(inv,targets={},paid={}),inv,1-k,bits=256)
        assert bound['classification']==('new_cost_lower' if sign==1 else 'new_cost_higher'),name
        moments={int(r):inv['targets'].get(r,0)-inv['paid'].get(r,0) for r in inv['targets'].keys()|inv['paid'].keys()}
        low,high=interval['moment'](moments,k)
        assert (low>0 if sign==1 else high<0),name
        result[name]=dict(kappa=str(k),integer_power=bound,directed_moment=[str(Q(x,interval['B'])) for x in (low,high)])
    write(work/'DIRECTED-PRICE.json',result)


def stage(name,pkg,work):
    app=work/'application'
    custody=read(work/'CUSTODY.json')
    assert custody['candidate']==CANDIDATE
    for rel,pin in custody['prepared'].items():
        assert digest((app/rel).read_bytes())==pin,rel
    if name=='signed':
        native=read(work/'native-exit.json')
        assert native['exit']==0 and native['candidate']==CANDIDATE
        assert native['result_sha256']==digest((app/'producer54/validation_native/NATIVE-RESULT.json').read_bytes())
    cmd=[sys.executable,'-I','-B','-X','pycache_prefix='+str(app/'isolated/pycache'),str(app/f'producer54/validation_{name}/run.py')]
    env=dict(os.environ,TMPDIR=str(app/'isolated'),PYTHONPYCACHEPREFIX=str(app/'isolated/pycache'),
             OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    started=datetime.now(timezone.utc).isoformat(); tick=time.monotonic()
    with (work/(name+'.stdout')).open('x') as out,(work/(name+'.stderr')).open('x') as err:
        proc=subprocess.run(cmd,cwd=app,env=env,stdout=out,stderr=err)
    result=dict(stage=name,exit=proc.returncode,candidate=CANDIDATE,started_utc=started,
                ended_utc=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-tick)
    path=app/f'producer54/validation_{name}'/('NATIVE-RESULT.json' if name=='native' else 'RESULT.json')
    if not proc.returncode:
        result['result_sha256']=digest(path.read_bytes())
    write(work/(name+'-exit.json'),result)
    if proc.returncode:
        print((work/(name+'.stderr')).read_text(),file=sys.stderr)
        raise SystemExit(proc.returncode)
    actual=read(path)
    assert actual['status']==(A.NATIVE if name=='native' else A.SIGNED)
    # Elapsed time is recorded separately. All substantive native and signed fields
    # are available for registered comparison.
    write(work/(name+'-science.json'),{k:v for k,v in actual.items() if k not in ('timings','elapsed_seconds')})
    if name=='signed':
        ns=dict(read=read,canonical=canonical,digest=digest,Q=Q,NATIVE_MARKER=A.NATIVE,SIGNED_MARKER=A.SIGNED,
                RETAINED=pkg/'sources/7647/closure/pr7644/retained/pr7605/retained/role902')
        path=app/'final_application.py'
        exec(compile(path.read_text(),str(path),'exec'),ns)
        final=ns['final_application'](app)
        assert final['candidate_canonical_sha256']==CANDIDATE
        price(pkg,work,app)
        write(work/'FINAL.json',final)
        print(json.dumps(final,sort_keys=True),flush=True)
    print('PASS_CONTACT7657_'+name.upper(),flush=True)


if __name__=='__main__':
    assert __debug__ and sys.version_info[:2]==(3,12) and sys.dont_write_bytecode
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('prepare','native','signed'))
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    pkg,work=args.package.resolve(),args.work.resolve()
    if args.stage=='prepare':
        prepare(pkg,work)
    else:
        stage(args.stage,pkg,work)
