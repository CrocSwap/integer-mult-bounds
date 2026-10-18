#!/usr/bin/env python3
"""Fast fail-closed packaging controls. Apache-2.0."""
import json
from pathlib import Path
import shutil
import runpy
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='ck dyadic controls ') as temp:
        root=Path(temp)
        package=root/'research/ck-all-dyadic-forest-seed23'
        package.mkdir(parents=True)
        for name in ('verify.py','SOURCES.json'):
            shutil.copyfile(HERE/name,package/name)
        for path in pins['files']:
            target=root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,target)
        verifier=runpy.run_path(str(package/'verify.py'))
        for path in pins['files']:
            target=root/path
            before=target.read_bytes()
            # Preserve compression validity when testing the word payload pin.
            if path.endswith('.gz'):
                import gzip
                changed=gzip.decompress(before)+b' '
                target.write_bytes(gzip.compress(changed,mtime=0))
            else:
                target.write_bytes(before+b' ')
            try:
                verifier['load']()
            except ValueError as error:
                if 'source pin:' not in str(error):
                    raise
            else:
                raise ValueError('source corruption not rejected: '+path)
            if (package/'EXPECTED.json').exists():
                raise ValueError('default verifier wrote receipt')
            rejected.append(path)
            target.write_bytes(before)
        source=next(iter(pins['files']))
        (root/source).unlink()
        try:
            verifier['load']()
        except FileNotFoundError:
            pass
        else:
            raise ValueError('missing dependency accepted')
    print('PASS_CK_DYADIC_PACKAGE source_corruption=2 missing_source=1 optimized=1 outputs_preserved=1')


if __name__=='__main__':
    main()
