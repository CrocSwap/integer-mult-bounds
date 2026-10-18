"""Exact modern-outer admission of the improved whole-owner supplier.

Run without -O. Outputs are external; the published sources remain read-only.
The complete native supplier and all-size interfaces are separate retained inputs.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
import argparse,gzip,hashlib,importlib.util,json,os,subprocess,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
TOOLKIT=HERE.parent
SUPPLIER=TOOLKIT.parent/'selective-borrowing-kappa'

def need(ok,label):
    if not ok:raise ValueError(label)
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def snapshot():
    return {p.relative_to(HERE).as_posix():sha(p) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

def main():
    need(__debug__,'Assertions must be enabled for the unchanged retained evidence scripts; run without -O')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,help='Optional external JSON receipt file')
    args=parser.parse_args()
    if args.out:
        need(not args.out.resolve().is_relative_to(TOOLKIT.parent.resolve()),'receipt must be outside both published packages')
        need(not args.out.exists(),'refuse to overwrite a previous receipt')
    pins=rd(HERE/'FILES.json')
    for rel,h in pins['files'].items():need(sha(HERE/rel)==h,'modern outer source drift: '+rel)
    for rel,h in pins['supplier_files'].items():need(sha(TOOLKIT/rel)==h,'supplier source drift: '+rel)
    for rel,h in rd(HERE/'UPSTREAM-SOURCES.json')['retained_sha256'].items():
        need(sha(HERE/rel)==h,'retained upstream source drift: '+rel)
    initial=snapshot()
    import numpy,sympy
    need(numpy.__version__=='2.4.6' and sympy.__version__=='1.14.0','use pinned numpy==2.4.6 and sympy==1.14.0')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE',None)
    logs=[]
    def command(path,*argv):
        r=subprocess.run([sys.executable,'-B',str(path),*map(str,argv)],capture_output=True,text=True,encoding='utf8',env=env,timeout=900)
        logs.append(r.stdout+r.stderr)
        need(r.returncode==0,path.name+' failure:\n'+r.stdout[-4000:]+r.stderr[-4000:])
        return r.stdout
    spec=rd(HERE/'SPEC.json');endpoint=rd(HERE/'ENDPOINT.json')
    need(sha(TOOLKIT/'OWNERS.json.gz')=='11a8742b501446c258ef4a1fa423ec2f8c041135c94f4d82356f7bd6f7da3d1c','new literal whole-owner table')
    with tempfile.TemporaryDirectory(prefix='kappa-modern-outer-') as td:
        work=Path(td)
        command(TOOLKIT/'owners_replay.py','--out',work/'owners')
        owner=rd(work/'owners/RESULT.json')
        need(owner==rd(TOOLKIT/'OWNERS-EXPECTED.json'),'new physical owner receipt')
        need(owner['profile']==spec['expected']['global_profile'],'actual complete supplier profile')
        need(owner['paid_mass']==520704 and owner['deficit']==2560,'literal mass and deficit')
        command(SUPPLIER/'local/invoice.py','--variant',SUPPLIER/'local/data','--owners',TOOLKIT/'OWNERS.json.gz','--out',work/'invoice.json')
        need(rd(work/'invoice.json')==rd(TOOLKIT/'INVOICE-EXPECTED.json'),'fresh finite work/precision/stock invoice')
        profile={int(r):n for r,n in owner['profile'].items()}
        M=load('modern_mercator',SUPPLIER/'arithmetic/vendor/moment.py')
        B=load('modern_atanh',SUPPLIER/'arithmetic/vendor/base_two_moment.py');B.log_bounds=lru_cache(None)(B.log_bounds)
        C=Q(endpoint['complex_lower']);above=Q(endpoint['complex_above'])
        need(C==Q(84179,50000000) and above-C==Q(1,10**8),'explicit eight-digit endpoint bracket')
        moment_receipts=[]
        def moments(z,bad):
            m=M.moment(profile,73,7168,z,bad)
            b=B.moment(73,7168,list(profile.items()),z)
            if bad:
                surcharge=B.moment(73,7168,[(1,32*73*73*sum(profile.values()))],z)
                b=(b[0]+surcharge[0]/10**16,b[1]+surcharge[1]/10**16)
            return m,b
        for bad in (False,True):
            merc,atanh=moments(C,bad)
            need(merc[1]<1 and atanh[1]<1,'two exact engines accept supplier endpoint')
            moment_receipts.append({'conservative':bad,'mercator_upper':str(merc[1]),'atanh_upper':str(atanh[1])})
        merc,atanh=moments(above,True)
        need(merc[0]>1 and atanh[0]>1,'both exact engines reject enclosing upper endpoint')
        evidence=command(HERE/'outer/run_outer.py',work/'outer-replay')
        need('PASS_EXACT_REPLAY 19' in evidence and 'PASS_OUTER' in evidence,'all retained outer evidence replayed')
    ledger=rd(HERE/'outer/LEDGER.json');row=ledger['rows']['struct_boundary_radix_union']
    checks={k:Q(v['rational']) for k,v in row['strict_checks'].items()}
    need(len(checks)==54 and min(checks.values())>0,'all54 retained strict rows')
    controls=ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(controls)==17 and all(any(Q(v['rational'])<=0 for v in failed.values()) for failed in controls.values()),'all17 rejecting controls')
    derived=Q(row['kappa']['rational']);advertised=Q(168357,10**8)
    need(derived==C-Q(1,10**54)-Q(1,10**30),'unchanged fixed-grid ledger conclusion')
    need(advertised<derived,'strict admission of advertised rational kappa')
    need(all(Q(v['rational'])>advertised for v in row['margins'].values()),'all modern cost margins exceed advertised kappa')
    baseline=Q(rd(HERE/'upstream-inputs/ENDPOINT.json')['complex_lower'])-Q(1,10**246)-Q(1,10**222)
    need(advertised>baseline,'strict improvement over pinned PR2265 claim')
    need(snapshot()==initial,'modern outer package stayed read-only')
    result={'status':'PASS_NEW_SUPPLIER_MODERN_OUTER_UNDER_ADDITIONAL_PREMISES','kappa':str(advertised),'kappa_decimal':'0.00168357','derived_fixed_grid_kappa':str(derived),'supplier_C':str(C),'owners_sha256':sha(TOOLKIT/'OWNERS.json.gz'),'profile':spec['expected']['global_profile'],'m':73,'live':7168,'largest_child_rank':max(profile),'rank_mass':520704,'deficit':2560,'strict_rows':54,'rejecting_controls':17,'supplier_independent_replays':19,'structure_schedule_gauge_padding':True,'two_exact_endpoint_engines':moment_receipts,'new_invoice_matches':True,'source_read_only':True,'dependencies':{'numpy':numpy.__version__,'sympy':sympy.__version__},'scope':'Conditional on full native supplier admission and the additional capped-fusion, gauge-free, radix-union and fine-prime-padding all-size premises. These additional premises differ from the legacy47-row balanced outer; finite evidence does not discharge them.'}
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        args.out.with_suffix('.log').write_text('\n'.join(logs),encoding='utf8')
    print(json.dumps({k:result[k] for k in ('status','kappa','kappa_decimal','strict_rows','rejecting_controls','supplier_independent_replays','source_read_only')},indent=2))

if __name__=='__main__':main()
