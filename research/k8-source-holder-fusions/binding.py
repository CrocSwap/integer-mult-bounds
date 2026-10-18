"""Whole-head supplier binding for this package (standard library; answers the #1195 review continuation point).

From a completed verify.py work directory and this checkout, records:
  native provider    the rebuilt word, every native local artifact (content hash and the semantic identity PLAN.json.gz
                     binds), the native step list, and the provider directory the strict run bound (PLAN artifact hashes);
  owner allocation   OWNERS.json.gz, PLAN.json.gz and SPEC.json hashes, the PLAN's replicas, calls, widths and idle part,
                     and the strict run's independent owner/profile audit;
  admission          the strict REPLAY.json (status, kappa, endpoints, controls), the stage list with log hashes, and
                     this package's verify receipt;
  predecessors       every consumed predecessor file (SOURCE-PINS.json) with its SHA256 and Git blob id, and the Git tree
                     ids of the five inherited #1148 package directories at this head;
  reconciliation     with --predecessor OLD NEW (Git commits of the predecessor PR): every inherited path whose blob differs
                     between OLD and NEW, and whether this package consumes it.
'stable' holds only fields that must be identical on any fresh run; --check compares them with a recorded receipt.
usage: python -B binding.py --work COMPLETED_VERIFY_WORK [--native NATIVE_DIR] (--out RECEIPT.json | --check RECEIPT.json)
       (--native: the --native-from directory of a verify.py run that reused a native replay; default WORK/native)"""
import argparse, gzip, hashlib, json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent; ROOT = P.parents[1]
INHERITED = ['k8-coordinated-owners', 'k8-eight-ends', 'k8-eight-ends-t16', 'k8-three-demotions', 'k8-joint-entrances']
def raw(p): return Path(p).read_bytes()
def sha(p): return hashlib.sha256(raw(p)).hexdigest()
def payload(p): b = raw(p); return hashlib.sha256(gzip.decompress(b) if str(p).endswith('.gz') else b).hexdigest()
def blob(p): b = raw(p); return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()
def rd(p): return json.loads(gzip.decompress(raw(p)) if str(p).endswith('.gz') else raw(p))
def git(*args):
    try: return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError): return None
def tree(rel, rev='HEAD'):
    out = git('rev-parse', rev + ':' + rel); return out.strip() if out else None
def reconcile(old, new):
    rows = []
    for line in git('diff', '--raw', '--no-abbrev', '--no-renames', old, new, '--', *['research/' + p for p in INHERITED]).splitlines():
        meta, path = line.split('\t'); _, _, a, b, status = meta.split()
        rows.append(dict(path=path, status=status, blob_old=None if set(a) == {'0'} else a, blob_new=None if set(b) == {'0'} else b,
                         consumed=path in rd(P / 'SOURCE-PINS.json')))
    return dict(old=git('rev-parse', old).strip(), new=git('rev-parse', new).strip(), changed=rows,
                inherited_trees_equal_new={p: tree('research/' + p) == tree('research/' + p, new) for p in INHERITED})
