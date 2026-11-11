# SPDX-License-Identifier: Apache-2.0
"""Authenticate complete source archives and rebuild the immediate predecessor.
Source archive validation follows Clear1nsight's retained predecessor loader.
"""
from contextlib import contextmanager
from hashlib import sha1,sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip,importlib.util,json,sys,tarfile
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw)if raw[:2]==b'\x1f\x8b' else raw)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
@contextmanager
def archive(package):
    pin=read(package/'INPUTS.json');a=package/pin['archive']
    need(sha256(a.read_bytes()).hexdigest()==pin['archive_sha256'],'Exact archive bytes')
    files={r['path']:r for r in pin['files']};need(len(files)==len(pin['files']),'Unique source inventory')
    with TemporaryDirectory(prefix='terminal-cut-source-') as tmp,tarfile.open(a) as tf:
        root=Path(tmp);seen=set()
        for member in tf:
            if member.isdir():continue
            name=member.name;dst=root/name
            need(member.isfile() and name in files and name not in seen and dst.resolve().is_relative_to(root),'Regular in-root inventoried member')
            raw=tf.extractfile(member).read();r=files[name]
            need((len(raw),sha256(raw).hexdigest(),sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())==(r['size'],r['sha256'],r['git_blob']),'Exact source member '+name)
            dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);seen.add(name)
        need(seen==set(files),'Complete source closure')
        yield root/pin['prefix']
@contextmanager
def ancestry():
    need(read(HERE/'INPUTS.json')['source_head']=='ed090b57ed88f8859e5ff4643645099e6ba856ea','Exact #7277 head')
    with archive(HERE) as parent:
        loader=load('exact7277_loader',parent/'source.py')
        constructor=load('exact7277_constructor',parent/'construct.py')
        with loader.sources() as (vendor,audit,rank9,bundle,_,previous):
            word=constructor.construct(previous)
            need(canonical(word)==gzip.decompress((parent/'WORD.json.gz').read_bytes()),'Regenerate whole #7277 source')
            need(sha256(canonical(word)).hexdigest()==read(HERE/'WITNESS.json')['source_word_sha256'],'Exact #7277 word')
            yield vendor,audit,rank9,bundle,parent,word,loader

@contextmanager
def sources():
    with ancestry() as (vendor,audit,rank9,bundle,parent,word,_):
        yield vendor,audit,rank9,bundle,parent,word

@contextmanager
def bundles():
    with archive(HERE) as parent:
        loader=load('exact7277_bundle_loader',parent/'source.py')
        with loader.bundles() as (parts,_,tmp):
            yield parts,parent,tmp
