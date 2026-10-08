#!/usr/bin/env python3
"""Verify immutable inputs, exact moments and bridge; optionally replay ledgers.
Zhihao Chen / Codex. Moment enclosure adapted from the retained PR36/39 checker.
"""
import argparse,hashlib,json,subprocess,sys,tempfile,shutil,time
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def read(p):return json.loads(Path(p).read_text())
def ceil(x):return -(-x.numerator//x.denominator)
def logs(x):
    x=Q(x);power=0
    while x>2:x/=2;power+=1
    def term(y):
        z=(y-1)/(y+1);lo=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(24)),Q())
        return lo,lo+2*z**49/(49*(1-z*z))
    lo,hi=term(x);l2,h2=term(Q(2));lo+=power*l2;hi+=power*h2
    return Q((lo*10**24).__floor__(),10**24),Q(ceil(hi*10**12),10**12)
def moment(m,W,H,a):
    lower=Q();upper=Q()
    for t,n in H.items():
        assert 0<t<m and n>0
        lo,hi=logs(Q(m,t));u,w=a*lo,a*hi;assert 0<=u<=w<1
        weight=Q(n*t,m*W)
        lower+=weight*(1+u+u*u/2+u*u*u/6)
        upper+=weight*(1+w+w*w/(2*(1-w/3)))
    return lower,upper
def stable(x):
    if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k not in ('elapsed',)}
    if isinstance(x,list):return [stable(v) for v in x]
    return x
def verify_pins():
    pins=read(HERE/'SOURCE.json')
    for rel,sha in pins['files'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha,('source drift',rel)
    foreign=read(HERE/'swapnil-round7/IMPORT.json')
    for rel,sha in foreign['files'].items():
        assert hashlib.sha256((HERE/'swapnil-round7'/rel).read_bytes()).hexdigest()==sha,('foreign drift',rel)
    # Portability edits are limited to resolving a preserved equal histogram
    # and the inherited assembly module from this repository root.
    for name in ('round7_literal_frame_ledger.py','round7_tensor_endpoint_controls.py','round6_complex_interface_controls.py','round6_complex_literal_ledger.py','round7_balanced_assembly_candidate.py'):
        old=(HERE/'validation-prior'/name).read_text()
        if name=='round6_complex_literal_ledger.py':
            old=old.replace("old=json.loads((HERE/'swapnil-round6/independent/complex-twostage/hist_24.json').read_text())", "old=json.loads((HERE/'swapnil-round7/lean/round6-histograms.json').read_text())['cx']; old['hist']=dict(old['hist'])")
        if name=='round7_balanced_assembly_candidate.py':
            old=old.replace("HERE/'integration/scripts'", "HERE.parents[1]/'scripts'").replace("HERE/'integration/scripts/structured_bulk_assembly.py'", "HERE.parents[1]/'scripts/structured_bulk_assembly.py'")
        assert old==(HERE/name).read_text(),('unreviewed port edit',name)
    return len(pins['files'])

def main():
    assert __debug__,'verification requires assertions'
    ap=argparse.ArgumentParser();ap.add_argument('--replay',action='store_true');ap.add_argument('--replay-own',action='store_true');args=ap.parse_args()
    count=verify_pins();bit=read(HERE/'round7-literal-ledger/result.json');cx=read(HERE/'round6-complex-literal-ledger/result.json')
    assert all(bit[k] for k in ('complete_forward_F2','complete_reflected_F2','reflected_frame_continuity','histogram_matches_external'))
    assert all(cx[k] for k in ('actual_forward_equal_frames','reflected_continuity','actual_geometry_passed','histogram_matches_pinned'))
    H={int(t):n for t,n in bit['histogram'].items()};C={int(t):n for t,n in cx['full_histogram'].items()}
    assert sum(t*n for t,n in H.items())==57403754177
    assert sum(t*n for t,n in C.items())==119453132304
    expected=read(HERE/'swapnil-round7/lean/round6-histograms.json')['cx']
    assert C==dict(expected['hist'])
    ab,ac=Q(31987,500000000),Q(36926111,500000000000)
    mb=moment(529,108516254,H,ab);mc=moment(576,207387136,C,ac)
    assert mb[1]<1 and mc[1]<1
    cert=read(HERE/'round7-balanced-assembly-candidate.json')
    assert cert['source_assembly_sha256']==hashlib.sha256((ROOT/'scripts/structured_bulk_assembly.py').read_bytes()).hexdigest()
    assert Q(cert['candidate_kappa'])==Q(63965813,10**12)>Q(1,16384)
    assert len(cert['assembly']['strict_constraints'])==47 and len(cert['assembly']['margins'])==7
    assert all(Q(x)>0 for x in cert['assembly']['strict_constraints'].values())
    assert all(Q(x)>Q(cert['candidate_kappa']) for x in cert['assembly']['margins'].values())
    job=read(HERE/'validation-prior/swapnil-round7-validation-job.json')
    assert job['state']=='completed_upstream_finite_checks'
    assert all(x['returncode']==0 for x in job['stages']) and job['stages'][-1]['expected_rejection_seen']
    # All regenerated outputs live in a disposable tree; never rewrite a
    # source pin or erase the original measured receipt.
    with tempfile.TemporaryDirectory(prefix='deferred-signed-') as tmp:
        root=Path(tmp);pkg=root/'research/deferred-signed';shutil.copytree(HERE,pkg)
        (root/'scripts').mkdir();shutil.copy2(ROOT/'scripts/structured_bulk_assembly.py',root/'scripts/structured_bulk_assembly.py')
        jobs=[('check_complex_identity.py',None,120),('round7_balanced_assembly_candidate.py','round7-balanced-assembly-candidate.json',120)]
        if args.replay or args.replay_own:
            jobs=[('round7_literal_frame_ledger.py','round7-literal-ledger/result.json',180),
                  ('round7_tensor_endpoint_controls.py','round7-tensor-endpoint-controls.json',120),
                  ('round6_complex_interface_controls.py','round6-complex-interface-controls.json',120),
                  ('round6_complex_literal_ledger.py','round6-complex-literal-ledger/result.json',180)]+jobs
        for script,out,limit in jobs:
            r=subprocess.run([sys.executable,script],cwd=pkg,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=limit)
            assert r.returncode==0,(script,r.stdout[-4000:])
            if out is not None:assert stable(read(pkg/out))==stable(read(HERE/out)),('regeneration drift',out)
            print('PASS',script,flush=True)
        if args.replay:
            src=pkg/'swapnil-round7';dd='independent/deferred-readout/'
            for argv,limit in [([dd+'check_word.py','23'],180),([dd+'check_frames.py','23'],1800),([dd+'check_lifted.py','23'],1800),([dd+'check_stair.py','23'],180),([dd+'check_stair.py','23','--control'],180)]:
                r=subprocess.run([sys.executable]+argv,cwd=src,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=limit)
                assert r.returncode==0,(argv,r.stdout[-4000:])
                if '--control' in argv:assert 'certified=False' in r.stdout
                print('PASS native',argv,flush=True)
    print('PASS',count,'pins; both independent moments; 47 constraints; 7 margins; kappa=63965813/10^12 > 2^-14')
    print('Conditional on retained analytic/fixed-tape interfaces; not formal verification of the full theorem.')
if __name__=='__main__':main()
