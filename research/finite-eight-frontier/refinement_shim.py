"""Public fresh-output adapter. Mathematical R325 source is copied unchanged.
No local root receipt is forged: positive provenance is the fresh original
ten-stage run performed by verify.py in this same output tree.
"""
import argparse,hashlib,json,sys
from pathlib import Path
sys.set_int_max_str_digits(100000);sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:raise ValueError(why)

def pin(p):
    b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--pins',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    need(sys.flags.utf8_mode==1,'UTF8 required')
    source=json.loads((HERE/'SOURCE_BINDING.json').read_bytes())
    for name,wanted in source['implementation_files'].items():need(pin(HERE/'implementation'/name)==wanted,'frozen arithmetic source changed')
    pins=json.loads(a.pins.read_bytes())
    actual={q.relative_to(a.baseline).as_posix():pin(q) for q in a.baseline.rglob('*') if q.is_file()}
    need(actual==pins,'fresh original output closure changed')
    report=json.loads((a.baseline/'verification.json').read_bytes())
    need(report['fresh_stages']==sorted(('virtual','raw','bit','kernel','scalar','primes','banks','complex','math','finite')) and report['inputs_unchanged'] is True and report['status']=='PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION','fresh original baseline prerequisite')
    need(report['manifest_sha256']==source['baseline_files']['MANIFEST.json']['sha256'],'exact original manifest')
    sys.path.insert(0,str(HERE/'implementation'))
    import checker
    data={n:json.loads((a.baseline/(n+'.json')).read_bytes()) for n in ('raw','bit','physical','global_result','kernel','scalar','primes','banks','complex','math','finite','verification')}
    result=checker.compute(data);result['controls']=checker.controls(data,result)
    need(len(result['controls'])==source['refinement_control_count'],'all refinement controls')
    with a.out.open('x',encoding='utf-8') as f:json.dump(checker.serial(result),f,sort_keys=True);f.write('\n')

if __name__=='__main__':main()
