"""Exact latest-profile native transfer. Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
No physical operator, all-fiber, compiler, analytic or recovery proof is certified here.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse,copy,importlib.util,json
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def check():
    pins=json.loads((HERE/'INPUT-PINS.json').read_bytes())
    for name,digest in pins.items():need(sha256((HERE/name).read_bytes()).hexdigest()==digest,'source pin drift: '+name)
    provider=load('provider_rebind','provider_rebind.py');native=load('native_lift','native_lift.py')
    proof=provider.check()
    latest=json.loads((HERE/'LATEST-ARITHMETIC.json').read_bytes())
    qC=F(proof['uniform_saving']);target=F('0.0030217758')
    choice=native.choose(qC,target)
    need(target==F(latest['kappa']),'same rational saving as latest PR4610 headline')
    old=F('0.0030217754');gain=target-old;need(gain==F(1,2500000000),'native improvement exactly four times 10^-10')
    controls={}
    for label,p,t in [('closed_provider_endpoint',qC,qC),('above_provider',qC,qC+F(1,10**13)),('closed_native_boundary',F(1,4),F(3,32))]:
        try:native.choose(p,t)
        except ValueError:controls[label]=True
        else:raise ValueError('control accepted: '+label)
    bad=copy.deepcopy(latest);bad['compiler']['uniform_saving']='0.0030217759'
    try:provider.check(latest_override=bad)
    except ValueError:controls['unfunded_native_provider']=True
    else:raise ValueError('unfunded provider accepted')
    bad=copy.deepcopy(latest);bad['paid']['1']+=1
    try:provider.check(latest_override=bad)
    except ValueError:controls['wrong_complete_paid_profile']=True
    else:raise ValueError('wrong profile accepted')
    need(len(controls)==5,'all five negative controls')
    return {'status':'PASS_LATEST_NATIVE_TRANSFER_ARITHMETIC','word_ram_kappa':str(target),'previous_native_kappa':str(old),'native_gain':str(gain),'complete_paid_profile_changed':False,'new_global_kappa_claimed':False,'new_operator_replay_claimed':False,'provider':proof,'native_parameters':choice,'negative_controls':controls,'scope':'Fresh exact arithmetic and source-bound sufficient transfer; inherited all-fiber algebra, native execution, whole-job, compiler, precision, analytic and recovery premises remain explicit.'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
