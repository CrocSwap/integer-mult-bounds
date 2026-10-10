#!/usr/bin/env python3
"""Immutable source regeneration, native admission and independent pricing.

Retains Dugongue's PR254 native pipeline and eumemic's source527 sources.
New retiming composition and wrapper: substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(value,message):
    if not value:raise RuntimeError(message)
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def integrity():
    manifest=read(HERE/'MANIFEST.json')['files']
    actual={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()and p!=HERE/'MANIFEST.json'}
    need(actual==set(manifest),'missing or unexpected package file')
    for name,h in manifest.items():need(sha(HERE/name)==h,'package hash mismatch: '+name)
    return sha(HERE/'MANIFEST.json')
def main():
    need(__debug__,'assertions must remain enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cxx',default='g++')
    ap.add_argument('--boost-include',type=Path)
    args=ap.parse_args();out=args.output.resolve()
    need(out!=HERE and HERE not in out.parents and not out.exists(),'output must be new and outside the package')
    before=integrity();started=time.monotonic()
    cmd=[sys.executable,'-B',str(HERE/'source/verify.py'),'--output',str(out),'--cxx',args.cxx]
    if args.boost_include:cmd+=['--boost-include',str(args.boost_include.resolve())]
    subprocess.run(cmd,check=True)
    subprocess.run([sys.executable,'-B',str(HERE/'independent_price.py'),str(out)],check=True)
    fresh=read(out/'CERTIFICATE.json');independent=read(out/'INDEPENDENT-PYTHON-PRICE.json');result=read(HERE/'RESULT.json')
    need(fresh['baseline_regenerated_from_source']and fresh['package_inputs_unchanged'],'fresh immutable source replay required')
    need(fresh['package_manifest_sha256']==result['source_package_manifest_sha256'],'pinned source package identity')
    need(fresh['kappa']==independent['kappa']==result['kappa'],'native/independent/declared price disagreement')
    need(independent==read(HERE/'expected/INDEPENDENT-PYTHON-PRICE.json'),'independent fresh receipt differs')
    need(before==integrity(),'input manifest changed during replay')
    certificate=dict(status='PASS_IMMUTABLE_PR254_PLUS25_NATIVE_ADMISSION_AND_TWO_INDEPENDENT_PYTHON_MOMENTS',
                     kappa=result['kappa'],kappa_decimal=result['kappa_decimal'],
                     parent_head=result['parent_head'],parent_kappa=result['parent_kappa'],
                     manifest_sha256=before,source_package_manifest_sha256=fresh['package_manifest_sha256'],
                     baseline_regenerated_from_source=True,package_inputs_unchanged=True,
                     native_checkers=7,post_retiming_and_all_used_prime_checks=True,
                     independent_python_moment_engines=2,strict_outer_constraints=47,
                     adjacent_coarse_and_kappa_rejected=True,new_record_sha256=fresh['new_record_sha256'],
                     inherited_all_size_interfaces=True,lean_certificate=False,
                     public_eight_stage_python_replay_claimed=False,
                     elapsed_seconds=time.monotonic()-started)
    (out/'RETIMING-CERTIFICATE.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print('PASS full PR254-plus25 package: kappa = '+result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
