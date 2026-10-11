#!/usr/bin/env python3
"""Bind a complete fresh PR353/354 source replay to native compaction inputs."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def check_source(out):
    out=Path(out);proof=out/'source353354';source=ROOT/'vendor/source353354';pin=read(ROOT/'SOURCE.json')['changed_source']
    assert sha(source/'MANIFEST.json')==pin['manifest_sha256']
    v=read(proof/'VERIFICATION.json');steps=read(proof/'STAGES.json')
    assert v['status']=='PASS_STRICT_SOURCE353354_REGENERATION' and v['source_manifest_sha256']==pin['manifest_sha256'] and v['source_files_unchanged'] is True
    assert v['full_newbase_admission'] is True and v['producer_word_regenerated'] is True and v['all_four_selections_regenerated'] is True and v['base_matches_pinned353'] is True
    assert v['twin_cap']==471 and v['local_residual_bank_replicas']==300
    assert steps==v['steps'] and [x['stage']for x in steps]==pin['source_steps'] and all(x['actual_exit']==0 for x in steps)
    assert v['final_word_sha256']==pin['expected_outputs']['candidate/249-records.bin']
    f2=v['final_F2'];assert all(f2[k]==0 for k in ('violations','final_mismatch','X_not_restored','H_not_restored','resid_sigma0','resid_other')) and f2['copies']==20
    assert pin['expected_outputs']==read(source/'EXPECTED.json')
    names=['VERIFICATION.json','STAGES.json']
    for key,h in pin['expected_outputs'].items():
        prefix,name=key.split('/')
        rel={'base':'base','staged':'stages/04-sink','candidate':'candidate','selection':'pkg'}[prefix]+'/'+name
        assert sha(proof/rel)==h,key
        names.append(rel)
    base=proof/'base'
    for name in ('249-records.bin','249-states.json','frames.json'):
        assert (base/name).read_bytes()==(proof/'stages/00-parity'/name).read_bytes()
        names.append('stages/00-parity/'+name)
    st=read(proof/'candidate/249-states.json')
    assert st['record_sha256']==sha(proof/'candidate/249-records.bin') and st['record_count']==406979
    ad=proof/'newbase-source-admission';a=read(ad/'ADMISSION.json');z=read(ad/'source-scalar.json');virtual=read(ad/'virtual.json')
    assert a['status']=='PASS_STRICT_NEWBASE_VIRTUAL_GEOMETRY_INTEGER_DECODER_DIRTY_AND_F2_WORD'
    assert a['source_manifest_sha256']==pin['manifest_sha256'] and a['source_word_sha256']==pin['expected_outputs']['base/249-records.bin']
    roles=read(ad/'original-helper-roles.json');assert roles==a['original_helper_roles']==list(range(8100))
    assert a['source_scalar']==z and a['virtual']==virtual
    assert z['status']=='PASS_FRESH_P10_PRODUCER_SIGNED_DECODER_AND_PARITY_FUSED_F2_INVERSE_AND_CONTROLS'
    assert len(z['controls'])==11 and all(row['rejected'] is True for row in z['controls'].values())
    assert z['F2']['formal_columns']==10020 and z['F2']['all_targets'] is True and z['F2']['all_source_and_dirty_restored'] is True
    for direction in ('forward','inverse'):
        row=z[direction];assert row['all_formal_columns']==10020 and row['all_source_and_dirty_restored'] is True and row['arbitrary_target_contents_preserved'] is True
    assert len(z['integer'])==2 and {row['direction']for row in z['integer']}=={-1,1}
    assert all(row['mode']=='Z' and row['formal_columns']==10020 and row['all_targets'] is True and row['all_source_and_dirty_restored'] is True for row in z['integer'])
    assert virtual['status']=='PASS_PR168_V4_VIRTUAL_AND_PR200_PHYSICAL_ADMISSION_OF_P10_WORD'
    assert len(virtual['virtual_controls_rejected'])==5 and len(virtual['physical_controls_rejected'])==4
    assert len(virtual['physical_formal'])==2 and {q['ring']for q in virtual['physical_formal']}=={'0','2'}
    assert all(q['all_dirty_and_source_columns_restored'] is True and q['defining_decoder'] is True and q['formal_variables']==10020 for q in virtual['physical_formal'])
    for name in ('ADMISSION.json','source-scalar.json','virtual.json','physical.json','parity.json','original-helper-roles.json'):names.append('newbase-source-admission/'+name)
    for name in ('graph_p10.json','kchron_p10.json','profile_p10.json','word_p10.json.gz','frames_p10.json.gz'):
        old=source/'pkg/bitword/selected/bit'/name;new=proof/'producer-regeneration/final'/name
        assert (gzip.decompress(old.read_bytes())==gzip.decompress(new.read_bytes())) if name.endswith('.gz') else (old.read_bytes()==new.read_bytes())
        names.append('producer-regeneration/final/'+name)
    return ['source353354/'+name for name in names]
