"""Read pinned inputs and load the exact source modules. Apache-2.0."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha1,sha256
import gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD_PAID={1:2201,2:412,3:510,4:127,5:40,8:8}
OLD_HELPERS={4:28,7:7,8:47,9:326}
SOURCE='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
CE='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'
def need(ok,why):
    if not ok:raise ValueError(why)
def read(path):
    data=Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)
def load(relative,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module
def encode(x):
    if isinstance(x,Fraction):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v) for v in x]
    return x
def packed(x):return (json.dumps(encode(x),sort_keys=True,separators=(',',':'))+'\n').encode()
def authenticate():
    pins=read(HERE/'SOURCES.json')
    for row in pins['files']:
        if row['usage']!='input':continue
        p=ROOT
        for part in Path(row['path']).parts:
            p/=part;need(not p.is_symlink(),'No source alias')
        data=p.read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'Source bytes: '+row['path'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'Source Git blob')
    raw=gzip.decompress((ROOT/SOURCE).read_bytes())
    need(sha256(raw).hexdigest()==PAYLOAD,'Final PR4610 payload')
    return json.loads(raw)
