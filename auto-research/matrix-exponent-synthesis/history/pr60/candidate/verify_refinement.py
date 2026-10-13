"""Fresh exact arithmetic only; inherited PR60 construction is not rerun."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import argparse,importlib.util,json,subprocess
PIN='e7a492dd8bee4e6f574ced784a62af2ce735edc4'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def js(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):js(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [js(v) for v in value]
    return value
def exact(value):
    if isinstance(value,dict):return {k:exact(v) for k,v in value.items()}
    if isinstance(value,list):return [exact(v) for v in value]
    if isinstance(value,str) and '/' in value:return Q(value)
    return value
def main():
    p=argparse.ArgumentParser();p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--arithmetic',type=Path,default=Path(__file__).with_name('arithmetic.json'))
    p.add_argument('--output',type=Path,default=Path(__file__).with_name('arithmetic-verification.json'))
    a=p.parse_args();root=a.upstream.resolve()
    if not __debug__:raise RuntimeError('run without Python -O')
    assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==PIN
    record=json.loads(a.arithmetic.read_text());assert record['source_commit']==PIN
    for prefix in ('source_certificate','moment_code','assembly_code'):
        path=(root/record[prefix+'_path']).resolve();assert path.is_relative_to(root)
        assert sha256(path.read_bytes()).hexdigest()==record[prefix+'_sha256'],prefix+' changed'
    native=json.loads((root/record['source_certificate_path']).read_text())
    assert record['source_profile']==native['bit'],'profile differs from pinned PR60 certificate'
    math=load('pinned60_arithmetic',root/record['moment_code_path'])
    assembly=load('pinned60_balanced',root/record['assembly_code_path'])
    profile=native['bit'];ab=Q(record['bit_saving']);kappa=Q(record['kappa']);h=Q(record['h_backoff'])
    assert h==Q(1,10**18)
    rows={int(t):n for t,n in profile['child_multiplicities'].items()}
    moment=math.moment(profile['m'],profile['W'],rows,ab)
    assert moment['upper']<1 and js(moment)==record['moment']
    bridge=exact(record['finite_bridge'])
    result=assembly.assembly(bridge,ab,kappa,h=h,a_complex=Q(717,10**7))
    assert js(result)==record['assembly'] and len(result['constraints'])==47
    assert all(x>0 for x in result['constraints'].values())
    old=Q(record['comparison']['old_published_kappa']);old_a=Q(record['comparison']['old_bit_saving'])
    assert kappa>old and kappa>old_a/(1+old_a)
    assert js(assembly.cutoffs(bridge,result))==record['eventual_bounds']
    receipt=dict(status='PASS fresh arithmetic refinement',source_commit=PIN,kappa=str(kappa),
        bit_saving=str(ab),constraints=47,margins=7,exceeds_published_kappa=True,
        exceeds_old_scoped_limit=True,profile_unchanged=True,
        arithmetic_sha256=sha256(a.arithmetic.read_bytes()).hexdigest(),
        inherited_construction_replayed_here=False,
        scope='Fresh exact moment, assembly and eventual-bound arithmetic; construction validation inherited from PR60; no new graph or full multiplication formalization claimed')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS',kappa,'; 47 strict constraints; inherited construction not rerun')
if __name__=='__main__':main()
