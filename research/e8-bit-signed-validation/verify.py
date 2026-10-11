"""Fresh full composition, signed defining witness and corrected finite invoice.
Usage: python3 -B verify.py /fresh/output. Python 3.12+, assertions enabled.
Prepared with OpenAI Codex assistance. Apache-2.0; inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import gzip
import importlib.util
import json
import os
import subprocess
import sys
import invoice
import prefix

assert __debug__ and sys.version_info >= (3,12)
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def manifest(directory, count):
    assert not (directory/'MANIFEST.sha256').is_symlink()
    rows=[line.split(None,1)for line in (directory/'MANIFEST.sha256').read_text().splitlines()]
    names={name for _,name in rows}
    assert len(names)==len(rows)==count-1
    assert 'MANIFEST.sha256' not in names
    assert all(Path(name).name==name and name not in ('.','..')for name in names)
    assert {p.name for p in directory.iterdir()}==names|{'MANIFEST.sha256'}
    for want,name in rows:
        p=directory/name;assert p.is_file() and p.resolve().is_relative_to(directory) and not p.is_symlink()
        assert digest(p)==want,name
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def validate(output, composition_output, parent, baseline):
    """Check extra obligations from a freshly completed composition run."""
    assert not output.exists();output.mkdir()
    source=read(HERE/'SOURCE.json');pins=source['signed_source']
    prior=read(composition_output/'RECEIPT.json')
    assert prior['status']=='PASS_FRESH_PR378_HELPER_NINE_COMPLEX_AND_UNSPLIT_R822_COMPOSITION'
    bit=composition_output/'baseline/replay/bit';unsplit=composition_output/'baseline/replay/unsplit-bit'
    word_raw=gzip.decompress((bit/'word.json.gz').read_bytes())
    assert sha256(word_raw).hexdigest()==source['word_payload_sha256']
    assert digest(bit/'records/249-records.bin')==source['records_sha256']
    signed_dir=output/'signed-work';signed_dir.mkdir();(signed_dir/'records').mkdir()
    assert digest(HERE/'signed_source.py')==pins['member_sha256']
    (signed_dir/'audit_signed_source.py').write_bytes((HERE/'signed_source.py').read_bytes())
    (signed_dir/'word.json.gz').write_bytes((bit/'word.json.gz').read_bytes())
    record_names=['249-records.bin','249-states.json','frames.json']
    for name in record_names:(signed_dir/'records'/name).write_bytes((bit/'records'/name).read_bytes())
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    with (output/'signed.log').open('w')as log:
        subprocess.run([sys.executable,'-B',str(signed_dir/'audit_signed_source.py')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    signed=read(signed_dir/'RESULT.json')
    assert signed['status']=='PASS_EXACT_SIGNED_DEFINING_DECODER_AND_LITERAL_PARITY_PROJECTION'
    assert signed['source_pr376_candidate_sha256']==digest(bit/'word.json.gz')
    for path,want in signed['input_sha256'].items():assert digest(path)==want
    assert digest(signed_dir/'audit_signed_source.py')==pins['member_sha256']
    for name in record_names:assert (signed_dir/'records'/name).read_bytes()==(bit/'records'/name).read_bytes()
    # Preserve the untouched upstream receipt in signed-work. Publish a portable
    # view bound to native payload bytes, not compression metadata or local paths.
    portable=copy.deepcopy(signed);portable.pop('seconds');portable.pop('source_pr376_candidate_sha256')
    portable['word_payload_sha256']=source['word_payload_sha256']
    portable['input_sha256']={**{'word_payload':source['word_payload_sha256']},
        **{'records/'+name:digest(bit/'records'/name)for name in record_names}}
    portable['audit_source_sha256']=pins['member_sha256'];write(output/'SIGNED.json',portable)
    template,binding=prefix.source_template(parent/'code/complex/code/bridged.py',source['schedule']['bridged_sha256'])
    assert digest(parent/'code/bit/checkers/columns_k.cpp')==source['schedule']['native_columns_source_sha256']
    write(output/'SCHEDULE.json',dict(template=template,binding=binding))
    actual=prefix.run(bit/'records/249-records.bin',template,binding);write(output/'PREFIX.json',actual)
    witness=prefix.run(signed_dir/'signed-records.bin',template,binding);write(output/'SIGNED-PREFIX.json',witness)
    old=read(unsplit/'finite.json');priced=read(unsplit/'kappa-input.json')
    assert template['checked_idle']['blocks_per_role_pair']==priced['idle_blocks_per_role_pair']
    native=read(unsplit/'columns.json')
    assert [(x['stage'],x['signed_inverse'])for x in native['stages']]==list(enumerate(template['reverse']))
    finite=invoice.run(priced,old,read(unsplit/'finite-input.json'),bit/'records/249-records.bin',
        signed_dir/'signed-records.bin',signed,actual,witness)
    write(output/'FINITE.json',finite)
    A=load('signed_supplement_assembly',baseline/'assembly.py')
    assembly=A.run(parent,priced,finite,read(composition_output/'complex-supplier.json'))
    write(output/'ASSEMBLY.json',assembly)
    original=read(composition_output/'assembly.json');comparable=copy.deepcopy(assembly)
    cutoffs=[]
    for new,oldcut in zip(comparable['finite_cutoffs'],original['finite_cutoffs']):
        assert new['cutoff_log2']==oldcut['cutoff_log2']
        cutoffs.append(dict(stage=new['stage'],cutoff_log2=new['cutoff_log2'],
            original_coefficient=oldcut['charged_coefficient'],compensated_coefficient=new['charged_coefficient']))
        new['charged_coefficient']=oldcut['charged_coefficient']
    assert len(cutoffs)==8 and comparable==original
    for name in record_names:assert digest(bit/'records'/name)==portable['input_sha256']['records/'+name]
    assert sha256(gzip.decompress((bit/'word.json.gz').read_bytes())).hexdigest()==source['word_payload_sha256']
    result=dict(status='PASS_SIGNED_DEFINING_SOURCE_AND_COMPLETE_SEVEN_STAGE_BIT_VALIDATION',
        kappa=assembly['kappa'],original_counted_coefficient=old['coefficient'],
        compensated_counted_coefficient=finite['coefficient'],extra_unit_additions_per_invocation=264,
        invocations=49,even_compensation_additions_per_invocation=112,
        actual_emitted_scalar_prefix=actual['payload_prefix'],signed_witness_scalar_prefix=witness['payload_prefix'],
        both_prefix_bits=[actual['bits'],witness['bits']],payload_allowance_bits=104,
        unchanged_eight_cutoffs=cutoffs,all_other_assembly_fields_identical=True,
        output_sha256={name:digest(output/name)for name in ['SIGNED.json','SCHEDULE.json','PREFIX.json','SIGNED-PREFIX.json','FINITE.json','ASSEMBLY.json']},
        source=source,
        scope='Signed integer restoration is local defining-source evidence; global restored payload columns are over F2. The actual emitted parity gates and profile are unchanged. The corrected prefix bounds are scalar bounds, not a new chart/compiler theorem. Inherited finite construction, row, routing, precision/recovery and analytic interfaces, including the stage-specific C_full caveat, remain conditional.')
    write(output/'VALIDATION.json',result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    for name,directory in [('composition','e8-far-helper-composition'),('baseline','e8-nine-stage-composition'),
        ('bit','e8-bit-helper-reuse'),('bit-parent','e8-bit-seven-stage'),
        ('complex','nine-stage-complex-e8'),('far','e8-complex-far-retiming')]:
        p.add_argument('--'+name,type=Path,default=HERE.parent/directory)
    a=p.parse_args();out=a.output.resolve();composition=a.composition.resolve()
    paths={name:getattr(a,name.replace('-','_')).resolve()for name in ['baseline','bit','bit-parent','complex','far']}
    assert not out.exists()
    for q in [HERE,composition,*paths.values()]:assert not out.is_relative_to(q)
    for q in [out,composition,*paths.values(),Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(q))
    manifest(HERE,10);source=read(HERE/'SOURCE.json');pins=source['composition']
    assert len(pins['files'])==16
    manifest(composition,16)
    assert digest(composition/'MANIFEST.sha256')==pins['manifest_sha256']
    for name,want in pins['files'].items():assert digest(composition/name)==want,name
    out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable)
    for key in ('PYTHONOPTIMIZE','PR315','CX_SOURCE_PINS','CX_PINS','CX_RECORD','CX_RECEIPT','B3_OUT'):env.pop(key,None)
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    argv=[sys.executable,'-B',str(composition/'verify.py'),str(out/'composition')]
    for name,path in paths.items():argv+=['--'+name,str(path)]
    print('CHECK full-fresh-composition',flush=True)
    with (out/'composition.log').open('w')as log:subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('CHECK signed-source-prefix-and-compensated-invoice',flush=True)
    result=validate(out/'validation',out/'composition',paths['bit-parent'],paths['baseline'])
    expected=read(HERE/'EXPECTED.json')
    assert result['output_sha256']==expected['output_sha256']
    assert result['kappa']==expected['kappa']
    manifest(HERE,10);manifest(composition,16)
    for name,want in pins['files'].items():assert digest(composition/name)==want,name
    receipt=dict(status='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT',kappa=result['kappa'],
        composition_receipt_sha256=digest(out/'composition/RECEIPT.json'),
        validation_receipt_sha256=digest(out/'validation/VALIDATION.json'),
        package_manifest_sha256=digest(HERE/'MANIFEST.sha256'),
        original_counted_coefficient=result['original_counted_coefficient'],
        compensated_counted_coefficient=result['compensated_counted_coefficient'],
        actual_emitted_scalar_prefix=result['actual_emitted_scalar_prefix'],
        signed_witness_scalar_prefix=result['signed_witness_scalar_prefix'],
        all_eight_cutoff_integers_unchanged=True,all_frozen_sources_unchanged=True,scope=result['scope'])
    write(out/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)


if __name__=='__main__':main()
