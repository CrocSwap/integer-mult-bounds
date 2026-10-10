"""Fill the swap package from chain_swap outputs. usage: finalize_swap.py PKG CHAIN_DIR"""
import json, hashlib, shutil, sys
from fractions import Fraction
from pathlib import Path
PKG, RUN = map(Path, sys.argv[1:3]); lead = RUN / 'lead'; plateau = RUN / 'plateau'; sand = plateau / 'sandwich'; SV = RUN / 'sandwich-verify'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
exp = PKG / 'expected'
for name, src in {'COHORT249-REPLAY.json': plateau, 'INDEPENDENT-LEGALITY.json': plateau, 'INDEPENDENT-PREFIX.json': plateau, 'COHORT-BANK-REVIEW.json': RUN / 'bank', 'COHORT-FIVE-STAGE-COLUMNS.json': plateau,
                  'COHORT-EXACT-PRICE.json': plateau, 'COHORT-FINITE-INVOICE.json': plateau, 'DESCENT-RETIMING.json': plateau, 'PLATEAU-RETIMING.json': plateau, 'PLATEAU-SOURCE-SPANS.json': plateau, 'FRAME-TABLE-AUDIT.json': plateau, 'TARGET-PREFIX.json': plateau}.items():
    shutil.copy(src / ('BANK-REVIEW.json' if name == 'COHORT-BANK-REVIEW.json' else name), exp / name)
exps = PKG / 'expected-sandwich'
for name, src in {'CLEANUP-SANDWICH.json': sand, 'COHORT249-REPLAY.json': sand, 'INDEPENDENT-LEGALITY.json': SV, 'INDEPENDENT-PREFIX.json': SV, 'COHORT-FIVE-STAGE-COLUMNS.json': SV, 'SANDWICH-BANK-INVOICE.json': SV, 'COHORT-EXACT-PRICE.json': SV, 'COHORT-FINITE-INVOICE.json': SV}.items():
    shutil.copy(src / name, exps / name)
shutil.copy(plateau / 'target-selection.json', PKG / 'inputs/target-selection.json')
shutil.copy(RUN / 'descent-selection.json', PKG / 'inputs/descent-selection.json'); shutil.copy(RUN / 'plateau-selection.json', PKG / 'inputs/plateau-selection.json')
res = load(PKG / 'RESULT.json'); native = load(plateau / 'COHORT-EXACT-PRICE.json')['cohort_candidate']; sw = load(SV / 'COHORT-EXACT-PRICE.json')['cohort_candidate']
tp = load(plateau / 'TARGET-PREFIX.json'); cs = load(sand / 'CLEANUP-SANDWICH.json'); rep = load(lead / 'COHORT249-REPLAY.json')
def decimal(k):
    x = Fraction(k); q, r = divmod(x.numerator * 10**18, x.denominator); assert r == 0; s = str(q).rjust(19, '0'); return s[:-18] + '.' + s[-18:]
res.update(previous_delivery_kappa=res['kappa_decimal'], cohort_record_sha256=sha(lead / 'COHORT249-PRE-DESCENT-RECORDS.bin'), descent_record_sha256=sha(lead / 'COHORT249-RECORDS.bin'),
           plateau_record_sha256=sha(plateau / 'COHORT249-PRE-TARGET-RECORDS.bin'), new_record_sha256=sha(plateau / 'COHORT249-RECORDS.bin'),
           kappa_native_seven_checkers=native['kappa'], kappa_native_decimal=decimal(native['kappa']), kappa=sw['kappa'], kappa_decimal=decimal(sw['kappa']),
           pivots=rep['new_gauges'], entrance_rank=rep['new_entrance_rank'], pivot_role_swapped_pair_families=83,
           target_prefix_groups=tp['selected_groups'], target_prefix_deleted_reads=tp['deleted_prefix_adds'], target_prefix_setup_restore_additions=tp['inserted_setup_restore_adds'],
           sandwich_record_sha256=sha(sand / 'COHORT249-RECORDS.bin'), sandwich_helpers_retired=cs['helpers_retired'], sandwich_helpers_scanned=load(PKG / 'inputs/sandwich-selection.json')['scanned_sandwich_helpers'],
           sandwich_normalized_stock=sw['stock'], native_normalized_stock=native['stock'])
(PKG / 'RESULT.json').write_text(json.dumps(res, indent=2) + '\n')
for p in PKG.rglob('__pycache__'): shutil.rmtree(p)
files = {p.relative_to(PKG).as_posix(): sha(p) for p in sorted(PKG.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json'}
(PKG / 'MANIFEST.json').write_text(json.dumps({'files': files}, indent=2) + '\n')
print(json.dumps({k: res[k] for k in ('kappa', 'kappa_decimal', 'kappa_native_seven_checkers', 'kappa_native_decimal', 'cohort_record_sha256', 'descent_record_sha256', 'plateau_record_sha256', 'new_record_sha256', 'sandwich_record_sha256', 'sandwich_helpers_retired', 'sandwich_helpers_scanned')}, indent=1), 'files', len(files))
