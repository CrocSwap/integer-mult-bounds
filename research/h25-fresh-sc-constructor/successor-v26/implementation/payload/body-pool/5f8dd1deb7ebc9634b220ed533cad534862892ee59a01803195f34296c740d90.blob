"""One serial complete replay; no automatic retries or performance selection."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types
ROOT=Path(__file__).resolve().parent
pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('replay.py','archive_support.py'):
    if sha256((ROOT/name).read_bytes()).hexdigest()!=pins[name]:raise ValueError('replay source pin: '+name)
S=types.ModuleType('_gf2_full_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def run(arm,evidence,timeout=180):
    import fcntl
    import os
    import tempfile
    S.need(arm in ('B','C') and type(timeout) is int and 1<=timeout<=180,'bounded single B/C replay')
    S.need(sys.platform=='linux' and sys.version_info[:2]==(3,12) and sys.flags.optimize==0,'Linux CPython3.12 with full assertions')
    manifest=S.authenticate();evidence=S.external(evidence)
    guard=S.source_module('_gf2_full_guard',ROOT/'guard.py')
    lock_path=Path(tempfile.gettempdir())/('croc-gf2-full-'+sha256(str(ROOT).encode()).hexdigest()[:20]+'.lock')
    with lock_path.open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        evidence.mkdir(parents=True)
        guard.HERE=evidence;guard.SOURCE=ROOT
        guard.CLOSURE=tuple(sorted(set(manifest['files'])|{'CODE-SOURCES.json'}))
        guard.TIMEOUT=timeout;guard.RSS_CAP=1024**3;guard.AGGREGATE=timeout
        prior=os.environ.get('CROC_GF2_FULL_OUTPUT')
        os.environ['CROC_GF2_FULL_OUTPUT']=str(evidence/'scientific')
        try:
            receipt=guard.run('complete-'+arm,'full_'+arm+'.py',False)
        finally:
            if prior is None:os.environ.pop('CROC_GF2_FULL_OUTPUT',None)
            else:os.environ['CROC_GF2_FULL_OUTPUT']=prior
        S.authenticate()
        scientific=json.loads((evidence/'scientific/receipt.json').read_text())
        anchor=json.loads((ROOT/'anchor.json').read_text())
        S.need(receipt['status']=='PASS' and scientific['status']=='FULL_NETWORK_COMPLETE_PASS' and scientific['science']==anchor['science'],'complete frozen caller and retained exact science')
        S.need(scientific['mode']==('baseline' if arm=='B' else 'candidate'),'requested complete arm')
        return dict(guard=receipt,scientific=scientific,evidence=str(evidence),automatic_retries=0)


def main():
    S.need(len(sys.argv)==3 and sys.argv[1] in ('B','C'),'replay.py B|C NEW_EXTERNAL_EVIDENCE_DIRECTORY')
    result=run(sys.argv[1],Path(sys.argv[2]))
    print(json.dumps(dict(status='PASS_FRESH_FULL_REPLAY',evidence=result['evidence'],new_timings_replace_fixed_samples=False)))


if __name__=='__main__':main()
