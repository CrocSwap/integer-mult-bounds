"""Open the byte-pinned PR5545 source closure (same pins as PR5551); Apache-2.0.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
Mechanism and all predecessor credit: see README.md.
"""
from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
from pathlib import Path,PurePosixPath
import gzip,importlib.util,json,sys,tarfile,tempfile

HERE=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:
        raise ValueError(why)

def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

@contextmanager
def closure():
    pins=json.loads((HERE/'SOURCES.json').read_bytes())['retained_source']
    raw=(HERE/'inputs'/Path(pins['path']).name).read_bytes()
    need(sha256(raw).hexdigest()==pins['sha256'],'Retained PR5545 capsule byte pin')
    with tempfile.TemporaryDirectory(prefix='p104-two-handoffs-')as tmp:
        root=Path(tmp)
        with tarfile.open(fileobj=BytesIO(gzip.decompress(raw)),mode='r:')as archive:
            members=archive.getmembers();names=[m.name for m in members]
            need(len(names)==len(set(names)),'Unique retained source paths')
            for m in members:
                n=PurePosixPath(m.name)
                need(m.isfile()and not n.is_absolute()and '..'not in n.parts,'Regular retained source path')
                t=root/m.name;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(archive.extractfile(m).read())
        mraw=(root/'.research-export.json').read_bytes()
        need(sha256(mraw).hexdigest()==pins['export_manifest_sha256'],'Exact export inventory')
        man=json.loads(mraw)
        need(man['commit']==pins['commit']and len(man['files'])==pins['files']==33,'Exact predecessor closure')
        need(set(names)=={'.research-export.json'}|{r['path']for r in man['files']},'No omitted or extra file')
        for r in man['files']:
            b=(root/r['path']).read_bytes()
            need(len(b)==r['size']and sha256(b).hexdigest()==r['sha256'],'Source file '+r['path'])
        yield root
