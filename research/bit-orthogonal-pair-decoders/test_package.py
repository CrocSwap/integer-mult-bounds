"""Package tests: both checkers pass, unsafe -O is refused, and mutations are rejected.

Run from the repository root:  python3 -I -B research/bit-orthogonal-pair-decoders/test_package.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MARKER = 'PASS_BIT_ORTHOGONAL_PAIR_DECODERS'


def run(pkg, *flags, script='verify.py'):
    cmd = [sys.executable, '-I', '-B', *flags, str(pkg / script), '--repo', str(REPO)]
    return subprocess.run(cmd, capture_output=True, text=True)


def tampered(edit):
    tmp = Path(tempfile.mkdtemp(prefix='bit-pair-test-'))
    pkg = tmp / HERE.name
    shutil.copytree(HERE, pkg, ignore=shutil.ignore_patterns('__pycache__'))
    edit(pkg)
    return tmp, pkg


def edit_json(path, change):
    data = json.loads(path.read_text(encoding='utf-8'))
    change(data)
    path.write_text(json.dumps(data, indent=1) + '\n', encoding='utf-8')


def swap_two_partners(data):
    pairs = data['pairs']
    pairs[0][1], pairs[1][1] = pairs[1][1], pairs[0][1]


def break_pin(data):
    key = sorted(data['pricing_inputs'])[0]
    data['pricing_inputs'][key] = '0' * 64


def main():
    results = []

    r = run(HERE)
    ok = r.returncode == 0 and r.stdout.strip().splitlines()[-1].startswith(MARKER)
    results.append(('verifier passes', ok, r.stdout[-400:] + r.stderr[-400:]))
    results.append(('changed-reader counterexample is checked',
                    r.returncode == 0 and 'PASS G.reader-basis-scope' in r.stdout,
                    r.stdout[-400:] + r.stderr[-400:]))

    # The pinned moment/outer engines signal their own rejections with assert, so -O would weaken them.
    r = run(HERE, '-O')
    ok = r.returncode != 0 and 'FAIL H.assertions' in r.stdout and MARKER not in r.stdout
    results.append(('verifier refuses -O (pinned engines need assert)', ok, r.stdout[-400:] + r.stderr[-400:]))

    r = run(HERE, script='independent_check.py')
    ok = r.returncode == 0 and r.stdout.strip().splitlines()[-1].startswith('PASS_BIT_PAIR_INDEPENDENT')
    results.append(('independent checker passes', ok, r.stdout[-400:] + r.stderr[-400:]))

    tmp = Path(tempfile.mkdtemp(prefix='bit-pair-test-'))
    try:
        out = tmp / 'RESULTS.json'
        r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'), '--repo', str(REPO), '--out', str(out)],
                           capture_output=True, text=True)
        committed = HERE / 'RESULTS.json'
        ok = r.returncode == 0 and committed.exists() and out.read_bytes() == committed.read_bytes()
        results.append(('RESULTS.json regenerates byte for byte', ok, r.stdout[-200:] + r.stderr[-400:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for name, script, filename, change, needle in [
            ('swapped partners rejected', 'verify.py', 'WITNESS.json', swap_two_partners, 'FAIL D.duality'),
            ('swapped partners rejected independently', 'independent_check.py', 'WITNESS.json', swap_two_partners,
             'FAIL X.dual-identity'),
            ('broken pricing pin rejected', 'verify.py', 'SOURCES.json', break_pin, 'FAIL H.pin')]:
        tmp, pkg = tampered(lambda p: edit_json(p / filename, change))
        try:
            r = run(pkg, script=script)
            ok = r.returncode != 0 and needle in r.stdout
            if needle == 'FAIL H.pin':
                ok &= 'PASS H.bit-gate' not in r.stdout
            results.append((name, ok, r.stdout[-400:] + r.stderr[-400:]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    for name, ok, detail in results:
        print(('PASS ' if ok else 'FAIL ') + name)
        if not ok:
            print(detail)
    if not all(ok for _, ok, _ in results):
        sys.exit(1)
    print('PASS_PACKAGE_TESTS %d' % len(results))


if __name__ == '__main__':
    main()
