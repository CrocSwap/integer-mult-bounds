#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Prepare and fully admit a changed-replica literal order/fill derivative.

PR2833 extension by Yiyang Lu with OpenAI Codex assistance: add the exact
immutable dirt-entry source profile and exact full outer-claim comparisons to
PR2833 and the newer PR2843 T124 allocation. All
inherited native, owner, invoice, block-norm, controls and release checks retained.

Research runtime only: native providers must already have passed freshly and
are authenticated by --native-receipt. --prepare-only stops before discovery.
Default complete admission preserves the original verify.py and release stages.
Source inputs and the native cache are read-only; all output uses fresh --work.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

SOURCE_COMMIT = 'local-joint12-refit393'
SOURCE_MANIFEST = '1e75eabffe1ce311cc3bddc05e76118cbdedfc806200a906c57fbc5a5dd213eb'
PARENT_MANIFEST = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
PRECISION = dict(endpoint_digits=24, grid_digits=18, margin_digits=28, bootstrap_steps=12)
COMPARISON_SHA = '252b7bbdbef293f643633ff95ba7d1eabbe83e1eebcd1cb06f51834256bde1f3'
COMPARISON_HEAD = 'e8b771ba132fe632796b28c1742a8d096c04519f'
NATIVE_STAGES = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
# Supported immutable source versions; CLI selection never accepts arbitrary hashes.
SOURCE_PROFILES = {
    'pr2853': dict(commit='pr2853-dirtentry4', manifest='44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be', helpers=408, source_file_count=549, upstream_head='d01045dfb67428679618027dff552f1d032fa999'),
    'pr2833': dict(commit='pr2833-dirtentry', manifest='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f', helpers=408, source_file_count=541, upstream_head='e9307b48d7d1b690939935ecef0f8e524e6d92f4'),
    'pr2766': dict(commit='local-joint12-refit393', manifest='1e75eabffe1ce311cc3bddc05e76118cbdedfc806200a906c57fbc5a5dd213eb', helpers=415, source_file_count=491, upstream_head='e6df920cd0110e4b629e2ad84eddcb539001e174'),
    'pr2802': dict(commit='local-joint12-pr2733', manifest='9c72b4301057a6c204c40bb6584eb74b779e06618bcd98d706d726c3e2c92451', helpers=408, source_file_count=506, upstream_head='17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd'),
}
COMPARISONS = {
    'pr2853': dict(pr=2853, head='d01045dfb67428679618027dff552f1d032fa999', sha256='eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa', field='kappa_rational'),
    'pr2848': dict(pr=2848, head='c50d12e4720cd1fef2b5a65e337e37de9731879a', sha256='aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9', field='kappa'),
    'pr2843': dict(pr=2843, head='47a7227c044cd0cabb1432a06c61dd5d60c07f5a', sha256='0adc0edfade0260c65e79867b6c8b96f58dfe29d38aa30cfb8f3d5e9c7e828d9', field='kappa'),
    'pr2833': dict(pr=2833, head='e9307b48d7d1b690939935ecef0f8e524e6d92f4', sha256='6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70', field='kappa_rational'),
    'pr2767': dict(pr=2767, head='e8b771ba132fe632796b28c1742a8d096c04519f', sha256='252b7bbdbef293f643633ff95ba7d1eabbe83e1eebcd1cb06f51834256bde1f3', field='kappa_rational'),
    'pr2802': dict(pr=2802, head='17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd', sha256='a2fcbc8a3ad3095ecbd310a26c02e9d11c28e4d105669a08bbdfb39d7704db51', field='kappa'),
}



