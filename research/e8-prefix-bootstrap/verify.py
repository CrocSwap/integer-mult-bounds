"""Replay all twelve PR390 stages, then derive the refined conditional witness."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
    own=read(ROOT/'MANIFEST.json')
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}==set(own)|{'MANIFEST.json'}
    for name,h in own.items():assert sha(ROOT/name)==h,name
    parent=ROOT.parent/'e8-prefix-restoration';spec=read(ROOT/'SOURCE.json')
    assert sha(parent/'MANIFEST.json')==spec['upstream_manifest_sha256']
    expected=read(ROOT/'UPSTREAM-MANIFEST.json')['files']
    actual={str(p.relative_to(parent)):sha(p) for p in parent.rglob('*') if p.is_file() and p!=parent/'MANIFEST.json'}
    mismatch={k:dict(expected=expected.get(k),actual=actual.get(k)) for k in expected.keys()|actual.keys() if expected.get(k)!=actual.get(k)}
    assert not mismatch,('PR390 source bytes changed',mismatch)
    return parent,spec

def main():
    assert __debug__,'Assertions must stay enabled'
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args();out=args.output.resolve()
    parent,spec=integrity();assert not out.exists() and ROOT not in out.parents and parent not in out.parents
    out.mkdir(parents=True);(out/'tmp').mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(out/'tmp'))
    print('RUN all twelve pinned PR390 stages',flush=True)
    with (out/'source390.log').open('w') as f:subprocess.run([sys.executable,'-B',str(parent/'verify.py'),str(out/'source390')],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    baseline=read(out/'source390/RESULT.json')
    assert baseline['status']=='PASS_NEW_E8_PREFIX_RESTORATION_CONDITIONAL_COMPOSITION' and len(baseline['checks'])==12
    for key in ('kappa','bit_coarse','complex_coarse'):assert Q(baseline[key])==Q(spec[key]),key
    physical=read(out/'source390/hetero/RESULT.json')
    assert physical['profile']==read(ROOT/'EXPECTED-PROFILE.json')
    assert physical['invoice']['physical_row_coefficient']==15449<20161
    from coarse_precision import certify
    precision=certify(physical['profile'],physical['m'],physical['live'],Q(physical['coarse']))
    assert precision==read(ROOT/'EXPECTED-COARSE.json')
    from refine import refine
    witness=refine(Q(precision['coarse_lower']),Q(baseline['bit_coarse']))
    assert witness==read(ROOT/'EXPECTED-WITNESS.json')
    k=Q(witness['kappa']);u=Q(precision['coarse_upper']);assert u/(1+u)<k+Q(1,10**18)
    integrity()
    result=dict(status='PASS_FULL_PR390_REPLAY_AND_FINITE_BOOTSTRAP',kappa=str(k),kappa_float=float(k),baseline_kappa=baseline['kappa'],gain=str(k-Q(baseline['kappa'])),source_stages=len(baseline['checks']),strict_constraints=47,negative_controls=len(witness['negative_controls_rejected']),two_exact_moment_engines=True,bootstrap_rounds=witness['bootstrap_rounds'],next_grid_above_paid_moment_ceiling=True,conditional_scope=spec['scope'])
    for name,data in [('COARSE.json',precision),('WITNESS.json',witness),('RESULT.json',result)]:(out/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
