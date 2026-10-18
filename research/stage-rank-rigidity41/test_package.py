#!/usr/bin/env python3
"""Source and finite receipt controls. @woklerx / OpenAI Codex, Apache-2.0."""
import hashlib,json
from pathlib import Path
import runpy,tempfile

HERE=Path(__file__).resolve().parent


def main():
    m=runpy.run_path(str(HERE/'verify.py'));namespace=m['pins'].__globals__
    original=json.loads((HERE/'SOURCES.json').read_text());snapshot=(HERE/'BASE-SELECTED.json').read_bytes()
    with tempfile.TemporaryDirectory(dir=HERE,prefix='controls-') as folder:
        target=Path(folder);namespace['HERE']=target
        def rejects(manifest,snap=snapshot):
            (target/'SOURCES.json').write_text(json.dumps(manifest));(target/'BASE-SELECTED.json').write_bytes(snap)
            try:m['pins']()
            except ValueError:return
            raise ValueError('corrupted source contract accepted')
        missing=json.loads(json.dumps(original));del missing['files'][next(iter(missing['files']))];rejects(missing)
        extra=json.loads(json.dumps(original));extra['files']['README.md']='0'*64;rejects(extra)
        wrong=json.loads(json.dumps(original));wrong['files'][next(iter(wrong['files']))]='0'*64;rejects(wrong)
        wrong=json.loads(json.dumps(original));wrong['base_commit']='0'*40;rejects(wrong)
        rejects(original,snapshot+b' ')
        changed=json.loads(snapshot);changed['kappa']='1/100';raw=json.dumps(changed).encode()
        repinned=json.loads(json.dumps(original));repinned['base_selected_sha256']=hashlib.sha256(raw).hexdigest();rejects(repinned,raw)
    namespace['HERE']=HERE
    receipt=json.loads((HERE/'EXPECTED.json').read_text())
    changed=json.loads(json.dumps(receipt));changed['group_states']=float(changed['group_states'])
    m['need'](m['encoded'](receipt)!=m['encoded'](changed),'typed receipt control')
    changed=json.loads(json.dumps(receipt));changed['minimum_rank_volume']=4
    m['need'](m['encoded'](receipt)!=m['encoded'](changed),'rank floor receipt control')
    print('PASS_STAGE_RANK_PACKAGE controls=8 source_inventory=exact')


if __name__=='__main__':main()
