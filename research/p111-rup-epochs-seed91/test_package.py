#!/usr/bin/env python3
"""Source-binding, epoch-state and complete-receipt rejection controls."""
import argparse
import gzip
import importlib.util
import json
import marshal
from pathlib import Path
import shutil
import subprocess
import struct
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def execute(package, cwd):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'replay.py')],
                          cwd=cwd, capture_output=True, text=True, timeout=120)


def run():
    rejected = []
    with tempfile.TemporaryDirectory(prefix='p111 epoch relocation ') as folder:
        workspace = Path(folder)
        package = workspace/ROOT.name
        source = workspace/'p111-minrank-proof-reconciliation'
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(ROOT.parent/source.name, source, ignore=shutil.ignore_patterns('__pycache__'))
        def rejection(label, path, transform, error):
            raw = path.read_bytes()
            try:
                changed = transform(raw)
                if changed == raw:
                    raise ValueError('vacuous mutation: '+label)
                path.write_bytes(changed)
                result = execute(package, workspace)
                if result.returncode == 0 or error not in result.stderr:
                    raise ValueError('accepted mutation or wrong failure: '+label+'\n'+result.stderr)
                rejected.append(label)
            finally:
                path.write_bytes(raw)
        for name in ('lrat.py', 'encoding.py', 'compare_original.py', 'controls.py',
                     'verify.py', 'SOURCES.json', 'EXPECTED.json'):
            rejection('changed predecessor '+name, source/name,
                      lambda raw:raw+b'\n# changed\n', 'predecessor pin: '+name)
        for c in (8,9):
            rejection(f'changed c{c} proof payload', source/f'proofs/c{c}.lrat.gz',
                      lambda raw:gzip.compress(gzip.decompress(raw)+b'1 0 0\n',mtime=0),
                      'predecessor pin: proofs/')
        rejection('stale assignment epoch', package/'candidate.py',
                  lambda raw:raw.replace(b'epoch = position + 1', b'epoch = 1'),
                  'ValueError')
        rejection('falsified full receipt', package/'replay.py',
                  lambda raw:raw.replace(b'result = module.compute()',
                                        b'result = module.compute()\n        result["seed"] = 0'),
                  'complete predecessor receipt differs')
        injection = ('import sys,types;sys.path.insert(0,sys.argv[1]);'
                     'import replay;sys.modules["lrat"]=types.ModuleType("lrat");replay.load()')
        result = subprocess.run([sys.executable,'-I','-O','-B','-c',injection,str(package)],
                                cwd=workspace,capture_output=True,text=True,timeout=120)
        if result.returncode == 0 or 'preloaded predecessor module' not in result.stderr:
            raise ValueError('preloaded checker module was not rejected')
        rejected.append('preloaded unrelated checker module')
        # Change gzip headers/stream while preserving every decoded proof byte.
        for c in (8,9):
            path = source/f'proofs/c{c}.lrat.gz'
            raw = path.read_bytes()
            rewritten = gzip.compress(gzip.decompress(raw),compresslevel=1,mtime=91)
            if raw == rewritten:
                raise ValueError('gzip control did not change container')
            path.write_bytes(rewritten)
        # A timestamp-valid malicious bytecode cache must never override the
        # authenticated lrat.py source. -B alone would still read this cache.
        path = source/'lrat.py'
        cache = Path(importlib.util.cache_from_source(str(path),optimization='1'))
        cache.parent.mkdir(exist_ok=True)
        stat = path.stat()
        header = importlib.util.MAGIC_NUMBER + struct.pack('<III',0,int(stat.st_mtime)&0xffffffff,stat.st_size)
        cache.write_bytes(header + marshal.dumps(compile('raise RuntimeError("untrusted bytecode")',str(path),'exec')))
        probe = subprocess.run([sys.executable,'-I','-O','-B','-c',
                                'import sys;sys.path.insert(0,sys.argv[1]);import lrat',str(source)],
                               cwd=workspace,capture_output=True,text=True,timeout=120)
        if probe.returncode == 0 or 'untrusted bytecode' not in probe.stderr:
            raise ValueError('poisoned bytecode control was not active')
        # The exact minimal layout runs from an unrelated cwd with paths containing
        # spaces. Optimized isolated mode remains enabled in every subprocess.
        result = execute(package, Path(tempfile.gettempdir()))
        if result.returncode:
            raise ValueError('relocation/recompression rejected: '+result.stderr)
        positive = json.loads(result.stdout)
    return {'status':'PASS','rejected':rejected,'negative_controls':len(rejected),
            'relocated_recompressed_positive':positive,'recompressed_proofs':2,
            'authenticated_source_over_bytecode':True,
            'bytecode_poison_calibrated':True,
            'flags':['-I','-O','-B']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = run()
    output = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(output)
    print(output,end='')