# Discovery records are shared by parallel mutation-audit processes on Windows.
# Only discovery bookkeeping changes; strict pin comparison below it is untouched.
DISCOVERY_APPEND_OLD = "   with open(os.environ['WITNESS_RECORD'],'a')as f:f.write(json.dumps([key,got],default=str)+chr(10))"
DISCOVERY_APPEND_NEW = r'''   import time as _wr_time
   _wr_path=Path(os.environ['WITNESS_RECORD'])
   _wr_lock=_wr_path.with_name(_wr_path.name+'.append.lock')
   _wr_deadline=_wr_time.monotonic()+60
   _wr_fd=None
   while _wr_fd is None:
    try:_wr_fd=os.open(_wr_lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
     if _wr_time.monotonic()>=_wr_deadline:raise TimeoutError('discovery record lock timeout; existing lock preserved')
     _wr_time.sleep(.005)
   try:
    with _wr_path.open('a',encoding='utf-8',newline='\n')as _wr_out:
     _wr_out.write(json.dumps([key,got],default=str)+chr(10))
     _wr_out.flush()
   finally:
    os.close(_wr_fd)
    _wr_lock.unlink()'''


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    body = path.read_bytes()
    return json.loads(gzip.decompress(body) if path.suffix == '.gz' else body)


def write(path, value):
    # All output targets belong to this fresh work tree; never unlink an open lock.
    lock = path.with_name(path.name + '.lock')
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        descriptor = None
        path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
    finally:
        if descriptor is not None:
            os.close(descriptor)
        lock.unlink()


