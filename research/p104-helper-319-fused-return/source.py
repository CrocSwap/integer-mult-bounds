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
def sources():
    need(read(HERE / "INPUTS.json")["source_head"] == '9d0119eb12fbd9fa534b48cd37b68e7099757b91', "Exact #7314 head")
    with archive(HERE) as parent:
        prior = load("parent_7314_source", parent / "source.py")
        emit = load("parent_7314_construct", parent / "construct.py")
        with prior.sources() as (vendor, audit, rank9, bundle, _, older):
            word = emit.construct(older)
            raw = gzip.decompress((parent / "WORD.json.gz").read_bytes())
            need(canonical(word) == raw and sha256(raw).hexdigest() == '0358b9f6e0340fb3e5aa46c747c558b32a5280cbf9cd92c3b9de627dd18a9a4f',
                 "Regenerate the exact #7314 word")
            yield vendor, audit, rank9, bundle, parent, word


@contextmanager
def bundles():
    with archive(HERE) as parent:
        prior = load("parent_7314_composition", parent / "source.py")
        with prior.bundles() as (parts, _, temp):
            yield parts, parent, temp
