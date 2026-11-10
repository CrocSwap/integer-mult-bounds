"""Authenticate #7122 and its full #7121 closure; reconstruct both exact words.
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
def peer_bundle():
    pin=read(HERE/'INPUTS.json');archive=HERE/pin['archive']
    need(sha256(archive.read_bytes()).hexdigest()==pin['archive_sha256'],'Frozen complete #7122 export')
    old_path=list(sys.path)
    with tempfile.TemporaryDirectory(prefix='p104-recharted-split-source-') as tmp:
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
        peer=root/pin['prefix']
        for local,original in [('rechart.py','construct.py'),('RECHART.json','CHANGES.json'),('PEER-EARLY.json','EARLY-RESULT.json')]:
            need((HERE/local).read_bytes()==(peer/original).read_bytes(),'Byte-identical credited peer input '+local)
        try:yield peer
        finally:sys.path[:]=old_path

@contextmanager
def bundles():
    with peer_bundle() as peer:
        parent=load('recharted_split_peer_composition',peer/'source.py')
        with parent.bundles() as (parts,previous,work):yield parts,previous,work

@contextmanager
def sources():
    with peer_bundle() as peer:
        parent=load('recharted_split_peer_native',peer/'source.py')
        with parent.sources() as (vendor,archive,rank9,bundle,previous,word):
            emitter=load('recharted_split_peer_emitter',HERE/'rechart.py')
            changed=emitter.construct(word,read(HERE/'RECHART.json'))
            need(canonical(changed)==gzip.decompress((peer/'WORD.json.gz').read_bytes()),'Every reconstructed #7122 native byte')
            need(sha256(canonical(word)).hexdigest()=='0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc','Exact retained #7121 source')
            need(sha256(canonical(changed)).hexdigest()=='880a2402e01a6a92ce8bfde2046fa6375014b16ca4f89d6cc6f5cead621e54f8','Exact #7122 rechart')
            yield vendor,archive,rank9,bundle,previous,word
