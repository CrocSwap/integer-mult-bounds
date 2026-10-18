# SPDX-License-Identifier: Apache-2.0
"""Authenticate the complete package and replay independent offline applications."""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path, PurePosixPath
sys.dont_write_bytecode = True

def need(ok, msg):
    if not ok: raise ValueError(msg)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def authenticate(root):
    pins = json.loads((root / 'MANIFEST.json').read_bytes())
    for name in pins:
        q = PurePosixPath(name)
        need(not q.is_absolute() and '..' not in q.parts and '\\' not in name, 'unsafe manifest path')
    actual = {}
    for f in root.rglob('*'):
        need(not f.is_symlink(), 'package symlink')
        if f.is_file() and f != root / 'MANIFEST.json': actual[f.relative_to(root).as_posix()] = sha(f)
    need(actual == pins, 'complete package inventory or hash mismatch')
    return pins

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--hash-only', action='store_true')
    ap.add_argument('--work', type=Path)
    a = ap.parse_args(); need(not sys.flags.optimize, 'assertions required')
    root = Path(__file__).resolve().parents[1]; pins = authenticate(root)
    if a.hash_only:
        print(json.dumps(dict(status='PASS_COMPLETE_PACKAGE_HASHES', files=len(pins)+1))); return
    need(a.work is not None, '--work required for independent replays')
    work = a.work.resolve()
    need(not work.exists() and not work.is_relative_to(root) and not root.is_relative_to(work), 'fresh external work required')
    work.mkdir(parents=True)
    phase = root / 'applications/phase-completion'
    shutil.copytree(phase, work / 'phase')
    cmds = [
        ('owners', [root/'tools/audit_owners.py', '--source-package', root/'vendor/pr2848', '--candidate', root/'candidate', '--out', work/'OWNERS.json']),
        ('moment', [root/'tools/audit_moment.py', '--candidate', root/'candidate', '--baseline', root/'vendor/pr2848', '--out', work/'MOMENT.json']),
        ('reader-base', [root/'applications/adapters/reader_adapter.py', '--word', root/'vendor/pr2848/sources/PR2833-WORD-base.json.gz', '--out', work/'READER-BASE.json']),
        ('reader-extra', [root/'applications/adapters/reader_adapter.py', '--word', root/'vendor/pr2848/sources/PR2833-WORD-extra.json.gz', '--out', work/'READER-EXTRA.json']),
        ('reader-prefix', [root/'applications/adapters/reader_prefix.py', '--reader-receipt', work/'READER-BASE.json', '--out', work/'READER-PREFIX.json']),
        ('pauli', [root/'applications/adapters/verify_pauli_recovery.py', root/'applications/adapters/six-qubit-recovery']),
        ('phase', [work/'phase/tests.py', '--report', work/'PHASE.json'])]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    stages=[]
    for label, args in cmds:
        log = work/(label+'.txt')
        with log.open('w',encoding='utf-8',newline='\n') as out:
            proc = subprocess.run([sys.executable, '-B', *map(str,args)],cwd=work,env=env,stdout=out,stderr=subprocess.STDOUT)
        need(proc.returncode == 0, 'failed '+label+'; see '+str(log))
        stages.append(dict(stage=label,exit_code=0,output_sha256=sha(log)));print('PASS',label,flush=True)
    need(authenticate(root)==pins, 'read-only package changed during replay')
    claim = json.loads((root/'CLAIM.json').read_bytes())
    from fractions import Fraction as Q
    admission = json.loads((root/'evidence/ADMISSION-RESULT.json').read_bytes())
    release = json.loads((root/'evidence/RELEASE-RECEIPT.json').read_bytes())
    native = json.loads((root/'evidence/NATIVE-RESULT.json').read_bytes())
    need(admission['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE', 'stored complete release statuses')
    need(sha(root/'evidence/RELEASE-RECEIPT.json')==admission['release_receipt_sha256']==claim['release_receipt_sha256'], 'stored release receipt binding')
    need(Q(admission['kappa'])==Q(release['kappa_decimal'])==Q(claim['kappa']), 'stored exact headline binding')
    need(native['status']=='PASS_PR2833_FRESH_NATIVE_PREPARATION' and sha(root/'evidence/NATIVE-RECEIPT.json')==native['native_receipt_sha256'], 'stored fresh native receipt binding')
    moment = json.loads((work/'MOMENT.json').read_bytes())
    need(Q(moment['target'])==Q(claim['kappa']), 'independent target differs from headline')
    result=dict(status='PASS_PACKAGE_AND_SEPARATE_OFFLINE_CHECKS', files=len(pins)+1, package_manifest_sha256=sha(root/'MANIFEST.json'),stages=stages,scope='Fresh offline finite owner, rational moment, Pauli and prime-phase checks. Full native/outer replay is reproduce.py; inherited all-size hypotheses remain.')
    (work/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'])
if __name__=='__main__': main()
