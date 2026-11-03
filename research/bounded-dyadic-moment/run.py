"""Run the complete price with an explicit second-engine dependency."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE/'inputs/root-source'
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(SOURCE))


def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_bytes())


def run(mode, bits=160):
    from bounded import Moment,exponential,logarithm
    old = SOURCE/'inputs'
    source = load(old/'tree/research/kappa-rebuild/architecture/mixed_target_probe.py','retained_moment')
    exact = load(HERE/'inputs/integer-taylor/integer_exp.py','integer_exp')
    engine = Moment(source.log_interval if mode == 'exact' else lambda r:logarithm(r,bits),
                    exact.exp_interval if mode == 'exact' else lambda x:exponential(x,bits))
    def dependencies(path,name):
        if path.name == 'mixed_target_probe.py':
            return engine
        return load(path,name)
    load(old/'algebra.py','algebra')
    load(old/'controller.py','controller')
    price = load(SOURCE/'pricing_fast.py','price')
    result = read(old/'RESULT.json')
    local,native,physical = (result[k] for k in ('local','native','physical'))
    for record,keys in [(local,['paid','helpers']),(native,['helpers']),
                        (physical,['main_targets','whole_idle_jobs'])]:
        for key in keys:
            record[key] = {int(k):v for k,v in record[key].items()}
    env = SimpleNamespace(ROOT=old/'tree',load=dependencies,read=read)
    output = price.run(local,native,read(old/'CONTROLLER.json'),physical,env)
    if output != result['complete_cost']:
        raise ValueError('Complete price/compiler/outer receipt differs')
    return output,engine


if __name__ == '__main__':
    from verify import authenticate
    authenticate()
    result,engine = run(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 160)
    print(json.dumps({'result':result,'exponential_calls':len(engine.calls)},sort_keys=True))
