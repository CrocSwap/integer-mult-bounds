"""Chain with rebinding: new cohort lead -> rebound descent -> rebound plateau -> rebound target-prefix -> seven native checkers -> sandwich (k=126) + checks.
usage: chain_swap.py PKG LEAD_SRC X BIN W269WORD SEL273 OLD_PRE_DESCENT OLD_POST_DESCENT P270 OUT"""
import json, sys, subprocess, shutil, hashlib, time
from pathlib import Path
sys.dont_write_bytecode = True
PKG, LEADSRC, X, BIN, W269, SEL273, OLDPRE, OLDPOST, P270, W = map(Path, sys.argv[1:11]); PY = sys.executable; T0 = time.time(); tm = {}
HERE = Path(__file__).resolve().parent; SHIM = sys.argv[11] if len(sys.argv) > 11 else None
if W.exists(): shutil.rmtree(W)
W.mkdir(parents=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(label, cmd, cwd=None):
    t = time.time(); log = W / (label + '.log')
    with log.open('w') as lf: r = subprocess.run([str(c) for c in cmd], stdout=lf, stderr=subprocess.STDOUT, cwd=cwd or W)
    tm[label] = round(time.time() - t, 1); print(f'{label}: exit {r.returncode} ({tm[label]}s)', flush=True)
    if r.returncode: print(log.read_text()[-3000:]); raise SystemExit(label + ' FAILED')
lead = W / 'lead'; shutil.copytree(LEADSRC, lead)
sys.path.insert(0, str(P270)); from rebind_descent import rebind
al = rebind(OLDPRE, lead / 'COHORT249-RECORDS.bin', PKG / 'inputs/descent-selection.json', W / 'descent-selection.json')
print('rebind descent:', al['status'], al['events_compared'], flush=True)
shutil.copy(W / 'descent-selection.json', lead / 'descent-selection.json'); (lead / 'DESCENT-REBIND-EVIDENCE.json').write_text(json.dumps(al, indent=2) + '\n')
run('descent', [PY, '-B', PKG / 'code/descent_retiming.py', X, lead, lead / 'descent-selection.json'])
print('post-descent sha', sha(lead / 'COHORT249-RECORDS.bin'), json.load((lead / 'DESCENT-RETIMING.json').open())['local_histogram_delta'], flush=True)
run('rebind-plateaus', [PY, '-B', P270 / 'rebind_plateaus.py', OLDPOST, PKG / 'inputs/plateau-selection.json', lead / 'COHORT249-RECORDS.bin', W / 'plateau-selection.json'])
plateau = W / 'plateau'
run('plateau', [PY, '-B', PKG / 'code/plateau_retiming.py', X, lead, W / 'plateau-selection.json', plateau], cwd=PKG / 'code')
run('plateau-spans', [PY, '-B', PKG / 'code/verify_plateau_spans.py', X, plateau, plateau / 'PLATEAU-RETIMING.json'], cwd=PKG / 'code')
print('post-plateau sha', sha(plateau / 'COHORT249-RECORDS.bin'), flush=True)
bound = plateau / 'target-selection.json'
run('rebind-target', [PY, '-B', HERE / 'rebind_target.py', W269, SEL273, plateau / 'COHORT249-RECORDS.bin', bound])
run('target-prefix', [PY, '-B', PKG / 'code/target_prefix.py', X, plateau, bound])
print('post-target sha', sha(plateau / 'COHORT249-RECORDS.bin'), json.load((plateau / 'TARGET-PREFIX.json').open())['local_histogram_delta'], flush=True)
run('frame-tables', [PY, '-B', PKG / 'code/verify_frame_tables.py', X, plateau, '--output', plateau / 'FRAME-TABLE-AUDIT.json'], cwd=PKG / 'code')
bank = W / 'bank'; bank.mkdir()
run('c1-legality', [BIN / 'cohort-legality-independent', X, plateau, plateau / 'INDEPENDENT-LEGALITY.json'])
run('c2-prefix', [BIN / 'cohort-prefix-independent', X, plateau, plateau / 'INDEPENDENT-PREFIX.json'])
run('c3-bank', [BIN / 'cohort-bank-review', X, plateau / 'COHORT249-INITIAL.json', plateau / 'COHORT249-FRAMES.json', bank, 'actual_multicut'])
run('c4-five-stage', [BIN / 'cohort-five-stage-columns', plateau / 'COHORT249-RECORDS.bin', plateau / 'COHORT-FIVE-STAGE-COLUMNS.json'])
run('c5-price', [BIN / 'cohort-price', plateau / 'COHORT249-REPLAY.json', plateau / 'COHORT-EXACT-PRICE.json'])
run('c6-finite', [BIN / 'cohort-finite-invoice', plateau / 'COHORT249-RECORDS.bin', plateau / 'COHORT-EXACT-PRICE.json', bank / 'BANK-REVIEW.json', plateau / 'COHORT-FIVE-STAGE-COLUMNS.json', plateau / 'COHORT-FINITE-INVOICE.json'])
cc = json.load((plateau / 'COHORT-EXACT-PRICE.json').open())['cohort_candidate']
print('NATIVE', json.dumps(dict(kappa=cc['kappa'], kappa_decimal=cc['kappa_decimal'], stock=cc['stock'], rank_mass=cc['rank_mass'], deficit=cc['deficit'], word_sha=sha(plateau / 'COHORT249-RECORDS.bin'))), flush=True)
# sandwiches: rescan, maximal set with k = 0 mod 3
run('scan-sandwich', [PY, '-B', HERE / 'scan_sandwich.py', X, plateau, W / 'scan-sandwich.json'])
scan = json.load((W / 'scan-sandwich.json').open()); helpers = sorted(c['helper'] for c in scan['chosen']); k = len(helpers) - len(helpers) % 3; helpers = helpers[:k]
sel = dict(status='FROZEN_CLEANUP_SANDWICH_HELPERS', input_record_sha256=sha(plateau / 'COHORT249-RECORDS.bin'), helpers=helpers, expected_local_histogram_delta={'1': 2*k, '20': k, '21': -2*k},
           scanned_sandwich_helpers=len(scan['chosen']), provenance='Helpers with exactly the three-gate cleanup sandwich t += a; a += b; t += a after the first kernel cut, rescanned on this package word after the target-prefix stage (PR271 mechanism, evmckinney9); the largest subset with k = 0 mod 3 (each helper-replica frees 20 bank width units, 800k in total, which must tile width-120 banks), taken in helper-id order. Each joint cut frame of (a, b) is four-dimensional and nondegenerate for 9I - J.')
(PKG / 'inputs/sandwich-selection.json').write_text(json.dumps(sel, indent=1) + '\n'); print('sandwich helpers', len(scan['chosen']), '-> k', k, flush=True)
run('sandwich', [PY, '-B', PKG / 'code/cleanup_sandwich.py', X, plateau, PKG / 'inputs/sandwich-selection.json', plateau / 'sandwich'])
run('sandwich-verify', [PY, '-B', HERE / 'sandwich_verify.py', PKG, X, plateau / 'sandwich', bank / 'BANK-REVIEW.json', BIN, W / 'sandwich-verify', plateau / 'COHORT-EXACT-PRICE.json', 'clang++'] + ([SHIM] if SHIM else []))
print((W / 'sandwich-verify.log').read_text()[-900:]); print('timings', tm, 'total', round(time.time() - T0, 1))
