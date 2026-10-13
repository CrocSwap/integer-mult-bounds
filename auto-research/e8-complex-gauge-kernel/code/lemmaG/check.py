"""Independent check stage for Lemma G (PROOF.md §2) on the emitted artefacts of one variant.  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: check.py BASE VARIANT OUTDIR [--mutants]
BASE/VARIANT/{split-centres,hosted} is a run_variant.py work directory (BASE = the output directory of verify.py).  The scripts of this directory import no
script of the package and none of PR #433/#442 except the vendored `clifford_exact`, which is used only as the DEFINITION of the label operators T_F and of the port
gate C_q (every executed transition, data adapter and wrapper is decoded from its serialized recipe).
  gd.selftest        the exact Gaussian-dyadic applier agrees with the vendored state-vector routine on 19 operators
  run_labels.py      label / scalar / accounting checker on both orientations (clauses G0-G4, S, ACC), the 72 calls' program digests
  lg_instances.py    I-tr, I-comp, I-centre, I-helper: exact operator identities of every Lemma G instance on all 512 basis columns   (not for the anchor)
  lg_e2e.py          the complete emitted program end to end, both orientations, against the transform computed from definitions
  lg_mutants.py      the 14 necessity controls (--mutants; headline word only)
Writes LEMMA-G-CHECK.json (deterministic content only) into OUTDIR; any failure raises."""
import json, os, subprocess, sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
base, name, outd = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve(); mut = '--mutants' in sys.argv[4:]
outd.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, LG_BASE=str(base), PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None)
def run(script, *args):
    log = outd / (Path(script).stem + '-' + name + '.log')
    with log.open('w') as f: q = subprocess.run([sys.executable, '-B', str(HERE / script), *args], cwd=outd, env=env, stdout=f, stderr=subprocess.STDOUT)
    if q.returncode: raise RuntimeError((script, name, log.read_text()[-2000:]))
sys.path.insert(0, str(HERE)); import lg_phys as P; from gd import selftest
S = dict(variant=name, selftest_operators=selftest(P.ce))
run('run_labels.py', name)
L = json.loads((outd / ('LABELS-' + name + '.json')).read_text())[name]
keys = ('n_label_violations', 'scalar_violations', 'events', 'sha256', 'compensation_gates', 'kernel_updates', 'entering', 'entrance_rank', 'local_mass', 'paid_profile')
S['labels'] = {o: {k: L[o][k] for k in keys} for o in ('forward', 'backward')}; S['calls'] = {k: L['calls'][k] for k in ('n', 'ok', 'orient')}; S['inputs'] = L['inputs']
assert all(S['labels'][o]['n_label_violations'] == 0 and S['labels'][o]['scalar_violations'] == [] for o in S['labels']) and S['calls']['ok'], 'label / scalar checker'
if name != 'anchor':
    run('lg_instances.py', name)
    I = json.loads((outd / ('INSTANCES-' + name + '.json')).read_text())
    S['instances'] = {'I-tr': dict(transitions=I['I-tr']['transitions'], failures=len(I['I-tr']['failures'])),
                      'I-comp': dict(compensation_gates=I['I-comp']['compensation_gates'], targets=I['I-comp']['targets'], entering_helpers_compensating=I['I-comp']['entering_helpers_compensating'],
                                     input_registers=I['I-comp']['input_registers'], failures=len(I['I-comp']['failures'])),
                      'I-centre': dict(centres=I['I-centre']['centres'], chains=sorted(Counter('-'.join(map(str, d['path_dims'])) for d in I['I-centre']['detail']).items()), failures=len(I['I-centre']['failures'])),
                      'I-helper': dict(entering_helpers=I['I-helper']['entering_helpers'], widths=dict(sorted(I['I-helper']['widths'].items())), failures=len(I['I-helper']['failures']))}
    assert all(x['failures'] == 0 for x in S['instances'].values()), 'instance identities'
run('lg_e2e.py', name)
E = json.loads((outd / ('E2E-' + name + '.json')).read_text())
S['end_to_end'] = dict(status=E['status'], columns=E['columns'], kinds=dict(sorted(E['kinds'].items())), dense=E['dense'], seed=E['seed'], failures=len(E['failures']))
assert E['status'] == 'PASS' and not E['failures'], 'end-to-end identity'
if mut:
    run('lg_mutants.py')
    M = json.loads((outd / 'MUTANTS.json').read_text())
    S['necessity_mutants'] = [dict(mutant=m['mutant'], rejected=m['rejected'], checker_flags=m['checker_flags'], physics=m['physics']) for m in M]
    assert len(M) == 14 and all(m['rejected'] for m in M), 'necessity controls'
(outd / 'LEMMA-G-CHECK.json').write_text(json.dumps(S, indent=1, sort_keys=True) + '\n'); print(name, 'PASS Lemma G independent checks', flush=True)
