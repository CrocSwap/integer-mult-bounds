"""Exact Git-object copies for the changed-owner gates.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FILES=['research/kappa-round5-coupled-main-20261022/'+name for name in [
       'README.md','lift_native.py','involutive_lift.py','caller_probe.py','INVOLUTIVE-LIFT.json']]
FILES+=['research/kappa-rebuild/complex/rebuild_native.py',
        'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/certificate.json.gz',
        'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
        'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py']
FILES+=['research/kappa-lean-verification-20261022/'+name for name in
        ['verify_lean.py','lean-toolchain','lakefile.toml','lake-manifest.json']]


def main():
    prior=HERE/'SOURCES.json'
    commit=(json.loads(prior.read_bytes())['files'][0]['commit'] if prior.exists() else
            subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip())
    pairs=[(commit,path) for path in FILES]
    pairs += [('34434d4ea5d9edf58529eaf79b543cd6c58f3e41','research/center-chart-bound/'+name)
              for name in ['README.md','PROOF.md','RESULT.json']]
    rows=[]
    for rev,path in pairs:
        blob=subprocess.check_output(['git','rev-parse',rev+':'+path],cwd=ROOT).decode().strip()
        raw=subprocess.check_output(['git','cat-file','blob',blob],cwd=ROOT)
        target=HERE/'sources'/path;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw:raise ValueError('Never overwrite a different source pin')
        target.write_bytes(raw)
        rows.append(dict(commit=rev,path=path,blob=blob,copy=target.relative_to(HERE).as_posix(),sha256=sha256(raw).hexdigest()))
    (HERE/'SOURCES.json').write_text(json.dumps(dict(status='PINNED_EXACT_OWNER_PROTOCOL_INPUTS',files=rows),indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PINNED_EXACT_OWNER_PROTOCOL_INPUTS',len(rows))


if __name__=='__main__':main()
