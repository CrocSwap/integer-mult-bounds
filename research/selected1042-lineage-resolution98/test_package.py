"""Mutation controls on temporary package metadata, without editing sources."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

P = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lineage98',P/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def main():
    scratch=v.ROOT/'.firecrawl'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lineage98-',dir=scratch) as temp:
        target=Path(temp)
        for name in ('SOURCES.json','BASE-SELECTED.json','EXPECTED.json'):
            shutil.copyfile(P/name,target/name)
        original={name:(target/name).read_bytes() for name in ('SOURCES.json','BASE-SELECTED.json','EXPECTED.json')}
        v.P=target
        controls=[]
        def reject(name,filename,change):
            value=json.loads(original[filename]);change(value)
            (target/filename).write_text(json.dumps(value),encoding='utf-8')
            try:
                v.main()
            except ValueError:
                controls.append(name)
            else:
                raise ValueError('accepted package mutation: '+name)
            finally:
                (target/filename).write_bytes(original[filename])
        reject('missing mandatory pin','SOURCES.json',lambda x:x['files'].pop(v.OLD))
        reject('changed source digest','SOURCES.json',lambda x:x['files'].__setitem__(v.OLD,'0'*64))
        reject('changed frozen snapshot','BASE-SELECTED.json',lambda x:x.__setitem__('kappa','1/2'))
        reject('floating result count','EXPECTED.json',lambda x:x.__setitem__('selected_R',480.0))
        v.main()
    print('PASS_LINEAGE98_PACKAGE mutations=4 restored_receipt_passed')

if __name__=='__main__':
    main()
