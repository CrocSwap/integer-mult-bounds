#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Derive a source-bound minimal integer prefix reserve from pinned PR2824.

Preserves the credited PR2824/PR2827 replica construction and pins PR2833's
complete changed native source chain. Original source profiles remain available.
Prepared with substantial OpenAI Codex assistance. No input is modified.
"""
import argparse
import hashlib
import json
from pathlib import Path

PINS = {
    'lift_parent.py': '4255131a44bd94473fc55fe468c32d0b6435862955797fe22a2e8ebfce60942d',
    'replica_parent.py': '48bdbf28f59d80edb266803ec61bf5e22e8fb5e5a0e2b88004b6039147589bd4',
    'admit_frontier_replica.py': 'd3274dd18f2ef27efbd9b53155654164019d95cd96640de87470c7e9d92d00e5',
}

PREFIX_LOAD = '''    prefix_binding=P.read(base/'LOCAL-PREFIX-BOUND.json')
    P.require(prefix_binding['schema']=='authenticated-actual-local-prefix/1','prefix binding schema')
    P.require(set(prefix_binding['providers'])=={'base','extra'},'two prefix providers')
    for tag,rec in prefix_binding['providers'].items():
        P.require(rec['word_sha256']==P.sha(base/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz')),'prefix complete word binding')
        P.require(set(rec['orientations'])=={'forward','backward'},'both prefix orientations')
    prefix_bound=max(v['prefix_bits_upper'] for p in prefix_binding['providers'].values() for v in p['orientations'].values())
    P.require(type(prefix_bound)is int and 0<prefix_bound<=192 and prefix_bound==prefix_binding['maximum'],'actual local prefix bound')
'''

BINDING = '''    # Native inputs were authenticated above as complete source/cache trees.
    # Independently recounted invoice and assembly require the same exact maximum.
    prefix_records = {}
    for tag, entry in natives.items():
        local = entry / 'local'
        replay = read(local / 'INDEPENDENT-LOCAL-REPLAY.json')
        need(replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'prefix native status')
        need(replay['canonical_word_sha256']==sha(local/'CANONICAL-WORD.json.gz') and replay['local_programs_sha256']==sha(local/'LOCAL-PROGRAMS.json.gz'), 'prefix word/program binding')
        need(set(replay['local'])=={'forward','backward'}, 'both prefix orientations')
        for rec in replay['local'].values():
            peak=Q(rec['prefix_l1_upper'])
            need(rec['charged_payload_bits']==192 and 0<peak<2**192, 'unchanged native192-bit cap')
            need(rec['prefix_bits_upper']==peak.numerator.bit_length()-peak.denominator.bit_length()+1, 'exact prefix peak to bits')
        prefix_records[tag]=dict(word_sha256=sha(package/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz')),
                                canonical_word_sha256=replay['canonical_word_sha256'],
                                local_programs_sha256=replay['local_programs_sha256'],
                                replay_sha256=sha(local/'INDEPENDENT-LOCAL-REPLAY.json'),
                                orientations=replay['local'])
    prefix_bound=max(r['prefix_bits_upper'] for p in prefix_records.values() for r in p['orientations'].values())
    write(package/'LOCAL-PREFIX-BOUND.json', dict(schema='authenticated-actual-local-prefix/1',
          native_receipt_sha256=sha(a.native_receipt), maximum=prefix_bound, providers=prefix_records,
          scope='Actual complete local peaks; native192-bit caps and primitive work remain charged. Global invoice independently recounts and checks this maximum.'))
'''

CONTROLS = '''# Source-bound prefix mutations must fail even with an otherwise valid invoice.
from witness import GEO
_actual_bound=GEO['local_prefix_bits_bound']
for _delta in (-1,1):
 GEO['local_prefix_bits_bound']=_actual_bound+_delta
 try:
  try:assemble(owner,invoice,sha(op),sha(ip))
  except AssertionError as e:
   assert str(e)=='source-bound local prefix equality'
   rejected.append(dict(name='changed_actual_prefix_'+str(_delta),reason=str(e)))
  else:raise AssertionError('accepted altered actual local prefix')
 finally:GEO['local_prefix_bits_bound']=_actual_bound
# Coherently lower all charged-reserve views to the exact required prefix.
# Even with matching row accounting, strict prefix slack must reject equality.
import assemble as _assembly_module
import witness as _witness_module
_saved_payload=(_assembly_module.PAYLOAD,_witness_module.PAYLOAD,GEO['charged_prefix_bits'])
_bad=copy.deepcopy(invoice)
_insufficient=_bad['global_prefix_bits']
_bad['charged_prefix_bits']=_insufficient
_bad['row_prefix_extra']=2*_insufficient
_bad['finite']['physical_row_coefficient']=2*_bad['finite']['physical_stock_bits']+9909+252+2*_insufficient
_assembly_module.PAYLOAD=_witness_module.PAYLOAD=GEO['charged_prefix_bits']=_insufficient
try:
 try:assemble(owner,_bad,sha(op),digest(_bad))
 except AssertionError as e:
  assert str(e)=='strict global prefix reserve'
  rejected.append(dict(name='insufficient_global_payload',reason=str(e)))
 else:raise AssertionError('accepted insufficient global payload')
finally:
 _assembly_module.PAYLOAD,_witness_module.PAYLOAD,GEO['charged_prefix_bits']=_saved_payload
_bad=copy.deepcopy(invoice)
_bad['finite']['physical_row_coefficient']=_bad['finite']['retained_row_coefficient']
try:assemble(owner,_bad,sha(op),digest(_bad))
except AssertionError as e:
 assert str(e)=='strict retained row ceiling'
 rejected.append(dict(name='row_at_retained_ceiling',reason=str(e)))
else:raise AssertionError('accepted row at retained ceiling')
'''

RUNTIME_PATCHES = [
    ('audit_fast.py', [
        ("_part.with_suffix('.tmp').write_text(_j.dumps([_idx[0],_own]));_part.with_suffix('.tmp').replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)",
         "_tmp=_part.with_name(_part.name+'.%d.%d.tmp'%(_AF_SHARD,os.getpid()));_tmp.write_text(_j.dumps([_idx[0],_own]));_tmp.replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)")]),
    ('code/witness.py', [
        ("assert PAYLOAD==1<<(192+(GEO['dimension']+1)//2+2*CALLS+4).bit_length()",
         "assert type(GEO['local_prefix_bits_bound']) is int and 0<GEO['local_prefix_bits_bound']<=192\nassert type(PAYLOAD) is int and PAYLOAD>0\nassert PAYLOAD==GEO['local_prefix_bits_bound']+(GEO['dimension']+1)//2+2*CALLS+5, 'minimal integer prefix reserve'")]),
    ('independent_core.py', [
        ("payload = 1 << (192 + (M+1)//2 + 2*len(c['order']) + 4).bit_length()",
         "require(type(localbits) is int and 0 < localbits <= 192, 'actual native prefix bound')\n    payload = localbits + (M+1)//2 + 2*len(c['order']) + 5")]),
    ('code/invoice_allcold.py', [
        ("    localbits=max(r['prefix_bits'] for p in providers.values() for r in p['local'].values())",
         "    localbits=max(r['prefix_bits'] for p in providers.values() for r in p['local'].values())\n    assert localbits==GEO['local_prefix_bits_bound'], 'source-bound local prefix equality'")]),
    ('code/assemble.py', [
        (" assert 0<finite['physical_row_coefficient']<finite['retained_row_coefficient']==20161",
         " assert 0<finite['physical_row_coefficient']<finite['retained_row_coefficient']==20161, 'strict retained row ceiling'"),
        (" assert 0<invoice['global_prefix_bits']<=invoice['charged_prefix_bits']==PAYLOAD",
         " assert 0<invoice['global_prefix_bits']<invoice['charged_prefix_bits']==PAYLOAD, 'strict global prefix reserve'"),
        (" assert invoice['row_prefix_extra']==2*PAYLOAD",
         " assert max(z['prefix_bits']for p in invoice['providers'].values()for z in p['local'].values())==GEO['local_prefix_bits_bound'], 'source-bound local prefix equality'\n assert invoice['row_prefix_extra']==2*PAYLOAD")]),
    ('geometry_controls.py', [
        ("a.out.write_text(json.dumps(dict(status=", CONTROLS+"a.out.write_text(json.dumps(dict(status=")]),
    ('verify.py', [
        ("len(rd(work/'GEOMETRY-CONTROLS.json')['rejected'])==6", "len(rd(work/'GEOMETRY-CONTROLS.json')['rejected'])==10"),
        ("controller=15,independent_owner=8,geometry=6", "controller=15,independent_owner=8,geometry=10")]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();source=a.source_dir.resolve();out=a.out.resolve()
    if out.exists() or out.is_relative_to(source):
        raise ValueError('fresh external output directory required')
    for name,digest in PINS.items():
        if sha(source/name)!=digest:
            raise ValueError('pinned PR2824 source differs: '+name)
    records=[];outputs={}

    def derive(oldname,newname,replacements):
        body=(source/oldname).read_text(encoding='utf-8')
        for before,after in replacements:
            if body.count(before)!=1:
                raise ValueError(('nonunique exact preimage',oldname,before))
            body=body.replace(before,after)
        compile(body,newname,'exec')
        raw=body.encode('utf-8');outputs[newname]=raw
        records.append(dict(source='research/replica-tail-gain/'+oldname,target=newname,
                            source_sha256=PINS[oldname],target_sha256=hashlib.sha256(raw).hexdigest(),
                            replacements=replacements))

    derive('lift_parent.py','lift_parent.py',[
        ("source_names=['inputs/PLAN.json'", "source_names=['LOCAL-PREFIX-BOUND.json','inputs/PLAN.json'"),
        ("    order=P.read(owners/'ORDER.json');", PREFIX_LOAD+"    order=P.read(owners/'ORDER.json');"),
        ("charged_prefix_bits=1<<(192+37+2*len(order)+4).bit_length()",
         "local_prefix_bits_bound=prefix_bound,charged_prefix_bits=prefix_bound+37+2*len(order)+5"),
    ])
    derive('replica_parent.py','replica_parent.py',[])
    runtime=''.join('    patch('+repr(name)+', '+repr(pairs)+')\n' for name,pairs in RUNTIME_PATCHES)
    comparisons="""COMPARISONS = {
    'pr2833': dict(pr=2833, head='e9307b48d7d1b690939935ecef0f8e524e6d92f4', sha256='6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70', field='kappa'),
    'pr2827': dict(pr=2827, head='4dc1286a476874447f76826885c6af99409a1d46', sha256='f26209f7903557cf3dddd8e6d99b4b2b2f99bbd4b5eb0e6161150830e94b02d0', field='kappa'),
    'pr2824': dict(pr=2824, head='f1826afe1f487333f2c1e5bf862bae2211ce8dd9', sha256='7a3de63f42f72564fdc3bd69a7269b7c364f67526ef76b18063241da59bfef52', field='kappa'),
"""
    derive('admit_frontier_replica.py','admit_integer_prefix.py',[
        ('SOURCE_PROFILES = {\n', "SOURCE_PROFILES = {\n    'pr2833': dict(commit='e9307b48d7d1b690939935ecef0f8e524e6d92f4', manifest='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f', helpers=408, source_file_count=541, upstream_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4'),\n"),
        ('COMPARISONS = {\n',comparisons),
        ("ap.add_argument('--source-profile', choices=sorted(SOURCE_PROFILES), default='pr2802')",
         "ap.add_argument('--source-profile', choices=sorted(SOURCE_PROFILES), default='pr2833')"),
        ("ap.add_argument('--comparison-profile', choices=sorted(COMPARISONS), default='pr2802')",
         "ap.add_argument('--comparison-profile', choices=sorted(COMPARISONS), default='pr2833')"),
        ("need(previous == Q(comparison_claim['kappa']), 'comparison rational/decimal equality')",
         "need(previous == Q(comparison_claim['kappa']), 'comparison rational/decimal equality')\n    need(previous == Q(comparison_claim.get('kappa_rational', comparison_claim['kappa'])), 'exact headline rational/decimal equality without truncation')"),
        ("    write(work / 'RUNTIME-PATCHES.json', patches)",runtime+BINDING+"    write(work / 'RUNTIME-PATCHES.json', patches)"),
    ])
    out.mkdir(parents=True)
    for name,raw in outputs.items():
        (out/name).write_bytes(raw)
    derivation=dict(schema='source-bound-integer-prefix-derivation/1',source_pr=2824,
                    source_head='f1826afe1f487333f2c1e5bf862bae2211ce8dd9',
                    scientific_source_pr=2833,scientific_source_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4',
                    scientific_source_manifest_sha256='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f',
                    scientific_source_file_count=541,
                    comparison_pr=2833,comparison_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4',
                    comparison_claim_sha256='6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70',
                    builder_sha256=sha(Path(__file__)),changes=records,runtime_patches=RUNTIME_PATCHES,
                    reserve_rule='PAYLOAD = authenticated actual global prefix + 1',
                    geometry_controls=10,unchanged_native_cap=192,unchanged_row_ceiling=20161,
                    unchanged_outer_cutoff='L = 1 << e; carried ell recurrence unchanged',
                    shard_transport_repair='Unique per-shard and PID temporary path before atomic replacement to the existing per-shard final path. All audit predicates, control names and exact-once merge assertions remain unchanged.',
                    attribution='Dugongue PR2824/PR2827 replica work; PR2833 changed native words and its complete credited predecessor chain; inherited Tekalign/PR2802 source-chain credits retained in generated source headers. Integer-reserve derivative prepared with substantial OpenAI Codex assistance.',
                    scope='Finite reserve selector only. Native words, scalar work, helpers, stock, row ceiling, cutoff and inherited conditional obligations remain charged.')
    (out/'DERIVATION.json').write_text(json.dumps(derivation,indent=2)+'\n',encoding='utf-8')
    print('PASS_GENERATED_INTEGER_PREFIX_ADAPTER',out)


if __name__=='__main__':
    main()
