#!/usr/bin/env python3
"""One fixed, serial differential qualification; all work stays in one cgroup."""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def bindings(out):
    controls=read(out/'CONTROLS.json');need(controls['status']=='PASS_SOURCE_FREE_CONTROLS','source-free controls missing')
    b=read(out/'built/edit-manifest.json');e=read(out/'exact/status.json')
    need(e['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY','exact success missing')
    need(e['exact_gzip_sha256']==sha(out/'exact/EXACT.json.gz'),'exact gzip changed')
    r=read(out/'rankone/RANKONE.json');rs=read(out/'rankone/status.json')
    need(rs['status']==r['status']=='RANKONE_ONLY_UNQUALIFIED','rankone success missing')
    need(r['exact_gzip_sha256']==e['exact_gzip_sha256'] and r['exact_sha256']==e['exact_sha256'] and r['exact_status_sha256']==sha(out/'exact/status.json'),'rankone/exact mismatch')
    need(r['candidate_word_canonical_sha256']==b['candidate_canonical_sha256'] and r['candidate_word_gzip_sha256']==b['candidate_gzip_sha256'],'rankone candidate mismatch')
    p=read(out/'physical/PHYSICAL.json');ps=read(out/'physical/status.json')
    need(ps['status']==p['status']=='CHANGED_ROUTE_PHYSICAL_DIFFERENTIAL_PASS_UNQUALIFIED','physical success missing')
    need(p['source_word_canonical_sha256']==r['source_word_canonical_sha256'] and p['candidate_word_canonical_sha256']==b['candidate_canonical_sha256'] and p['candidate_gzip_sha256']==b['candidate_gzip_sha256'],'physical source/candidate mismatch')
    z=read(out/'price/PRICE.json');need(z['status']=='PROVISIONAL_UNDER_COMMON_U','provisional pricing missing')
    need(z['bindings']['candidate_canonical_sha256']==b['candidate_canonical_sha256'] and z['bindings']['exact_gzip_sha256']==e['exact_gzip_sha256'] and z['bindings']['manifest_sha256']==sha(out/'built/edit-manifest.json'),'price source/exact mismatch')
    return {str(p.relative_to(out)):sha(p) for p in (out/'CONTROLS.json',out/'built/candidate-word.json.gz',out/'built/edit-manifest.json',out/'built/status.json',out/'exact/EXACT.json.gz',out/'exact/status.json',out/'rankone/RANKONE.json',out/'rankone/status.json',out/'physical/PHYSICAL.json',out/'physical/status.json',out/'price/PRICE.json',out/'price/invoice-source-normalized.json',out/'price/invoice-new.json')}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir();t0=time.monotonic();deadline=t0+580;rows=[]
    need(__debug__,'assertion-dependent retained oracles require normal Python')
    stages=[('controls','controls.py',5,[]),('built','build.py',10,[]),('exact','exact.py',220,['--built',str(a.out/'built')]),('rankone','rankone.py',80,['--built',str(a.out/'built'),'--exact',str(a.out/'exact')]),('physical','physical.py',200,['--built',str(a.out/'built')]),('price','price.py',70,['--built',str(a.out/'built'),'--exact',str(a.out/'exact')])]
    report={'status':'INCOMPLETE','stages':rows,'qualified_kappa':False,'scope':'One differential/scalar/changed-phase/provisional-invoice gate. Fresh native/signed/common-U resource qualification remains required.'}
    try:
        for name,script,cap,extra in stages:
            left=deadline-time.monotonic();need(left>0,'combined 580-second conservative deadline')
            argv=([sys.executable,'-I','-B',str(HERE/script),'--out',str(a.out/'CONTROLS.json')] if name=='controls' else [sys.executable,'-I','-B',str(HERE/script),'--root',str(a.root),'--out',str(a.out/name),*extra])
            begin=time.monotonic()
            with (a.out/(name+'.stdout')).open('x') as so,(a.out/(name+'.stderr')).open('x') as se:
                p=subprocess.run(argv,stdout=so,stderr=se,timeout=min(cap,left),check=False,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
            row={'name':name,'argv':argv,'exit_code':p.returncode,'wall_seconds':time.monotonic()-begin,'stage_cap_seconds':cap};rows.append(row);write(a.out/'PARTIAL.json',report)
            print(json.dumps(row,sort_keys=True),flush=True);need(p.returncode==0,'failed '+name)
            if name=='controls':
                need(read(a.out/'CONTROLS.json')['status']=='PASS_SOURCE_FREE_CONTROLS','controls receipt not passed')
                row['receipt_sha256']=sha(a.out/'CONTROLS.json');write(a.out/'PARTIAL.json',report)
        report['receipt_hashes']=bindings(a.out)
        need(report['receipt_hashes']['CONTROLS.json']==rows[0]['receipt_sha256'],'controls receipt changed after stage')
        report['status']='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U'
    except BaseException as e:
        report.update(error_type=type(e).__name__,error=str(e))
    report['wall_seconds']=time.monotonic()-t0;write(a.out/'RESULT.json',report);print(json.dumps({'status':report['status'],'wall_seconds':report['wall_seconds']},sort_keys=True),flush=True)
    return 0 if report['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U' else 1
if __name__=='__main__':raise SystemExit(main())
