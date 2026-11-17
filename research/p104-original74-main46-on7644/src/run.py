# SPDX-License-Identifier: Apache-2.0
"""Apply the original helper757 native and signed application engines to a frozen derived word."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import inspect
import json
import os
from pathlib import Path
import runpy
import shutil
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
BASE = 'e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd'
PINS = {
    'application.py':'b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e',
    'build.py':'db60577c9cf43d2d7d83b3452c47e3eb43096e566984c3f9c26309238fbc6396',
    'SOURCE-VERSIONS.json':'ce3910302d76c9050c14e1a40edf498be7dd4c5e32773e9ce7384ab99fd27410',
    'data/word.json.gz':'37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d',
    'data/NATIVE.json':'0ada1e2e7de8887e6ebbd16cda3c8b9738d71873857657ff4fa6e180653cf888',
    'data/SIGNED.json':'0dda72ce4f1612ee6c8b6f4078b538f972d24b0108552d6ec50e545a1458cc16',
    'data/invoice-new.json':'b38afd7ca590b5c4c301ee4fbe0e123f0c7220c2bd1f40c66adf208652e3ce15',
    'data/FINAL.json':'f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add',
}

def module(path):
    return SimpleNamespace(**runpy.run_path(str(path)))


def write(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2)+'\n')


def patch(text, edits, history):
    for before, after in edits:
        assert text.count(before)==1, ('Expected one occurrence', before)
        text = text.replace(before,after)
        history.append(dict(before=before,after=after,occurrences=1))
    return text


def native_patches(c):
    return [
        ("PATCHES=[]", "support=load('chart1062_support', ROOT/'word_checks.py')\nPATCHES=[]"),
        ("    routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}", 
         "    routes=lambda w:dict(enumerate(support.routes(w)))"),
        ("    report=[]", """    base=read(ROOT/'frozen-composition/7605-WORD.json.gz')
    triples,_=support.chart_contract(base,word)
    affected |= {pair for a,b,c in triples for pair in ((a,b),(b,c),(a,c))}
    maps={}
    report=[]"""),
        ("        actual=interpreter.recipe(recipe)", "        actual=interpreter.recipe(recipe)\n        maps[a,b]=actual"),
        ("    return {'all_affected_pairs':report", "    composed=support.physical(interpreter,maps,triples)\n    return {'composed_1062':composed,'all_affected_pairs':report"),
        ("        need(new==dict(peer,program=emitted),'Exact timed helper757 word and unchanged metadata')",
         f"""        baseline=read(ROOT/'frozen-composition/7605-WORD.json.gz')
        need(baseline==dict(peer,program=emitted),'Exact timed helper757 word and unchanged metadata')
        need(sha256(canonical(baseline)).hexdigest()=='{BASE}','Exact #7605 canonical word')
        path=ROOT/'frozen-composition/EDITS.json'
        need(sha256(path.read_bytes()).hexdigest()=='{c['edit_sha']}','Frozen #7605 patch')
        tagged=support.reconstruct(baseline,read(path))
        need(new==dict(baseline,program=[e for _,e in tagged]),'Exact frozen edit on original #7605')
        triples,expected_delta=support.chart_contract(baseline,new)
        need(expected_delta=={c['delta']!r},'Expected native change from original routes')"""),
        ("        oldN,peerN,N=map(I.native,(old,peer,new))", """        oldN,peerN,baselineN,N=map(I.native,(old,peer,baseline,new))
        baseline_receipt=read(ROOT/'frozen-composition/7605-NATIVE.json')
        need(normalized(baselineN)==baseline_receipt['native'] and baseline_receipt['word_canonical_sha256']==sha256(canonical(baseline)).hexdigest(),'Exact original #7605 inventory')
        need(all(N[k]==baselineN[k]for k in('public','helpers','rises','owned_peak','lifetimes','bad_inputs')),'Fixed #7605 ownership and target contract')
        need(delta(N['paid'],baselineN['paid'])==expected_delta,'Measured paid difference from #7605')"""),
        ("delta(N['paid'],peerN['paid'])=={1:-2,2:1}", "delta(baselineN['paid'],peerN['paid'])=={1:-2,2:1}"),
        ("delta(N['paid'],oldN['paid'])=={1:-7,2:-5,4:1,6:1,7:1}", "delta(baselineN['paid'],oldN['paid'])=={1:-7,2:-5,4:1,6:1,7:1}"),
        ("len(new['program'])==len(old['program'])+164", f"len(baseline['program'])==len(old['program'])+164 and len(new['program'])=={c['length']}"),
        ("        forward,grid=audit.replay(new,list(enumerate(new['program'])),set())", "        forward,grid,base_forward,protected=support.inspect_owned_contacts(baseline,new,tagged,audit)"),
        ("        controls={}", "        controls=support.negatives(new,tagged,base_forward,protected,audit,I.native,rejects,triples)"),
        ("native=N,forward=forward_receipt", "native=N,original_7605_operand_clocks=len(protected),original_7605_clear_rows=len(base_forward[2]),forward=forward_receipt"),
        ("PASS_HELPER757_COMPLETE_NATIVE", "PASS_CHART1062_COMPLETE_NATIVE"),
    ]


def signed_patches(c):
    return [
        ("PASS_HELPER757_COMPLETE_NATIVE","PASS_CHART1062_COMPLETE_NATIVE"),
        ("PASS_HELPER757_COMPLETE_SIGNED_APPLICATION","PASS_CHART1062_COMPLETE_SIGNED_APPLICATION"),
        ("  assert delta=={1:-102,2:-51,3:17,4:17,5:17} and after['T']==before['T']",
         """  bword=read(FROZEN/'7605-WORD.json.gz')
  bnative=ind.native(bword)
  assert sha256(canonical(bword)).hexdigest()=='""" + BASE + """' and normal(bnative)==read(FROZEN/'7605-NATIVE.json')['native'] and not bnative['bad_inputs']
  binvoice=ind.invoices(bword,C,bnative)
  prior=read(FROZEN/'7605-SIGNED.json')['price']
  assert normal(binvoice)==prior['after'] and after['T']==binvoice['T']==before['T']
  assert binvoice['S']==1424 and not binvoice['empty_root_credits']
  def diff(x,y):return {r:x.get(r,0)-y.get(r,0) for r in set(x)|set(y) if x.get(r,0)!=y.get(r,0)}
  assert diff(binvoice['P'],before['P'])=={1:-102,2:-51,3:17,4:17,5:17}
  assert diff(after['P'],binvoice['P'])==""" + repr({r:17*n for r,n in c['delta'].items()})),
        ("sum(after['P'].values())==110366",f"sum(binvoice['P'].values())==110366 and sum(after['P'].values())=={c['paid']}"),
        ("{r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}=={1:-34,2:17}","diff(binvoice['P'],peer_invoice['P'])=={1:-34,2:17}"),
        ("  public_claim=Q('0.0036504442446')",f"""  public_claim=Q({c['claim']!r})
  assert Q(prior['gate']['raw_bracket'][1])<public_claim<=Q(gate['claim'])
  assert directed.moment(G.signed(binvoice),public_claim)[1]<0,'Immediate incumbent rejects the candidate public claim'"""),
        ("price_record=normal(dict(public_claim_gate=public_gate", "price_record=normal(dict(original_7605=binvoice,original_7605_raw=prior['gate']['raw_bracket'],public_claim_gate=public_gate"),
    ]


def final_source(app,c,history):
    text = inspect.getsource(app.final_application)
    return patch(text, [
        ("read(HERE / 'data/word.json.gz')","read(root / 'frozen-composition/CANDIDATE-WORD.json.gz')"),
        ("read(HERE / 'data/invoice-new.json')","read(root / 'frozen-composition/CANDIDATE-INVOICE.json')"),
        ("assert sum(invoice['P'].values()) == 110366",f"assert sum(invoice['P'].values()) == {c['paid']}"),
        ("Q('0.0036504442446')",f"Q({c['claim']!r})"),
        ("Q('0.00365044424467')",f"Q({c['claim']!r}) + Q(7,10**14)"),
        ("return dict(status='PASS_HELPER757_FINAL_APPLICATION', claim='0.0036504442446',",
         f"""base = read(root / 'frozen-composition/7605-FINAL.json')
    assert base['assumptions'] == signed['assumptions'] and base['caller_sha256']==signed['caller_sha256']
    assert native['original_7605_clear_rows']==74 and native['original_7605_operand_clocks']>0
    assert len(native['charts']['composed_1062'])=={len(c['triples'])}
    assert partial['crossing_probe_rejected']
    return dict(status='PASS_CHART1062_FINAL_APPLICATION', claim={c['claim']!r},
                original_canonical_sha256={BASE!r}, original_7605_raw=base['raw_crossing'],
                complete_paid_delta={repr({r:17*n for r,n in c['delta'].items()})},
                ordinary_change_over_7605=ordinary-base['ordinary_bound'],
                tape_change_over_7605={{k:tape[k]-base['tape'][k] for k in fields}},"""),
        ("paid_calls=110366",f"paid_calls={c['paid']}"),
    ],history)


def prepare(args,root):
    assert not root.exists()
    u=module(HERE/'word_checks.py')
    for path, pin in PINS.items():
        assert u.digest((args.package/path).read_bytes())==pin, path
    app=module(args.package/'application.py')
    baseline=app.authenticate()
    word=app.read(args.word)
    assert u.digest(app.canonical(baseline))==BASE and u.digest(app.canonical(word))==args.sha
    assert u.digest(args.incumbent.read_bytes())=='5ea13a376c00be2363e9508f23d9ceaf299fb297fb54c82a6cd2b8559aa92bac', 'Pinned #7644 incumbent invoice'
    edits=app.read(args.edits)
    tagged=u.reconstruct(baseline,edits)
    assert dict(baseline,program=[e for _,e in tagged])==word
    triples,delta=u.chart_contract(baseline,word)
    old_bill=app.read(args.package/'data/invoice-new.json')
    bill=app.read(args.invoice)
    assert {k:v for k,v in old_bill.items() if k!='paid'}=={k:v for k,v in bill.items() if k!='paid'}
    assert u.differences({int(r):n for r,n in bill['paid'].items()},
                         {int(r):n for r,n in old_bill['paid'].items()})=={r:17*n for r,n in delta.items()}
    assert Q(args.claim)>Q(app.read(args.package/'data/FINAL.json')['raw_crossing'][1])
    c=dict(sha=args.sha,edit_sha=u.digest(args.edits.read_bytes()),claim=args.claim,triples=triples,delta=delta,
           paid=sum(bill['paid'].values()),length=len(word['program']),package=str(args.package.resolve()))
    app.prepare(root,word)
    f=root/'frozen-composition'
    shutil.copyfile(HERE/'word_checks.py',root/'word_checks.py')
    for name,out in [('word.json.gz','7605-WORD.json.gz'),('NATIVE.json','7605-NATIVE.json'),
                     ('SIGNED.json','7605-SIGNED.json'),('FINAL.json','7605-FINAL.json')]:
        shutil.copyfile(args.package/'data'/name,f/out)
    for path,out in [(args.word,'CANDIDATE-WORD.json.gz'),(args.edits,'EDITS.json'),(args.invoice,'CANDIDATE-INVOICE.json'),(args.incumbent,'7644-INVOICE.json')]:
        shutil.copyfile(path,f/out)
    shutil.copyfile(args.word,root/'producer54/reroute/WORD.json.gz')
    history={}
    for stage,edits in [('native',native_patches(c)),('signed',signed_patches(c))]:
        path=root/f'producer54/validation_{stage}/run.py'
        original=path.read_text()
        records=[]
        new=patch(original,edits,records)
        compile(new,str(path),'exec')
        path.write_text(new)
        history[stage]=dict(original=u.digest(original.encode()),adapted=u.digest(new.encode()),edits=records)
    records=[]
    source=final_source(app,c,records)
    path=root/'final_application.py'
    compile(source,str(path),'exec')
    path.write_text(source)
    history['final']=dict(adapted=u.digest(source.encode()),edits=records)
    write(root/'CHART1062-ADAPTATION.json',history)
    pinned=[p for p in f.iterdir() if p.is_file()]+[root/'word_checks.py',root/'final_application.py',
           root/'producer54/reroute/WORD.json.gz',root/'producer54/validation_native/run.py',
           root/'producer54/validation_signed/run.py',root/'CHART1062-ADAPTATION.json']
    c['prepared_pins']={str(p.relative_to(root)):u.digest(p.read_bytes()) for p in pinned}
    write(root/'FROZEN.json',c)
    print(json.dumps({k:v for k,v in c.items() if k!='prepared_pins'}),flush=True)


def price_check(root,app,c):
    """Independent integer interval prices for old and new; signed stage separately checks log/exp."""
    engine=module(Path(c['package'])/'retained/pricing/evaluate_recursive_power.py')
    old,_=engine.load_invoice(Path(c['package'])/'data/invoice-new.json')
    new,_=engine.load_invoice(root/'frozen-composition/CANDIDATE-INVOICE.json')
    incumbent7644,_=engine.load_invoice(root/'frozen-composition/7644-INVOICE.json')
    zero=dict(new,paid={},targets={})
    signed=app.read(root/'producer54/validation_signed/RESULT.json')
    lo,hi=map(Q,signed['price']['gate']['raw_bracket'])
    claim=Q(c['claim'])
    certs={}
    for label,invo,k,sign in [('incumbent_at_claim',old,claim,'new_cost_higher'),('7644_at_claim',incumbent7644,claim,'new_cost_higher'),('claim',new,claim,'new_cost_lower'),
                              ('tested',new,claim+Q(7,10**14),'new_cost_lower'),('lower',new,lo,'new_cost_lower'),
                              ('upper',new,hi,'new_cost_higher')]:
        bound=engine.evaluate(zero,invo,1-k,bits=256)
        assert bound['classification']==sign,label
        certs[label]={'kappa':str(k),'integer_bounds':bound}
    # A separate directed log/exp interval engine compares both literal invoices.
    interval_path=Path(c['package'])/'retained/role902/engines/interval_gate.py'
    assert module(HERE/'word_checks.py').digest(interval_path.read_bytes())=='60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5'
    directed=module(interval_path)
    def signed_hist(path):
        invo=app.read(path)
        ranks=set(invo['paid']) | set(invo['targets'])
        return {int(r):invo['targets'].get(r,0)-invo['paid'].get(r,0) for r in ranks}
    old_h=signed_hist(root/'frozen-composition/7644-INVOICE.json')
    new_h=signed_hist(root/'frozen-composition/CANDIDATE-INVOICE.json')
    old_interval=directed.moment(old_h,claim)
    new_interval=directed.moment(new_h,claim)
    assert old_interval[1]<0 and new_interval[0]>0, 'Directed decimal interval #7644 comparison'
    certs['logexp_7644_at_claim']={'kappa':str(claim), 'incumbent_interval':list(map(str,old_interval)),
                                  'candidate_interval':list(map(str,new_interval)), 'scale':'10^80'}
    write(root/'DIRECTED-PRICE.json',certs)


def launch(stage,root,package=None,timeout=480):
    c=json.loads((root/'FROZEN.json').read_bytes())
    u=module(HERE/'word_checks.py')
    for name,pin in c['prepared_pins'].items():
        assert u.digest((root/name).read_bytes())==pin,name
    pkg=(package or Path(c['package'])).resolve()
    c['package']=str(pkg)
    for name,pin in PINS.items():
        assert u.digest((pkg/name).read_bytes())==pin,name
    app=module(pkg/'application.py')
    assert u.digest(app.canonical(app.authenticate()))==BASE
    if stage=='signed':
        native_record=app.read(root/'native.receipt.json')
        assert native_record['exit']==0 and native_record['candidate']==c['sha']
        native=root/'producer54/validation_native/NATIVE-RESULT.json'
        assert native_record['result_sha256']==u.digest(native.read_bytes())
        assert app.read(native)['word_canonical_sha256']==c['sha']
    assert not (root/f'{stage}.receipt.json').exists()
    cache=root/'isolated/pycache'
    script=root/f'producer54/validation_{stage}/run.py'
    command=[sys.executable,'-I','-B','-X',f'pycache_prefix={cache}',str(script)]
    environment=dict(os.environ,TMPDIR=str(root/'isolated'),PYTHONPYCACHEPREFIX=str(cache),
                     OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    started=datetime.now(timezone.utc).isoformat(); tick=time.monotonic()
    with (root/f'{stage}.stdout').open('x') as out,(root/f'{stage}.stderr').open('x') as err:
        proc=subprocess.Popen(command,cwd=root,env=environment,stdout=out,stderr=err,start_new_session=True)
        try:
            code=proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            code=124
    receipt=dict(stage=stage,exit=code,seconds=time.monotonic()-tick,started=started,
                 ended=datetime.now(timezone.utc).isoformat(),candidate=c['sha'],command=command)
    if code==0:
        record=root/f'producer54/validation_{stage}'/('NATIVE-RESULT.json' if stage=='native' else 'RESULT.json')
        receipt['result_sha256']=u.digest(record.read_bytes())
    write(root/f'{stage}.receipt.json',receipt)
    print(json.dumps(receipt),flush=True)
    if code:
        sys.stderr.write((root/f'{stage}.stderr').read_text())
        raise SystemExit(code)
    if stage=='signed':
        namespace=vars(app).copy()
        namespace.update(NATIVE_MARKER='PASS_CHART1062_COMPLETE_NATIVE',SIGNED_MARKER='PASS_CHART1062_COMPLETE_SIGNED_APPLICATION')
        source=root/'final_application.py'
        exec(compile(source.read_text(),str(source),'exec'),namespace)
        result=namespace['final_application'](root)
        assert result['candidate_canonical_sha256']==c['sha']
        price_check(root,app,c)
        write(root/'FINAL.json',result)
        print(json.dumps(result,sort_keys=True),flush=True)


def main():
    assert __debug__ and sys.version_info[:2]==(3,12) and sys.dont_write_bytecode, 'Use Python 3.12 -I -B'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('prepare','native','signed'))
    parser.add_argument('--work',type=Path,default=HERE/'work')
    parser.add_argument('--package',type=Path,help='Exact original #7605 research/p104-timed-helper757 directory')
    parser.add_argument('--word',type=Path)
    parser.add_argument('--sha')
    parser.add_argument('--edits',type=Path)
    parser.add_argument('--invoice',type=Path)
    parser.add_argument('--incumbent',type=Path,help='Exact #7644 data/invoice.json')
    parser.add_argument('--claim')
    parser.add_argument('--timeout',type=int,default=480,help='Per-stage process timeout, at most 1800 seconds')
    args=parser.parse_args()
    assert 1 <= args.timeout <= 1800
    root=args.work.resolve()
    assert root.is_relative_to(HERE) and root!=HERE
    if args.stage=='prepare':
        assert all((args.package,args.word,args.sha,args.edits,args.invoice,args.incumbent,args.claim))
        prepare(args,root)
    else:
        launch(args.stage,root,args.package,args.timeout)

if __name__=='__main__':
    main()
