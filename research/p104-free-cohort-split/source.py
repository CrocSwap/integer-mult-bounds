"""Authenticate exact #7112 closure and reconstruct every predecessor edit.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha256, sha1
from pathlib import Path
import contextlib, gzip, importlib.util, io, json, sys, tarfile, tempfile
HERE = Path(__file__).resolve().parent

def need(ok, why):
    if not ok: raise ValueError(why)

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)

def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec); sys.modules[name] = out
    spec.loader.exec_module(out)
    return out

def extract(archive, root, pins=None):
    root.mkdir(parents=True, exist_ok=True); seen = set()
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir(): continue
            path = root/member.name
            need(member.isfile() and path.resolve().is_relative_to(root.resolve()) and path not in seen,
                 'Unique safe regular archive member')
            raw = tar.extractfile(member).read()
            if pins is not None:
                need(member.name in pins, 'Listed source member')
                pin = pins[member.name]
                need(len(raw) == pin['size'] and sha256(raw).hexdigest() == pin['sha256'] and
                     sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
                     'Exact source Git blob and SHA256')
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw); seen.add(path)
    if pins is not None: need(seen == {root/p for p in pins}, 'Complete listed source closure')
    sums = root/'SHA256SUMS'
    if sums.exists():
        for line in sums.read_text().splitlines():
            digest, name = line.split(None, 1); path = root/name.lstrip('*')
            need(path.resolve().is_relative_to(root.resolve()) and sha256(path.read_bytes()).hexdigest() == digest,
                 'Nested source checksum')

@contextmanager
def sources():
    pins=read(HERE/'INPUTS.json'); archive=HERE/'inputs/pr7112.tar'
    need(sha256(archive.read_bytes()).hexdigest()==pins['archive_sha256'],'Frozen outer archive')
    old_path=list(sys.path)
    with tempfile.TemporaryDirectory(prefix='p104-7112-') as tmp:
        root=Path(tmp);extract(archive,root,{x['path']:x for x in pins['files']})
        parent=root/'research/p104-smooth-swap-split'
        parent_source=load('cohort_parent_source',parent/'source.py')
        with parent_source.sources() as (vendor,previous,rank9,bundle,word):
            saved={name:sys.modules.get(name) for name in ('support','split')}
            try:
                load('support',parent/'support.py');load('split',parent/'split.py')
                emitter=load('cohort_parent_construct',parent/'construct.py')
                word=emitter.construct(word,read(parent/'WITNESS.json'))
            finally:
                for name,module in saved.items():
                    if module is None:sys.modules.pop(name,None)
                    else:sys.modules[name]=module
            need(canonical(word)==gzip.decompress((parent/'WORD.json.gz').read_bytes()),'Entire reconstructed #7112')
            need(sha256(canonical(word)).hexdigest()==pins['source_canonical_sha256'],'Pinned #7112 canonical word')
            try:yield vendor,previous,rank9,bundle,parent,word
            finally:sys.path[:]=old_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with sources() as source:
        raw = canonical(source[-1])
        with args.output.open('xb') as out: out.write(gzip.compress(raw, mtime=0))
