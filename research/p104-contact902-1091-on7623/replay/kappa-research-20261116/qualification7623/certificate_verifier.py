#!/usr/bin/env python3
"""Run the minimally adapted standalone oracle and its controls on both words."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

VERIFIER_SHA='74447393f6b5b1baa0823e7dc73ec26daa8bd0b39436ccd6eac457bddd94bad8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,s):
    if not x:raise ValueError(s)
def run(root,gate,prepared,out):
    root,gate,prepared,out=map(Path,(root,gate,prepared,out));out.mkdir(parents=True,exist_ok=False);start=time.monotonic();records=[]
    report={'status':'INCOMPLETE','verifications':records,'scope':'180 public-column linear CLEAR relations only; common U and physical erasure unimplemented'}
    try:
        verifier=Path(__file__).with_name('verify_certificates.py');need(sha(verifier)==VERIFIER_SHA,'standalone verifier hash')
        prep=json.loads((prepared/'status.json').read_text());need(prep['status']=='PREPARED_RELATIONS_UNVERIFIED_EXTERNALLY','preparation incomplete')
        need(prep['gate_result_sha256']==sha(gate/'RESULT.json'),'gate receipt changed')
        for side,word,cert in [('source',root/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data/word.json.gz',prepared/'source-certificate.json'),('candidate',gate/'built/candidate-word.json.gz',prepared/'certificate.json')]:
            limit=180-(time.monotonic()-start);need(limit>0,'180 second deadline')
            proc=subprocess.run([sys.executable,'-I','-B',str(verifier),str(word),str(cert)],capture_output=True,text=True,timeout=limit,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
            (out/(side+'.stdout')).write_text(proc.stdout);(out/(side+'.stderr')).write_text(proc.stderr)
            row={'side':side,'exit_code':proc.returncode,'word_sha256':sha(word),'certificate_sha256':sha(cert),'stdout_sha256':sha(out/(side+'.stdout'))};records.append(row)
            need(proc.returncode==0 and 'CLEARs checked=180 failures=[]' in proc.stdout and 'control corrupted coefficient' in proc.stdout and 'control cleared-field-as-term' in proc.stdout and proc.stdout.count('rejected: True')==2 and 'PASS_CLEAR_CERTIFICATES' in proc.stdout,'standalone or controls failed: '+side)
        report['status']='PASS_SOURCE_AND_CANDIDATE_PUBLIC_CLEAR_RELATIONS_ONLY'
    except Exception as e:report.update(error_type=type(e).__name__,error=str(e))
    report['wall_seconds']=time.monotonic()-start;(out/'status.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--gate',required=True);p.add_argument('--prepared',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    return 0 if run(a.root,a.gate,a.prepared,a.out)['status']=='PASS_SOURCE_AND_CANDIDATE_PUBLIC_CLEAR_RELATIONS_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
