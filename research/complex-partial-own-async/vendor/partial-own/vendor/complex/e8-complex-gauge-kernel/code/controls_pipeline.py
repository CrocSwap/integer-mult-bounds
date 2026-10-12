"""Mutation controls that run through the CERTIFYING scripts (audit_gk.py, emit_gk.py).  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: controls_pipeline.py VARIANT_WORKDIR SELECTION.json OUT.json
Every control writes a mutated FULL-WORD.json.gz into a fresh copy of the variant's split-centres directory and runs audit_gk.py then
emit_gk.py there; the pair must FAIL (nonzero exit).  The unmutated word must pass.  The selection-level words are built with
gk_word.build(check=False), so the structural assertions of the builder are NOT what rejects them."""
import copy, gzip, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
CODE = Path(__file__).resolve().parent; sys.path.insert(0, str(CODE))
import gk_word as GW
from gk_common import V, basis
work = Path(sys.argv[1]).resolve(); sel = json.loads(Path(sys.argv[2]).read_text())
base = json.load(gzip.open(work / 'sc_base/FULL-WORD.json.gz'))
good = json.load(gzip.open(work / 'split-centres/FULL-WORD.json.gz'))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1'); env.pop('PYTHONOPTIMIZE', None)
def run_pair(word):
    tmp = Path(tempfile.mkdtemp(prefix='gkctl-', dir=work))
    try:
        os.symlink(work / 'work', tmp / 'work'); shutil.copytree(work / 'sc_base', tmp / 'split-centres')
        (tmp / 'split-centres/FULL-WORD.json.gz').write_bytes(GW.dump(word))
        for script in ('audit_gk.py', 'emit_gk.py'):
            q = subprocess.run([sys.executable, '-B', str(CODE / script)], cwd=tmp, env=env, capture_output=True, text=True)
            if q.returncode: return script, (q.stderr.strip().splitlines() or ['?'])[-1][:160]
        return None, ''
    finally: shutil.rmtree(tmp, ignore_errors=True)
assert run_pair(good) == (None, ''), 'the unmutated word must pass the certifying scripts'
out = []
def expect_fail(name, word, must=None):
    script, msg = run_pair(word)
    assert script is not None, ('mutation accepted by the certifying scripts: ' + name)
    if must: assert must in msg, (name, msg)
    out.append(dict(control=name, rejected_by=script, message=msg))
def mut(fn):
    w = copy.deepcopy(good); fn(w); return w
kern = next(i for i, e in enumerate(good['A']) if e[0] == 'add' and e[1] >= 2 * V and e[2] >= 2 * V and str(e[2]) in good['start_extra'])
gaug = next(i for i, e in enumerate(good['A']) if e[0] == 'add' and V <= e[1] < 2 * V and str(e[2]) in good['start_extra'])
expect_fail('kernel: donor update omitted', mut(lambda w: w['A'].pop(kern)))
expect_fail('kernel: donor update sign flipped', mut(lambda w: w['A'][kern].__setitem__(3, -w['A'][kern][3])))
expect_fail('gauge: compensation gate omitted', mut(lambda w: w['A'].pop(gaug)))
expect_fail('gauge: compensation coefficient doubled', mut(lambda w: w['A'][gaug].__setitem__(3, 2 * w['A'][gaug][3])))
def bad_entrance(w):
    e = w['A'][gaug]; E = e[-1]; w['start_extra'][str(e[2])] = [next(x for x in range(1, 512) if basis(E + [x]) != basis(E))]
expect_fail('gauge: entrance outside the frame of its gates', mut(bad_entrance))
expect_fail('helper with a frame-zero compensation given an entrance', mut(lambda w: w['start_extra'].__setitem__(str(2 * V + next(h for h in range(w['report']['R']) if str(2 * V + h) not in w['start_extra'])), [1])))
# ---- register classes other than helpers: a data or target register has #433's own start frame and adapter; a helper-style entrance (start_extra: residual wrapper,
# spectators, bank footprint) is defined for helper registers only
expect_fail('helper-style entrance given to a data register', mut(lambda w: w['start_extra'].__setitem__('3', [1, 2][:1])))
expect_fail('helper-style entrance given to a target register', mut(lambda w: w['start_extra'].__setitem__(str(V + 3), [1])))
expect_fail('target level forgotten', mut(lambda w: w['target_levels'].pop(next(iter(w['target_levels'])))))
# ---- centre chain broken: two entering helpers a, b whose targets share a centre, b's entrance replaced by an incomparable line that is
# otherwise legal (inside b's frames); the word is built without the builder's structural checks, and `profile` (a second checker)
# is used only to find the case: the certifying script must reject it by its own centre-chain assertion.
col = GW.responses(base); first = GW.first_frames(base)
gh = sorted(int(h) for h in sel['gauge']); done = False
for b in gh:
    if done: break
    for x in sorted(GW.span(first[b])):
        if not x or done: continue
        E0 = basis(sel['gauge'][str(b)])
        if basis([x]) == E0 or len(E0) != 1: continue
        for a in gh:
            if a == b or set(col[a]) & set(col[b]): continue
            sel2 = {'gauge': {str(a): sel['gauge'][str(a)], str(b): [x]}}
            w = GW.build(base, sel2, check=False)
            try: GW.profile(w)
            except AssertionError as e:
                if 'served levels must descend' not in str(e): continue
            else: continue
            expect_fail('centre levels not a chain (word built without the builder\'s structural checks)', w, 'centre level outside the previous frame'); done = True; break
assert done, 'no centre-chain control available'
Path(sys.argv[3]).write_text(json.dumps(dict(status='PASS_CERTIFYING_PIPELINE_MUTATION_CONTROLS', controls=out), indent=1) + '\n'); print(len(out), 'controls rejected by the certifying scripts')
