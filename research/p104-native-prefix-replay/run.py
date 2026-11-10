"""Run the full native checker with an explicit state evaluator."""
from pathlib import Path
import gzip, importlib.util, json, sys, time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def run(engine):
    name={'original':'inputs/clifford_exact.py','gated':'gated_clifford.py','prefix':'prefix_clifford.py'}[engine]
    C=load(HERE/name,'compiled_'+engine)
    V=load(HERE/('native_gray.py' if engine == 'prefix' else 'inputs/native_verify.py'),'independent_native')
    driver=load(HERE/'native.py','native_driver')
    w=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    start=time.monotonic();result=driver.native(w,C,V);seconds=time.monotonic()-start
    wanted=json.loads((HERE/'inputs/RESULT.json').read_text())['native']
    if json.loads(json.dumps(result))!=wanted:raise ValueError('Complete native receipt differs')
    return result,seconds

if __name__=='__main__':
    from verify import authenticate
    authenticate()
    result,seconds=run(sys.argv[1]);print(json.dumps({'native':result,'seconds':seconds},sort_keys=True))
