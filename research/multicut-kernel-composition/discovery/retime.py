"""Chain: PR259 word (stable_sort) -> #263 descent (baseline 80af) ; our 883 word -> rebound descent -> rebound plateaus -> native checkers."""
import json, sys, subprocess, shutil, hashlib, time, os
from pathlib import Path
sys.dont_write_bytecode = True
S = Path(sys.argv[1]); W = S / sys.argv[3]
if W.exists(): shutil.rmtree(W)
W.mkdir(parents=True)
BIN = S / 'mc851/out-headroom/bin'; X = S / 'mc851/out-headroom/temporal/CURRENT249-EXPORT'
P263 = S / 'pr263/repo/research/multicut-kernel-condensation'; P270 = S / 'round3/r270/research/crosscut-response-pairs'
PY = S / 'build/venv/bin/python'; T0 = time.time(); tm = {}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(label, cmd, cwd=None):
    t = time.time(); log = W / (label + '.log')
    with log.open('w') as lf: r = subprocess.run([str(c) for c in cmd], stdout=lf, stderr=subprocess.STDOUT, cwd=cwd or W)
    tm[label] = round(time.time() - t, 1); print(f'{label}: exit {r.returncode} ({tm[label]}s)', flush=True)
    if r.returncode: print(log.read_text()[-2500:]); raise SystemExit(label + ' FAILED')
# a. baseline chain
base = W / 'base259'; (base / 'lead').mkdir(parents=True)
run('a1-pr259-transform-stable', [BIN / 'cohort-transform', X, S / 'pr259/data/candidates.json', base / 'lead'])
sel263 = json.load((P263 / 'inputs/descent-selection.json').open())
print('pr259 stable-sort word sha', sha(base / 'lead/COHORT249-RECORDS.bin'), 'matches #263 selection input:', sha(base / 'lead/COHORT249-RECORDS.bin') == sel263['input_record_sha256'], flush=True)
run('a2-descent-on-pr259', [PY, '-B', P263 / 'code/descent_retiming.py', X, base / 'lead', P263 / 'inputs/descent-selection.json'])
plat = json.load((P270 / 'inputs/plateau-selection.json').open())
print('post-descent pr259 sha', sha(base / 'lead/COHORT249-RECORDS.bin'), 'matches #270 plateau input:', sha(base / 'lead/COHORT249-RECORDS.bin') == plat['input_sha256'], flush=True)
# b. our word
lead = W / 'lead'; shutil.copytree(Path(sys.argv[2]) / 'lead', lead)
sys.path.insert(0, str(P270)); from rebind_descent import rebind
alignment = rebind(base / 'lead/COHORT249-PRE-DESCENT-RECORDS.bin', lead / 'COHORT249-RECORDS.bin', P263 / 'inputs/descent-selection.json', lead / 'descent-selection.json')
(lead / 'DESCENT-REBIND-EVIDENCE.json').write_text(json.dumps(alignment, indent=2) + '\n'); print('rebind descent:', alignment['status'], alignment['events_compared'], flush=True)
run('b1-descent-on-883', [PY, '-B', P263 / 'code/descent_retiming.py', X, lead, lead / 'descent-selection.json'])
print('883 post-descent sha', sha(lead / 'COHORT249-RECORDS.bin'), json.load((lead / 'DESCENT-RETIMING.json').open())['local_histogram_delta'], flush=True)
bound = W / 'bound-plateau-selection.json'
run('b2-rebind-plateaus', [PY, '-B', P270 / 'rebind_plateaus.py', base / 'lead/COHORT249-RECORDS.bin', P270 / 'inputs/plateau-selection.json', lead / 'COHORT249-RECORDS.bin', bound])
plateau = W / 'plateau'
run('b3-plateau-retiming', [PY, '-B', P270 / 'plateau_retiming.py', X, lead, bound, plateau], cwd=P270)
run('b4-plateau-spans', [PY, '-B', P270 / 'verify_plateau_spans.py', X, plateau, plateau / 'PLATEAU-RETIMING.json'], cwd=P270)
run('b5-frame-tables', [PY, '-B', P270 / 'verify_frame_tables.py', X, plateau, '--output', plateau / 'FRAME-TABLE-AUDIT.json'], cwd=P270)
bank = W / 'bank'; bank.mkdir()
run('c1-legality', [BIN / 'cohort-legality-independent', X, plateau, plateau / 'INDEPENDENT-LEGALITY.json'])
run('c2-prefix', [BIN / 'cohort-prefix-independent', X, plateau, plateau / 'INDEPENDENT-PREFIX.json'])
run('c3-bank', [BIN / 'cohort-bank-review', X, plateau / 'COHORT249-INITIAL.json', plateau / 'COHORT249-FRAMES.json', bank, 'actual_multicut'])
run('c4-five-stage', [BIN / 'cohort-five-stage-columns', plateau / 'COHORT249-RECORDS.bin', plateau / 'COHORT-FIVE-STAGE-COLUMNS.json'])
run('c5-price', [BIN / 'cohort-price', plateau / 'COHORT249-REPLAY.json', plateau / 'COHORT-EXACT-PRICE.json'])
run('c6-finite', [BIN / 'cohort-finite-invoice', plateau / 'COHORT249-RECORDS.bin', plateau / 'COHORT-EXACT-PRICE.json', bank / 'BANK-REVIEW.json', plateau / 'COHORT-FIVE-STAGE-COLUMNS.json', plateau / 'COHORT-FINITE-INVOICE.json'])
cc = json.load((plateau / 'COHORT-EXACT-PRICE.json').open())['cohort_candidate']; rep = json.load((plateau / 'COHORT249-REPLAY.json').open())
print(json.dumps(dict(kappa=cc['kappa'], kappa_decimal=cc['kappa_decimal'], coarse=cc['coarse'], stock=cc['stock'], calls=cc['calls'], rank_mass=cc['rank_mass'], deficit=cc['deficit'], constraints=cc['positive_constraints'], adjacent_rejected=cc['next_kappa_rejected'], word_sha=sha(plateau / 'COHORT249-RECORDS.bin'), records=rep['new_records'], plateau_delta=rep.get('plateau_histogram_delta'), timings=tm, total=round(time.time()-T0, 1)), indent=1))
