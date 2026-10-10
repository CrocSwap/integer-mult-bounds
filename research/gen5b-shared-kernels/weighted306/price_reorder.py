"""Independent PR306 declared-profile arithmetic; upstream programs stay inert.

Composing the selected 156 kernels is provisional until a separate bridge
validates transformed paths, scalar order, source spans and finite charts.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
from context306 import BASE as OLD,INPUTS,OUTPUT,read_new,verify_new
import witness
import reproduce_pr305 as old
import price_candidate as pc
import price_witness as pw
HEAD='0314371983b8837f01723f5af2c70217f75b01cc'

def source_contract():
    manifest=json.loads((HERE/'inputs.json').read_text())
    checks={}
    for row in manifest['files']:
        raw=(INPUTS/row['local']).read_bytes()
        assert len(raw)==row['bytes']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
        checks[row['path']]=hashlib.sha256(raw).hexdigest()
    old.verify_sources()
    newmanifest=read_new('MANIFEST.json')['files']
    inherited=old.read('PINS.json')['files']
    unchanged=[name for name,pin in inherited.items() if newmanifest.get(name)==pin['sha256']]
    changed=set(inherited)-set(unchanged)
    assert changed=={'MANIFEST.json','finite_check.py','expected/kernel-pins.json','README.md','NOTICE.md'}
    assert len(unchanged)==34
    for name,digest in checks.items():
        if name!='MANIFEST.json':assert newmanifest[name]==digest
    return dict(head=HEAD,new_source_sha256=checks,unchanged_inherited_files=unchanged,
        inherited_manifest_sha256=hashlib.sha256((OLD/'inputs.json').read_bytes()).hexdigest(),
        newly_verified_files=len(checks),inherited_verified_files=len(inherited),upstream_programs_executed=False)

def reorder_delta():
    pins=read_new('expected/kernel-pins.json');out=Counter();stages=[]
    for name,number in [('reorder',237),('reorder2',2)]:
        selection=read_new(name+'-selection.json')
        assert len(selection['moves'])==selection['selected']==pins[name+'_count']==number
        h=old.histogram(selection['expected_local_delta'])
        assert h==old.histogram(pins[name+'_local_delta'])
        assert sum(h.values())==0 and old.mass(h)==0
        out.update(h);stages.append(dict(stage=name,moves=number,declared_delta=old.clean(h)))
    return out,stages

def run():
    OUTPUT.mkdir(parents=True,exist_ok=True);integrity=source_contract();inventory=old.inventory();h,profile=old.final_profile()
    pins=read_new('expected/kernel-pins.json');delta,stages=reorder_delta()
    for key in ['bank_families','pivot_residual_census','completion_rank_histogram','entrance_rank_histogram','literal_stock','physical_R','banks_total','scalar_events','literal_unit_additions']:
        assert pins[key]==old.read('expected/kernel-pins.json')[key],key
    h.update({r:5*n for r,n in delta.items()});assert min(h.values())>=0
    assert sum(h.values())==pins['priced_five_stage_calls']
    assert old.mass(h)==pins['priced_five_stage_rank_mass']
    W=F(inventory['literal_stock'],60);assert 120*W-old.mass(h)==4400
    bracket=old.bracket(h,120,W);assembly=old.assembly(bracket['lower'])
    assert assembly['kappa']==F(pins['kappa'])
    baseline=dict(status='PASS_INDEPENDENT_DECLARED_PROFILE_ARITHMETIC',source_head=HEAD,
        physical_admission=False,all_size_theorem=False,upstream_programs_executed=False,
        integrity=integrity,stages=stages,local_reorder_delta=old.clean(delta),histogram=old.clean(h),calls=sum(h.values()),
        rank_mass=old.mass(h),literal_stock=inventory['literal_stock'],inventory=inventory,
        bit_root_bracket=bracket,assembly=assembly)
    (OUTPUT/'baseline-receipt.json').write_text(json.dumps(old.ae.serial(baseline),indent=2)+'\n')
    witness_path=witness.write_case('156');kd,counts=pw.witness_delta(witness_path)
    assert kd=={1:197,2:283,3:-283,4:70,5:-70}
    combined=Counter(delta);combined.update(kd)
    result=pc.price(old.clean(combined),{24:-156,23:156},{23:156},label='PROVISIONAL_PR306_PLUS156')
    result.update(source_head=HEAD,baseline_kappa=assembly['kappa'],
        improvement_over_pr306=result['assembly']['kappa']-assembly['kappa'],
        improvement_percent_over_pr306=100*(result['assembly']['kappa']/assembly['kappa']-1),
        selected_kernel_delta=kd,candidate_counts=counts,
        composition_verified=False,scope='Declared price screen only. Reorder deltas and shared-kernel composition require independent transformed-word validation.')
    (OUTPUT/'combined156-provisional-receipt.json').write_text(json.dumps(old.ae.serial(result),indent=2)+'\n')
    summary=dict(baseline_kappa=assembly['kappa_decimal'],baseline_coarse=old.ex.dec(bracket['lower']),
        candidate_kappa=result['assembly']['kappa_decimal'],candidate_coarse=old.ex.dec(result['bit_root_bracket']['lower']),
        improvement_percent=old.ex.dec(result['improvement_percent_over_pr306']),
        stock=result['literal_stock'],calls=result['calls'],rank_mass=result['rank_mass'],
        composition_verified=False,strict_assembly_inequalities=47)
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return baseline,result,summary
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    print(json.dumps(run()[2],indent=2))
