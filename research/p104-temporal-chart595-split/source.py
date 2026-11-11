"""Authenticate complete #7145 source and #7143 temporal methods. Apache-2.0; retained author notices apply."""
from pathlib import Path
from contextlib import contextmanager
from hashlib import sha256,sha1
import json,gzip,tarfile,tempfile,importlib.util,sys
HERE=Path(__file__).resolve().parent
def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def need(ok,why):
    if not ok:raise ValueError(why)
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
@contextmanager
def parent_bundle():
    with tempfile.TemporaryDirectory(prefix='endpoint-temporal-source-') as tmp:
        root=Path(tmp);folders=[]
        for manifest in ('INPUTS.json','PEER-INPUTS.json'):
            pin=read(HERE/manifest);archive=HERE/pin['archive']
            need(sha256(archive.read_bytes()).hexdigest()==pin['archive_sha256'],'Complete frozen archive')
            pins={r['path']:r for r in pin['files']};seen=set()
            with tarfile.open(archive) as tar:
                for m in tar:
                    if m.isdir():continue
                    path=root/m.name
                    need(m.isfile() and m.name in pins and m.name not in seen and path.resolve().is_relative_to(root.resolve()),'Unique safe source member')
                    raw=tar.extractfile(m).read();item=pins[m.name]
                    need(len(raw)==item['size'] and sha256(raw).hexdigest()==item['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'Exact source size/SHA256/Git blob')
                    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);seen.add(m.name)
            need(seen==set(pins),'Complete file inventory');folders.append(root/pin['prefix'])
        parent,peer=folders;reuse=read(HERE/'REUSE.json')
        need(reuse['head']==read(HERE/'PEER-INPUTS.json')['head'],'Exact credited implementation source')
        for item in reuse['files']:
            name=item['path'];need(Path(name).name==name,'Root implementation')
            origin=item.get('source_path',name);need(Path(origin).name==origin,'Root source implementation')
            raw=(HERE/name).read_bytes();need(raw==(peer/origin).read_bytes() and sha256(raw).hexdigest()==item['sha256'],'Byte-identical credited implementation '+name)
        need((HERE/'PEER-RESULT.json').read_bytes()==(peer/'RESULT.json').read_bytes(),'Exact concurrent comparator receipt')
        yield parent
@contextmanager
def sources():
    with parent_bundle() as parent:
        s=load('rechart_parent_source',parent/'source.py')
        with s.sources() as (vendor,archive,rank9,bundle,oldparent,oldword):
            names=('source','construct','support','split','rechart','retime')
            saved={k:sys.modules.get(k) for k in names};saved_path=list(sys.path)
            try:
                for k in names:sys.modules.pop(k,None)
                sys.path.insert(0,str(parent))
                c=load('rechart_parent_construct',parent/'construct.py')
                word=c.construct(oldword,read(parent/'WITNESS.json'))
            finally:
                sys.path[:]=saved_path
                for k,v in saved.items():
                    if v is None:sys.modules.pop(k,None)
                    else:sys.modules[k]=v
            need(canonical(word)==gzip.decompress((parent/'WORD.json.gz').read_bytes()),'Every reconstructed #7145 word byte')
            yield vendor,archive,rank9,bundle,parent,word
@contextmanager
def bundles():
    with parent_bundle() as parent:
        s=load('rechart_composition_source',parent/'source.py')
        with s.bundles() as (parts,previous,root):yield parts,parent,root
