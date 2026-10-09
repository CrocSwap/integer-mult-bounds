#!/usr/bin/env python3
"""V8 fresh-source finite verification. Writes only to a new external directory."""
import sys
if not __debug__:raise SystemExit('refusing optimized Python: exact checks require assertions')
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,time,traceback
ROOT=Path(__file__).resolve().parent
REQUIRED={'bit','scalar','primes','complex','finite','math'}


def progress(message):print(datetime.now(timezone.utc).strftime('%H:%M:%S UTC')+'  '+message,flush=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def serialize(x):
    from fractions import Fraction
    if isinstance(x,Fraction):return str(x)
    if isinstance(x,dict):return {str(k):serialize(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serialize(v)for v in x]
    return x

def load(name):
    s=importlib.util.spec_from_file_location('v8_'+name,ROOT/(name+'.py'))
    m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def validate_digest(name,actual,expected):
    assert actual==expected, 'package/source hash mismatch: '+name

def integrity():
    path=ROOT/'MANIFEST.json';m=json.loads(path.read_text())
    assert m['schema']=='integer-mult-local-lab-v8/1'
    actual=set()
    for p in ROOT.rglob('*'):
        assert not p.is_symlink(), 'package symlink is not admitted'
        if p.is_file():actual.add(p.relative_to(ROOT).as_posix())
    assert actual==set(m['files'])|{'MANIFEST.json'}, 'missing or unlisted package files'
    for relative,expected in m['files'].items():validate_digest(relative,sha(ROOT/relative),expected)
    return m,sha(path)

def validate_required(results):
    assert set(results)==REQUIRED, 'missing mandatory proof stage'
    assert all(isinstance(results[k],dict)and results[k]for k in REQUIRED), 'empty proof stage'

def cheap_controls():
    rejected=[]
    try:validate_digest('mutated input','0'*64,'1'*64)
    except AssertionError:rejected.append('corrupt input')
    else:raise AssertionError('corrupt input accepted')
    good={k:{'computed':True}for k in REQUIRED}
    for name in sorted(REQUIRED):
        bad=dict(good);bad.pop(name)
        try:validate_required(bad)
        except AssertionError:rejected.append('omitted '+name+' stage')
        else:raise AssertionError('omitted stage accepted')
    return rejected

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    assert sys.version_info>=(3,11), 'Python 3.11 or newer required'
    try:import sympy
    except ImportError:raise SystemExit('SymPy is missing. Install the pinned requirements.txt with this Python interpreter, then rerun.')
    assert sympy.__version__=='1.14.0', 'Use sympy==1.14.0 from requirements.txt'
    manifest,package_hash=integrity();controls=cheap_controls()
    progress('V8 package hashes, Python and SymPy preflight passed')
    if args.preflight_only:
        print(json.dumps(dict(status='PASS_PREFLIGHT_ONLY',package_sha256=package_hash,files=len(manifest['files']),controls=controls),sort_keys=True));return
    if args.output is None:parser.error('--output is required for full verification')
    output=args.output.resolve()
    assert not output.is_relative_to(ROOT), 'output must be outside the immutable package'
    assert not output.exists(), 'output must be a new path; failed outputs are preserved'
    output.mkdir(parents=True)
    start=time.monotonic();timings={};results={}
    def save(name,value):
        (output/name).write_text(json.dumps(serialize(value),sort_keys=True,indent=2)+'\n')
    def stage(name,call):
        t=time.monotonic();value=call();timings[name]=time.monotonic()-t
        results[name]=value;save(name+'.json',value);progress(name+' passed in '+format(timings[name],'.1f')+' seconds');return value
    try:
        progress('Regenerating source paths, physical instructions and exact five-window geometry')
        portable=load('portable_bit')
        bit=portable.run(package_root=ROOT,run_geometry=True)
        results['bit']=portable.summary(bit);timings['bit']=bit['seconds'];save('bit.json',results['bit'])
        save('raw-ledger.json',bit['raw']);progress('Fresh BIT physical and global lowering passed')
        scalar=stage('scalar',lambda:load('scalar_check').run(bit['context'],bit['records'],progress))
        progress('Recomputing all used exact basis determinants and bundled completions')
        primes=stage('primes',lambda:load('prime_check').run(bit['context'],bit['physical'],progress))
        progress('Regenerating complex labels, scalar bill, splice and finite guard')
        complex_result=stage('complex',lambda:load('portable_complex').run(package_root=ROOT,progress=progress))
        math=stage('math',lambda:load('math_check').run(bit['raw'],complex_result['five_stage_histogram']))
        finite=stage('finite',lambda:load('finite_check').run(bit['raw'],bit['physical'],scalar,primes,math,global_result=bit['global_result']))
        validate_required(results)
        assert primes['physical_inventory_bound'] and len(primes['controls'])==6
        assert len(scalar['controls'])==6 and scalar['F2']['formal_columns']==20163
        expected=json.loads((ROOT/'expected-math.json').read_text())['mathematics']
        contract=expected['contract']
        assert contract['bit']['cover_expansion'].startswith('phase-major:')
        assert len(bit['phase_major_schedule'])==13
        assert bit['raw']['five_stage_profile']['W']==contract['bit']['W']==23683
        assert bit['raw']['five_stage_profile']['m']==contract['bit']['m']==120
        assert bit['global_result']['paid_calls']==495304
        assert math['mathematics']['kappa']=='703701743496697/1000000000000000000'
        _,after=integrity();assert after==package_hash, 'package changed during verification'
        certificate=dict(schema='five-stage-v8-reproduced-mathematics/1',**math['mathematics'],contract=contract)
        save('certificate.json',certificate)
        report=dict(schema='five-stage-v8-execution/1',status='PASS_FRESH_SOURCE_FINITE_CANDIDATE',package_sha256=package_hash,
                    kappa=math['mathematics']['kappa'],kappa_decimal=math['mathematics']['kappa_decimal'],
                    fresh_stages=sorted(REQUIRED),timings=timings,total_seconds=time.monotonic()-start,inputs_unchanged=True,
                    negative_controls=controls,
                    scope='Fresh finite source preparation, all-column F2/inverse, phase-major physical program and geometry, all-used determinant witnesses, complex label/scalar/splice/guard, finite BIT accounting and exact outer47. Pinned complex symbolic correctness and retained all-size compiler/tape/prime-supply/recovery theorems remain assumptions. No Lean rebuild, executed all-size multiplier or measured runtime claim.')
        save('verification.json',report);print(json.dumps(report,sort_keys=True))
    except BaseException as error:
        save('failure.json',dict(status='FAIL',error=str(error),completed_stages=sorted(results),timings=timings,traceback=traceback.format_exc()))
        raise

if __name__=='__main__':main()
