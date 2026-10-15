"""Accepted-but-unbound: the selected chain's cross-stage owner-map binding.

The frozen PR1087 selected chain (verify_t16.py stage sequence) certifies the
frozen data/OWNERS.json.gz role map twice over: lift16 checks every role inside
its owner's actual window and independent-t16 rechecks it against invocation
times. `emit` copies that map verbatim into the hosted template's
`hosting.pooled_slots`, and `audit` (audit_allcold.py line 172) binds ten of the
eleven pooled-slot fields back to the base-derived call owners. The eleventh
field, `time`, and the naming field `hosting.owner_map_sha256`, are bound to
nothing: no frozen stage and no line of the complete caller compares them with
the frozen OWNERS map.

This harness executes that missing implication against the archived selected
fixture (research/community-frontier1094-audit/selected-replay.tar.gz). Each
fixture models a defective-but-coherent emitter: the hosted template is
rewritten exactly as emit serialises it (canonical JSON, HOSTED.json's
template_sha256 recomputed), so every template-hash binding stays tight and
only the audited field differs from the frozen owner map. The full frozen stage
sequence from audit through independent-t16 runs unchanged and out-of-process,
followed by verify_t16.py's final binding (reimplemented 1:1, pinned below).

Fixtures:
  F0        unmutated fixture: every stage passes, receipts reproduce the
            archived selected receipts, and the link check passes.
  F1        two equal-width pooled slots swap their `time` (a role-to-time
            permutation that preserves every per-time width count): accepted by
            the whole chain, link check fails on exactly two roles.
  F2        `hosting.owner_map_sha256` set to a wrong digest: accepted by the
            whole chain, link check fails on the naming field.
  F3        control: one pooled slot's `port` (a checked roles field) changes:
            rejected by audit at line 172.
  F4        control: a time change with a stale HOSTED.json template_sha256
            (artifact inconsistency): rejected by audit at line 185.

Stdlib only; Python 3.12 replay.  Usage:
  python3 -B research/selected-ownermap-binding-gap/verify.py            # compare with EXPECTED.json
  python3 -B research/selected-ownermap-binding-gap/verify.py --write    # regenerate EXPECTED.json
"""
import argparse, gzip, hashlib, json, os, re, shutil, subprocess, sys, tarfile, tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

assert __debug__, 'assertions must stay enabled'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges'
MC = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
RETAINED_INVOICE = MC / 'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json'
RUNPORT = MC / 'code/run_portable.py'
sha = lambda b: hashlib.sha256(b).hexdigest()
AUDIT_SHA = '1467a2acb654e62552c69fb9a7c4c85f70a02120881d222313865058ab71a6cc'
VERIFY_T16_SHA = '050e2dfba59911b8f29fd94422833d421367a0ad01c5e4ae916a75a235ee5e46'
RUNPORT_SHA = '322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955'
ARCHIVED_RECEIPTS = ('ASYNC-AUDIT.json', 'OWNERS-AND-PROFILE.json', 'GLOBAL-PREFIX.json',
                     'PREFIX-AND-INVOICE.json', 'IDLE-REMAINDER-FRAMES.json')


def pins_ok():
    rows = [f for f in json.loads((HERE / 'SOURCES.json').read_text())['files'] if f['usage'] == 'input']
    for f in rows:
        assert sha((ROOT / f['path']).read_bytes()) == f['sha256'], 'pinned input changed: ' + f['path']
    return [f['path'] for f in rows]


def extract(tmp):
    source = tmp / 'source'
    source.mkdir()
    with tarfile.open(STAGE / 'upstream1087.tar.gz') as t:
        assert sha(t.extractfile('verify_t16.py').read()) == VERIFY_T16_SHA, 'verify_t16.py is not the pinned PR1087 driver'
        t.extractall(source, filter='data')
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):  # the stage package's three frozen overlays
        (source / 'data' / name).write_bytes((STAGE / 'data' / name).read_bytes())
    script = source / 'code/audit_allcold.py'
    assert sha(script.read_bytes()) == AUDIT_SHA, 'audit_allcold.py is not the pinned PR1087 file'
    assert sha(RUNPORT.read_bytes()) == RUNPORT_SHA, 'run_portable.py is not the pinned wrapper'
    strict = tmp / 'strict'
    strict.mkdir()
    prefix = 'candidate/strict/'
    with tarfile.open(ARCHIVE) as t:
        members = [m for m in t.getmembers() if m.name.startswith(prefix) and m.isfile()]
        for m in members:
            m.name = m.name[len(prefix):]
        t.extractall(strict, members=members, filter='data')
    return source, strict


