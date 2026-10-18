#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate archived P53/T74 release evidence; no scientific replay is run.

Marius-Paul Dumitrean, with substantial OpenAI Codex assistance.
The separate reproduce.py runs fresh native providers and complete admission.
This checker uses only the Python standard library and imports no package code.
"""
import argparse
import ast
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE_HEAD = 'd01045dfb67428679618027dff552f1d032fa999'
SOURCE_MANIFEST = '44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be'
COMPARISON_SHA = 'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'
EVIDENCE_MANIFEST = 'a639c487bc5aa1e3573b369555f5fe53a20c119d62e32f826002394462fc9ce6'
PARENT_MANIFEST = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
PREPARER_SHA = 'a256d553549aa6317a52308a37b6144bb84a293139d35a98a1f6df09df43e1a0'
EXPECTED_C = Q('0.001719378870495538841812')
EXPECTED = EXPECTED_C-Q(1,10**46)-Q(1,10**70)
NATIVE_STAGES = ['native','ledgers','local-replay','wrappers','phases']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root, exclude=()):
    result = {}
    need(root.is_dir() and not root.is_symlink(), 'regular input directory')
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'symlink in authenticated tree')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            if name not in exclude:
                result[name] = sha(path)
    return result


def rational(value):
    return Q(value['rational']) if isinstance(value,dict) else Q(value)


def stages_ok(stages, expected, field='name', ordered=False):
    names = [row[field] for row in stages]
    need(len(names) == len(set(names)) == len(expected), 'distinct complete stage set')
    need((names == expected if ordered else set(names) == set(expected))
         and all(row['exit_code'] == 0 for row in stages), 'all required stages passed')


def check(package, source, evidence):
    need(sha(evidence/'MANIFEST.json') == EVIDENCE_MANIFEST, 'exact archived evidence manifest')
    manifest = read(evidence/'MANIFEST.json')
    need(len(manifest) == 167 and tree(evidence,('MANIFEST.json','COMPLETE.json')) == manifest,
         'all167 archived evidence files and exact inventory')
    complete = read(evidence/'COMPLETE.json')
    need(complete['status'] == 'PASS_COMPLETE_PUBLICATION_EVIDENCE_INDEX'
         and complete['file_count'] == 167
         and complete['total_bytes'] == sum((evidence/p).stat().st_size for p in manifest),
         'complete archive metadata/count/size')
    need(sha(source/'MANIFEST.json') == SOURCE_MANIFEST, 'exact P53 source manifest')
    source_files = read(source/'MANIFEST.json')
    need(len(source_files) == 549 and tree(source,('MANIFEST.json',)) == source_files,
         'all549 P53 source files')
    comparison_path = source/'outer/OUTER-CLAIM.json'
    need(sha(comparison_path) == COMPARISON_SHA, 'complete pinned P53 comparison claim')
    comparison = read(comparison_path)
    previous = Q(comparison['kappa_rational'])
    need(previous == Q(comparison['kappa']) and EXPECTED > previous, 'full3046-digit comparison')
    claim = read(package/'CLAIM.json')
    frozen = read(package/'data/CANDIDATE.json')
    data = {name:sha(package/'data'/name) for name in
            ('ORDER.json','FILL.json.gz','DISPATCH.json','PROFILE.json')}
    need(data == frozen['candidate_sha256'] == claim['candidate_sha256'], 'current candidate artifact hashes')
    need(Q(frozen['target']) == Q(claim['kappa']) == Q(claim['kappa_decimal']) == EXPECTED
         and Q(frozen['complex_lower']) == Q(claim['complex_lower']) == EXPECTED_C,
         'current exact candidate/claim target')
    need(frozen['source_head'] == frozen['comparison_head'] == claim['source_head'] == SOURCE_HEAD
         and frozen['comparison_claim_sha256'] == claim['comparison_claim_sha256'] == COMPARISON_SHA,
         'current candidate source and comparator')
    order = read(package/'data/ORDER.json')
    profile = read(package/'data/PROFILE.json')
    need(frozen['replicas'] == claim['replicas'] == 74 and len(order) == 666,
         'frozen T74 literal call count')
    C = evidence/'candidate'
    final = read(C/'RESULT.json')
    release = read(C/'release/RELEASE-RECEIPT.json')
    need(final['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'actual complete release PASS')
    need(Q(final['kappa']) == Q(final['kappa_decimal']) == Q(release['kappa_decimal']) == EXPECTED
         and Q(final['complex_lower']) == EXPECTED_C, 'archived exact admitted headline')
    need(Q(final['comparison_kappa']) == previous and Q(final['gain']) == EXPECTED-previous,
         'complete exact comparator and gain')
    need(final['comparison_pr'] == 2853 and final['comparison_head'] == SOURCE_HEAD
         and final['comparison_claim_sha256'] == COMPARISON_SHA
         and final['source_upstream_head'] == SOURCE_HEAD
         and final['source_commit'] == 'pr2853-dirtentry4'
         and final['source_manifest_sha256'] == SOURCE_MANIFEST
         and final['source_file_count'] == 549 and final['replicas'] == 74
         and final['actual_expected_helpers'] == 408, 'admitted source/interface/comparison pins')
    for field,name in [('fill','FILL.json.gz'),('order','ORDER.json'),('dispatch','DISPATCH.json')]:
        need(final[field+'_sha256'] == data[name], 'admitted current '+field)
    need(final['profile'] == profile, 'current complete paid profile')
    need(final['release_receipt_sha256'] == claim['full_release_receipt_sha256']
         == complete['release_receipt_sha256'] == sha(C/'release/RELEASE-RECEIPT.json'),
         'published full-release receipt hash')
    need(final['package_manifest_sha256'] == release['manifest_sha256']
         == complete['package_manifest_sha256'] == sha(C/'package/MANIFEST.json'), 'generated package manifest binding')
    generated = read(C/'package/MANIFEST.json')
    for path in (C/'package').rglob('*'):
        if path.is_file() and path.name != 'MANIFEST.json':
            need(generated[path.relative_to(C/'package').as_posix()] == sha(path), 'archived generated artifact hash')
    stages = read(C/'STAGES.json')
    stages_ok(stages,['owners','parent-lift','rebind','discovery','outer-check_ledger.py',
                      'outer-independent_check.py','release'],ordered=True)
    need(final['stages'] == stages, 'final recorded complete admission stages')
    for row in stages:
        need(row['log_sha256'] == sha(C/(row['name']+'.log')), 'admission stage log binding')

    # Independently inspect the saved layers, rather than trusting LAYER-BINDING's summary.
    P=C/'package';strict=C/'release/verify/strict'
    asm=read(strict/'ASSEMBLY.json');supplier=Q(asm['kappa'])
    verify=read(C/'release/verify/RESULT.json');spec=read(P/'new/SPEC.json')
    ledger=read(P/'outer/LEDGER.json');ind=read(P/'outer/INDEPENDENT.json');outer=read(P/'outer/OUTER-CLAIM.json');b=read(P/'outer/B.json')
    need(supplier == Q(verify['kappa']) == Q(read(strict/'RESULT.json')['kappa'])
         == Q(read(P/'CLAIM.json')['kappa']) == Q(spec['expected']['kappa']), 'fresh supplier layer')
    need(EXPECTED_C == Q(asm['complex_lower']) == Q(spec['expected']['complex_lower'])
         == rational(ledger['complex_lower_pinned']), 'admitted complex endpoint layers')
    need(all(x == profile for x in [asm['complex_profile'],spec['expected']['global_profile'],
         b['profile'],ledger['profile']]), 'full paid profile across layers')
    need(Q(b['b']) == EXPECTED_C-Q(1,10**104) and Q(b['b_above_endpoint']) == EXPECTED_C+Q(1,10**24),
         'strict endpoint neighborhood')
    moments=[x for x in asm['moments'] if x['side']=='complex']
    need(len(moments)==2 and {x['accept'] for x in moments}=={True,False}, 'accept/reject complex moment pair')
    for row in moments:
        need(row['surcharge'] is False and Q(row['endpoint']) == (EXPECTED_C if row['accept'] else EXPECTED_C+Q(1,10**24)), 'exact moment endpoints')
        for method in ('mercator','base_two'):
            lo,hi=map(Q,row[method]);need(lo<=hi and (hi<0 if row['accept'] else lo>0), 'directed exact moment signs')
    row=ledger['rows']['struct_boundary_radix_union']
    need(len(row['strict_checks'])==63 and all(rational(v)>0 for v in row['strict_checks'].values()), '63 strict modern margins')
    rejects=ledger['rejecting_controls']['struct_boundary_radix_union']
    need(len(rejects)==17 and all(isinstance(v,dict) and v
         and all(rational(margin)<=0 for margin in v.values()) for v in rejects.values()),
         '17 modern controls each contain actual nonpositive failed margins')
    need(EXPECTED == rational(row['kappa']) == Q(outer['kappa']) == Q(outer['kappa_rational'])
         == Q(ind['rows']['struct_boundary_radix_union']['kappa']) > supplier,
         'modern headline equals C minus both exact slacks')
    need(ind['status']=='PASS_INDEPENDENT_BALANCE_DERIVATION'
         and ind['source_sha256']==sha(P/'new/SPEC.json'), 'independent outer source binding')
    need((ledger['m'],ledger['W'])==(73,66304), 'modern global dimension/live count')
    counts={}
    for name,path,key,expected in [
        ('admission',strict/'ADMISSION-CONTROLS.json','rejected_controls',119),
        ('bit',strict/'BIT-CONTROLS.json','rejected_controls',12),
        ('independent_owner',strict/'INDEPENDENT.json','controls_rejected',8),
        ('geometry',C/'release/verify/GEOMETRY-CONTROLS.json','rejected',6),
        ('controller',strict/'global/audit/ASYNC-AUDIT.json','mutations_rejected',25)]:
        doc=read(path);names=[v['name'] if isinstance(v,dict) else v for v in doc[key]]
        need(doc['status'].startswith('PASS_') and len(names)==len(set(names))==expected,
             'actual distinct '+name+' rejection array')
        counts[name]=len(names)
    need(complete['control_counts']==counts, 'archive actual control counts')
    owner=read(strict/'INDEPENDENT.json');controller=read(strict/'global/audit/ASYNC-AUDIT.json')
    need(owner['roles']==controller['complex_hosted_residuals']==271728
         and owner['calls']==controller['complete_invocations']==666
         and owner['live']==66304 and owner['physical']==66794
         and owner['profile']==controller['complex_profile']==profile
         and controller['all_provider_program_phase_and_wrapper_bindings'] is True
         and controller['one_owner_per_complete_invocation'] is True, 'owner/program/phase binding receipts')
    prefix=read(strict/'global/audit/GLOBAL-PREFIX.json');bn=prefix['tensor_block_norm']
    need(bn['status']=='PASS_TENSOR_BLOCK_NORM_CERTIFICATE' and bn['replicas']==74
         and bn['physical_families']==66794 and bn['live_families']==66304
         and bn['max_active_depth']==18 and bn['local_actual_prefix_bits']==70
         and bn['physical_stock_bits']==2644 and bn['stock_l2_bits']==1322
         and prefix['global_prefix_bits']==bn['actual_prefix_bits']==1452
         and bn['required_reserve_bits']==1510
         and prefix['retained_payload_bits']==bn['retained_payload_bits']==2048
         and owner['physical_row_coefficient']==19545<owner['row_limit']==20161,
         'actual blocknorm/reserve/stock row')
    text=(C/'release/verify/rebuild-borrow-words.log').read_text()
    need('PASS_REBUILD_BORROW' in text,'complete changed-word source rebuild')
    new={};expected={'dirtentry4_'+name+'_rejected' for name in
        ('read_dropped','read_sign_flipped','partner_read_dropped','removal_missing','wrong_entrance_frame')}
    for tag,raw in re.findall(r'^DIRTENTRY4-CONTROLS (base|extra) (.*)$',text,re.M):
        need(tag not in new,'one new-control receipt per provider');doc=ast.literal_eval(raw)
        rows={k:v for k,v in doc.items() if k.endswith('_rejected')}
        need(set(rows)==expected and all(v is True for v in rows.values()), 'five actual new dirtentry controls')
        for key in expected:
            reason=doc[key.removesuffix('_rejected')+'_reason']
            need(reason and 'paid profile mismatch' not in reason and 'width inventory mismatch' not in reason,
                 'structural/algebraic control reason')
        new[tag]=doc
    need(set(new)=={'base','extra'},'both providers new controls')

    N=evidence/'native';cache=N/'native-cache';nr=read(N/'RESULT.json');native=read(N/'NATIVE-RECEIPT.json')
    need(nr['status']=='PASS_PR2853_FRESH_NATIVE_PREPARATION'
         and nr['source_file_count']==549 and nr['source_manifest_sha256']==SOURCE_MANIFEST
         and nr['preparer_sha256']==PREPARER_SHA==sha(package/'prepare_aphase_native.py')
         and nr['native_receipt_sha256']==final['native_receipt_sha256']==complete['native_receipt_sha256']
         ==sha(N/'NATIVE-RECEIPT.json'), 'native producer/source/receipt binding')
    need(native['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
         and native['manifest_sha256']==SOURCE_MANIFEST and native['source_commit']=='pr2853-dirtentry4'
         and native['fresh_current_provider_count']==native['fresh_retained_native_count']==2
         and native['fresh_retained_parent'] is True and native['reused_retained_parent'] is False
         and native['reused_retained_native_count']==0, 'four fresh archived native chains and parent')
    need(len(native['cache_files'])==63 and tree(cache)==native['cache_files'], 'complete63 native cache files')
    ns=read(N/'STAGES.json');stages_ok(ns,['native-base','native-extra','native-retained-base','native-retained-extra','retained-parent'])
    need(nr['stages']==ns,'native stage receipt equality')
    for row in ns:need(row['log_sha256']==sha(N/(row['name']+'.log')),'native stage log binding')
    old=source/'vendor/pr1297'
    need(sha(old/'MANIFEST.json')==PARENT_MANIFEST and tree(old,('MANIFEST.json',))==read(old/'MANIFEST.json'), 'full retained parent source')
    words={tag:source/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz') for tag in ('base','extra')}
    retained={'base':old/'gauge44-word.json.gz','extra':old/'extra-word.json.gz'}
    for word in list(words.values())+list(retained.values()):
        entry=cache/sha(word)
        need(read(entry/'local/FULL-WORD.json.gz')==read(word), 'each native full word matches source')
        stages_ok(read(entry/'STEPS.json'),NATIVE_STAGES,field='step',ordered=True)
        for name in ['INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json']:
            need(read(entry/'local'/name)['status'].startswith('PASS_'), 'local/native/phase/wrapper receipt PASS')
    for tag,word in words.items():
        entry=cache/sha(word);binding=native['providers'][tag]
        need(binding['word_sha256']==sha(word) and tree(entry,('CACHE.json',))==binding['complete_native_files'], 'current provider complete cache binding')
        local=read(entry/'local/LOCAL-CHECKS.json');phase=read(entry/'local/CLIFFORD-REVIEW.json')
        for direction in ('forward','backward'):
            q=local[direction]
            need(q['all_columns']==632 and q['private_centers_cleared'] is True
                 and q['private_coefficient_stream_cleared_after_each_macro'] is True
                 and q['zero_buffers_returned_to_zero']==72, 'all current columns and private work clear')
        need(phase['directed_edges']==2943 and phase['warp_recipes']==180
             and phase['warp_recipes_equal_exact_512_column_product'] is True
             and phase['all_child_equalities_include_global_phase'] is True, 'current full phase products')
    parentdir=cache/'_receipts'/PARENT_MANIFEST;pr=read(parentdir/'RECEIPT.json')
    need(sha(parentdir/'RECEIPT.json')==native['retained_parent_receipt_sha256']
         and pr['schema']=='parent-receipt/1' and pr['vendor_manifest_sha256']==PARENT_MANIFEST
         and pr['claim_sha256']==sha(old/'CLAIM.json')
         and pr['words']=={tag:sha(word) for tag,word in retained.items()}, 'retained parent receipt source binding')
    need(set(pr['files'])=={'RESULT.json','STAGES.json'}
         and set(tree(parentdir))=={'RECEIPT.json','RESULT.json','STAGES.json'}
         and all(sha(parentdir/k)==v for k,v in pr['files'].items()), 'all retained parent receipt files')
    ps=read(parentdir/'STAGES.json');names=[name+'-'+tag for tag in ('base','extra') for name in
        ('literal-word','independent-local','fusion-controls','x54-controls','kernel543-controls','kernel-controls','leaver-premise')]+['literal-construct','strict-global']
    stages_ok(ps,names)
    parent=read(parentdir/'RESULT.json')
    need(parent['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
         and parent['stages']==ps and parent['kappa']==read(old/'CLAIM.json')['kappa']
         and parent['base_native_reuse'] is True and parent['extra_native_reuse'] is True
         and read(N/'retained-parent/RESULT.json')==parent and read(N/'retained-parent/STAGES.json')==ps,
         'actual16 parent stages/claim/PASS binding')
    wrapper=read(evidence/'wrapper/RESULT.json');ws=read(evidence/'wrapper/STAGES.json')
    stages_ok(ws,['complete-admission'],field='stage',ordered=True)
    need(wrapper['status']=='PASS_APHASE_RESIDUE_COMPLETE_REPLAY' and Q(wrapper['kappa'])==EXPECTED
         and wrapper['candidate_result_sha256']==sha(C/'RESULT.json')
         and wrapper['fresh_native_this_invocation'] is False and wrapper['explicit_native_reuse'] is True
         and wrapper['stages']==ws and ws[0]['log_sha256']==sha(evidence/'wrapper/complete-admission.log')
         and wrapper['native_binding']=={'native_receipt_sha256':sha(N/'NATIVE-RECEIPT.json'),
             'result_sha256':sha(N/'RESULT.json'),'cache_files':native['cache_files']}, 'actual prepared-native wrapper invocation')
    for name in ['reproduce.py','admit_aphase_residue.py','prepare_aphase_native.py','data/CANDIDATE.json']+['data/'+x for x in data]:
        need(wrapper['executable_and_data_sha256'][name]==sha(package/name), 'executed wrapper input '+name)
    need(Q(complete['headline_kappa'])==Q(complete['headline_decimal'])==EXPECTED
         and Q(complete['complex_lower'])==EXPECTED_C and Q(complete['gain_vs_PR2853'])==EXPECTED-previous
         and complete['comparison_pr']==2853 and complete['comparison_head']==SOURCE_HEAD
         and complete['comparison_claim_sha256']==COMPARISON_SHA and complete['profile']==profile
         and complete['modern_strict_constraints']==63 and complete['modern_rejections']==17
         and complete['new_PR2853_rebuild_controls_per_provider']==5
         and complete['native_current_providers']==complete['native_retained_providers']==2
         and complete['native_retained_parent_stages']==16, 'complete summary matches actual evidence')
    return {'status':'PASS_ARCHIVED_P53_COMPLETE_RELEASE_EVIDENCE','kappa':str(EXPECTED),
            'evidence_files':167,'source_files':549,'native_cache_files':63,'native_chains':4,
            'retained_parent_stages':16,'actual_rejection_counts':counts,'new_source_rejections':10,
            'modern_strict_constraints':63,'modern_rejections':17,
            'evidence_manifest_sha256':EVIDENCE_MANIFEST,'source_manifest_sha256':SOURCE_MANIFEST,
            'controller_note':'The inherited summary says15; the authenticated actual controller array has25 distinct rejections.',
            'scope':'Read-only archive-byte, source, candidate, exact-layer and successful execution-receipt validation. This does not rerun native chains, global admission, outer arithmetic, or Lean, and does not resolve inherited theorem assumptions.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,default=HERE)
    ap.add_argument('--source',type=Path)
    ap.add_argument('--evidence',type=Path)
    a=ap.parse_args();package=a.package.resolve()
    source=(a.source or package.parent/'gmx-t74-borrow43-handoff').resolve()
    evidence=(a.evidence or package/'evidence/full').resolve()
    need(not a.package.is_symlink() and not (a.source and a.source.is_symlink())
         and not (a.evidence and a.evidence.is_symlink()), 'input directory symlinks prohibited')
    print(json.dumps(check(package,source,evidence),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
