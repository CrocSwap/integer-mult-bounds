"""Authenticate #7140 causal-buffer's complete source closure and reconstruct its native word.
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
    need(sha256(archive.read_bytes()).hexdigest()==pin['archive_sha256'],'Frozen complete #7140 causal-buffer export')
    old_path=list(sys.path)
    with tempfile.TemporaryDirectory(prefix='p104-temporal_chart120-source-') as tmp:
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
        parent=root/pin['prefix']
        reuse=read(HERE/'REUSE.json');need(reuse['head']==pin['head'],'Exact implementation reuse source')
        for item in reuse['files']:
            name=item['path'];need(Path(name).name==name,'Root implementation file')
            a=(HERE/name).read_bytes();b=(parent/name).read_bytes()
            need(a==b and sha256(a).hexdigest()==item['sha256'],'Byte-identical credited implementation '+name)
        imports=load('temporal_chart120_parent_sources',parent/'source.py')
        try:
            with imports.bundles() as (sources,composition,work):yield sources,parent,work
        finally:sys.path[:]=old_path

@contextmanager
def sources():
    with bundles() as (parts,composition,work):
        parent=composition;original=load('temporal_chart120_native_source',parent/'source.py')
        with original.sources() as (vendor,archive,rank9,bundle,oldparent,word):
            saved={name:sys.modules.get(name)for name in ('support','split')}
            try:
                load('support',parent/'support.py');load('split',parent/'split.py')
                emitter=load('temporal_chart120_parent_construct',parent/'construct.py')
                word=emitter.construct(word,read(parent/'WITNESS.json'),read(parent/'PATHS.json'))
            finally:
                for name,obj in saved.items():
                    if obj is None:sys.modules.pop(name,None)
                    else:sys.modules[name]=obj
            need(canonical(word)==gzip.decompress((parent/'WORD.json.gz').read_bytes()),'Every reconstructed previous causal-buffer native byte')
            need(sha256(canonical(word)).hexdigest()=='81f9b2e0a170aa3ab0cd4bb1056c834ebe0b98eaf37abe5986c6e53abd1257ea','Exact frozen current native')
            yield vendor,archive,rank9,bundle,parent,word
