#!/usr/bin/env python3
"""Complete replay for the repacked fill: retained parent, native providers, rebind, discovery and strict global admission,
geometry controls, exact outer ledger, independent balance and the outer evidence replays.  Same stages and commands as
PR2530's full_replay.py, run on this package's derivative (build.py).

Optional reuse (both default to fresh runs):
  --parent-from DIR    a completed retained-parent work directory (vendor/pr1297/verify.py --work DIR), status-checked
  --native-base DIR, --native-extra DIR   completed run_native_borrow.py directories, bound to the derivative's words
"""
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, time
from fractions import Fraction as Q
from pathlib import Path
from build import HERE, ROOT, build, read, write, need, sha
PR2530 = ROOT / 'research/source-partner-lifetimes'


def full(work, parent_from=None, native_from=None):
    work.mkdir(parents=True, exist_ok=False); p = build(work / 'build')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', AUDIT_FAST_SHARDS='4')
    for k in ['PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD']:
        env.pop(k, None)
    stages = []

    def run(name, script, *args):
        cmd = [sys.executable, '-B', str(script), *map(str, args)]; start = time.monotonic()
        with (work / (name + '.log')).open('w') as log:
            r = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, command=[c.replace(str(work), '${REPLAY_ROOT}') for c in cmd], exit_code=r.returncode, seconds=round(time.monotonic() - start, 1),
                           script_sha256=hashlib.sha256(Path(script).read_bytes()).hexdigest()))
        write(work / 'STAGES.json', stages); need(r.returncode == 0, 'failed ' + name + '; see ' + str(work / (name + '.log'))); print('PASS', name, flush=True)

    vend = p / 'vendor/pr1297'
    if parent_from:
        shutil.copytree(parent_from, work / 'parent', symlinks=True)
        pr = read(work / 'parent/RESULT.json')
        need(pr['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and pr['kappa'] == read(vend / 'CLAIM.json')['kappa'], 'reused retained parent receipt')
        stages.append(dict(name='retained-parent', reused=str(parent_from), result_sha256=sha(work / 'parent/RESULT.json'), vendor_manifest_sha256=sha(vend / 'MANIFEST.json')))
        print('PASS retained-parent (reused, status-checked)', flush=True)
    else:
        run('retained-parent', vend / 'verify.py', '--work', work / 'parent')
    for tag in ['base', 'extra']:
        word = p / f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
        if native_from and native_from.get(tag):
            src = Path(native_from[tag]); shutil.copytree(src, work / ('native-' + tag))
            need(gzip.decompress((work / ('native-' + tag) / 'local/FULL-WORD.json.gz').read_bytes()) == gzip.decompress(word.read_bytes()), 'reused native bound to word ' + tag)
            st = read(work / ('native-' + tag) / 'STEPS.json')
            need([x['step'] for x in st] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(x['exit_code'] == 0 for x in st), 'reused native steps ' + tag)
            stages.append(dict(name='native-' + tag, reused=str(src), word_sha256=sha(word))); print('PASS native-' + tag + ' (reused, bound)', flush=True)
        else:
            run('native-' + tag, p / 'new/run_native_borrow.py', word, work / ('native-' + tag))
    run('rebind', p / 'new/rebind.py', p, work / 'native-base/local', work / 'native-extra/local', work / 'rebound')
    runtime = work / 'parent/layout/source_partners'; runtime.mkdir()
    for n in ['replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py', 'audit_fast.py']:
        shutil.copy2(p / n, runtime / n)
    for n in ['code', 'construction', 'inputs']:
        shutil.copytree(p / n, runtime / n)
    shutil.copytree(work / 'rebound', runtime / 'candidate'); shutil.copytree(work / 'native-extra', runtime / 'native-extra')
    data = runtime / 'candidate'
    run('discover', runtime / 'replay.py', '--data', data, '--work', work / 'discovery', '--local', work / 'native-base/local', '--discover')
    run('strict', runtime / 'replay.py', '--data', data, '--work', work / 'strict', '--local', work / 'native-base/local')
    run('geometry-controls', runtime / 'geometry_controls.py', '--source', work / 'parent/layout/joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold', '--strict', work / 'strict', '--out', work / 'GEOMETRY-CONTROLS.json')
    result = read(work / 'strict/RESULT.json'); need(result['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL', 'strict status')
    for n in ['PLAN.json', 'PROFILE.json', 'SPEC.json']:
        shutil.copy2(data / n, p / 'new' / n)
    write(p / 'CLAIM.json', dict(kappa=result['kappa'], scope='Conditional finite construction; inherited interfaces remain.'))
    spec = read(p / 'new/SPEC.json'); C = Q(spec['expected']['complex_lower']); DIG = spec['outer_refinement']['endpoint_digits']
    write(p / 'outer/B.json', dict(b=str(C - Q(1, 10 ** (DIG + 80))), b_above_endpoint=str(C + Q(1, 10 ** DIG)), profile=spec['expected']['global_profile'], live=spec['expected']['live']))
    for name in ['check_ledger.py', 'independent_check.py']:
        run('outer-' + name, p / 'outer' / name)
    run('outer-evidence', p / 'outer/run_outer.py', work / 'outer-replay')
    ledger = read(p / 'outer/LEDGER.json'); k = Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])
    previous = read(work / 'build/source/research/gmx-t74-borrow43-handoff/outer/OUTER-CLAIM.json'); need(k > Q(previous['kappa']), 'strict improvement over pinned PR2462')
    leader = read(PR2530 / 'CLAIM.json'); need(k > Q(leader['kappa']), 'strict improvement over PR2530')
    need(ledger['profile'] == spec['expected']['global_profile'] and ledger['W'] == 66304, 'outer supplier binding')
    need(sum(int(r) * n for r, n in ledger['profile'].items()) == 73 * 66304 - 23680, 'rank mass')
    for n in ['LEDGER.json', 'INDEPENDENT.json', 'B.json']:
        shutil.copy2(p / 'outer' / n, work / ('OUTER-' + n))
    receipt = dict(status='PASS_SOURCE_PARTNER_REPACK_COMPLETE_FINITE_ADMISSION_AND_OUTER', kappa=str(k), complex_lower=str(C),
                   pr2530_kappa=leader['kappa'], gain_over_pr2530=str(k - Q(leader['kappa'])), previous_kappa=previous['kappa'],
                   source_commit='ef34071fee6dfb0286e9850a5cec4e36d9eb126d', global_profile=ledger['profile'], supplier=result,
                   outer_checks=len(ledger['rows']['struct_boundary_radix_union']['strict_checks']), outer_controls=len(ledger['rejecting_controls']['struct_boundary_radix_union']),
                   stages=stages, scope='Conditional finite construction and exact outer arithmetic; no independent human review or complete multiplication theorem.')
    write(work / 'RESULT.json', receipt); print(receipt['status'], str(k), flush=True)
    return receipt


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--parent-from', type=Path)
    ap.add_argument('--native-base', type=Path); ap.add_argument('--native-extra', type=Path); a = ap.parse_args()
    full(a.work.resolve(), a.parent_from.resolve() if a.parent_from else None, dict(base=a.native_base, extra=a.native_extra))
