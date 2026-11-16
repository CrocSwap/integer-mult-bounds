#!/usr/bin/env python3
"""One fresh complete native/signed qualification of the already fixed word."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir();root=a.root;out=a.out;work=out/'work';t0=time.monotonic();deadline=t0+2390;rows=[]
    app=[str(HERE/'application.py'),'--root',str(root),'--work',str(work)]
    stages=[('prepare',60,[*app,'--stage','prepare']),('certificates',90,[str(HERE/'certificates.py'),'--root',str(root),'--gate',str(root/'compose7620/run/case'),'--out',str(out/'certificates')]),('certificate-verifier',180,[str(root/'inputs/pr7620/verify_certificates.py'),str(root/'compose7620/run/case/built/candidate-word.json.gz'),str(out/'certificates/certificate.json')]),('native',1250,[*app,'--stage','native']),('signed',780,[*app,'--stage','signed']),('resources',20,[str(HERE/'resources.py'),'--root',str(root),'--work',str(work),'--out',str(out/'resources')])]
    report={'status':'INCOMPLETE','stages':rows,'conditional_application_qualified':False,'supplier_U_implemented':False}
    try:
        for name,cap,tail in stages:
            left=deadline-time.monotonic();need(left>0,'conservative combined deadline')
            argv=[sys.executable,'-I','-B',*tail];start=time.monotonic()
            with (out/(name+'.stdout')).open('x') as so,(out/(name+'.stderr')).open('x') as se:
                p=subprocess.run(argv,stdout=so,stderr=se,check=False,timeout=min(cap,left),env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
            row={'name':name,'argv':argv,'exit_code':p.returncode,'wall_seconds':time.monotonic()-start,'stage_cap_seconds':cap};rows.append(row);write(out/'PARTIAL.json',report);print(json.dumps(row,sort_keys=True),flush=True);need(p.returncode==0,'failed stage '+name)
        r=read(out/'resources/RESOURCE-COMPARISON.json');need(r['status']=='PASS_CONDITIONAL_COMMON_U_APPLICATION','resource conjunction missing')
        signed_receipt=read(work/'signed.receipt.json');need(signed_receipt['stale_native_results_rejected']==2 and set(signed_receipt['stale_native_receipt_bindings_rejected'])=={'run_id','native_result_sha256','adapter_sha256','launcher_sha256'},'stale result/receipt controls missing')
        report.update(status='PASS_QUALIFIED_CONDITIONAL_COMMON_U_KAPPA',conditional_application_qualified=True,claim=r['claim'],claim_decimal=r['claim_decimal'],resource_comparison_sha256=sha(out/'resources/RESOURCE-COMPARISON.json'),native_receipt_sha256=sha(work/'native.receipt.json'),signed_receipt_sha256=sha(work/'signed.receipt.json'),certificate_sha256=sha(out/'certificates/certificate.json'),same_original_premise_dominance_established=False,selected_frontier_changed=False)
    except BaseException as exc:report.update(error_type=type(exc).__name__,error=str(exc))
    report['wall_seconds']=time.monotonic()-t0;write(out/'RESULT.json',report);print(json.dumps({'status':report['status'],'wall_seconds':report['wall_seconds']},sort_keys=True),flush=True)
    return 0 if report['conditional_application_qualified'] else 1
if __name__=='__main__':raise SystemExit(main())
