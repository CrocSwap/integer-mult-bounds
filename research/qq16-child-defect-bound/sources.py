"""Authenticate unchanged PR2540 before import. Apache-2.0; ywz65 + Codex."""
import hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PREFIX='research/qq16-complete-native-decoder/'
def need(ok,message):
    if not ok:raise ValueError(message)
def authenticate():
    for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':
            raw=(ROOT/r['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==r['sha256'],'input hash: '+r['path'])
    for r in json.loads((HERE/'SNAPSHOTS.json').read_text())['files']:
        raw=(HERE/r['snapshot']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==r['sha256'],'snapshot hash: '+r['snapshot'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'snapshot blob')
class ExportRoot:
    def __truediv__(self,path):
        t=str(path)
        return HERE/'vendor/pr2540'/t[len(PREFIX):] if t.startswith(PREFIX) else ROOT/path
def load():
    authenticate()
    path=HERE/'vendor/pr2540/verify.py'
    spec=importlib.util.spec_from_file_location('retained_2540_defect',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.ROOT=ExportRoot();m.N.ROOT=m.ROOT
    return m
