"""Temporary metadata mutation checks for the opt-in audit package."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('audit86',P/'verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)

def main():
    scratch=v.ROOT/'.firecrawl';scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='signed86-',dir=scratch) as temp:
        t=Path(temp)
        for name in ('SOURCES.json','BASE-SELECTED.json','EXPECTED.json','engine.py'):
            shutil.copyfile(P/name,t/name)
        original={name:(t/name).read_bytes() for name in ('SOURCES.json','BASE-SELECTED.json','EXPECTED.json')}
        v.P=t;controls=[]
        for label,name,change in (
            ('missing source pin','SOURCES.json',lambda x:x['files'].pop(v.OLD+'CERTIFICATE.json')),
            ('changed source hash','SOURCES.json',lambda x:x['files'].__setitem__(v.OLD+'CERTIFICATE.json','0'*64)),
            ('changed selected context','BASE-SELECTED.json',lambda x:x.__setitem__('kappa','1/2')),
            ('floating count','EXPECTED.json',lambda x:x.__setitem__('exact_minors',4030.0))):
            value=json.loads(original[name]);change(value);(t/name).write_text(json.dumps(value),encoding='utf8')
            try:v.main()
            except ValueError:controls.append(label)
            else:raise ValueError('accepted package mutation '+label)
            finally:(t/name).write_bytes(original[name])
        original_read = Path.read_bytes
        def changed_production(path):
            data = original_read(path)
            return data + b'\n' if path == v.PRODUCTION else data
        with patch.object(Path, 'read_bytes', changed_production):
            try:
                v.run()
            except ValueError as exc:
                if 'live production source pin' not in str(exc):
                    raise
                controls.append('changed live production source')
            else:
                raise ValueError('accepted unpinned live production source')
        v.main()
    print('PASS_SIGNED_MODULAR_PACKAGE mutations=5 restored_receipt_passed')

if __name__=='__main__':main()
