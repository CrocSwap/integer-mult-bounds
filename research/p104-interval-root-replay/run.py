"""Replay every price, compiler and outer predicate with explicit inputs."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_bytes())


def arguments():
    result = read(HERE/'inputs/RESULT.json')
    local,native,physical = (result[k] for k in ('local','native','physical'))
    for record,keys in [(local,['paid','helpers']),(native,['helpers']),
                        (physical,['main_targets','whole_idle_jobs'])]:
        for key in keys:
            record[key] = {int(k):v for k,v in record[key].items()}
    return local,native,read(HERE/'inputs/CONTROLLER.json'),physical,result['complete_cost']


def run(engine):
    load(HERE/'inputs/algebra.py','algebra')
    load(HERE/'inputs/controller.py','controller')
    source = HERE/('inputs/pricing.py' if engine == 'baseline' else 'pricing_fast.py')
    price = load(source,'price_'+engine)
    local,native,word,physical,wanted = arguments()
    environment = SimpleNamespace(ROOT=HERE/'inputs/tree',load=load,read=read)
    start = time.monotonic()
    result = price.run(local,native,word,physical,environment)
    seconds = time.monotonic()-start
    if result != wanted:
        raise ValueError('Complete price/compiler/outer receipt differs')
    return result,seconds


if __name__ == '__main__':
    from verify import authenticate
    authenticate()
    result,seconds = run(sys.argv[1])
    print(json.dumps({'result':result,'seconds':seconds},sort_keys=True))
