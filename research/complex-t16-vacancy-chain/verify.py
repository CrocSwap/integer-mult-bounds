"""Reconstruct four placements, then run the unchanged strict T16 admission."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def run(main,work):
    pins=json.loads((P/'INPUTS.json').read_text())
    for name,h in pins.items():assert sha(main/name)==h,'Changed dependency: '+name
    package_pins=json.loads((P/'MANIFEST.json').read_text())
    actual={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f!=P/'MANIFEST.json' and '__pycache__' not in f.parts}
    assert actual==package_pins,'Package inventory mismatch'
    modspec=importlib.util.spec_from_file_location('vacancy_build',P/'build.py')
    mod=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(mod)
    blobs=mod.derive(main)
    for name,b in zip(('OWNERS.json.gz','PLAN.json','SPEC.json'),blobs):
        assert b==(P/'data'/name).read_bytes(),'Reconstruction mismatch: '+name
    source=work/'source';source.mkdir(parents=True)
    archive=main/'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
    with tarfile.open(archive) as t:
        for m in t.getmembers():
            assert m.isfile() and (source/m.name).resolve().is_relative_to(source.resolve())
        t.extractall(source,filter='data')
    original=json.loads((source/'MANIFEST.json').read_text())
    assert {str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file() and f!=source/'MANIFEST.json'}==original
    for name in ('OWNERS.json.gz','PLAN.json','SPEC.json'):
        shutil.copyfile(P/'data'/name,source/'data'/name)
    local=work/'local';local.mkdir()
    local_pins=json.loads((P/'LOCAL-PINS.json').read_text())
    with tarfile.open(main/'research/community-frontier1094-audit/selected-replay.tar.gz') as t:
        prefix='candidate/strict/global/base/providers/gauge44/'
        for name,h in local_pins.items():
            member=t.getmember(prefix+name);assert member.isfile()
            b=t.extractfile(member).read();assert hashlib.sha256(b).hexdigest()==h
            (local/name).write_bytes(b)
    # No discovery, source reconstruction, optimizer, credential environment,
    # or native cold rebuild. The full controller and invoice are regenerated.
    env={k:os.environ[k] for k in ('PATH','SYSTEMROOT','WINDIR','TMPDIR','TEMP','TMP') if k in os.environ}
    env.update(PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
    subprocess.run([sys.executable,'-E','-S','-B',str(source/'verify_t16.py'),
                    '--main',str(main),'--local',str(local),'--work',str(work/'strict')],env=env,check=True)
    result=json.loads((work/'strict/REPLAY.json').read_text())
    target=json.loads((P/'CANDIDATE.json').read_text())
    assert result['status']=='PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
    assert result['kappa']==target['expected_updates']['kappa']
    assert result['complex_profile']==target['expected_updates']['global_profile']
    assert result['controls']==dict(admission=69,bit_supplier=12,independent_t16=6,controller_mutations=15)
    for name,h in pins.items():assert sha(main/name)==h
    print('PASS_FOUR_HELPER_VACANCY_CHAIN',result['kappa_decimal'])


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main',type=Path,default=P.parents[1])
    ap.add_argument('--work',type=Path)
    args=ap.parse_args()
    if args.work:
        args.work.mkdir(parents=True,exist_ok=False)
        run(args.main.resolve(),args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='four-helper-vacancy-') as d:
            run(args.main.resolve(),Path(d))
