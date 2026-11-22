#!/usr/bin/env python3
"""Corrupt each archival boundary and require the real extractor to reject it."""
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil

HERE=Path(__file__).resolve().parent
spec=spec_from_file_location('endpoint_source_integrity',HERE/'verify.py')
verifier=module_from_spec(spec)
spec.loader.exec_module(verifier)

with TemporaryDirectory(prefix='endpoint-corruption-') as work:
    base=Path(work);files=base/'package';files.mkdir()
    names=('SOURCE-E264.json','source-e264.tar.gz','predecessor-8030.tar.gz')
    for name in names:
        shutil.copyfile(HERE/name,files/name)
    verifier.HERE=files
    for index,name in enumerate(names):
        target=files/name;old=target.read_bytes()
        if name.endswith('.json'):
            obj=json.loads(old);obj['source_tree']='0'*40
            target.write_text(json.dumps(obj))
        else:
            target.write_bytes(old[:-1]+bytes((old[-1]^1,)))
        dest=base/str(index);dest.mkdir()
        try:
            verifier.checked_source(dest)
        except ValueError:
            pass
        else:
            raise AssertionError('Corrupted source accepted: '+name)
        target.write_bytes(old)
print('PASS_E264_THREE_SOURCE_CORRUPTIONS_REJECTED',flush=True)
