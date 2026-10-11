"""Fresh full baseline, signed local word, phases, banks and exact outer witness."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent
BOOT=ROOT.parent/'e8-prefix-bootstrap'
SOURCE=ROOT.parent/'e8-prefix-restoration'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
    expected=read(ROOT/'MANIFEST.json')
    assert {str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}==expected
    import importlib.util
    spec=importlib.util.spec_from_file_location('bootstrap_integrity',BOOT/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.integrity()
def main():
    assert __debug__
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();out=a.output.resolve();integrity()
    assert not out.exists() and all(p not in out.parents for p in [ROOT,BOOT,SOURCE]);out.mkdir(parents=True);(out/'tmp').mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(out/'tmp'),COMPLEX_PUBLIC=str(SOURCE/'public'));env.pop('PYTHONOPTIMIZE',None)
    for k in ['COMPLEX_CERT','COMPLEX_OUTPUT','COMPLEX_SINK_AUDIT','COMPLEX_PREWHITE','COMPLEX_BASELINE_OUTPUT']:env.pop(k,None)
    checks=[]
    def run(name,cmd,extra=None):
        print('RUN',name,flush=True);start=time.monotonic()
        with (out/(name+'.log')).open('w') as f:subprocess.run([str(x) for x in cmd],env={**env,**(extra or {})},stdout=f,stderr=subprocess.STDOUT,check=True)
        checks.append(dict(name=name,seconds=time.monotonic()-start,log_sha256=sha(out/(name+'.log'))))
    def py(name,path,*args,extra=None):run(name,[sys.executable,'-B',path,*args],extra)
    py('baseline-twelve',SOURCE/'verify.py',out/'source390')
    baseline=read(out/'source390/RESULT.json');assert len(baseline['checks'])==12 and baseline['status']=='PASS_NEW_E8_PREFIX_RESTORATION_CONDITIONAL_COMPOSITION'
    py('signed-reconstruction',ROOT/'construct.py',out/'candidate')
    constructed=read(out/'candidate/RESULT.json');assert len(constructed['negative_controls'])==4
    cp=out/'candidate/candidate.json.gz';audit=out/'candidate/sink-audit.json';code=SOURCE/'code'
    candidate=dict(COMPLEX_CERT=str(cp),COMPLEX_OUTPUT=str(out/'complex'),COMPLEX_BASELINE_OUTPUT=str(out/'source390/far'))
    py('signed-local',code/'complex-compose.py',extra=candidate)
    py('signed-phases',code/'complex-clifford-delta.py',extra=candidate)
    hetero=dict(COMPLEX_CERT=str(cp),COMPLEX_OUTPUT=str(out/'hetero'),COMPLEX_SINK_AUDIT=str(audit),COMPLEX_PREWHITE=str(SOURCE/'data/prewhite.json'))
    py('heterogeneous-local',code/'complex-hetero-compose.py',extra=hetero)
    py('endpoint-phases',code/'complex-bank-phase.py',extra=hetero)
    binary=out/'source390'/('heterobanks.exe' if os.name=='nt' else 'heterobanks')
    run('signed-bank-geometry',[binary,out/'candidate/candidate.json',out/'HETEROBANKS.json'])
    py('signed-bank-review',code/'bit-heterobank-review.py','--banks',out/'HETEROBANKS.json','--certificate',cp,'--sink-audit',audit,'--output',out/'BANK-REVIEW.json')
    py('signed-global-template',code/'root-global.py',extra={**hetero,'HETEROBANKS':str(out/'HETEROBANKS.json'),'BANK_PHASE':str(out/'hetero/BANK-ENDPOINT-PHASE.json'),'BANK_REVIEW':str(out/'BANK-REVIEW.json')})
    physical=read(out/'hetero/RESULT.json');assert physical['profile']==read(ROOT/'EXPECTED-PROFILE.json')
    assert physical['invoice']['physical_row_coefficient']==15449<20161
    py('signed-bit-composition',code/'bit-compose-replay.py',out/'bit','--pr381',SOURCE/'public/381/source/research/e8-nine-stage-kappa','--reuse',SOURCE/'public/376/source/research/e8-bit-helper-reuse','--complex',physical['coarse'])
    bit=read(out/'bit/BIT-COMPOSITION-RECEIPT.json');assert bit['pricing']['bit_coarse']==baseline['bit_coarse']
    sys.path.insert(0,str(BOOT));from coarse_precision import certify;from refine import refine
    coarse=certify(physical['profile'],physical['m'],physical['live'],Q(physical['coarse']));assert coarse==read(ROOT/'EXPECTED-COARSE.json')
    witness=refine(Q(coarse['coarse_lower']),Q(bit['pricing']['bit_coarse']));assert witness==read(ROOT/'EXPECTED-WITNESS.json')
    k=Q(witness['kappa']);u=Q(coarse['coarse_upper']);assert u/(1+u)<k+Q(1,10**18)
    previous=Q(read(ROOT/'SOURCE.json')['baseline_kappa']);assert k>previous;integrity()
    result=dict(status='PASS_FULL_SIGNED_PREFIX_AND_HETEROGENEOUS_COMPOSITION',kappa=str(k),kappa_float=float(k),baseline_kappa=str(previous),gain=str(k-previous),baseline_stages=12,changed_stages=checks,strict_constraints=47,signed_negative_controls=4,bootstrap_negative_controls=len(witness['negative_controls_rejected']),two_exact_moment_engines=True,profile=physical['profile'],finite_invoice=physical['invoice'],conditional_scope=read(ROOT/'SOURCE.json')['scope'])
    for name,data in [('COARSE.json',coarse),('WITNESS.json',witness),('RESULT.json',result)]:(out/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
