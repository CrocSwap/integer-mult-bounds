"""Fresh signed baseline, fused global construction, finite invoice and bit replay."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,importlib.util,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent
SIGNED=ROOT.parent/'e8-signed-prefix'
SOURCE=ROOT.parent/'e8-prefix-restoration'
BOOT=ROOT.parent/'e8-prefix-bootstrap'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
    own=read(ROOT/'MANIFEST.json')
    assert {str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}==own
    spec=importlib.util.spec_from_file_location('signed_integrity',SIGNED/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.integrity()
def main():
    assert __debug__
    out=Path(sys.argv[1]).resolve();integrity();assert not out.exists() and all(p not in out.parents for p in [ROOT,SIGNED,SOURCE,BOOT]);out.mkdir(parents=True);(out/'tmp').mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(out/'tmp'));env.pop('PYTHONOPTIMIZE',None)
    for k in ['COMPLEX_CERT','COMPLEX_OUTPUT','COMPLEX_SINK_AUDIT','COMPLEX_PREWHITE','COMPLEX_BASELINE_OUTPUT']:env.pop(k,None)
    checks=[]
    def run(name,cmd):
        print('RUN',name,flush=True);start=time.monotonic()
        with (out/(name+'.log')).open('w') as f:subprocess.run([str(x) for x in cmd],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
        checks.append(dict(name=name,seconds=time.monotonic()-start,log_sha256=sha(out/(name+'.log'))))
    run('full-signed-baseline',[sys.executable,'-B',SIGNED/'verify.py',out/'baseline'])
    run('fusion-global-invoice',[sys.executable,'-B',ROOT/'fusion.py',out/'baseline',out/'fusion'])
    result=read(out/'fusion/RESULT.json');assert result['status']=='PASS_SIGNED_FUSION_LOCAL_GLOBAL_TEMPLATE_INVOICE_AND_EXACT_PRICE'
    assert len(result['controls_rejected'])==13
    for key in ['profile','invoice']:assert result[key]==read(ROOT/('EXPECTED-'+key.upper()+'.json'))
    for name in ['COARSE','WITNESS']:assert read(out/'fusion'/(name+'.json'))==read(ROOT/('EXPECTED-'+name+'.json'))
    run('fresh-bit-composition',[sys.executable,'-B',SOURCE/'code/bit-compose-replay.py',out/'bit','--pr381',SOURCE/'public/381/source/research/e8-nine-stage-kappa','--reuse',SOURCE/'public/376/source/research/e8-bit-helper-reuse','--complex',result['coarse']])
    bit=read(out/'bit/BIT-COMPOSITION-RECEIPT.json');baseline_bit=read(out/'baseline/bit/BIT-COMPOSITION-RECEIPT.json');assert bit['pricing']['bit_coarse']==baseline_bit['pricing']['bit_coarse']
    sys.path.insert(0,str(BOOT));from refine import refine
    witness=refine(Q(read(out/'fusion/COARSE.json')['coarse_lower']),Q(bit['pricing']['bit_coarse']));assert witness==read(out/'fusion/WITNESS.json')
    integrity();answer=dict(status='PASS_FULL_SIGNED_PREFIX_PADDING_FUSION_AND_BIT_COMPOSITION',kappa=result['kappa'],kappa_float=result['kappa_float'],gain=result['gain'],baseline_kappa=result['baseline_kappa'],checks=checks,strict_constraints=47,fusion_controls=13,signed_controls=4,bootstrap_controls=len(witness['negative_controls_rejected']),fused_occurrences=result['fused_occurrences'],remaining_padding=result['remaining_padding'],invoice=result['invoice'],conditional_scope=result['scope'])
    (out/'RESULT.json').write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer,indent=2),flush=True)
if __name__=='__main__':main()
