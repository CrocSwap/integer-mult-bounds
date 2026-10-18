"""Independent literal-oracle equivalence and rejection controls; no new kappa."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import importlib.util,json,hashlib,sys,subprocess,argparse
import integer_exp as fast
if not __debug__:raise RuntimeError('Assertions must be enabled')
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
SOURCE='research/complex-k492-owner-repair/vendor/multicold/engines/moment.py'

def original():
    path=ROOT/SOURCE
    pins=json.loads((P/'SOURCES.json').read_text())
    expected=next(r['sha256'] for r in pins['files'] if r['path']==SOURCE)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Original engine source drift'
    spec=importlib.util.spec_from_file_location('original_coarse_moment',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def literal(x):
    return sum((x**j/F(factorial(j)) for j in range(25)),F(0))

def verify():
    engine=original();cases=0
    values=sorted({F(0),F(1,10)-F(1,10**20),F(1,100),F(1,1000)}|{F(i,17*1000) for i in range(1,84,3)})
    for i,l in enumerate(values):
        for u in (l,values[min(i+1,len(values)-1)],values[-1]):
            expected=engine.exponential(l,u)
            observed=fast.exponential(l,u,engine.DYAD)
            assert observed==expected
            a,d=fast._polynomial(l);assert F(a,d)==literal(l)
            a,d=fast._polynomial(u);assert F(a,d)==literal(u)
            tail=(u**25/F(factorial(25)))/(1-u/F(26))
            assert observed==(engine.floor(literal(l)),engine.ceil(literal(u)+tail))
            cases+=1
    profiles=[({1:3,2:5,4:7,8:2},73,100),({1:11,3:9,7:3},32,100),({1:12,2:8,4:5},16,100)]
    moments=0
    for profile,m,W in profiles:
        for endpoint in (F(0),F(1,1000),F(16797549561255445,10**19),F('0.0016797549561255445')+F(1,10**1000)):
            for bad in (False,True):
                assert fast.moment(engine,profile,m,W,endpoint,bad)==engine.moment(profile,m,W,endpoint,bad)
                moments+=1
    # These failures exercise the retained range and profile contracts.
    rejected=0
    for l,u in [(F(-1,100),F(0)),(F(1,100),F(0)),(F(0),F(1,10))]:
        try:fast.exponential(l,u)
        except AssertionError:rejected+=1
        else:raise AssertionError('invalid exponential range accepted')
    for profile in ({0:1},{73:1},{1:0}):
        try:fast.moment(engine,profile,73,100,F(1,1000))
        except AssertionError:rejected+=1
        else:raise AssertionError('invalid profile accepted')
    try:fast.exponential(0.001,0.002)
    except TypeError:rejected+=1
    else:raise AssertionError('float endpoint accepted')
    cp=subprocess.run([sys.executable,'-O','-B',str(P/'integer_exp.py')],capture_output=True,text=True)
    assert cp.returncode!=0 and 'Assertions must be enabled' in cp.stderr
    return {'status':'PASS_EXACT_COARSE_EXPONENTIAL_EQUIVALENCE','exponential_cases':cases,'whole_moment_cases':moments,'rejection_controls':rejected+1,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),'scope':'Opt-in exact arithmetic adapter; frozen engines and selected certificate unchanged. No new kappa or full supplier admission claim.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
    result=verify()
    if args.out:args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],result['exponential_cases'],result['whole_moment_cases'],result['rejection_controls'])
