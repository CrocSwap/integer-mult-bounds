"""Authenticate #7123's complete source closure and reconstruct its native word.
Prepared for dillona with OpenAI Codex assistance. Apache-2.0.
All source authors and nested notices remain credited.
"""
from contextlib import contextmanager
from hashlib import sha256,sha1
from pathlib import Path
import gzip,importlib.util,json,sys,tarfile,tempfile
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)
def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj

@contextmanager
def bundles():
    pin=read(HERE/'INPUTS.json');archive=HERE/pin['archive']
    need(sha256(archive.read_bytes()).hexdigest()==pin['archive_sha256'],'Frozen complete #7123 export')
    old_path=list(sys.path)
    with tempfile.TemporaryDirectory(prefix='p104-nonunit_pivot-source-') as tmp:
        root=Path(tmp);pins={x['path']:x for x in pin['files']};seen=set()
        with tarfile.open(archive) as tar:
            for member in tar:
                if member.isdir():continue
                path=root/member.name
                need(member.isfile() and member.name in pins and member.name not in seen and path.resolve().is_relative_to(root.resolve()),'Unique safe listed source member')
                raw=tar.extractfile(member).read();p=pins[member.name]
                need(len(raw)==p['size'] and sha256(raw).hexdigest()==p['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==p['git_blob'],'Exact source Git blob and SHA256')
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);seen.add(member.name)
        need(seen==set(pins),'Complete source inventory')
        parent=root/pin['prefix'];imports=load('nonunit_pivot_parent_sources',parent/'source.py')
        try:
            with imports.bundles() as (sources,composition,work):yield sources,parent,work
        finally:sys.path[:]=old_path

@contextmanager
def sources():
    with bundles() as (parts,composition,work):
        parent=composition;original=load('nonunit_pivot_native_source',parent/'source.py')
        with original.sources() as (vendor,archive,rank9,bundle,oldparent,word):
            saved={name:sys.modules.get(name) for name in ('support','split','rechart','retime')}
            try:
                load('support',parent/'support.py');load('split',parent/'split.py')
                load('rechart',parent/'rechart.py');load('retime',parent/'retime.py')
                emitter=load('nonunit_pivot_native_parent_construct',parent/'construct.py')
                word=emitter.construct(word,read(parent/'WITNESS.json'))
            finally:
                for name,obj in saved.items():
                    if obj is None:sys.modules.pop(name,None)
                    else:sys.modules[name]=obj
            need(canonical(word)==gzip.decompress((parent/'WORD.json.gz').read_bytes()),'Every reconstructed #7123 native byte')
            need(sha256(canonical(word)).hexdigest()=='34cc0c51ca9eaaf2bf3789b8ea2c92f0837b4be9f0fedb22a6150169038e8c38','Exact current native')
            yield vendor,archive,rank9,bundle,parent,word
