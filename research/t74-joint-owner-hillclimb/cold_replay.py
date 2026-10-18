"""Replay the changed owner construction, with cold or source-bound reuse.

The immutable predecessor supplies the unchanged native words and admitted
parent construction. Without --baseline their complete admission runs first.
The changed data always receives fresh discovery, strict physical invoice,
controller checks, moment certification and fine-prime outer verification.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',type=Path,required=True)
    ap.add_argument('--candidate-source-root',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,
                    help='Reuse a complete pinned upstream verify directory')
    ap.add_argument('--data',type=Path,default=HERE/'data')
    ap.add_argument('--base-word',type=Path)
    ap.add_argument('--extra-word',type=Path)
    ap.add_argument('--base-native',type=Path,
                    help='Reuse complete native evidence for the bundled changed base word')
    ap.add_argument('--extra-native',type=Path,
                    help='Reuse complete native evidence for the bundled changed extra word')
    ap.add_argument('--work',type=Path,required=True)
    a=ap.parse_args()
    if not __debug__:raise RuntimeError('Assertions must be enabled')
    work=a.work.resolve();work.mkdir(parents=True,exist_ok=False)
    source=a.source_root.resolve();data=a.data.resolve()
    from upstream_replay import check_manifest, PACKAGE_PATH
    check_manifest(source/PACKAGE_PATH)
    from native_evidence import _source_binding
    _source_binding(a.candidate_source_root.resolve()/'research/gmx-t74-borrow43-width-exchange')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',
             OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')

    def run(name,script,*args):
        log=work/(name+'.log')
        with log.open('w') as stream:
            r=subprocess.run([sys.executable,'-B',str(HERE/script),*map(str,args)],
                             env=env,stdout=stream,stderr=subprocess.STDOUT)
        if r.returncode:
            raise RuntimeError(name+' failed: '+log.read_text()[-2500:])
        print('PASS',name,flush=True)

    baseline=a.baseline.resolve() if a.baseline else work/'upstream/verify'
    if not a.baseline:
        run('upstream','upstream_replay.py','--source-root',source,'--work',work/'upstream')
    native_options=[]
    changed_words={}
    for kind in ['base','extra']:
        word=getattr(a,kind+'_word')
        bundled=HERE/'words'/(kind+'.json.gz')
        if word is None and bundled.is_file():word=bundled
        native=getattr(a,kind+'_native')
        if word is None:
            assert native is None,'A changed native cache requires its exact input word'
            continue
        word=word.resolve();assert word.is_file()
        if native is None:
            native=work/('native-'+kind)
            script=a.candidate_source_root.resolve()/'research/gmx-t74-borrow43-width-exchange/new/run_native_borrow.py'
            log=work/('native-'+kind+'.log')
            with log.open('w') as stream:
                r=subprocess.run([sys.executable,'-B',str(script),str(word),str(native)],
                                 env=env,stdout=stream,stderr=subprocess.STDOUT)
            if r.returncode:
                raise RuntimeError('Changed native '+kind+' failed: '+log.read_text()[-2500:])
            print('PASS native-'+kind,flush=True)
        native_options += ['--'+kind+'-native',str(native.resolve()),
                           '--'+kind+'-word',str(word)]
        changed_words[kind]={'word_sha256':sha(word),'reused_native':bool(getattr(a,kind+'_native'))}
    run('changed-owner','delta_replay.py','--source-root',source,'--baseline',baseline,
        '--candidate-source-root',a.candidate_source_root.resolve(),
        '--data',data,'--work',work/'delta',*native_options)
    result=json.loads((work/'delta/DELTA-ADMISSION.json').read_bytes())
    assert result['status']=='PASS_CHANGED_T74_FULL_DELTA_ADMISSION'
    assert result['genuine_improvement_over_pr2288']
    assert result['genuine_improvement_over_pr2312']
    receipt=dict(status='PASS_SOURCE_BOUND_CHANGED_OWNER_REPLAY',
                 reused_baseline=bool(a.baseline),
                 changed_words=changed_words,
                 baseline_head=result['baseline_head'],
                 source_manifest_sha256=result['source_manifest_sha256'],
                 adopted_supplier_head=result['adopted_supplier_head'],
                 comparison_supplier=result['comparison_supplier'],
                 final_kappa=result['final_kappa'],gain=result['gain'],
                 delta_receipt_sha256=sha(work/'delta/DELTA-ADMISSION.json'),
                 replay_scripts_sha256={p:sha(HERE/p) for p in
                     ['cold_replay.py','delta_replay.py','upstream_replay.py',
                      'baseline_cache.py','native_evidence.py','fetch_upstream.py',
                      'fetch_suppliers.py','owner_binding.py']},
                 native_evidence_manifests_sha256={kind:
                     sha(HERE/'evidence/native-bindings'/(kind+'.json'))
                     for kind in changed_words},
                 scope=result['scope'])
    (work/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],flush=True)


if __name__=='__main__':main()