CANON = lambda t: json.dumps(t, sort_keys=True, separators=(',', ':')).encode()


def load_template(hosted):
    raw = gzip.decompress((hosted / 'GLOBAL-TEMPLATE.json.gz').read_bytes())
    t = json.loads(raw)
    assert CANON(t) == raw, 'fixture template is not emit-canonical'
    return t


def reemit(hosted, t, summary_raw=None):
    """Rewrite GLOBAL-TEMPLATE.json.gz exactly as emit serialises it (canonical JSON payload,
    portable gzip, HOSTED.json coherent). Only decompressed bytes are ever hashed downstream."""
    raw = CANON(t)
    gz = bytearray(gzip.compress(raw, 9, mtime=0))
    gz[9] = 255
    (hosted / 'GLOBAL-TEMPLATE.json.gz').write_bytes(bytes(gz))
    res = json.loads((hosted / 'HOSTED.json').read_text()) if summary_raw is None else summary_raw
    res['template_sha256'] = sha(raw)
    (hosted / 'HOSTED.json').write_bytes((json.dumps(res, indent=2) + '\n').encode('utf-8'))
    return sha(raw)


def time_swap(t):
    """First deterministic equal-width cross-time pair in pooled-slot order; swap their times."""
    slots = t['hosting']['pooled_slots']
    for a in range(len(slots)):
        for b in range(a + 1, len(slots)):
            if slots[a]['width'] == slots[b]['width'] and slots[a]['time'] != slots[b]['time']:
                pair = (a, b, dict(slots[a]), dict(slots[b]))
                slots[a]['time'], slots[b]['time'] = slots[b]['time'], slots[a]['time']
                return pair
    raise AssertionError('no equal-width cross-time pooled-slot pair')


def width_profile(slots):
    return dict(sorted(Counter((s['time'], s['width']) for s in slots).items()))


def run_stages(tmp, source, strict, fixture):
    """Run the frozen post-emit stage sequence exactly as verify_t16.py invokes it; stop at the first failure."""
    g, g8 = strict / 'global', strict / 'global8'
    work = tmp / ('run-' + fixture)
    work.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(MC), GAIN_PR564_SOURCE=str(MC))
    for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(k, None)
    env['WITNESS_SPEC'] = str(source / 'data/SPEC.json')
    spec = json.loads((source / 'data/SPEC.json').read_text())
    ledger = []

    def run(name, script, *args, extra=None):
        log = work / (name + '.log')
        with log.open('w') as s:
            rc = subprocess.run([sys.executable, '-B', str(RUNPORT), str(script), *map(str, args)],
                                cwd=str(ROOT), env=dict(env, **(extra or {})),
                                stdout=s, stderr=subprocess.STDOUT).returncode
        entry = dict(stage=name, exit_code=rc)
        if rc:
            text = log.read_text(errors='replace')
            frames = re.findall(r'File "[^"]*?([A-Za-z_0-9]+\.py)", line (\d+)', text)
            entry['failure'] = dict(exception=(re.findall(r'^(\w*(?:Error|Exception))(?::|$)', text, re.M) or ['?'])[-1],
                                   line=int(frames[-1][1]) if frames else None,
                                   script=frames[-1][0] if frames else None)
        ledger.append(entry)
        return rc == 0

    code, t16 = source / 'code', source / 't16'
    ok = run('audit', code / 'audit_allcold.py', g / 'base', g / 'hosted', g / 'audit/ASYNC-AUDIT.json',
             '--mutation-controls')
    if ok:
        ok = run('invoice', code / 'invoice_allcold.py', '--base', g / 'base', '--hosted', g / 'hosted',
                 '--audit', g / 'audit', '--out', g / 'audit', '--retained-invoice', RETAINED_INVOICE)
    if ok:
        ok = run('assembly', code / 'assemble.py', MC, g, work / 'ASSEMBLY.json')
    if ok:
        for nm, sc, out in (('admission-controls', 'assembly_controls.py', 'ADMISSION-CONTROLS.json'),
                            ('bit-supplier-controls', 'bit_supplier_controls.py', 'BIT-SUPPLIER-CONTROLS.json')):
            if not run(nm, code / sc, '--source-package', MC, '--owner', g / 'audit/OWNERS-AND-PROFILE.json',
                       '--invoice', g / 'audit/PREFIX-AND-INVOICE.json', '--out', work / out):
                ok = False
                break
    if ok:
        ok = run('independent-t16', t16 / 'indep16.py', '--baseline-parent',
                 g8 / 'base/split-centres/GLOBAL-TEMPLATE.json.gz', '--owners', source / 'data/OWNERS.json.gz',
                 '--word', g / 'base/providers/gauge44/CANONICAL-WORD.json.gz', '--out', work / 'INDEPENDENT-T16.json',
                 extra={'T16_EXPECTED_IDLE': json.dumps(spec['expected']['idle_remainder_profile']),
                        'T16_EXPECTED_WIDTHS': json.dumps(spec['providers']['gauge44']['inventory'])})
    return ledger, work


