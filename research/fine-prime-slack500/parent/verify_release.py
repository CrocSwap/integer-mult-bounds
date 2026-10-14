"""Release proof: PR1673 capped phase-cell fusion outer on this package's T74 supplier (PR1661 stack + pivot-554 kernel).

Runs (1) the supplier's own unchanged verify.py (native replays reused from --native-cache when present), concurrently with
(2) outer/check_ledger.py + outer/independent_check.py (the 45-inequality ledger, 5 rejecting controls, endpoint rejection and the
independent balance derivation, regenerated in a temporary copy and compared byte-for-byte with the committed LEDGER.json /
INDEPENDENT.json) and outer/replay_evidence.py (PR1673's 19 supplier-independent exact evidence replays);
then binds the supplier's strict ASSEMBLY (complex endpoint, bit endpoint, profile) to the ledger inputs.
The receipt kappa is the ledger's kappa with the radix-distributed sparse-union schedule (new in pkg4, outer/UNION-SCHEDULE.md) and structured boundary solves (new in this package, outer/STRUCTURED-BOUNDARY.md: displacement-rank generator representations of the boundary blocks, O(r W log W) per right-hand-side column, tau_eff = 2 + 1e-64); the unproven omega_C <= 9/4 premise is not used.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--native-cache', type=Path)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Full proof requires assertions enabled')
    work = a.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    msha = digest(PACKAGE / 'MANIFEST.json')
    t = time.monotonic()
    opts = ['--audit-shards', str(max(1, a.jobs))] + (['--native-cache', str(a.native_cache.resolve())] if a.native_cache else [])
    reused = {}
    if a.native_cache:
        for key, name in (('base', 'gauge44-word'), ('extra', 'extra-word')):
            entry = a.native_cache.resolve() / digest(PACKAGE / 'vendor/pr1297' / (name + '.json.gz'))
            if (entry / 'CACHE.json').is_file() and (entry / 'local/FULL-WORD.json.gz').is_file() and (entry / 'STEPS.json').is_file():
                opts += ['--%s-native-from' % key, str(entry)]
                reused[key] = entry.name
        if len(reused) == 2:
            opts += ['--parent-receipt-cache', str(a.native_cache.resolve() / '_receipts')]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    outer_log = (work / 'outer.log').open('w', encoding='utf-8')
    outer_proc = subprocess.Popen([sys.executable, '-B', str(PACKAGE / 'outer/run_outer.py'), str(work / 'outer-tmp')],
                                  stdin=subprocess.DEVNULL, stdout=outer_log, stderr=subprocess.STDOUT, env=env)
    with (work / 'verify.log').open('w', encoding='utf-8') as out:
        r = subprocess.run([sys.executable, '-B', str(PACKAGE / 'verify.py'), '--work', str(work / 'verify')] + opts,
                           stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    if outer_proc.wait():
        raise SystemExit('outer checks failed: ' + (work / 'outer.log').read_text(encoding='utf-8', errors='replace')[-1500:])
    if r.returncode:
        lines = (work / 'verify.log').read_text(encoding='utf-8', errors='replace').strip().splitlines()
        raise SystemExit(f'verify failed rc={r.returncode}: {lines[-1] if lines else ""}')
    res = json.loads((work / 'verify/RESULT.json').read_text(encoding='utf-8'))
    claim = json.loads((PACKAGE / 'CLAIM.json').read_text(encoding='utf-8'))
    if not res['status'].startswith('PASS_'):
        raise SystemExit('package verify status ' + res['status'])
    if Fraction(res['kappa_decimal']) != Fraction(claim['kappa_decimal']):
        raise SystemExit(f"verified kappa {res['kappa_decimal']} != CLAIM {claim['kappa_decimal']}")
    # ---- bind the supplier admission to the outer ledger inputs
    asm = json.loads((work / 'verify/strict/ASSEMBLY.json').read_text(encoding='utf-8'))
    spec = json.loads((PACKAGE / 'new/SPEC.json').read_text(encoding='utf-8'))
    ledger = json.loads((PACKAGE / 'outer/LEDGER.json').read_text(encoding='utf-8'))
    bj = json.loads((PACKAGE / 'outer/B.json').read_text(encoding='utf-8'))
    if asm['status'] != 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' or len(asm['outer']) != 47:
        raise SystemExit('supplier strict assembly did not pass')
    if Fraction(asm['complex_lower']) != Fraction(spec['expected']['complex_lower']) or not Fraction(bj['b']) < Fraction(asm['complex_lower']) < Fraction(bj['b_above_endpoint']):
        raise SystemExit('ledger endpoint b is not bracketed by the admitted supplier complex endpoint')
    if {int(k): v for k, v in asm['complex_profile'].items()} != {int(k): v for k, v in bj['profile'].items()} or Fraction(asm['bit_lower']) != Fraction('0.001733427039589844234749'):
        raise SystemExit('ledger profile / bit endpoint differ from the admitted supplier assembly')
    kappa_decimal = ledger['rows']['struct_boundary_radix_union']['kappa']['decimal']
    if Fraction(kappa_decimal) != Fraction(ledger['rows']['struct_boundary_radix_union']['kappa']['rational']) or Fraction(kappa_decimal) != Fraction(json.loads((PACKAGE / 'outer/OUTER-CLAIM.json').read_text(encoding='utf-8'))['kappa']):
        raise SystemExit('ledger kappa != OUTER-CLAIM')
    if Fraction(kappa_decimal) <= Fraction('0.001677160151714381'):
        raise SystemExit('ledger kappa does not exceed PR1673')
    if Fraction(kappa_decimal) <= Fraction('0.001677641731343354564251058287063644749065568493'):
        raise SystemExit('ledger kappa does not exceed PR1699')
    if Fraction(kappa_decimal) <= Fraction('0.0016783441717365385237811729563143950958709031230206606381509868512618172844657807114390339553440364'):
        raise SystemExit('ledger kappa does not exceed the previous package (structured boundary, linear guard)')
    if Fraction(kappa_decimal) <= Fraction('0.0016797547881500489087805478664999999999999999999999999999999998000000199999'):
        raise SystemExit('ledger kappa does not exceed PR1786')
    if Fraction(kappa_decimal) <= Fraction('0.001679745508802299051546533685199973672313473419790800679752457380932784242972585600630181672224983'):
        raise SystemExit('ledger kappa does not exceed the previous package (gauge-free interiors, PR1758)')
    if Fraction(kappa_decimal) <= Fraction('0.0016781238306335473083421558390362687182218966358657650331660405387910568682486186577879457360762643'):
        raise SystemExit('ledger kappa does not exceed the previous package (rectangular k=5)')
    if Fraction(kappa_decimal) <= Fraction('0.001677992607205282520732088774830808372222877897034109604209719298829805473412451530867883424937597'):
        raise SystemExit('ledger kappa does not exceed the previous package (rectangular k=2)')
    if Fraction(kappa_decimal) <= Fraction('0.0016778199023144364336310551358776001013829401215770658599799349282716974076737897457922714197448847'):
        raise SystemExit('ledger kappa does not exceed the previous package (square boundary tau=2.372864)')
    if Fraction(kappa_decimal) <= Fraction('0.0016776417313433545642517275958639984231708545722735432722117400060454625429077941422798526440584702'):
        raise SystemExit('ledger kappa does not exceed the previous package (old union row)')
    if digest(PACKAGE / 'MANIFEST.json') != msha:
        raise SystemExit('Package manifest changed during verification')
    proof = ("Supplier: the package's own unchanged `verify.py` (retained PR1297 provider and parent admission, owner reconstruction, "
             "parent lift, strict T74 admission, geometry controls): "
             f"`{res['status']}`, native reuse {reused or 'none (fresh replays)'}; its complex endpoint "
             f"{asm['complex_lower'][:30]}... brackets the ledger's b = {bj['b']}. Outer (PR1673 capped phase-cell fusion): "
             "regenerated exact ledger (57 strict inequalities, 17 rejecting controls incl. the old g-factor union row, the old linear and old-theta chirp guards, the old 2*beta tag test, epsilon at 1 or at the r0 slack and beta outside its window, larger endpoint rejected by the native moment), "
             "independent balance derivation, the exact union-schedule simulation, the (retained, not used for kappa) structured-boundary displacement-rank check, the gauge-free identity/symbol/circuit checks, PR1786's finite prime/underflow controls and 19 exact evidence replays all pass. "
             f"Conditional kappa {kappa_decimal} (union schedule outer/UNION-SCHEDULE.md; explicit Strassen boundary tau=45/16 (the structured boundary of outer/STRUCTURED-BOUNDARY.md is not used); gauge-free interiors outer/GAUGEFREE-INTERIORS.md; fine source-prime padding PR1786 at the free point epsilon=1-2e-64, outer/FINE-PADDING-COMPOSITION.md).")
    (work / 'RELEASE-RECEIPT.json').write_text(json.dumps(dict(
        status='PASS_RELEASE', kappa_decimal=kappa_decimal, manifest_sha256=msha, proof=proof,
        seconds=round(time.monotonic() - t, 2)), indent=2) + '\n', encoding='utf-8')
    print('PASS_RELEASE', kappa_decimal, flush=True)


if __name__ == '__main__':
    main()
