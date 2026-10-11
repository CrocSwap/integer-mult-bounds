"""Run the complex pipeline for one selection (kernel / gauge words, or the empty anchor).  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: run_variant.py NAME SELECTION.json KEY CHANGED_DIR WORKDIR [--controls] [--discover-check] [--anchor]
CHANGED_DIR = PR #442 replay output's parent/changed (contains split-centres/ and work/); WORKDIR must not exist.
Steps (cwd = WORKDIR, as the inherited scripts expect):
  gk_word -> audit_gk (exact arbitrary-dirt + inverse-transpose + frame chains) -> emit_gk (emitted program replay, both orientations)
  -> exact Gaussian phase recipes (PR #433's complex_phases_full.py, unmodified, for every used transition) -> integrate_gk (parent template)
  -> replay_gk (independent read-back) -> hosted_gk (whole-residual idle-axis hosting; frozen selection) -> audit_hosted_gk
At --anchor (empty selection) the unmodified inputs must reproduce PR #433's and #442's files byte for byte."""
import gzip, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; CODE = ROOT / 'code'; R = ROOT.parent
name, selp, key, changed, work = sys.argv[1], Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]), Path(sys.argv[5])
flags = set(a for a in sys.argv[6:])
assert not work.exists(); work.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
log = open(work / 'run.log', 'w'); steps = []
def run(step, script, *args, cwd=None):
    t = time.monotonic()
    q = subprocess.run([sys.executable, '-B', str(script), *map(str, args)], cwd=cwd or work, env=env, stdout=log, stderr=subprocess.STDOUT, text=True)
    if q.returncode: raise RuntimeError((name, step, 'see ' + str(work / 'run.log')))
    steps.append(dict(step=step, seconds=round(time.monotonic() - t, 1))); print(name, 'PASS', step, flush=True)
shutil.copytree(changed / 'work', work / 'work', symlinks=False)
shutil.copy(changed / 'BIT-PRICE.json', work / 'BIT-PRICE.json')
base = work / 'sc_base'; shutil.copytree(changed / 'split-centres', base, symlinks=False)
sc = work / 'split-centres'; shutil.copytree(base, sc)
run('gk_word', CODE / 'gk_word.py', base / 'FULL-WORD.json.gz', selp, sc / 'GK-WORD.json.gz')
os.replace(sc / 'GK-WORD.json.gz', sc / 'FULL-WORD.json.gz')
if '--controls' in flags:
    run('mutation controls (word)', CODE / 'controls_gk.py', sc / 'FULL-WORD.json.gz', work / 'CONTROLS-WORD.json')
    run('mutation controls (selection)', CODE / 'controls_sel.py', base / 'FULL-WORD.json.gz', selp, work / 'CONTROLS-SELECTION.json')
    run('mutation controls (through the certifying scripts)', CODE / 'controls_pipeline.py', work, selp, work / 'CONTROLS-PIPELINE.json')
run('audit_gk', CODE / 'audit_gk.py'); run('emit_gk', CODE / 'emit_gk.py')
if '--anchor' in flags:
    for f in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json'):
        assert (sc / f).read_bytes() == (base / f).read_bytes(), ('anchor: ' + f + ' differs from PR #433')
    print(name, 'ANCHOR canonical word, local programs and local checks identical to PR #433', flush=True)
    # canonical word identical => PR #433's phase recipes apply unchanged (they are bound to the canonical hash)
else:
    run('phases (exact Gaussian recipes, all used transitions)', R / 'split-centres-global/code/complex_phases_full.py')
    run('adapters_gk (paid residual wrappers: L^-1 S_E R^-1 = C_[w] x I, exactly)', CODE / 'adapters_gk.py', sc / 'CANONICAL-WORD.json.gz', sc / 'RESIDUAL-ADAPTERS.json', work / 'LEMMA-A.json')
run('integrate_gk', CODE / 'integrate_gk.py'); run('replay_gk', CODE / 'replay_gk.py')
if '--anchor' in flags:
    for f in ('GLOBAL-TEMPLATE.json.gz', 'INDEPENDENT-REPLAY.json'):
        assert (sc / f).read_bytes() == (base / f).read_bytes(), ('anchor: ' + f + ' differs from PR #433')
    print(name, 'ANCHOR parent global template and independent replay identical to PR #433', flush=True)
host = work / 'hosted'
ONE = [] if '--anchor' in flags else ['--one-helper-per-family']      # the anchor uses PR #442's rule; every other word PR #458's
if '--anchor' in flags: sel_args = []
elif '--discover' in flags: sel_args = [*ONE, '--key', key, '--discover-to', work / 'SELECTION-new.json']      # development only: freeze a new selection
else: sel_args = [*ONE, '--selection', ROOT / 'data/SELECTION.json', '--key', key]
run('hosted_gk', CODE / 'hosted_gk.py', sc, host, *sel_args)
if '--discover-check' in flags and '--anchor' not in flags:
    run('hosted_gk --discover (selection recomputed with HiGHS)', CODE / 'hosted_gk.py', sc, work / 'hosted-rediscovered', *ONE, '--key', key, '--discover-to', work / 'SELECTION-rediscovered.json')
    a = json.loads((ROOT / 'data/SELECTION.json').read_text())[key]; b = json.loads((work / 'SELECTION-rediscovered.json').read_text())[key]
    assert a['patterns'] == b['patterns'], 'rediscovered selection differs'
    assert (host / 'GLOBAL-TEMPLATE.json.gz').read_bytes() == (work / 'hosted-rediscovered' / 'GLOBAL-TEMPLATE.json.gz').read_bytes()
run('audit_hosted_gk', CODE / 'audit_hosted_gk.py', sc, host, work / 'HOSTING-AUDIT.json', *ONE)
if '--controls' in flags and '--anchor' not in flags:
    run('mutation controls (one-owner rule on every register class, through the generators)', CODE / 'controls_hosting.py', work, ROOT / 'data/SELECTION.json', key, work / 'CONTROLS-HOSTING.json')
(work / 'STEPS.json').write_text(json.dumps(dict(name=name, steps=steps, canonical_word_sha256=sha(sc / 'CANONICAL-WORD.json.gz'),
                                                 hosted_template_sha256=json.loads((host / 'HOSTED.json').read_text())['template_sha256']), indent=1) + '\n')
print(name, 'DONE', flush=True)
