"""Authenticated read-only extraction and rebuilding of the exact #7105 input."""
from contextlib import contextmanager
from hashlib import sha256,sha1
from pathlib import Path
import importlib.util,json,sys,tarfile,tempfile
HERE=Path(__file__).resolve().parent

def need(ok, why):
    if not ok:raise ValueError(why)

def read(p):
    import gzip
    raw=Path(p).read_bytes()
    return json.loads(gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()

@contextmanager
def sources():
    pins=read(HERE/'INPUTS.json');archive=HERE/'inputs/pr7105.tar'
    need(sha256(archive.read_bytes()).hexdigest()==pins['archive_sha256'],'Immutable source archive SHA256')
    with tempfile.TemporaryDirectory(prefix='kappa7105-')as tmp:
        root=Path(tmp).resolve();expected={x['path']:x for x in pins['files']};seen=set()
        with tarfile.open(archive)as tar:
            for member in tar:
                if member.isdir():continue
                need(member.isfile()and member.name in expected and member.name not in seen,'Unique listed regular source member')
                path=root/member.name;need(path.resolve().is_relative_to(root),'Safe source member')
                raw=tar.extractfile(member).read();pin=expected[member.name]
                need(len(raw)==pin['size'] and sha256(raw).hexdigest()==pin['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Exact per-file Git blob and SHA256')
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);seen.add(member.name)
        need(seen==set(expected),'Complete source closure')
        previous=root/'research/p104-causal-retimed-step'
        old_path=list(sys.path);sys.path.insert(0,str(previous))
        try:
            source_engine=load('pr7105_source',previous/'source.py')
            constructor=load('pr7105_constructor',previous/'construct.py')
            with source_engine.sources() as (base,ancestor):
                word=constructor.construct(ancestor,read(previous/'WITNESS.json'))
                need(canonical(word)==canonical(read(previous/'WORD.json.gz')),'Entire regenerated #7105 source word')
                need(sha256(canonical(word)).hexdigest()==pins['source_canonical_sha256'],'Exact regenerated #7105 canonical SHA256')
                yield base,word,previous
        finally:sys.path[:]=old_path

if __name__=='__main__':
    import argparse,gzip
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    with sources()as(base,word,previous):
        raw=canonical(word)
        with args.output.open('xb')as out:out.write(gzip.compress(raw,mtime=0)if args.output.suffix=='.gz'else raw+b'\n')
