#!/usr/bin/env python3
"""Manifest integrity controls; @woklerx / OpenAI Codex, Apache-2.0."""
import hashlib
import json
from pathlib import Path
import runpy
import tempfile

HERE=Path(__file__).resolve().parent


def main():
    m=runpy.run_path(str(HERE/'verify.py'))
    namespace=m['load_rows'].__globals__
    pins=json.loads((HERE/'SOURCES.json').read_text())
    snapshot=(HERE/'BASE-SELECTED.json').read_bytes()
    with tempfile.TemporaryDirectory(prefix='package-controls-',dir=HERE) as raw:
        target=Path(raw)
        namespace['HERE']=target
        def rejects(manifest,selected=snapshot):
            (target/'SOURCES.json').write_text(json.dumps(manifest))
            (target/'BASE-SELECTED.json').write_bytes(selected)
            try:
                m['load_rows']()
            except ValueError:
                return
            raise ValueError('corrupted package accepted')
        deleted=json.loads(json.dumps(pins))
        del deleted['files'][next(iter(deleted['files']))]
        rejects(deleted)
        extra=json.loads(json.dumps(pins))
        extra['files']['README.md']='0'*64
        rejects(extra)
        wrong=json.loads(json.dumps(pins))
        wrong['files'][next(iter(wrong['files']))]='0'*64
        rejects(wrong)
        base=json.loads(json.dumps(pins));base['base_commit']='0'*40
        rejects(base)
        rejects(pins,snapshot+b' ')
        selected=json.loads(snapshot);selected['kappa']='1/100'
        changed=json.dumps(selected).encode()
        repinned=json.loads(json.dumps(pins));repinned['base_selected_sha256']=hashlib.sha256(changed).hexdigest()
        rejects(repinned,changed)
    namespace['HERE']=HERE
    expected=json.loads((HERE/'EXPECTED.json').read_text())
    changed=json.loads(json.dumps(expected));changed['candidates']=float(changed['candidates'])
    m['need'](m['canonical'](changed)!=m['canonical'](expected),'typed receipt mutation')
    # Every source outside the declared half-integer alphabet must be excluded.
    try:
        m['horner'](1,3)
    except ValueError:
        pass
    else:
        raise ValueError('nondyadic price accepted')
    print('PASS_X4_TWO_SHEAR_PACKAGE controls=8 inventory=exact source_snapshot=frozen')


if __name__=='__main__':
    main()
