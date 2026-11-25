"""Release proof for the T74 exact-fill package: runs this package's own verify.py unchanged.

Completed, hash-checked native replays of the two (PR1297, byte-unchanged) provider words are reused from
--native-cache DIR/<sha256 of word file>/ when present (verify.py re-checks word binding and stage names);
otherwise verify.py runs fresh native replays. Writes WORK/RELEASE-RECEIPT.json.
Usage: python -B verify_release.py --main REPO --work NEW [--native-cache DIR] [--jobs N]
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
    ap.add_argument('--native-cache', type=Path)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Full proof requires assertions enabled')
    work = a.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    msha = digest(PACKAGE / 'MANIFEST.json')
    t = time.monotonic()
    opts = []
    reused = {}
    if a.native_cache:
        for key, name in (('base', 'gauge44-word'), ('extra', 'extra-word')):
            entry = a.native_cache.resolve() / digest(PACKAGE / 'vendor/pr1297' / (name + '.json.gz'))
            if (entry / 'CACHE.json').is_file() and (entry / 'local/FULL-WORD.json.gz').is_file() and (entry / 'STEPS.json').is_file():
                opts += ['--%s-native-from' % key, str(entry)]
                reused[key] = entry.name
    with (work / 'verify.log').open('w', encoding='utf-8') as out:
        r = subprocess.run([sys.executable, '-B', str(PACKAGE / 'verify.py'), '--work', str(work / 'verify')] + opts,
                           stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
    if r.returncode:
        lines = (work / 'verify.log').read_text(encoding='utf-8', errors='replace').strip().splitlines()
        raise SystemExit(f'verify failed rc={r.returncode}: {lines[-1] if lines else ""}')
    res = json.loads((work / 'verify/RESULT.json').read_text(encoding='utf-8'))
    claim = json.loads((PACKAGE / 'CLAIM.json').read_text(encoding='utf-8'))
    if not res['status'].startswith('PASS_'):
        raise SystemExit('package verify status ' + res['status'])
    if Fraction(res['kappa_decimal']) != Fraction(claim['kappa_decimal']):
        raise SystemExit(f"verified kappa {res['kappa_decimal']} != CLAIM {claim['kappa_decimal']}")
    if digest(PACKAGE / 'MANIFEST.json') != msha:
        raise SystemExit('Package manifest changed during verification')
    proof = ("The package's own unchanged `verify.py` (retained PR1297 provider and parent admission, owner reconstruction, "
             "parent lift, strict T74 admission with the configured outer witness and kappa grid, geometry controls): "
             f"`{res['status']} {res['kappa_decimal']}`; native reuse {reused or 'none (fresh replays)'}")
    (work / 'RELEASE-RECEIPT.json').write_text(json.dumps(dict(
        status='PASS_RELEASE', kappa_decimal=res['kappa_decimal'], manifest_sha256=msha, proof=proof,
        seconds=round(time.monotonic() - t, 2)), indent=2) + '\n', encoding='utf-8')
    print('PASS_RELEASE', res['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
