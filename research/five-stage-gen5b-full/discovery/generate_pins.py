"""Record expected/kernel-pins.json from a fresh replay of every stage (never run by verify.py).
Usage: python3 -B discovery/generate_pins.py OUTPUT_DIR"""
import sys,json,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;sys.path.insert(0,str(ROOT))
import pins;pins.RECORD={}
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
def load(name):
    s=importlib.util.spec_from_file_location('source527_'+name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
progress=lambda t:print(t,flush=True)
context=load('prepare').prepare();raw=load('raw_ledger').run(context)
bit=load('portable_bit').run(prepared_context=context,raw=raw,output_dir=out,run_geometry=True,package_root=ROOT);raw=bit['raw']
scalar=load('scalar_check').run(context,bit['records'],progress,2*1760+len(bit['context']['regs']))
primes=load('prime_check').run(bit['context'],bit['physical'],progress)
bankresult=load('bank_check').run(bit['context'],bit['global_result'],bit['lower']);banks=bankresult['banks'];banked=bankresult['banked_result']
complex_result=load('portable_complex').run(package_root=ROOT,progress=progress)
math=load('math_check').run(raw,complex_result['five_stage_histogram'],banks,bit['global_result'])
finite=load('finite_check').run(raw,bit['physical'],scalar,primes,math,banks,banked,bit['global_result'])
pins.RECORD['kappa']=math['mathematics']['kappa']
(ROOT/'expected/kernel-pins.json').write_text(json.dumps(pins.RECORD,indent=1,sort_keys=True)+'\n')
print(json.dumps(pins.RECORD,indent=1,sort_keys=True));print('kappa',math['mathematics']['kappa'],math['mathematics']['kappa_scientific'])