def final_binding(work, strict, source, strict_pristine):
    """verify_t16.py's final binding, asserted 1:1 against fresh stage outputs (plus verify_frontier1094's
    published physical inventory). Provider content binding against baseline1042's slots/local is not
    re-checked here: in a fixture run the bound copy is its own input, upstream of the mutation point."""
    g, g8 = strict / 'global', strict / 'global8'
    rd = lambda p: json.loads(Path(p).read_text())
    asm, ind = rd(work / 'ASSEMBLY.json'), rd(work / 'INDEPENDENT-T16.json')
    inv = rd(g / 'audit/PREFIX-AND-INVOICE.json')
    bc, ac = rd(work / 'BIT-SUPPLIER-CONTROLS.json'), rd(work / 'ADMISSION-CONTROLS.json')
    lift = rd(strict_pristine / 'lift/PARENT-LIFT-RECEIPT.json')
    owner, audit = rd(g / 'audit/OWNERS-AND-PROFILE.json'), rd(g / 'audit/ASYNC-AUDIT.json')
    spec8, spec16 = rd(source / 'data/SPEC-T8.json'), rd(source / 'data/SPEC.json')
    r16 = len(rd(source / 'data/T8/PLAN.json')['provider_registry']['gauge44']['widths'])
    checks = {}

    def ck(name, cond):
        checks[name] = bool(cond)

    ck('assembly_status_and_kappa', asm['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
       and asm['kappa'] == spec16['expected']['kappa'])
    ck('bit_supplier_controls', bc['status'] == 'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS'
       and len(bc['rejected_controls']) == 12 and bc['derived_deficit'] == 10272)
    ck('admission_controls', not ac['discovery_accepted_controls'] and len(ac['rejected_controls']) == 69)
    ck('independent_t16_status', ind['status'] == 'PASS_INDEPENDENT_T16_LITERAL_WINDOWS_CHARTS_PREFIX_ROW'
       and len(ind['controls_rejected']) == 6)
    ck('profile_equality', ind['profile'] == asm['complex_profile'])
    ck('idle_equality', {str(k): v for k, v in lift['idle16'].items()} == {str(k): v for k, v in ind['idle'].items()})
    ck('prefix_bits', ind['prefix_bits'] == inv['global_prefix_bits'] < 512)
    ck('row_coefficients', ind['physical_row_coefficient'] == inv['finite']['physical_row_coefficient']
       < inv['finite']['retained_row_coefficient'] == 20161)
    ck('charged_prefix_bits', inv['charged_prefix_bits'] == 512)
    ck('rank_mass_deficit', ind['rank_mass'] == owner['rank_mass'] == 1041408 and ind['deficit'] == owner['deficit'] == 5120)
    ck('finite_strict_checks', inv['strict_checks'] and all(inv['strict_checks'].values()))
    ck('outer_margins', len(asm['outer']) == 47 and all(Fraction(v) > 0 for v in asm['outer'].values()))
    ck('controller_mutation_controls', audit['mutation_controls_run'] and len(audit['mutations_rejected']) == 15)
    ck('roles_counts', ind['roles'] == owner['hosted_residuals'] == audit['complex_hosted_residuals'] == 144 * r16)
    ck('invocation_counts', ind['calls'] == audit['complete_invocations'] == inv['complete_invocation_sweeps'] == 144)
    ck('chart_counts', ind['actual_73_axis_charts'] == owner['actual_73column_sigmas']
       == audit['actual_orthogonal_73column_maps'])
    ck('template_sha_binding', asm['template_sha256'] == owner['template_sha256'] == inv['template_sha256'])
    ck('audit_file_hashes', inv['owner_audit_sha256'] == sha((g / 'audit/OWNERS-AND-PROFILE.json').read_bytes())
       and inv['controller_audit_sha256'] == sha((g / 'audit/ASYNC-AUDIT.json').read_bytes()))
    ck('kappa_improves_t8', Fraction(asm['kappa']) > Fraction(spec8['expected']['kappa']))
    ck('published_inventory', ind['roles'] == 69120 and ind['prefix_bits'] == 397 and inv['charged_prefix_bits'] == 512
       and ind['physical_row_coefficient'] == 16469
       and bc['derived_deficit'] == 10272
       and asm['kappa'] == '836330098538459/500000000000000000')
    return dict(checks=checks, passed=sum(checks.values()), total=len(checks))


def link_check(g, owners_bytes):
    """The audited obligation: accepted template pooled_slots == frozen OWNERS (times included), and
    hosting.owner_map_sha256 names that exact gzip. PR #1959's template_to_frozen_owners_binding."""
    owners = json.loads(gzip.decompress(owners_bytes))
    t = load_template(g / 'hosted')
    pooled = t['hosting']['pooled_slots']
    diffs = []
    for i, (z, o) in enumerate(zip(pooled, owners)):
        for k in o:
            if z[k] != o[k]:
                diffs.append(dict(index=i, field=k, template=z[k], owners=o[k]))
    if len(pooled) != len(owners):
        diffs.append(dict(index=None, field='length', template=len(pooled), owners=len(owners)))
    return dict(pooled_slots_equal_frozen_owners=not diffs,
                owner_map_sha256_names_frozen_gzip=t['hosting']['owner_map_sha256'] == sha(owners_bytes),
                roles=len(owners), diff_count=len(diffs), diffs=diffs[:8])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='regenerate EXPECTED.json instead of comparing with it')
    a = ap.parse_args()
    pinned = pins_ok()
    result = dict(status='PASS_SELECTED_OWNERMAP_BINDING_GAP', pinned_inputs=pinned,
                  audit_script_sha256=AUDIT_SHA, verify_t16_sha256=VERIFY_T16_SHA,
                  run_portable_sha256=RUNPORT_SHA, fixtures={})
    with tempfile.TemporaryDirectory(prefix='ownermap-binding-gap-') as d:
        tmp = Path(d)
        source, strict = extract(tmp)
        owners_bytes = (source / 'data/OWNERS.json.gz').read_bytes()
        pristine_hosted = tmp / 'pristine-hosted'
        shutil.copytree(strict / 'global/hosted', pristine_hosted)
        pristine_audit = tmp / 'pristine-audit'
        shutil.copytree(strict / 'global/audit', pristine_audit)
        strict_pristine = strict  # archived receipts (lift/, top level) are never overwritten
        g = strict / 'global'

        def restore():
            for src in (pristine_hosted, pristine_audit):
                dst = g / ('hosted' if src is pristine_hosted else 'audit')
                for f in dst.iterdir():
                    f.unlink()
                for f in src.iterdir():
                    (dst / f.name).write_bytes(f.read_bytes())

        def norm(name, r):
            """Receipts compared through canonical proof-relevant content. Two normalizations are
            environment serialisation, not mathematics (CONTRIBUTING.md 'Regenerated artifacts and
            hashes'): indep16 keys input_sha256 by absolute input paths, and the frozen invoice's
            artifact_semantic_sha256 map is serialized in directory-enumeration order, so the byte
            hash assemble records as input_sha256.fresh_invoice is machine-dependent."""
            r = json.loads(json.dumps(r))
            if name == 'INDEPENDENT-T16.json':
                r['input_sha256'] = sorted(r['input_sha256'].values())
            elif name == 'ASSEMBLY.json':
                r['input_sha256'] = {k: v for k, v in sorted(r['input_sha256'].items()) if k != 'fresh_invoice'}
            return r

        def diff_paths(a, b, prefix='', out=None):
            out = [] if out is None else out
            if type(a) is not type(b):
                out.append(prefix)
            elif isinstance(a, dict):
                for k in sorted(set(a) | set(b)):
                    diff_paths(a.get(k), b.get(k), prefix + '/' + str(k), out)
            elif isinstance(a, list) and len(a) == len(b):
                for i, (x, y) in enumerate(zip(a, b)):
                    diff_paths(x, y, prefix + '/' + str(i), out)
            elif a != b:
                out.append(prefix)
            return out

        def record(name, mutate, expect):
            restore()
            hosted = g / 'hosted'
            t = load_template(hosted)
            facts = mutate(t, hosted)
            ledger, work = run_stages(tmp, source, strict, name)
            accepted = all(e['exit_code'] == 0 for e in ledger)
            entry = dict(mutation=facts, stage_ledger=ledger, accepted_by_chain=accepted)
            if accepted:
                entry['final_binding'] = final_binding(work, strict, source, strict_pristine)
                archived = {f: json.loads((pristine_audit / f).read_text()) for f in ARCHIVED_RECEIPTS}
                archived['ASSEMBLY.json'] = json.loads(strict_pristine.joinpath('ASSEMBLY.json').read_text())
                archived['INDEPENDENT-T16.json'] = json.loads(strict_pristine.joinpath('INDEPENDENT-T16.json').read_text())
                fresh = {f: json.loads((g / 'audit' / f).read_text()) for f in ARCHIVED_RECEIPTS}
                fresh['ASSEMBLY.json'] = json.loads((work / 'ASSEMBLY.json').read_text())
                fresh['INDEPENDENT-T16.json'] = json.loads((work / 'INDEPENDENT-T16.json').read_text())
                entry['receipt_diff_paths_vs_archived'] = {
                    f: diff_paths(norm(f, archived[f]), norm(f, fresh[f]))[:12] for f in sorted(archived)}
                entry['receipts_match_archived'] = {f: not entry['receipt_diff_paths_vs_archived'][f]
                                                    for f in sorted(archived)}
            entry['link_check'] = link_check(g, owners_bytes)
            entry['expected'] = expect
            result['fixtures'][name] = entry
            return entry

        def f0(t, hosted):
            raw = CANON(t)
            hosted_bytes = (hosted / 'HOSTED.json').read_bytes()
            reemit(hosted, t)  # serialization fidelity: rewrite with zero semantic change
            same_payload = gzip.decompress((hosted / 'GLOBAL-TEMPLATE.json.gz').read_bytes()) == raw
            same_summary = json.loads((hosted / 'HOSTED.json').read_text()) == json.loads(hosted_bytes)
            assert same_payload and same_summary, 're-emit changed the fixture semantically'
            return dict(kind='unmutated re-emit', payload_identical=True, summary_identical=True)

        def f1(t, hosted):
            before = width_profile(t['hosting']['pooled_slots'])
            a, b, sa, sb = time_swap(t)
            after = width_profile(t['hosting']['pooled_slots'])
            assert before == after, 'the swap must preserve every per-time width count'
            digest = reemit(hosted, t)
            return dict(kind='equal-width cross-time pooled-slot time swap (coherent re-emit)',
                        template_sha256=digest, width_profile_preserved=True,
                        swapped=[dict(index=i, stage=s['stage'], replica=s['replica'], helper=s['helper'],
                                      width=s['width'], time_before=s['time'], time_after=t2)
                                 for i, s, t2 in ((a, sa, sb['time']), (b, sb, sa['time']))])

        def f2(t, hosted):
            t['hosting']['owner_map_sha256'] = '0' * 64
            digest = reemit(hosted, t)
            return dict(kind='hosting.owner_map_sha256 set to a wrong digest (coherent re-emit)',
                        template_sha256=digest, value='0' * 64)

        def f3(t, hosted):
            slot = t['hosting']['pooled_slots'][0]
            old = slot['port']
            slot['port'] = old + 1
            digest = reemit(hosted, t)
            return dict(kind='pooled-slot port (checked roles field) changed (coherent re-emit)',
                        template_sha256=digest,
                        changed=dict(index=0, stage=slot['stage'], replica=slot['replica'], helper=slot['helper'],
                                     field='port', frm=old, to=old + 1))

        def f4(t, hosted):
            pair = time_swap(t)
            raw = CANON(t)
            (hosted / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw, mtime=0))
            return dict(kind='time swap with stale HOSTED.json template_sha256 (artifact inconsistency)',
                        template_sha256=sha(raw), stale_summary=True,
                        swapped=[dict(index=i, stage=s['stage'], replica=s['replica'], helper=s['helper'],
                                      time_before=s['time']) for i, s in ((pair[0], pair[2]), (pair[1], pair[3]))])

        e0 = record('F0', f0, 'accepted; link check passes')
        assert e0['accepted_by_chain'] and e0['link_check']['pooled_slots_equal_frozen_owners'] \
            and e0['link_check']['owner_map_sha256_names_frozen_gzip'], 'F0 positive control failed'
        assert all(e0['receipts_match_archived'].values()), 'F0 does not reproduce the archived selected receipts: ' + \
            json.dumps(e0['receipt_diff_paths_vs_archived'], sort_keys=True)
        assert e0['final_binding']['passed'] == e0['final_binding']['total'], 'F0 final binding failed: ' + \
            json.dumps(e0['final_binding'], sort_keys=True)

        e1 = record('F1', f1, 'accepted; link check fails on exactly two role times')
        assert e1['accepted_by_chain'] and e1['final_binding']['passed'] == e1['final_binding']['total'], \
            'F1 must pass the complete caller and the final binding'
        assert not e1['link_check']['pooled_slots_equal_frozen_owners'] and e1['link_check']['diff_count'] == 2, \
            'F1 must fail the link check on exactly two fields'
        assert all(d['field'] == 'time' for d in e1['link_check']['diffs']), 'F1 diff must be time-only'
        assert e1['link_check']['owner_map_sha256_names_frozen_gzip'], 'F1 keeps the correct owner_map_sha256'

        e2 = record('F2', f2, 'accepted; link check fails on owner_map_sha256')
        assert e2['accepted_by_chain'] and e2['final_binding']['passed'] == e2['final_binding']['total'], \
            'F2 must pass the complete caller and the final binding'
        assert e2['link_check']['pooled_slots_equal_frozen_owners'] and not e2['link_check']['owner_map_sha256_names_frozen_gzip']

        e3 = record('F3', f3, 'rejected by audit at line 172')
        assert not e3['accepted_by_chain'] and e3['stage_ledger'][0]['failure']['line'] == 172, 'F3 rejection line'

        e4 = record('F4', f4, 'rejected by audit at line 185')
        assert not e4['accepted_by_chain'] and e4['stage_ledger'][0]['failure']['line'] == 185, 'F4 rejection line'
    out = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if a.write:
        (HERE / 'EXPECTED.json').write_text(out)
    else:
        assert out == (HERE / 'EXPECTED.json').read_text(), 'result differs from EXPECTED.json'
    print('PASS_SELECTED_OWNERMAP_BINDING_GAP f0_accepted=1 f1_accepted_time_swap=1 f2_accepted_sha=1 '
          'f3_rejected_line=%s f4_rejected_line=%s' % (result['fixtures']['F3']['stage_ledger'][0]['failure']['line'],
                                                       result['fixtures']['F4']['stage_ledger'][0]['failure']['line']))


if __name__ == '__main__':
    main()