def tree(root, exclude=()):
    result = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'unbound symlink: ' + str(path))
        name = path.relative_to(root).as_posix()
        if path.is_file() and name not in exclude:
            result[name] = sha(path)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'fill', 'order', 'dispatch', 'native-cache', 'native-receipt', 'work', 'replica-helper-dir', 'reconstructor', 'comparison-claim', 'blocknorm-checker'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--prepare-only', action='store_true')
    ap.add_argument('--source-profile', choices=sorted(SOURCE_PROFILES), default='pr2853')
    ap.add_argument('--comparison-profile', choices=sorted(COMPARISONS), default='pr2853')
    a = ap.parse_args()
    global SOURCE_COMMIT, SOURCE_MANIFEST, COMPARISON_SHA, COMPARISON_HEAD
    source_profile = SOURCE_PROFILES[a.source_profile]
    comparison = COMPARISONS[a.comparison_profile]
    SOURCE_COMMIT, SOURCE_MANIFEST = source_profile['commit'], source_profile['manifest']
    COMPARISON_SHA, COMPARISON_HEAD = comparison['sha256'], comparison['head']
    expected_helpers, comparison_pr = source_profile['helpers'], comparison['pr']
    need(not sys.flags.optimize and a.jobs > 0, 'enabled assertions and positive jobs required')
    source, cache, work = a.source.resolve(), a.native_cache.resolve(), a.work.resolve()
    need(not work.exists() and not work.is_relative_to(source) and not work.is_relative_to(cache),
         'fresh external work required')
    need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST, 'COMPOSED manifest pin')
    source_files = read(source / 'MANIFEST.json')
    need(len(source_files) == source_profile['source_file_count'] and tree(source, ('MANIFEST.json',)) == source_files,
         'complete COMPOSED source inventory and hashes')
    helper_dir = a.replica_helper_dir.resolve()
    helper_paths = [helper_dir / n for n in ('lift_parent.py', 'replica_parent.py')] + [a.reconstructor.resolve()]
    external_hashes = {str(p): sha(p) for p in helper_paths + [a.fill.resolve(), a.order.resolve(), a.dispatch.resolve(), a.comparison_claim.resolve(), a.blocknorm_checker.resolve()]}
    need(sha(a.comparison_claim) == COMPARISON_SHA, 'exact pinned frontier headline comparison')
    comparison_claim = read(a.comparison_claim)
    need('headline_kappa_source' not in comparison_claim and comparison['field'] in comparison_claim,
         'comparison must be full headline outer claim, not supplier-only CLAIM')
    previous = Q(comparison_claim[comparison['field']])
    need(previous == Q(comparison_claim['kappa']), 'comparison rational/decimal equality')
    order_input = read(a.order)
    need(order_input and all(isinstance(x,list) and len(x)==2 and all(type(v)is int for v in x) for x in order_input), 'literal integer call order')
    T = 1 + max(r for st,r in order_input)
    need(T > 0 and len(order_input)==9*T and set(map(tuple,order_input))=={(st,r) for st in range(9) for r in range(T)}, 'complete new replica coverage')
    need(all([st for st,r in order_input if r==rep]==list(range(9)) for rep in range(T)), 'source stage projection')
    dispatch_input = read(a.dispatch)
    need(len(dispatch_input)==9*T and {(st,r) for st,r,pid in dispatch_input}==set(map(tuple,order_input)), 'complete explicit dispatch')
    native_receipt = read(a.native_receipt)
    need(native_receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
         and native_receipt['source_commit'] == SOURCE_COMMIT
         and native_receipt['manifest_sha256'] == SOURCE_MANIFEST, 'native receipt source binding')
    need(tree(cache) == native_receipt['cache_files'], 'complete native/parent cache hashes')
    old = source / 'vendor/pr1297'
    need(sha(old / 'MANIFEST.json') == PARENT_MANIFEST, 'retained parent pin')
    parent_receipt = cache / '_receipts' / PARENT_MANIFEST / 'RECEIPT.json'
    need(sha(parent_receipt) == native_receipt['retained_parent_receipt_sha256'], 'parent receipt pin')
    pr = read(parent_receipt)
    need(pr['vendor_manifest_sha256'] == PARENT_MANIFEST and pr['claim_sha256'] == sha(old / 'CLAIM.json'),
         'parent receipt claim binding')
    for name, digest in pr['files'].items():
        need(sha(parent_receipt.parent / name) == digest, 'parent receipt file')
    parent_result = read(parent_receipt.parent / 'RESULT.json')
    need(parent_result['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
         and parent_result['kappa'] == read(old / 'CLAIM.json')['kappa'], 'retained parent completed admission')
    natives = {}
    for tag in ('base', 'extra'):
        word = source / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz')
        entry = cache / sha(word)
        binding = native_receipt['providers'][tag]
        need(binding['word_sha256'] == sha(word)
             and tree(entry, ('CACHE.json',)) == binding['complete_native_files'], 'native full-tree binding')
        need(read(entry / 'local/FULL-WORD.json.gz') == read(word), 'native complete word')
        stages = read(entry / 'STEPS.json')
        need([s['step'] for s in stages] == NATIVE_STAGES and all(s['exit_code'] == 0 for s in stages),
             'native five-stage coverage')
        checks = read(entry / 'local/LOCAL-CHECKS.json')
        need(all(checks[o]['paid_profile'] == read(word)['report']['local_profile'] for o in ('forward', 'backward')),
             'native actual paid profiles')
        natives[tag] = entry
    work.mkdir(parents=True)
    package = work / 'package'
    shutil.copytree(source, package)
    # Only the fresh external clone changes. Immutable source/cache inventories remain pinned.
    for hp in helper_paths[:2]:
        shutil.copy2(hp, package / hp.name)
        need(sha(package / hp.name)==external_hashes[str(hp)], 'helper copy hash')
    shutil.copy2(a.blocknorm_checker, package / 'blocknorm_certificate.py')
    shutil.copy2(a.blocknorm_checker, package / 'code/blocknorm_certificate.py')
    need(sha(package / 'blocknorm_certificate.py') == external_hashes[str(a.blocknorm_checker.resolve())], 'block-norm checker exact source binding')
    shutil.copy2(a.reconstructor, package / 'reconstruct.py')
    need(sha(package / 'reconstruct.py')==external_hashes[str(a.reconstructor.resolve())], 'reconstructor copy hash')
    # The original subprocesses also write generated hash-bound source. Windows
    # callers use a process-scoped LF adapter; no system configuration is changed.
    lf_probe = work / '.lf-preflight.txt'
    lf_probe.write_text('LF\n', encoding='utf-8')
    need(lf_probe.read_bytes()==b'LF\n', 'process-scoped LF output required on Windows')
    lf_probe.unlink()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', AUDIT_FAST_SHARDS=str(a.jobs))
    for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(name, None)
    stages, patches = [], []

    def run(name, script, *args):
        start = time.monotonic()
        command = [sys.executable, '-B', str(script), *map(str, args)]
        log = work / (name + '.log')
        with log.open('w') as output:
            result = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic() - start,
                           script_sha256=sha(script), log_sha256=sha(log), command=command))
        write(work / 'STAGES.json', stages)
        need(result.returncode == 0, 'failed ' + name + '; see ' + str(log))
        print('PASS', name, flush=True)

    def patch(name, replacements):
        path = package / name
        before = sha(path)
        body = path.read_text()
        for old_text, new_text in replacements:
            need(body.count(old_text) == 1, 'exact patch preimage: ' + name + ': ' + old_text[:80])
            body = body.replace(old_text, new_text)
        path.write_text(body)
        patches.append(dict(path=name, before_sha256=before, after_sha256=sha(path), replacements=replacements))

    # PR2843: exact per-shard/PID transport repair; predicates and merge unchanged.
    patch('audit_fast.py', [("_part.with_suffix('.tmp').write_text(_j.dumps([_idx[0],_own]));_part.with_suffix('.tmp').replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)", "_tmp=_part.with_name(_part.name+'.%d.%d.tmp'%(_AF_SHARD,os.getpid()));_tmp.write_text(_j.dumps([_idx[0],_own]));_tmp.replace(_part.with_name(_part.name+'.%d'%_AF_SHARD));_s.exit(0)")])
    # PR2530's already checked correction: restored zero buffers occupy physical
    # rows. COMPOSED's shipped SPEC includes them; its rebound SPEC omitted them.
    patch('new/rebind.py', [
        ("physical=spec['expected']['live'] + 8 + R + 2)",
         "physical=spec['expected']['live'] + 8 + R + 2 + max(len(rd(d / 'CANONICAL-WORD.json.gz').get('zero_buffers', [])) for d in locs.values()))")])
    # Preserve the exact fixed-grid-maximum equality while deriving precision
    # from the same SPEC read by both independent outer arithmetic checkers.
    patch('verify_release.py', [
        ('Fraction(1, 10 ** 3046) - Fraction(1, 10 ** 3022)',
         "Fraction(1, 10 ** (spec['outer_refinement']['endpoint_digits'] + 46)) - Fraction(1, 10 ** (spec['outer_refinement']['endpoint_digits'] + 22))"),
        ('epsilon=1-(1025/1024)e-3080', "epsilon=1-(1025/1024)e-{spec['outer_refinement']['endpoint_digits']+80}"),
        ('at the one 3000-digit rejection call', "at the one {spec['outer_refinement']['endpoint_digits']}-digit rejection call")])
    # Keep the native dimension and paid moment ledger fixed; bind replica
    # width to both the checked source geometry and the independent B invoice.
    patch('outer/check_ledger.py', [
        ('assert (m,W)==(73,66304)',
         "T=spec['geometry']['replicas']\nassert type(T) is int and T>0\nassert m==73 and W==896*T and W==BJ['live']")])
    patch('code/witness.py', [(DISCOVERY_APPEND_OLD, DISCOVERY_APPEND_NEW)])
    patch('verify.py', [
        ("run('lift-parent',P/'lift_parent.py','--owners',work/'rebuilt-owners','--out',work/'rebuilt-parent')",
         "run('lift-parent',P/'lift_parent.py','--package',P,'--owners',work/'rebuilt-owners','--out',work/'rebuilt-parent')")])
    # A sharper local reserve is certified against actual scalar/Horner
    # prefixes of BOTH orientations and BOTH providers. All sweep and physical
    # row charges remain unchanged; this never omits an invocation or bridge.
    patch('code/witness.py', [
        ("PAYLOAD==1<<(192+(GEO['dimension']+1)//2+2*CALLS+4).bit_length()",
         "PAYLOAD==1<<(128+(GEO['dimension']+1)//2+18+1330+1+4).bit_length()")])
    patch('code/invoice_allcold.py', [
        ("    required_prefix=localbits+input_l2_bits+call_count+bridge_sweeps+4",
         "    from blocknorm_certificate import certify\n    blocknorm=certify(template, {pid:base/'providers'/pid for pid in template['local_providers']})\n    assert blocknorm['status'] == 'PASS_TENSOR_BLOCK_NORM_CERTIFICATE'\n    assert localbits <= 128, 'actual native scalar/Horner prefix exceeds charged local reserve'\n    required_prefix=localbits+input_l2_bits+blocknorm['max_active_depth']+blocknorm['stock_l2_bits']+1+4")])
    patch('independent_core.py', [
        ("    payload = 1 << (192 + (M+1)//2 + 2*len(c['order']) + 4).bit_length()",
         "    require(localbits <= 128, 'measured native prefix exceeds local reserve')\n    payload = 1 << (128 + (M+1)//2 + 18 + 1330 + 1 + 4).bit_length()")])
    patch('code/invoice_allcold.py', [
        ("        complete_invocation_sweeps=call_count,bridge_sweeps=bridge_sweeps,row_prefix_extra=2*payload,",
         "        complete_invocation_sweeps=call_count,bridge_sweeps=bridge_sweeps,row_prefix_extra=2*payload,blocknorm=blocknorm,"),
        ("        primitive_arithmetic_margin_bits=4,controller_audit_sha256=", "        tensor_block_norm=blocknorm,partial_cover_margin_bits=1,physical_stock_l2_bits=blocknorm['stock_l2_bits'],primitive_arithmetic_margin_bits=4,controller_audit_sha256="),
        ("Sum every actual invocation and bridge sweep and take the maximum local scalar/Horner prefix over both orientations of the fixed provider.",
         "All invocations and bridge sweeps remain charged. Bound completed-boundary energy by at most eighteen active steps per owner replica, using exact tensor-isomorphic whole-family helper unitaries. Add the full group-indexed physical-stock sup-to-l2 factor and one partial-cover margin, then the maximum local scalar/Horner prefix.")])
    patch('independent_core.py', [
        ("    prefix = localbits + (M + 1) // 2 + len(c['order']) + c['bridges'] + 4",
         "    bn=c['blocknorm']\n    require(bn['status']=='PASS_TENSOR_BLOCK_NORM_CERTIFICATE' and bn['max_active_depth']==18 and bn['stock_l2_bits']<=1330, 'independent tensor block certificate')\n    prefix = localbits + (M + 1) // 2 + bn['max_active_depth'] + bn['stock_l2_bits'] + 1 + 4"),
        ("prefix_formula=dict(local_scalar=localbits, input_l2=(M + 1) // 2, invocations=len(c['order']), bridges=c['bridges'], margin=4)",
         "prefix_formula=dict(local_scalar=localbits, input_l2=(M + 1) // 2, invocations=len(c['order']), bridges=c['bridges'], active_block_depth=18,stock_l2=bn['stock_l2_bits'],partial_cover=1,margin=4),blocknorm=bn")])
    patch('audit_mixed.py', [
        ("pending=A.check_pending_axes(ctx);receipt=A.check_roles(ctx,roles)",
         "import blocknorm_certificate as BN;ctx['blocknorm']=BN.certify_context(ctx,roles,dirs,source_parent=parent);pending=A.check_pending_axes(ctx);receipt=A.check_roles(ctx,roles)")])
    patch('code/assemble.py', [
        (" assert invoice['global_prefix_bits']==max(z['prefix_bits']for p in invoice['providers'].values()for z in p['local'].values())+37+CALLS+CALLS+4",
         " bn=invoice['blocknorm']\n assert bn['status']=='PASS_TENSOR_BLOCK_NORM_CERTIFICATE' and bn['replicas']==REPLICAS\n assert bn['max_active_depth']==bn['boundary_depth_bits']==18 and bn['active_calls_per_block']==bn['bridges_per_block']==9\n assert bn['block_width_families']==896 and bn['physical_families']==invoice['physical'] and bn['live_families']==invoice['live']\n assert bn['partial_cover_bits']==1 and bn['input_l2_bits']==37 and bn['local_reserve_bits']==128 and bn['retained_payload_bits']==PAYLOAD\n localbits=max(z['prefix_bits']for p in invoice['providers'].values()for z in p['local'].values())\n assert bn['local_actual_prefix_bits']==localbits and localbits<=128\n assert invoice['global_prefix_bits']==bn['actual_prefix_bits']==localbits+37+18+bn['stock_l2_bits']+1+4\n assert bn['required_reserve_bits']==128+37+18+bn['stock_l2_bits']+1+4<PAYLOAD\n expected_endpoint=dict(all_arbitrary_columns=632,helper_to_data_response_zero=True,centres_first_clear_and_terminal_zero=8,zero_buffers_allocated_and_cleared=72,coefficient_work_contract='unchanged audited clear-before-and-after Horner macro')\n assert bn['endpoint_replay']=={pid:{o:expected_endpoint for o in ('forward','backward')} for pid in invoice['providers']}"),
        (" stock=group*invoice['physical'];streamed_mass=group*owner['rank_mass']",
         " stock=group*invoice['physical'];streamed_mass=group*owner['rank_mass']\n assert bn['physical_stock_bits']==stock.bit_length() and bn['stock_l2_bits']==(stock.bit_length()+1)//2<=1330")])
    patch('code/assembly_controls.py', [
        ("        i['global_prefix_bits'] = 1 + 37 + CALLS + CALLS + 4",
         "        i['global_prefix_bits'] = 1 + 37 + 18 + i['blocknorm']['stock_l2_bits'] + 1 + 4"),
        ("        ('wrong_global_prefix_sum', lambda o, i: i.__setitem__('global_prefix_bits', 224)),",
         "        ('wrong_global_prefix_sum', lambda o, i: i.__setitem__('global_prefix_bits', 224)),\n        ('missing_blocknorm', lambda o,i:i.pop('blocknorm')),\n        ('understated_active_depth',lambda o,i:i['blocknorm'].__setitem__('max_active_depth',17)),\n        ('understated_full_stock_norm',lambda o,i:i['blocknorm'].__setitem__('stock_l2_bits',10)),\n        ('missing_partial_cover_margin',lambda o,i:i['blocknorm'].__setitem__('partial_cover_bits',0)),\n        ('forged_helper_response',lambda o,i:i['blocknorm']['endpoint_replay'][next(iter(i['providers']))]['forward'].__setitem__('helper_to_data_response_zero',False)),")])
    patch('freeze_spec.py', [
        ("spec['expected']['assembly_controls_rejected'] = 32 + sum(", "spec['expected']['assembly_controls_rejected'] = 37 + sum(")])
    patch('replay.py', [
        ("len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==114", "len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==119")])
    patch('verify.py', [
        ("['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py','audit_fast.py']", "['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py','audit_fast.py','blocknorm_certificate.py']"),
        ("controls=dict(admission=114,bit=12,controller=15,independent_owner=8,geometry=6)", "controls=dict(admission=119,bit=12,controller=15,independent_owner=8,geometry=6)")])
    write(work / 'RUNTIME-PATCHES.json', patches)
    shutil.copy2(a.fill, package / 'new/borrow-fill/FILL.json.gz')
    shutil.copy2(a.order, package / 'new/borrow-fill/ORDER.json')
    shutil.copy2(a.dispatch, package / 'new/borrow-fill/DISPATCH.json')
    run('owners', package / 'reconstruct.py', '--out', work / 'owners')
    run('parent-lift', package / 'lift_parent.py', '--package', package, '--owners', work / 'owners', '--out', work / 'parent-data')
    for name in ('PLAN.json', 'OWNERS.json.gz', 'DISPATCH.json', 'PROFILE.json', 'CONSTRUCTION.json',
                 'GLOBAL-TEMPLATE.json.gz', 'SPEC.json'):
        shutil.copy2(work / 'parent-data' / name, package / name)
    shutil.copy2(work / 'owners/ORDER.json', package / 'ORDER.json')
    spec = read(package / 'SPEC.json')
    spec['outer_refinement'] = PRECISION
    spec['expected']['live'] = 896*T
    # COMPOSED's pre-life mechanism changes which helper labels retain width8.
    # Preserve its declared spot set; rebind and the original strict verifier
    # still check the actual native widths, including every other helper.
    source_spots = read(source / 'new/SPEC.json')['width_spot_helpers']
    need(source_spots == [278, 281, 284, 289], 'COMPOSED source spot-width pins')
    spec['width_spot_helpers'] = source_spots
    write(package / 'new/SPEC.json', spec)
    run('rebind', package / 'new/rebind.py', package, natives['base'] / 'local',
        natives['extra'] / 'local', work / 'rebound')
    spec = read(work / 'rebound/SPEC.json')
    for tag in ('base', 'extra'):
        c = read(natives[tag] / 'local/CANONICAL-WORD.json.gz')
        need(c['R']==expected_helpers and len(c['centers'])==8 and len(c.get('zero_buffers',[]))==72, 'unchanged full physical ABI including all private buffers')
    need(spec['expected']['physical'] == 896*T+expected_helpers+8+72+2, 'complete physical cost including all actual helpers and 72 buffers')
    layout = work / 'layout'
    layout.mkdir()
    with tarfile.open(old / 'upstream-layout.tar.gz') as archive:
        need(all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                 for m in archive.getmembers()), 'retained archive paths')
        archive.extractall(layout, filter='data')
    runtime = layout / 'packing74'
    runtime.mkdir()
    for name in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py', 'audit_fast.py', 'blocknorm_certificate.py'):
        shutil.copy2(package / name, runtime / name)
    for name in ('code', 'construction', 'inputs'):
        shutil.copytree(package / name, runtime / name)
    shutil.copytree(work / 'rebound', runtime / 'candidate')
    shutil.copytree(natives['extra'], runtime / 'native-extra')
    data = runtime / 'candidate'
    result = dict(status='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED', source_commit=SOURCE_COMMIT,
                  source_manifest_sha256=SOURCE_MANIFEST, native_receipt_sha256=sha(a.native_receipt),
                  fill_sha256=sha(package / 'new/borrow-fill/FILL.json.gz'),
                  order_sha256=sha(package / 'new/borrow-fill/ORDER.json'), dispatch_sha256=sha(package / 'new/borrow-fill/DISPATCH.json'), replicas=T, source_profile=a.source_profile, source_file_count=source_profile['source_file_count'], source_upstream_head=source_profile['upstream_head'], actual_expected_helpers=expected_helpers, comparison_pr=comparison_pr, comparison_head=COMPARISON_HEAD, comparison_claim_sha256=COMPARISON_SHA, comparison_kappa=str(previous), external_input_sha256=external_hashes, profile=read(work / 'rebound/PROFILE.json'),
                  patches=patches, scope='Prepared only; source/native/parent inputs authenticated and literal owner fill reconstructed.')
    write(work / 'RESULT.json', result)
    # Preparation still authenticates every read-only input at its end.
    need(tree(source, ('MANIFEST.json',))==source_files and tree(cache)==native_receipt['cache_files'], 'read-only inputs changed during preparation')
    need(all(sha(Path(p))==h for p,h in external_hashes.items()), 'external candidate/helper inputs changed')
    if a.prepare_only:
        print(result['status'], flush=True)
        return
    run('discovery', runtime / 'replay.py', '--data', data, '--work', work / 'discovery',
        '--local', natives['base'] / 'local', '--discover')
    supplier = read(work / 'discovery/RESULT.json')
    for name in ('PLAN.json', 'PROFILE.json', 'SPEC.json'):
        shutil.copy2(data / name, package / 'new' / name)
    spec = read(package / 'new/SPEC.json')
    original_claim = read(source / 'CLAIM.json')
    claim = dict(status='CONDITIONAL_CANDIDATE_EXPECTED_BY_REPLAY', kappa=supplier['kappa'],
                 kappa_decimal=supplier['kappa_decimal'], baseline_pr=comparison_pr, baseline_head=COMPARISON_HEAD,
                 baseline_kappa=str(previous), outer_refinement=PRECISION,
                 scope=original_claim['scope'], kappa_layers=original_claim['kappa_layers'],
                 headline_kappa_source='outer/OUTER-CLAIM.json',
                 verification='Candidate discovered from literal fill; full original verification must pass separately.')
    write(package / 'CLAIM.json', claim)
    C = Q(spec['expected']['complex_lower'])
    write(package / 'outer/B.json', dict(b=str(C-Q(1,10**104)), b_above_endpoint=str(C+Q(1,10**24)),
                                        profile=spec['expected']['global_profile'], live=spec['expected']['live']))
    for name in ('check_ledger.py', 'independent_check.py'):
        run('outer-' + name, package / 'outer' / name)
    ledger = read(package / 'outer/LEDGER.json')
    row = ledger['rows']['struct_boundary_radix_union']['kappa']
    kappa = Q(row['rational'])
    need(kappa == C-Q(1,10**70)-Q(1,10**46) and kappa > previous,
         'candidate must strictly improve full exact pinned frontier headline before full release')
    outer_claim = read(source / 'outer/OUTER-CLAIM.json')
    outer_claim.update(kappa=row['decimal'], kappa_rational=row['rational'],
                       baseline_head=COMPARISON_HEAD, baseline_kappa=str(previous), gain=str(kappa-previous),
                       b='certified complex_lower - 1e-104 (outer/B.json)',
                       retuned_slacks='Endpoint precision24; free gaps follow outer/check_ledger.py from the frozen SPEC.',
                       fixed_grid_maximum='kappa=C-10^-70-10^-46 exactly; same fixed-grid-maximum proof at precision24.')
    write(package / 'outer/OUTER-CLAIM.json', outer_claim)
    (package / 'provenance').mkdir(exist_ok=True)
    shutil.copy2(a.comparison_claim, package / ('provenance/PR' + str(comparison_pr) + '-HEADLINE-CLAIM.json'))
    write(package / 'MANIFEST.json', tree(package, ('MANIFEST.json',)))
    run('release', package / 'verify_release.py', '--main', source.parents[1], '--work', work / 'release',
        '--native-cache', cache, '--jobs', a.jobs)
    receipt = read(work / 'release/RELEASE-RECEIPT.json')
    need(receipt['status'] == 'PASS_RELEASE' and Q(receipt['kappa_decimal']) == kappa
         and receipt['manifest_sha256'] == sha(package / 'MANIFEST.json'), 'complete release binding')
    need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST
         and tree(source, ('MANIFEST.json',)) == source_files and tree(cache) == native_receipt['cache_files'],
         'read-only source/cache inputs changed')
    need(all(sha(Path(p))==h for p,h in external_hashes.items()), 'external candidate/helper inputs changed during admission')
    result.update(status='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',
                  complex_lower=str(C), kappa=str(kappa), kappa_decimal=row['decimal'],
                  gain=str(kappa-previous), release_receipt_sha256=sha(work / 'release/RELEASE-RECEIPT.json'),
                  package_manifest_sha256=sha(package / 'MANIFEST.json'), stages=stages,
                  scope='Conditional finite construction and modern outer arithmetic. Exact inherited theorem obligations remain. Both native providers explicitly reused from authenticated fresh five-stage runs.')
    write(work / 'RESULT.json', result)
    print(result['status'], row['decimal'], flush=True)


if __name__ == '__main__':
    main()
