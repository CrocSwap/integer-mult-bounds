#!/usr/bin/env python3
"""Replay the selected final stage, then compare its audit sub-stage with fast_copy.py.

1. Rebuild the selected PR1094 final stage unchanged: the archived gauge44 provider
   files from research/community-frontier1094-audit/selected-replay.tar.gz are the
   `--local` input of research/complex-t16-rare-pattern-exchanges/verify.py, which
   runs the frozen PR1087 verify_t16.py (all 11 sub-stages). Its ASYNC-AUDIT.json
   must equal the archived selected receipt byte for byte.
2. Rerun that stage's `audit` sub-stage (pinned audit_allcold.py with its 15
   mutation controls) in fresh copies of the same inputs, as the pinned
   `run_portable.py` command (legacy) and through fast_copy.py, alternating order.
   Every written file and the merged stdout/stderr log must equal the in-stage
   audit outputs byte for byte. Wall times are recorded; there is no threshold.
3. Controls: a tampered hosted template fails under both launchers; an unpinned
   script is refused; an identity "copy" (no copy) changes the outputs, so the
   copy is load-bearing; in-process semantics of the checked copy and fallback.

Timing only. No kappa, certificate, supplier, frontier or pinned source changes.
jackmgaller with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

assert __debug__, 'Assertions required'
PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
sys.path.insert(0, str(PKG))
import fast_copy  # noqa: E402

STAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges/verify.py'
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
MULTICOLD = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'
RUN_PORTABLE = MULTICOLD / 'code/run_portable.py'
KAPPA = '0.001672660197076918'
AUDIT_FILES = ('ASYNC-AUDIT.json', 'OWNERS-AND-PROFILE.json', 'IDLE-REMAINDER-FRAMES.json')
EXPECTED_STATS = {'fallback': 0, 'marshal': 4838}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(path):
    path = Path(path)
    return {str(f.relative_to(path)): sha(f) for f in sorted(path.rglob('*')) if f.is_file()}


def stage_env(spec):
    # Exactly verify_t16.py's env0 plus its WITNESS_SPEC for the `audit` sub-stage.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(MULTICOLD), GAIN_PR564_SOURCE=str(MULTICOLD))
    for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC', 'FAST_COPY_STATS'):
        env.pop(k, None)
    env['WITNESS_SPEC'] = str(spec)
    return env


def build_fixture(work):
    archived = work / 'archived'
    archived.mkdir()
    with tarfile.open(ARCHIVE) as t:
        for m in t.getmembers():
            assert m.isfile() and (archived / m.name).resolve().is_relative_to(archived), 'Unsafe member'
        t.extractall(archived, filter='data')
    local = work / 'local'
    shutil.copytree(archived / 'candidate/strict/global/base/providers/gauge44', local)
    stage = work / 'stage'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    t0 = time.monotonic()
    out = subprocess.run([sys.executable, '-B', str(STAGE), '--main', str(ROOT), '--local', str(local),
                          '--work', str(stage)], env=env, capture_output=True, text=True)
    seconds = time.monotonic() - t0
    assert out.returncode == 0, out.stdout[-3000:] + out.stderr[-3000:]
    assert out.stdout.strip().endswith('PASS_T16_RARE_PATTERN_EXCHANGES ' + KAPPA), out.stdout[-500:]
    g = stage / 'strict/global'
    archived_audit = archived / 'candidate/strict/global/audit/ASYNC-AUDIT.json'
    assert (g / 'audit/ASYNC-AUDIT.json').read_bytes() == archived_audit.read_bytes(), \
        'Fixture audit differs from the archived selected receipt'
    substages = json.loads((stage / 'strict/STAGES.json').read_text())
    return stage, seconds, substages


def run_audit(stage, dest, mode, script=None, extra_env=None):
    """Run the `audit` sub-stage on fresh copies of the stage's inputs."""
    g = stage / 'strict/global'
    dest.mkdir(parents=True)
    hosted = dest / 'hosted'
    shutil.copytree(g / 'hosted', hosted)
    (hosted / 'IDLE-REMAINDER-FRAMES.json.gz').unlink()  # written by the audit itself
    script = script or stage / 'source/code/audit_allcold.py'
    args = [str(script), str(g / 'base'), str(hosted), str(dest / 'audit/ASYNC-AUDIT.json'), '--mutation-controls']
    if mode == 'legacy':
        argv = [sys.executable, '-B', str(RUN_PORTABLE), *args]
    elif mode == 'fast':
        argv = [sys.executable, '-B', str(PKG / 'fast_copy.py'), str(RUN_PORTABLE), *args]
    else:  # in-process control copier selected by name
        code = ('import sys;sys.path.insert(0,%r);import fast_copy;'
                'fast_copy.main(sys.argv[1:],copier=lambda x,memo=None,_nil=None:x)') % str(PKG)
        argv = [sys.executable, '-B', '-c', code, str(RUN_PORTABLE), *args]
    env = stage_env(stage / 'source/data/SPEC.json')
    env.update(extra_env or {})
    log = dest / 'audit.log'
    t0 = time.monotonic()
    with log.open('w') as s:  # merged like verify_t16.py's run()
        rc = subprocess.run(argv, env=env, stdout=s, stderr=subprocess.STDOUT).returncode
    return rc, time.monotonic() - t0


