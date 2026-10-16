#!/usr/bin/env python3
"""Bind the published claim to retained, complete fresh replay evidence.

This bounded check authenticates receipts; it does not rerun native admission.
Apache-2.0. Marius-Paul Dumitrean with substantial OpenAI Codex assistance.
"""
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

import combined_adapt
import replay_engine

HERE = Path(__file__).resolve().parent
sys.set_int_max_str_digits(0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def bind_claim(claim, result, ledger):
    need(result['status'] == 'PASS_CONCENTRATED_PRELIFE_COMPLETE_FRESH_FINITE_ADMISSION_AND_OUTER',
         'Complete actual cold status')
    row = ledger['rows']['struct_boundary_radix_union']
    need(Q(claim['kappa']) == Q(result['kappa']) == Q(row['kappa']['rational']),
         'Exact published and outer kappa')
    need(Q(claim['kappa_decimal']) == Q(result['kappa_decimal']) ==
         Q(row['kappa']['decimal']) == Q(claim['kappa']), 'Exact decimal claim bindings')
    need(claim['global_profile'] == result['global_profile'] == ledger['profile'] ==
         read(HERE/'expected/PROFILE.json'), 'Complete paid profile')
    need(result['candidate_fill_sha256'] == sha(HERE/'expected/FILL.json.gz') and
         result['candidate_order_sha256'] == sha(HERE/'expected/ORDER.json'), 'Actual cold owner input')
    need(result['driver_sha256'] == sha(HERE/'replay_engine.py') and
         result['adapter_sha256'] == sha(HERE/'combined_adapt.py'), 'Executed driver and adapter')
    need(result['candidate_manifest_sha256'] == combined_adapt.CANDIDATE_MANIFEST and
         result['source_manifest_sha256'] == replay_engine.MANIFEST_SHA and
         result['source_head'] == replay_engine.SOURCE_HEAD and
         result['concentrated_source_head'] == combined_adapt.REFERENCE_HEAD,
         'Exact source and candidate bindings')
    old = Q(read(HERE.parent/'t74-concentrated-source-partners/CLAIM.json')['kappa'])
    need(Q(claim['kappa']) > old and Q(claim['gain']) == Q(claim['kappa'])-old,
         'Strict gain over the entire PR2696 rational')
    C = Q(read(HERE/'evidence/EXACT-PRICE.json')['endpoint']['lower'])
    need(Q(result['complex_lower']) == Q(claim['complex_lower']) == C ==
         Q(ledger['complex_lower_pinned']['rational']), 'Certified complex endpoint')
    need(Q(claim['kappa']) < C, 'Strictly interior outer saving')
    need(result['native_and_parent_reuse'] is False and
         result['inherited_parent_geometry_reuse'] is True,
         'Fresh native/parent receipts and explicit inherited geometry coverage')


def main():
    need(__debug__, 'Assertions are required; run without optimized Python')
    for name, digest in read(HERE/'ARTIFACTS.json').items():
        need(sha(HERE/name) == digest, 'Published artifact pin: '+name)
    source = HERE.parent/'gmx-t74-borrow43-handoff'
    reference = HERE.parent/'t74-concentrated-source-partners'
    combined_adapt.authenticate(HERE/'expected', reference)
    need(sha(source/'MANIFEST.json') == replay_engine.MANIFEST_SHA, 'Exact PR2679 manifest')
    pins = read(source/'MANIFEST.json')
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*')
              if p.is_file() and p != source/'MANIFEST.json'}
    need(actual == set(pins) and len(pins) == 491, 'Complete PR2679 source set')
    for name, digest in pins.items():
        need(sha(source/name) == digest, 'Frozen PR2679 source: '+name)
    archive = read(HERE/'ARCHIVE.json')
    raw = {}
    for group, records in archive.items():
        for name, record in records.items():
            data = (HERE/record['path']).read_bytes()
            if record['storage_compression'] == 'gzip':
                data = gzip.decompress(data)
            need(hashlib.sha256(data).hexdigest() == record['original_sha256'],
                 'Original receipt bytes: '+name)
            raw[group, name] = data

    def receipt(name, group='full'):
        data = raw[group, name]
        return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)

    def stages(items, count, label):
        need(len(items) == count and all(type(x['exit_code']) is int and
             x['exit_code'] == 0 for x in items), label)

    claim = read(HERE/'CLAIM.json')
    result = receipt('RESULT.json')
    ledger = receipt('derivative/outer/LEDGER.json')
    bind_claim(claim, result, ledger)
    need(sha(HERE/claim['full_receipt']) == claim['full_receipt_sha256'], 'Published full receipt')
    stages(result['stages'], 18, 'All eighteen current stages')
    need({x['name'] for x in result['stages']} == {
        'fine-engine-oracle', 'rebuild-words-566', 'rebuild-borrow-words',
        'native-base', 'native-extra', 'retained-parent', 'audit-local-566-base',
        'audit-local-566-extra', 'lemmag-labels', 'candidate-owner-reconstruction',
        'candidate-parent-lift', 'rebind', 'discover', 'strict', 'geometry-controls',
        'outer-check_ledger.py', 'outer-independent_check.py', 'outer-evidence'},
        'Every required top-level stage exactly once')
    need(result['stages'] == receipt('STAGES.json'), 'Actual top stage list')
    parent = receipt('parent/RESULT.json')
    stages(parent['stages'], 18, 'All eighteen retained-parent stages')
    need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and
         Q(parent['kappa']) == Q(read(source/'vendor/pr1297/CLAIM.json')['kappa']) and
         parent['stages'] == receipt('parent/STAGES.json'), 'Exact retained-parent admission')
    need(parent['base_native_reuse'] is False and parent['extra_native_reuse'] is False,
         'Fresh parent native chains')
    strict = receipt('strict/RESULT.json')
    need(strict['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL', 'Strict admission')
    stages(receipt('strict/STAGES.json'), 8, 'All eight strict stages')
    need(strict['steps'] == receipt('strict/STAGES.json') and
         [x['name'] for x in strict['steps']] ==
         ['bind', 'emit', 'audit', 'invoice', 'assembly', 'admission', 'bit', 'independent'],
         'Exact strict stage sequence')
    assembly = receipt('strict/ASSEMBLY.json')
    need(assembly['complex_profile'] == claim['global_profile'] and
         Q(assembly['complex_lower']) == Q(claim['complex_lower']) and
         len(assembly['outer']) == 47, 'Full supplier assembly and inequalities')
    need(Q(assembly['bit_lower']) == Q('0.001733427039589844234749'), 'Retained exact bit endpoint')
    need(len(receipt('strict/ADMISSION-CONTROLS.json')['rejected_controls']) == 114 and
         len(receipt('strict/BIT-CONTROLS.json')['rejected_controls']) == 12,
         'Complete supplier and bit rejection controls')
    need(strict['independent']['roles'] == 276390 and
         len(strict['independent']['controls_rejected']) == 8, 'Independent full owner check')
    controller = receipt('strict/global/audit/ASYNC-AUDIT.json')
    need(len(controller['mutations_rejected']) == 25, 'Actual current controller controls')
    invoice = receipt('strict/global/audit/PREFIX-AND-INVOICE.json')
    need((invoice['physical'], invoice['live'], invoice['helpers'], invoice['private_zero_buffers']) ==
         (66801, 66304, 415, 72), 'Complete charged physical invoice')
    need((claim['physical'], claim['live'], claim['helpers'], claim['private_zero_buffers'],
          claim['roles'], claim['calls'], claim['rank_mass']) ==
         (66801, 66304, 415, 72, 276390, 666, 4816512), 'Published complete inventory')
    need(sum(int(r)*n for r,n in claim['global_profile'].items()) == claim['rank_mass'],
         'Published full rank mass')
    need(len(receipt('GEOMETRY-CONTROLS.json')['rejected']) == 6, 'All geometry controls')
    stock = receipt('PRIVATE-STOCK-BINDING.json')
    for tag in ('base', 'extra'):
        steps = receipt(f'native-{tag}/STEPS.json')
        stages(steps, 5, 'Complete fresh native chain '+tag)
        need([x['step'] for x in steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'],
             'All native obligations '+tag)
        need(receipt(f'native-{tag}/local/FULL-WORD.json.gz') ==
             read(HERE/f'expected/words/{tag}.json.gz'), 'Complete actual native word '+tag)
        canonical = receipt(f'native-{tag}/local/CANONICAL-WORD.json.gz')
        need(canonical['R'] == 415 and len(canonical['zero_buffers']) == 72,
             'Native private-buffer inventory '+tag)
        need(hashlib.sha256(raw['full', f'native-{tag}/local/CANONICAL-WORD.json.gz']).hexdigest() ==
             stock['canonical_sha256'][tag], 'Actual stock/canonical binding '+tag)
        canonical_hash = stock['canonical_sha256'][tag]
        recipe_hash = hashlib.sha256(raw['full', f'native-{tag}/local/CLIFFORD-RECIPES.json']).hexdigest()
        program_hash = hashlib.sha256(raw['full', f'native-{tag}/local/LOCAL-PROGRAMS.json.gz']).hexdigest()
        phase = receipt(f'native-{tag}/local/CLIFFORD-REVIEW.json')
        recipes = receipt(f'native-{tag}/local/WARP-RECIPE-CHECKS.json')
        local = receipt(f'native-{tag}/local/LOCAL-CHECKS.json')
        independent = receipt(f'native-{tag}/local/INDEPENDENT-LOCAL-REPLAY.json')
        need(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and
             recipes['status'] == 'PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS' and
             phase['canonical_word_sha256'] == recipes['canonical_word_sha256'] == canonical_hash and
             phase['recipe_sha256'] == recipes['recipe_sha256'] == recipe_hash,
             'Actual physical phase and recipe bindings '+tag)
        need(phase['warp_recipes'] == recipes['warp_classes'] == 166 and
             recipes['operators'] == 65 and recipes['columns_each'] == 512 and
             len(recipes['controls_rejected']) == 13 and
             all(phase[k] is True for k in ('warp_recipes_rank_zero',
                 'warp_recipes_equal_exact_512_column_product',
                 'all_child_equalities_include_global_phase')), 'Complete native phase coverage '+tag)
        need(independent['canonical_word_sha256'] == canonical_hash and
             independent['local_programs_sha256'] == program_hash,
             'Independent native program binding '+tag)
        for orientation in ('forward', 'backward'):
            need(local[orientation]['all_columns'] == 639 and
                 local[orientation]['zero_buffers_returned_to_zero'] == 72 and
                 local[orientation]['paid_profile'] == claim['local_profile'] and
                 local[orientation]['private_centers_cleared'] is True and
                 local[orientation]['private_coefficient_stream_cleared_after_each_macro'] is True,
                 'Native arbitrary-input profile and cleanup '+tag+' '+orientation)
            need(independent['local'][orientation]['all_exact_columns'] == 639 and
                 independent['local'][orientation]['private_work_erased'] is True and
                 independent['local'][orientation]['zero_buffers_returned_to_zero'] == 72 and
                 independent['paid_profiles'][orientation] == claim['local_profile'],
                 'Independent native local coverage '+tag+' '+orientation)
        need(read(HERE/f'independent-inputs/{tag}.json.gz') ==
             read(HERE/f'expected/words/{tag}.json.gz'), 'Independent context word '+tag)
    need(read(HERE/'independent-inputs/PROVIDERS.json') == read(HERE/'expected/PROVIDERS.json'),
         'Independent actual width and paid-profile registry')
    row = ledger['rows']['struct_boundary_radix_union']
    need(len(row['strict_checks']) == 63 and
         len(ledger['rejecting_controls']['struct_boundary_radix_union']) == 17,
         'Modern outer inequalities and rejection controls')
    need(b'PASS_EXACT_REPLAY 19' in raw['full', 'outer-evidence.log'] and
         b'PASS_OUTER' in raw['full', 'outer-evidence.log'], 'Nineteen inherited outer replays')
    ordinary = receipt('combined-modern-ordinary-witness.json', 'audit')
    need(ordinary['script_sha256'] == sha(HERE/'ordinary_witness.py') and
         ordinary['source_ledger_sha256'] == hashlib.sha256(raw['full', 'derivative/outer/LEDGER.json']).hexdigest() and
         ordinary['source_spec_sha256'] == hashlib.sha256(raw['full', 'derivative/new/SPEC.json']).hexdigest() and
         Q(ordinary['exact_modern_kappa']) == Q(claim['kappa']) and
         ordinary['sufficient_stage_count'] == 37 and
         ordinary['minimum_or_optimal_stage_count_claimed'] is False,
         'Actual modern ordinary supplement')
    # Evidence controls test coupling to the executed run, not another root computation.
    rejected = []
    for name in ('kappa', 'profile', 'fill', 'driver'):
        c, r = copy.deepcopy(claim), copy.deepcopy(result)
        if name == 'kappa':
            c['kappa'] = str(Q(c['kappa'])+Q(1, 10**24))
        elif name == 'profile':
            c['global_profile']['1'] += 1
        elif name == 'fill':
            r['candidate_fill_sha256'] = '0'*64
        else:
            r['driver_sha256'] = '0'*64
        try:
            bind_claim(c, r, ledger)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Accepted changed admission binding: '+name)
    need(len(rejected) == 4, 'All admission-binding controls')
    print('PASS_PUBLISHED_FULL_ADMISSION_BINDINGS', len(archive['full']), 'receipts;',
          len(rejected), 'rejected binding controls')


if __name__ == '__main__':
    main()
