"""Authenticated frozen source exports; no Git or network at replay time.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha256,sha1
from pathlib import Path
from tempfile import TemporaryDirectory
import json,tarfile
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def read(path):return json.loads(Path(path).read_bytes())

def extract(archive,root,pins):
    seen=set()
    with tarfile.open(archive) as tar:
        for member in tar:
            if member.isdir():continue
            path=root/member.name
            need(member.isfile() and path.resolve().is_relative_to(root.resolve()) and member.name not in seen,'Unique safe regular source file')
            need(member.name in pins,'Declared source member')
            raw=tar.extractfile(member).read();pin=pins[member.name]
            need(len(raw)==pin['size'] and sha256(raw).hexdigest()==pin['sha256'] and
                 sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Exact source SHA256 and Git blob')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);seen.add(member.name)
    need(seen==set(pins),'Complete source closure')

@contextmanager
def sources():
    with TemporaryDirectory(prefix='p104-cohort-short-') as tmp:
        root=Path(tmp);out={}
        for bundle in read(HERE/'INPUTS.json'):
            archive=HERE/bundle['archive'];need(sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256'],'Frozen source archive')
            dst=root/str(bundle['pr']);extract(archive,dst,{x['path']:x for x in bundle['files']});out[bundle['pr']]=dst/bundle['prefix']
        for name,digest in read(out[7113]/'SHA256.json').items():need(sha256((out[7113]/name).read_bytes()).hexdigest()==digest,'Caller predecessor internal source pin')
        yield out,root
