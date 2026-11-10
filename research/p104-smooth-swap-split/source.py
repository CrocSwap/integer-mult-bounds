"""Authenticate the exact #7110 closure and rebuild its three predecessor edits.
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
    pins = read(HERE/'INPUTS.json'); archive = HERE/'inputs/pr7110.tar'
    need(sha256(archive.read_bytes()).hexdigest() == pins['archive_sha256'], 'Frozen outer archive')
    old_path = list(sys.path)
    with tempfile.TemporaryDirectory(prefix='p104-7110-') as tmp:
        root = Path(tmp); extract(archive, root, {x['path']: x for x in pins['files']})
        outer = root/'research/cocharted-rank9-helper-split'
        top = root/'top'; extract(outer/'REPLAY.tar.gz',top)
        bundle, parent, base = (root/x for x in ('bundle', 'parent', 'base'))
        extract(top/'predecessor.tar.gz', bundle)
        extract(bundle/'parent-replay.tar.gz', parent)
        extract(parent/'rank9-replay.tar.gz', base)
        coupled = base/'sources/kappa-coupled-boundaries-20261110T0908Z'
        extract(base/'payload/incumbent.tar.gz', coupled)
        vendor = coupled/'replay/research/shared-wire-split-composition'
        previous = coupled/'replay/research/shared-wire-stop-fusion'
        rank9 = base/'sources/kappa-rank9-lower-20261110T1247Z/evidence'
        first = load('source7108_build', parent/'build.py')
        word = first.build(read(coupled/'evidence/candidate.json.gz'))[0]
        need(sha256(canonical(word)).hexdigest() == '34085a6c502ac07530001bdcbc85ad0ec9637f5dda28c9593a0b0d6dd6613d24',
             'Exact reconstructed #7108')
        second = load('build', bundle/'build.py'); second.cut_proof(word)
        word = second.build(word)[0]
        need(sha256(canonical(word)).hexdigest() == 'db9b86eba69ca556be5abc1eb85292566fc065ddebad9a26b2da0475f22aec6b', 'Exact reconstructed #7109')
        sys.path.insert(0,str(top))
        emitter = load('source7110_emit',top/'emit.py')
        old_file,new_file,receipt = (root/x for x in ('old.json.gz','source.json.gz','emit.json'))
        old_file.write_bytes(gzip.compress(canonical(word),mtime=0))
        with contextlib.redirect_stdout(io.StringIO()):emitter.main(old_file,top/'WITNESS.json',new_file,receipt)
        need(read(receipt)==read(top/'EMIT.json'),'Frozen #7110 construction receipt')
        word=read(new_file)
        need(sha256(canonical(word)).hexdigest()==pins['source_canonical_sha256'],'Exact rebuilt #7110')
        need((outer/'RESULT.json').read_bytes() == (top/'RESULT.json').read_bytes(), 'Outer and bundled receipt')
        sys.path.insert(0, str(rank9))
        try: yield vendor, previous, rank9, top, word
        finally: sys.path[:] = old_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with sources() as source:
        raw = canonical(source[-1])
        with args.output.open('xb') as out: out.write(gzip.compress(raw, mtime=0))
