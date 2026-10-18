"""Authoring tool: lower the previously uncompiled PR2445 transport edges."""
from pathlib import Path
from functools import lru_cache
import argparse, gzip, hashlib, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import BASE,HERE,assemble,check_sources,load_module,native_source,physical_map,canon,need

def build():
    check_sources()
    CE=load_module('p104_two_target_compiler',BASE/'vendor/clifford_exact.py')
    N=load_module('p104_two_target_native_compile_check',BASE/'vendor/native_verify.py')
    convert=physical_map(native_source()['label_isometry'],N)
    frame=lambda f:canon(convert(x) for x in f)
    _,_,events,added=assemble()
    edges={}
    for i,event in enumerate(events):
        if i in added and event[0]=='transport':
            old,new=frame(event[2]),frame(event[3]);edges.setdefault((old,new),[]).append(i)
    @lru_cache(None)
    def chart(f):return CE.canonical_frame(9,f)
    out=[]
    for (old,new),indices in sorted(edges.items()):
        operation=chart(old).adjoint().then(chart(new))
        recipe,_=CE.lower_child(operation)
        need(recipe['rank']==abs(len(old)-len(new)),'native rank differs from logical charge')
        N.equal(N.recipe(recipe),N.adjoint(N.frame(old,9))+N.frame(new,9),'new complete native operator')
        inverse_recipe,_=CE.lower_child(chart(new).adjoint().then(chart(old)))
        need(inverse_recipe['rank']==recipe['rank'],'inverse transport rank')
        out.append(dict(old=list(old),new=list(new),events=indices,rank=recipe['rank'],recipe=recipe,inverse_recipe=inverse_recipe))
    return dict(schema_version=1,source_circuit_sha256=hashlib.sha256((HERE/'inputs/PR2445-CIRCUIT.json').read_bytes()).hexdigest(),transports=out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    raw=(json.dumps(build(),sort_keys=True,indent=2)+'\n').encode()
    with args.out.open('xb') as f:f.write(gzip.compress(raw,mtime=0))
    print('COMPILED_P104_TWO_TARGET_NATIVE',len(json.loads(raw)['transports']))

if __name__=='__main__':main()
