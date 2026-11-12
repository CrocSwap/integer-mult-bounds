"""Authenticate retained source and bind actual selected linear factors."""
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent

def require(ok, message):
    if not ok:raise ValueError(message)

def load(relative,name):
    spec=importlib.util.spec_from_file_location(name,HERE/relative)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value
    spec.loader.exec_module(value)
    return value

def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())['files']
    for pin in pins:
        data=(HERE/pin['local']).read_bytes()
        require(len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],'retained source bytes')
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['blob'],'retained Git blob identity')
    C=load('reference/clifford_exact.py','linear_source_clifford')
    V=load('reference/native_verify.py','linear_source_native')
    m=load('linear.py','linear_factor_program')
    word=json.loads(gzip.decompress((HERE/'reference/selected-native.json.gz').read_bytes()))
    event=word['program'][24472]
    require(event==['MOVE',415,3,99,False],'actual selected MOVE')
    left=C.canonical_frame(9,tuple(word['frames'][3]))
    right=C.canonical_frame(9,tuple(word['frames'][99]))
    recipe,_=C.lower_child(left.adjoint().then(right))
    require(recipe['rank']==1,'actual retained central rank')
    V.equal(V.recipe(recipe),V.adjoint(V.frame(word['frames'][3],9))+V.frame(word['frames'][99],9),'actual whole recipe binding')
    for side in ('right','left'):
        require(tuple(recipe[side]['matrix_rows'])==m.MATRICES[side],'source matrix '+side)
    print(json.dumps({'status':'PASS_SELECTED_LINEAR_SOURCE_GATE','canonical_base':'e54523517d0f03e58352e647c403a5af3e525a57','source_files':len(pins),'event_index':24472,'event':event,'complete_recipe':recipe,
        'scope':'Actual source recipe recomputed and checked; exported programs implement only its two linear address factors.'},indent=2,sort_keys=True))

if __name__=='__main__':main()
