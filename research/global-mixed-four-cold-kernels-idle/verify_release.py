"""Release proof for #1218-style packages (research/global-mixed-x54-fusions lineage).

Runs fast_verify.py: both fresh native replays (edge-parallel, byte-identical phases step)
followed by this package's own verify.py in native-reuse mode (all literal/controls/
construct/strict-global stages unchanged). Writes WORK/RELEASE-RECEIPT.json.
Usage: python -B verify_release.py --main REPO --work NEW [--jobs 4]
"""
import argparse, hashlib, json, subprocess, sys, time
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--native-cache', type=Path, help='optional DIR/<sha256 of word>/ cache of completed, hash-checked native replays; '
                    'cached words skip the fresh native (verify.py still re-checks them), others run fresh and are cached after a full pass. '
                    'Omit for a cold reviewer run.')
    a = ap.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Full proof requires assertions enabled')
    work = a.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    msha = digest(PACKAGE / 'MANIFEST.json')
    t = time.monotonic()
    with (work / 'fast-verify.log').open('w', encoding='utf-8') as out:
        r = subprocess.run([sys.executable, '-B', str(PACKAGE / 'fast_verify.py'), str(PACKAGE), '--work',
                            str(work / 'fast'), '--jobs', str(a.jobs)] + (['--native-cache', str(a.native_cache)] if a.native_cache else []),
                           stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    if r.returncode:
        lines = (work / 'fast-verify.log').read_text(encoding='utf-8', errors='replace').strip().splitlines()
        raise SystemExit(f'fast_verify failed rc={r.returncode}: {lines[-1] if lines else ""}')
    res = json.loads((work / 'fast/verify/RESULT.json').read_text(encoding='utf-8'))
    claim = json.loads((PACKAGE / 'CLAIM.json').read_text(encoding='utf-8'))
    if not res['status'].startswith('PASS_'):
        raise SystemExit('package verify status ' + res['status'])
    if Fraction(res['kappa_decimal']) != Fraction(claim['kappa_decimal']):
        raise SystemExit(f"verified kappa {res['kappa_decimal']} != CLAIM {claim['kappa_decimal']}")
    if digest(PACKAGE / 'MANIFEST.json') != msha:
        raise SystemExit('Package manifest changed during verification')
    proof = ('Fresh native replays of both provider words (phases step edge-parallel, byte-identical output; with --native-cache a word whose hash-checked completed replay is cached reuses it), then the '
             "package's own `verify.py` (literal words, independent local audit, fusion/X54 controls, leaver premise, "
             f"literal construct, strict global admission): `{res['status']} {res['kappa_decimal']}`")
    (work / 'RELEASE-RECEIPT.json').write_text(json.dumps(dict(
        status='PASS_RELEASE', kappa_decimal=res['kappa_decimal'], manifest_sha256=msha, proof=proof,
        seconds=round(time.monotonic() - t, 2)), indent=2) + '\n', encoding='utf-8')
    print('PASS_RELEASE', res['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
