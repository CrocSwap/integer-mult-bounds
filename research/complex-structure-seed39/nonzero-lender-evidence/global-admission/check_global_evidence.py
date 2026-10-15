#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit the frozen FOUR428 strict-run evidence without rerunning its pipeline.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
This checks finite admission evidence and its source bindings, not the modern
capped-phase-fusion outer certificate or an all-size theorem.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS_PIN = '2f60e326252cb126a3d78fd97451b53d4706b19ab74409973aa9a2375352cdb3'
PROFILE = {'1':1587402,'2':337002,'3':283401,'4':84246,'5':26121,'7':2814,'8':4994,'16':167,'48':24479}
STAGES = ['bind','emit','audit','invoice','assembly','admission','bit','independent']
FILES = {
    'result':'RESULT.json', 'independent':'INDEPENDENT.json', 'assembly':'ASSEMBLY.json',
    'admission':'ADMISSION-CONTROLS.json', 'bit':'BIT-CONTROLS.json',
    'controller':'global/audit/ASYNC-AUDIT.json', 'owners':'global/audit/OWNERS-AND-PROFILE.json',
    'invoice':'global/audit/PREFIX-AND-INVOICE.json', 'hosted':'global/hosted/HOSTED.json',
    'binding':'global/BINDING.json',
}
STATUSES = {
    'result':'PASS_STRICT_FOUR428_GLOBAL_AND_OUTER_ADMISSION',
    'independent':'PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW',
    'assembly':'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY',
    'admission':'PASS_EXACT_MIXED_048_ALLCOLD_NATIVE_ASSEMBLY_ADMISSION_NEGATIVE_CONTROLS',
    'bit':'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS',
    'controller':'PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS',
    'owners':'PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE',
    'invoice':'PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE',
    'hosted':'EMITTED_MIXED_PROVIDER_ASYNCHRONOUS_WHOLE_OWNER_COMPLEX_TEMPLATE',
    'binding':'PASS_FROZEN_048_ALLCOLD_DISPATCH_FRESH_PROVIDER_BINDING',
    'geometry':'PASS_T74_GEOMETRY_AND_CHARGE_CONTROLS',
}
OWNER_CONTROLS = ['private_namespace_collision','copy_replica_alias','missing_whole_helper',
                  'split_whole_helper','truncated_helper_width','cross_idle_boundary',
                  'cross_child_pending_axis_alias','wrong_provider_at_changed_call']
INTERFACE_CONTROLS = [p+': '+c for p in ('gauge44','extra') for c in
                      ('changed lifted target frame','missing split COPY child')]+['understated private buffer stock']
CONTROLLER_CONTROLS = ['alias two whole owners','helper on active data family','owner in private namespace',
                       'wrong residual width','wrong spectator coordinate','omit idle remainder','understate physical reserve']+[
    p+': '+c for p in ('extra','gauge44') for c in
    ('wrong provider at its invocation','stale per-call local program hash','stale serialized provider program',
     'unbound residual adapter hash','wrong per-call residual width','wrong sweep provider','entering helper width silently restored to nine')]
BUFFER_CONTROLS = ['omit allocation CLEAR','omit release CLEAR','alias private zero fields',
                   'wrong lower dispatch','unbound lowered call family','stale lowered program digest']
GEOMETRY_CONTROLS = ['old_prefix','old_call_count','old_parent_idle','old_stock','missing_call','low_row']


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def check_stages(stages):
    need([s['name'] for s in stages] == STAGES, 'strict stage coverage')
    need(all(type(s['exit_code']) is int and s['exit_code'] == 0 for s in stages), 'strict stage failure')


def documentation_path(relative):
    path = Path(relative)
    return path.name == 'README.md' or path.suffix == '.diff'


