"""Preserve the exact compared upstream model, without changing old inputs.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PINS=[('ddb7ead76479b1e281b485a78b65ce21cc7de8d7','research/general-gaussian-contact-search/'+name)
      for name in ['README.md','model.py','PAULI-SEARCH.json']]
PINS+=[('def829364e8e53a74eac7997b49b5366afd5bc29','research/phase-rank-debt/PROOF.md')]


def main():
    rows=[]
    for commit,path in PINS:
        blob=subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=ROOT).decode().strip()
        raw=subprocess.check_output(['git','cat-file','blob',blob],cwd=ROOT)
        target=HERE/'sources'/path
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw:raise ValueError('Never overwrite a different related source')
        target.write_bytes(raw)
        rows.append(dict(commit=commit,path=path,blob=blob,copy=target.relative_to(HERE).as_posix(),sha256=sha256(raw).hexdigest()))
    out=dict(status='PINNED_EXACT_UPSTREAM_MODELS',files=rows,
             core_freeze_sha256=sha256((HERE.parent/'FREEZE.json').read_bytes()).hexdigest())
    (HERE/'RELATED.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(out['status'],len(rows))


if __name__=='__main__':main()
