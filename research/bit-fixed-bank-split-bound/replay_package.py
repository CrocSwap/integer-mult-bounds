"""Replay the retained BIT support census from clean pinned inputs."""
from argparse import ArgumentParser
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
BIT = 'research/paired-query-only-bit/'


def unique(raw):
    def keyed(pairs):
        value = dict(pairs)
        assert len(value) == len(pairs), 'Duplicate JSON key'
        return value
    return json.loads(raw, object_pairs_hook=keyed)


def materialize(folder, target):
    for path in folder.rglob('*'):
        if path.is_file():
            out = target / path.relative_to(folder)
            out.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == '.gz':
                raw = gzip.decompress(path.read_bytes())
                unique(raw)
                out.with_suffix('').write_bytes(raw)
            else:
                if path.suffix == '.json':
                    unique(path.read_bytes())
                shutil.copyfile(path, out)


def replay(root):
    manifest = unique((HERE/'SOURCES.json').read_bytes())['files']
    pins = {p['path']:p for p in manifest}
    assert len(pins) == len(manifest), 'Duplicate source path'
    with TemporaryDirectory(prefix='bit-bank-replay-') as scratch:
        temp = Path(scratch)
        deps, adapter, output = [temp/p for p in ('deps','adapter','output')]
        materialize(HERE/'deps', deps)
        materialize(HERE/'adapter', adapter)
        (deps/'inputs').mkdir()
        for src,dst in (('retained/inputs/BIT-NATIVE-WORD.json.gz','WORD.json.gz'),
                        ('EFREE-RESULT.json','INVOICE.json')):
            path = BIT + src
            raw = (root/path).read_bytes()
            assert sha256(raw).hexdigest() == pins[path]['sha256']
            assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == pins[path]['git_blob']
            unique(gzip.decompress(raw) if dst.endswith('.gz') else raw)
            (deps/'inputs'/dst).write_bytes(raw)
        subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),str(deps),str(output),
                        '--adapter-root',str(adapter),'--seconds','120'], check=True, capture_output=True)
        assert unique((output/'PRICE.json').read_bytes()) == unique((HERE/'PRICE.json').read_bytes())
        result = runpy.run_path(str(HERE/'verify.py'))['verify'](deps,adapter,output)
        assert result == unique((HERE/'RESULT.json').read_bytes())
        return result


if __name__=='__main__':
    assert __debug__
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    print(json.dumps(replay(parser.parse_args().root),sort_keys=True,indent=2))
