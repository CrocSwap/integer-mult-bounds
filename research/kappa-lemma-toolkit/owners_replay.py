"""Reconstruct the improved physical owner charts using the frozen public auditor."""
import argparse,copy,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'selective-borrowing-kappa'
def load(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
def replay():
    O=load('retained_physical_owner_checker',BASE/'owners/verify.py')
    for rel,pin in O.PINS.items():
        if O.sha(O.HERE/rel)!=pin:raise ValueError('retained source drift: '+rel)
    trace=BASE/'local/data/forward.json';owners=HERE/'OWNERS.json.gz';context=O.context(trace);rows=O.read(owners)
    result,charts=O.check(rows,context,True)
    # Every actual new role is checked, with the same five semantic fault tests.
    controls=[]
    for name in ('wrong-copy-index','wrong-family','overflow-offset','wrong-width','omitted-role'):
        bad=copy.deepcopy(rows)
        if name=='wrong-copy-index':bad[0]['copy']+=112
        elif name=='wrong-family':bad[0]['family']+=1
        elif name=='overflow-offset':bad[0]['offset']=73
        elif name=='wrong-width':bad[0]['width']+=1
        else:bad.pop()
        try:O.check(bad,context)
        except(ValueError,KeyError):controls.append(name)
        else:raise ValueError('new owner mutation accepted: '+name)
    result.update(owners_sha256=O.sha(owners),source_trace_sha256=O.sha(trace),controls_rejected=controls,
        actual_chart_payload_sha256=hashlib.sha256(json.dumps(charts,sort_keys=True,separators=(',',':')).encode()).hexdigest())
    return json.loads(json.dumps(result)),charts
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
    if a.out.resolve().is_relative_to(HERE.parent):raise ValueError('receipt must be outside both source packages')
    a.out.mkdir(parents=True,exist_ok=False);result,charts=replay();(a.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(a.out/'CHARTS.json.gz').write_bytes(gzip.compress(json.dumps(charts,sort_keys=True,separators=(',',':')).encode(),mtime=0));print(json.dumps({k:result[k]for k in ['status','roles','actual_73column_charts','profile','paid_mass']}))