def outputs(stage_or_dest, in_stage=False):
    base = stage_or_dest / ('strict/global' if in_stage else '')
    files = {name: sha(base / 'audit' / name) for name in AUDIT_FILES}
    files['hosted/IDLE-REMAINDER-FRAMES.json.gz'] = sha(base / 'hosted/IDLE-REMAINDER-FRAMES.json.gz')
    files['audit.log'] = sha((stage_or_dest / 'strict/audit.log') if in_stage else (stage_or_dest / 'audit.log'))
    return files


def semantics():
    import marshal  # noqa: F401  (documented dependency of fast_copy)
    stats0 = dict(fast_copy.STATS)
    shared = [1, [2]]
    x = {'a': [shared, shared], 's': 'é\ud800', 'n': None, 'b': True, 'f': 0.1, 'i': 10 ** 40}
    y = fast_copy.checked_deepcopy(x)
    assert y == x and y is not x and y['a'] is not x['a'] and y['a'][0] is not shared
    assert y['a'][0] is y['a'][1], 'aliasing kept like deepcopy'
    y['a'][0][1].append(3)
    assert shared == [1, [2]], 'copy is independent of the original'

    class D(dict):
        pass

    class O:
        pass

    cyc = []
    cyc.append(cyc)
    fallbacks = [D(k=1), {'nan': math.nan}, {'o': O()}, cyc]
    for v in fallbacks:
        fast_copy.checked_deepcopy(v)
    z = fast_copy.checked_deepcopy(cyc)
    assert z is not cyc and z[0] is z
    assert type(fast_copy.checked_deepcopy(D(k=1))) is D
    memo = {}
    fast_copy.checked_deepcopy([1], memo)
    d = {k: fast_copy.STATS[k] - stats0[k] for k in stats0}
    assert d == {'marshal': 1, 'fallback': len(fallbacks) + 3}, d
    return dict(marshal_copies=1, fallbacks=d['fallback'],
                fallback_cases=['dict subclass', 'NaN (copy not equal)', 'custom object', 'cyclic list',
                                'cyclic list (identity check)', 'subclass type check', 'explicit memo'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, help='fresh directory outside the repository (default: temporary)')
    ap.add_argument('--rounds', type=int, default=1, help='alternating legacy/fast timing rounds')
    a = ap.parse_args()
    assert a.rounds >= 1
    if a.work is None:
        tmp = tempfile.TemporaryDirectory(prefix='audit-allcold-fast-copy.')
        work = Path(tmp.name).resolve() / 'run'  # e.g. macOS /var -> /private/var
    else:
        tmp = None
        work = a.work.resolve()
    assert not work.exists() and not work.is_relative_to(ROOT), 'Use a fresh directory outside the repository'
    work.mkdir(parents=True)
    script = work / 'stage/source/code/audit_allcold.py'

    stage, stage_seconds, substages = build_fixture(work)
    assert sha(script) in fast_copy.SCRIPTS and sha(RUN_PORTABLE) in fast_copy.RUN_PORTABLE
    assert sha(script) == sha(ROOT / 'research/gauge44-slots-t16/code/audit_allcold.py'), \
        'Same audit script as the cold baseline1042 t16 stage'
    reference = outputs(stage, in_stage=True)
    print('PASS fixture: selected final stage replayed, audit equals archived receipt', flush=True)

    times = {'legacy': [], 'fast': []}
    stats = None
    for i in range(a.rounds):
        for mode in (('legacy', 'fast') if i % 2 == 0 else ('fast', 'legacy')):
            dest = work / 'ab' / ('%s-%d' % (mode, i))
            extra = {'FAST_COPY_STATS': str(dest.parent / ('stats-%d.json' % i))} if mode == 'fast' else None
            rc, seconds = run_audit(stage, dest, mode, extra_env=extra)
            assert rc == 0, (mode, (dest / 'audit.log').read_text()[-3000:])
            assert outputs(dest) == reference, mode + ': audit outputs differ from the in-stage receipt'
            times[mode].append(seconds)
            if mode == 'fast':
                stats = json.loads((dest.parent / ('stats-%d.json' % i)).read_text())
                assert stats == EXPECTED_STATS, stats
        print('PASS round %d: legacy %.2fs, fast %.2fs, outputs identical' %
              (i, times['legacy'][-1], times['fast'][-1]), flush=True)
    report = json.loads((work / 'ab/fast-0/audit/ASYNC-AUDIT.json').read_text())
    assert report['mutation_controls_run'] and len(report['mutations_rejected']) == 15

    controls = {}
    # Tampered hosted template: both launchers must reject it.
    bad = work / 'controls/tampered'
    for part in ('source', 'strict'):
        shutil.copytree(stage / part, bad / part)
    t = bad / 'strict/global/hosted/GLOBAL-TEMPLATE.json.gz'
    obj = json.loads(gzip.decompress(t.read_bytes()))
    obj['physical'] -= 1
    t.write_bytes(gzip.compress(json.dumps(obj).encode(), mtime=0))
    for mode in ('legacy', 'fast'):
        rc, _ = run_audit(bad, bad / mode, mode)
        assert rc != 0 and 'AssertionError' in (bad / mode / 'audit.log').read_text(), mode + ' accepted tampering'
    controls['tampered_hosted_template'] = 'rejected by legacy and fast'
    # Unpinned script: one appended comment is refused before anything runs.
    other = work / 'controls/unpinned/audit_allcold.py'
    other.parent.mkdir(parents=True)
    shutil.copytree(script.parent, other.parent, dirs_exist_ok=True)
    other.write_bytes(script.read_bytes() + b'# changed\n')
    rc, _ = run_audit(stage, work / 'controls/unpinned/run', 'fast', script=other)
    assert rc != 0 and 'not on the allow-list' in (work / 'controls/unpinned/run/audit.log').read_text()
    controls['unpinned_script'] = 'refused'
    # Identity copier: without real copies the mutation controls corrupt the audited
    # template, so outputs must change (or the audit must fail).
    dest = work / 'controls/identity'
    rc, _ = run_audit(stage, dest, 'identity')
    changed = rc != 0 or not all((dest / 'audit' / n).is_file() for n in AUDIT_FILES) or outputs(dest) != reference
    assert changed, 'identity copier was not detected'
    controls['identity_copy'] = 'detected (exit %d)' % rc
    controls['checked_copy_semantics'] = semantics()

    legacy, fast = statistics.median(times['legacy']), statistics.median(times['fast'])
    result = dict(
        status='PASS_AUDIT_ALLCOLD_FAST_COPY_IDENTICAL',
        python=sys.version.split()[0], platform=sys.platform,
        audit_allcold_sha256=sha(script), run_portable_sha256=sha(RUN_PORTABLE),
        fast_copy_sha256=sha(PKG / 'fast_copy.py'),
        selected_stage_seconds=round(stage_seconds, 3),
        selected_stage_substages={s['name']: s['seconds'] for s in substages},
        audit_outputs_sha256=reference, rounds=a.rounds,
        legacy_seconds=[round(x, 3) for x in times['legacy']], fast_seconds=[round(x, 3) for x in times['fast']],
        median_speedup=round(legacy / fast, 3), deepcopy_calls=stats, mutation_controls=report['mutations_rejected'],
        controls=controls,
        scope='Same fixture, same pinned run_portable.py and audit_allcold.py bytes; only copy.deepcopy is replaced '
              'by a checked marshal round trip. Timing has no pass threshold. No kappa or certificate change.')
    if tmp is None:
        (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('legacy_seconds', 'fast_seconds', 'median_speedup', 'deepcopy_calls')}))
    print(result['status'], 'median speedup %.2fx' % result['median_speedup'])
    if tmp is not None:
        tmp.cleanup()


if __name__ == '__main__':
    main()