def hosted_template(work):
    """canonical hash of the emitted hosting template without async_schedule.source_plan_sha256: that field is the runtime
    PLAN hash, which binds CLIFFORD-REVIEW.json's elapsed seconds and so differs on every run."""
    t = rd(work / 'global/global/hosted/GLOBAL-TEMPLATE.json.gz'); t['async_schedule'] = dict(t['async_schedule']); t['async_schedule'].pop('source_plan_sha256')
    return hashlib.sha256(json.dumps(t, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def receipt(work, native_dir=None):
    res, rp = rd(work / 'RESULT.json'), rd(work / 'global/REPLAY.json')
    plan_pkg = rd(P / 'PLAN.json.gz'); g = rd(work / 'global/global/PLAN.json'); reg = g['provider_registry']['gauge44']
    nat = Path(native_dir) if native_dir else work / 'native'
    own = rd(work / 'global/global/audit/OWNERS-AND-PROFILE.json'); local = nat / 'local'
    native = {f.name: dict(content_sha256=payload(f)) for f in sorted(local.iterdir()) if f.is_file()}
    for name, h in plan_pkg['provider_registry']['gauge44']['artifact_semantic_sha256'].items():
        native.setdefault(name, {})['plan_semantic_sha256'] = h
    bound = {f.name: payload(f) for f in sorted((work / 'global/global/base/providers/gauge44').iterdir()) if f.is_file()}
    stable = dict(
        word=dict(payload_sha256=payload(work / 'FULL-WORD.json.gz'), package_word_payload_sha256=payload(P / 'FULL-WORD.json.gz'),
                  recipe_output_content_sha256=rd(P / 'RECIPE.json')['output_content_sha256']),
        native_provider=dict(steps=[s['step'] for s in rd(nat / 'STEPS.json')], semantic_identities=res['native_semantic_artifacts'],
                             plan_semantic_identities=plan_pkg['provider_registry']['gauge44']['artifact_semantic_sha256'],
                             local_artifacts=sorted(native), bound_paid_profile=reg['actual_paid_profile'],
                             orientation_program_sha256=reg['orientation_program_sha256'], widths=len(reg['widths']), ports=len(reg['ports']),
                             centers=reg['centers']),
        owner_allocation=dict(owners=dict(path='research/k8-joint-entrances/OWNERS.json.gz', sha256=sha(ROOT / 'research/k8-joint-entrances/OWNERS.json.gz'),
                                          payload_sha256=payload(ROOT / 'research/k8-joint-entrances/OWNERS.json.gz'), copied_sha256=sha(work / 'data/OWNERS.json.gz')),
                              plan=dict(package_payload_sha256=payload(P / 'PLAN.json.gz'), work_sha256=sha(work / 'data/PLAN.json')),
                              spec_sha256=sha(P / 'SPEC.json'), K=g['K'], T=g['T'], M=g['M'], L=g['L'], live=g['live'], deficit=g['deficit'],
                              profile=g['profile'], provider_calls=g['provider_calls'], source_owners_sha256=g['source_owners_sha256'],
                              assignment_content_sha256=g['assignment_content_sha256'],
                              hosted_template_sha256_without_runtime_plan=hosted_template(work),
                              audit={k: own[k] for k in ('status', 'paid_profile', 'live', 'physical', 'rank_mass', 'deficit',
                                                          'hosted_residuals', 'banked_residuals', 'owners_per_call', 'actual_helper_owner_charts',
                                                          'actual_73column_sigmas', 'explicit_idle_remainder_children', 'source_idle_children_charged')}),
        admission=dict(status=res['status'], strict_status=rp['status'], kappa=rp['kappa'], kappa_decimal=rp['kappa_decimal'],
                       complex_lower=rp['complex_lower'], bit_lower=rp['bit_lower'], global_profile=rp['profile'], idle=rp['idle'],
                       controls=rp['controls'], fusion_controls=res['fusion_controls'], outer_strict_inequalities=rp['outer_strict_inequalities'],
                       verify_steps=[s['step'] for s in res['steps']], strict_stages=[s['step'] for s in rp['steps']]),
        predecessors=dict(source_pins={rel: dict(sha256=sha(ROOT / rel), git_blob=blob(ROOT / rel), pinned=h) for rel, h in rd(P / 'SOURCE-PINS.json').items()},
                          parent_pins=rd(P / 'PARENT-PINS.json')))
    for rel, x in stable['predecessors']['source_pins'].items(): assert x['sha256'] == x['pinned'], ('source pin', rel)
    assert stable['native_provider']['semantic_identities'] == stable['native_provider']['plan_semantic_identities'], 'native semantic identities'
    assert stable['word']['payload_sha256'] == stable['word']['package_word_payload_sha256'] == stable['word']['recipe_output_content_sha256']
    assert stable['owner_allocation']['owners']['sha256'] == stable['owner_allocation']['owners']['copied_sha256']
    run = dict(native_local_content_sha256={k: v['content_sha256'] for k, v in native.items() if 'content_sha256' in v},
               bound_provider_payload_sha256=bound, plan_artifact_sha256=reg['artifact_sha256'],
               strict_stage_logs={s['step']: s['log_sha256'] for s in rp['steps']}, verify_step_logs={s['step']: s['log_sha256'] for s in res['steps']},
               replay_sha256=sha(work / 'global/REPLAY.json'), result_sha256=sha(work / 'RESULT.json'),
               owners_audit_sha256=sha(work / 'global/global/audit/OWNERS-AND-PROFILE.json'), template_sha256=own['template_sha256'],
               runtime_plan_sha256=rd(work / 'global/global/BINDING.json')['runtime_plan_sha256'], binding=rd(work / 'global/global/BINDING.json')['status'],
               native_reuse=res['native_reuse'], parent_reuse=res['parent_reuse'])
    trees = {p: tree('research/' + p) for p in INHERITED}
    return dict(stable=stable, run=run, trees=trees,
                note="'stable' is identical on every fresh run; 'run' hashes include timing-dependent logs and generated reviews.")
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', type=Path, required=True); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--out', type=Path); g.add_argument('--check', type=Path); ap.add_argument('--predecessor', nargs=2, metavar=('OLD', 'NEW'))
    ap.add_argument('--native', type=Path)
    a = ap.parse_args(); r = receipt(a.work.resolve(), a.native.resolve() if a.native else None)
    if a.predecessor: r['reconciliation'] = reconcile(*a.predecessor)
    if a.out:
        a.out.write_text(json.dumps(r, indent=1, sort_keys=True) + '\n'); print('WROTE', a.out)
    else:
        old = json.loads(a.check.read_text()); new_st, old_st = json.loads(json.dumps(r['stable'])), json.loads(json.dumps(old['stable']))
        if r['run']['parent_reuse'] or r['run']['native_reuse']:   # a run that reused completed replays skips those steps only
            ran = set(new_st['admission'].pop('verify_steps')); skipped = [x for x in old_st['admission'].pop('verify_steps') if x not in ran]
            assert set(skipped) <= {'parent', 'native'}, ('unexpected skipped steps', skipped)
        assert new_st == old_st, 'stable binding differs from the recorded receipt'
        trees = {k: v for k, v in r['trees'].items() if v is not None}
        assert all(old['trees'].get(k) == v for k, v in trees.items()), 'package tree ids differ from the recorded receipt'
        print('PASS_K8_SOURCE_HOLDER_FUSIONS_WHOLE_HEAD_BINDING', r['stable']['admission']['kappa_decimal'], 'trees checked:', len(trees))
if __name__ == '__main__':
    main()