def check_manifest(pins, original):
    for relative in pins:
        need(not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe frozen input path')
    # Paths and digests of all source, data, native artifacts and provenance
    # JSON must match. Only inert README/diff files may differ or be absent.
    required = {p:h for p,h in original.items() if not documentation_path(p)}
    current = {p:h for p,h in pins.items() if not documentation_path(p)}
    need(current == required, 'frozen executable/data/native input contract')


def check_receipts(data, template_hash, buffer_hash):
    for key,status in STATUSES.items():
        need(data[key]['status'] == status, 'strict receipt status: '+key)
    ind,ctl,owner,inv = (data[k] for k in ('independent','controller','owners','invoice'))
    need(data['result']['independent'] == ind, 'result independent receipt binding')
    for key,field in (('independent','profile'),('controller','complex_profile'),('owners','paid_profile'),
                      ('assembly','complex_profile'),('hosted','global_profile')):
        need(data[key][field] == PROFILE, 'complete global profile binding')
    for key in ('independent','controller','owners','invoice','hosted'):
        need(data[key]['physical'] == 66818, 'complete physical stock')
    need(ind['live'] == owner['live'] == inv['live'] == data['hosted']['live'] == 66304, 'live stock')
    need(ind['rank_mass'] == owner['rank_mass'] == ctl['rank_mass'] == data['hosted']['rank_mass'] == 4816512, 'rank mass')
    need(ind['deficit'] == owner['deficit'] == ctl['deficit'] == data['hosted']['deficit'] == 23680, 'rank deficit')
    need(ind['roles'] == owner['hosted_residuals'] == ctl['complex_hosted_residuals'] == 285048, 'whole helper roles')
    need(ind['calls'] == ctl['complete_invocations'] == inv['complete_invocation_sweeps'] == inv['bridge_sweeps'] == 666, 'complete calls')
    for key in ('controller','owners','invoice','hosted','assembly'):
        need(data[key]['template_sha256'] == template_hash, 'emitted template binding')
    for key in ('controller','owners','invoice','hosted'):
        need(data[key]['buffer_binding_sha256'] == buffer_hash, 'physical buffer binding')
    need([x['name'] for x in ind['controls_rejected']] == OWNER_CONTROLS, 'eight independent controls')
    need([x['name'] for x in ind['interface_controls_rejected']] == INTERFACE_CONTROLS, 'five interface controls')
    need(ctl['mutation_controls_run'] is True and ctl['mutations_rejected'] == CONTROLLER_CONTROLS, 'twenty-one controller controls')
    need(ctl['buffer_controls_rejected'] == owner['buffer_controls_rejected'] == BUFFER_CONTROLS, 'six buffer controls')
    need(data['geometry']['rejected'] == [dict(name=name,reason='strict arithmetic invariant')
         for name in GEOMETRY_CONTROLS], 'six geometry controls')
    for key,count in (('admission',114),('bit',12)):
        controls = data[key]['rejected_controls']
        need(len(controls) == len(set(controls)) == count, key+' control coverage')
    need(ind['private_zero_buffers'] == inv['private_zero_buffers'] == 76, 'private buffer inventory')
    need(inv['physical_stock_identity'] == dict(data_and_owner_families=66304,local_helpers=428,
         private_centres=8,coefficient_work=2,private_zero_buffers=76), 'physical stock identity')
    need(ind['prefix_bits'] == inv['global_prefix_bits'] == 1442 and
         ind['charged_prefix_bits'] == inv['charged_prefix_bits'] == 2048, 'prefix reserve binding')
    need(ind['physical_row_coefficient'] == inv['finite']['physical_row_coefficient'] == 19545 < 20161, 'row reserve binding')
    need(set(inv['strict_checks']) == {'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'} and
         all(x is True for x in inv['strict_checks'].values()), 'strict finite inequalities')
    need(Fraction(data['result']['kappa']) == Fraction(data['assembly']['kappa']) ==
         Fraction(data['admission']['valid_receipt_kappa']) == Fraction(data['bit']['kappa']), 'retained assembly kappa binding')
    for provider in inv['providers'].values():
        need(provider['helpers'] == 428 and provider['private_zero_fields'] == 76 and provider['warp_events'] == 112, 'provider inventory')
        for row in provider['local'].values():
            need(row['explicit_clear_macros'] == 152 and row['explicit_clear_real_components'] == 304 and
                 row['macros'] == row['native_scalar_macros']+152 and
                 row['real_component_primitives'] == row['native_real_component_primitives']+304, 'explicit clearing charges')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    root = args.work.resolve()
    runtime, strict = root/'layout/packing428', root/'strict'
    need(sha(HERE/'STRICT-INPUTS-ORIGINAL.json') == INPUTS_PIN, 'original strict-input manifest pin')
    original = read(HERE/'STRICT-INPUTS-ORIGINAL.json')
    pins = read(root/'STRICT-INPUTS.json')
    check_manifest(pins,original)
    actual = {p.relative_to(runtime).as_posix() for p in runtime.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    need(actual == set(pins), 'complete frozen runtime inventory')
    for relative,pin in pins.items():
        need(sha(runtime/relative) == pin, 'frozen runtime file: '+relative)
    need(pins['code/audit_allcold.py'] == '810a44956a92fd0562235eec3b16d8135af508131ad1a371914bb49efbc7fce6', 'reviewed mutation order')
    review = read(HERE/'INDEPENDENT-GLOBAL-DIFF-REVIEW.json')
    for relative,pin in review['reviewed_sha256'].items():
        if relative.startswith('runtime-overlay/'):
            target = relative.removeprefix('runtime-overlay/')
            need(sha(runtime/target) == pin == sha(HERE/relative), 'reviewed runtime source: '+target)
    need(sha(strict/'runtime/data/SPEC.json') == pins['candidate/SPEC.json'], 'strict frozen SPEC')
    need(not (strict/'WITNESS-RECORD.jsonl').exists(), 'strict run used discovery mode')
    stages = read(strict/'STAGES.json')
    check_stages(stages)
    for item in stages:
        need(sha(strict/(item['name']+'.log')) == item['log_sha256'], 'strict stage log hash')
    data = {key:read(strict/relative) for key,relative in FILES.items()}
    data['geometry'] = read(root/'GEOMETRY-CONTROLS.json')
    need(data['result']['steps'] == stages, 'strict result stage binding')
    template_path = strict/'global/hosted/GLOBAL-TEMPLATE.json.gz'
    template = read(template_path)
    template_hash = hashlib.sha256(gzip.decompress(template_path.read_bytes())).hexdigest()
    buffer_path = strict/'global/hosted/GLOBAL-BUFFER-BINDING.json.gz'
    buffer_hash = sha(buffer_path)
    need(buffer_hash == pins['candidate/GLOBAL-BUFFER-BINDING.json.gz'] and
         read(buffer_path) == template['buffer_binding'], 'actual emitted buffer source')
    need(template['physical'] == 66818 and template['live'] == 66304, 'emitted physical stock')
    check_receipts(data,template_hash,buffer_hash)
    profile = Counter()
    for call in template['calls']:
        record = template['local_providers'][call['provider_id']]['local_program_checks'][call['orientation']]
        need(call['local_program_sha256'] == record['sha256'], 'literal call program binding')
        profile.update({int(r):n for r,n in record['paid_profile'].items()})
    for child in template['idle_children']:
        need(child['replicas'] == 1, 'literal residual multiplicity')
        profile[child['rank']] += 1
    need({str(r):n for r,n in profile.items()} == PROFILE, 'emitted recursive profile recount')
    need(read(runtime/'candidate/PROFILE.json') == read(runtime/'candidate/PLAN.json')['profile'] == PROFILE, 'candidate profile pin')
    owner_path, ctl_path, invoice_path = (strict/FILES[k] for k in ('owners','controller','invoice'))
    need(data['invoice']['owner_audit_sha256'] == sha(owner_path) and
         data['invoice']['controller_audit_sha256'] == data['owners']['controller_audit_sha256'] == sha(ctl_path), 'invoice audit file binding')
    need(data['admission']['input_sha256']['owner_audit'] == sha(owner_path) and
         data['admission']['input_sha256']['fresh_invoice'] == sha(invoice_path), 'admission input binding')
    for key in ('admission','bit'):
        need(data[key]['assembler_sha256'] == pins['code/assemble.py'], 'control assembler source binding')
    need(data['hosted']['source_artifacts'] == data['owners']['source_artifacts'], 'provider artifact lists')
    for relative,pin in data['owners']['source_artifacts'].items():
        need(sha(strict/'global/base'/relative) == pin, 'actual provider artifact: '+relative)
    controls = []
    def rejects(label, change, reason):
        mutated = copy.deepcopy(data)
        change(mutated)
        try:
            check_receipts(mutated,template_hash,buffer_hash)
        except ValueError as exc:
            need(str(exc) == reason, 'wrong evidence mutation reason')
            controls.append(label)
        else:
            raise ValueError('accepted evidence mutation: '+label)
    rejects('discovery result substituted',lambda d:d['result'].__setitem__('status','DISCOVERY'),'strict receipt status: result')
    rejects('private stock understated',lambda d:d['invoice'].__setitem__('physical',66742),'complete physical stock')
    rejects('controller mutation omitted',lambda d:d['controller']['mutations_rejected'].pop(),'twenty-one controller controls')
    rejects('buffer mutation omitted',lambda d:d['controller']['buffer_controls_rejected'].pop(),'six buffer controls')
    rejects('geometry mutation omitted',lambda d:d['geometry']['rejected'].pop(),'six geometry controls')
    rejects('profile child omitted',lambda d:d['assembly']['complex_profile'].__setitem__('7',2813),'complete global profile binding')
    rejects('nonboolean finite guard',lambda d:d['invoice']['strict_checks'].__setitem__('precision',1),'strict finite inequalities')
    bad = copy.deepcopy(stages); bad.pop()
    try:
        check_stages(bad)
    except ValueError as exc:
        need(str(exc) == 'strict stage coverage','wrong omitted-stage rejection')
        controls.append('strict stage omitted')
    else:
        raise ValueError('accepted omitted strict stage')
    manifest_controls = []
    for label,change in (
        ('changed executable pin',lambda d:d.__setitem__('code/audit_allcold.py','0'*64)),
        ('missing native input',lambda d:d.pop('native-base/local/LOCAL-PROGRAMS.json.gz')),
        ('unreviewed executable added',lambda d:d.__setitem__('unreviewed.py','0'*64))):
        bad = copy.deepcopy(pins); change(bad)
        try:
            check_manifest(bad,original)
        except ValueError as exc:
            need(str(exc) == 'frozen executable/data/native input contract','wrong frozen-input rejection')
            manifest_controls.append(label)
        else:
            raise ValueError('accepted frozen-input mutation: '+label)
    docs = copy.deepcopy(pins); docs['README.md'] = '0'*64
    check_manifest(docs,original)
    receipt = dict(status='PASS_STRICT_FOUR428_GLOBAL_EVIDENCE_BINDINGS_NO_MODERN_OUTER_CLAIM',
                   base='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',seed=39,
                   strict_inputs_sha256=sha(root/'STRICT-INPUTS.json'),original_strict_inputs_sha256=INPUTS_PIN,
                   frozen_runtime_files=len(pins),stages=STAGES,
                   input_contract='Exact source/data/native/provenance path-digest map; only README.md and .diff files may differ. Every actual runtime file is listed and hash checked.',
                   input_contract_mutations_rejected=manifest_controls,
                   strict_stage_logs={s['name']:s['log_sha256'] for s in stages},
                   checked_output_sha256={relative:sha(strict/relative) for relative in FILES.values()},
                   template_content_sha256=template_hash,buffer_binding_sha256=buffer_hash,
                   geometry_receipt_sha256=sha(root/'GEOMETRY-CONTROLS.json'),
                   geometry_scope='Checks the six named rejection records. The receipt itself has no input/source hashes; geometry_controls.py is frozen by the runtime input contract.',
                   verified_controls=dict(independent=8,interface_and_stock=5,controller=21,buffer=6,geometry=6,admission=114,bit=12),
                   legacy_spec_metadata='expected.mutations_rejected=15 is inherited unused metadata. The actual controller receipt must contain all 21 named rejections; successful frozen inputs are unchanged.',
                   evidence_mutations_rejected=controls,profile=PROFILE,live=66304,physical=66818,roles=285048,calls=666,
                   prefix_bits=1442,charged_prefix_bits=2048,row_coefficient=19545,row_limit=20161,
                   retained_balanced_assembly_kappa=data['result']['kappa'],
                   scope='Frozen strict finite-admission evidence and source/log/profile/physical bindings. The retained balanced assembly value is not the modern capped-phase-fusion exponent. A separate modern outer certificate is required before claiming an improved kappa; inherited all-size assumptions remain.')
    if args.out:
        args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
