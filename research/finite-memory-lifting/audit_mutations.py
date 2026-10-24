"""Private semantic mutations; never edit the source package in place.

Apache-2.0; substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
from exact import G, fingerprint, need, scalar
from certify import certify
from check_certificate import check
from models import compose, difference, prefix_xor, transpose, unit

ROOT = Path(__file__).resolve().parent


def main():
    p = prefix_xor()
    data = difference(compose(transpose(p), p), unit(2)).problem()
    claim = certify(data)
    column = next(j for j in range(data['states']) if any(scalar(r[j]) for r in claim['basis']))
    changed = deepcopy(data)
    changed['right'] = [[int(i == column)] for i in range(data['states'])]
    bad = deepcopy(claim)
    bad['problem_sha256'] = fingerprint(changed)
    try:
        check(changed, bad)
    except ValueError:
        pass
    else:
        raise ValueError('baseline accepted bad dirty return')
    cases = [
        ('reverse-composition', 'models.py',
         "    need(a.d == b.d, 'composition local dimension')",
         "    need(a.d == b.d, 'composition local dimension')\n    a, b = b, a",
         ['verify.py', '--suite', 'core']),
        ('erase-positive-seed', 'certify.py',
         "            visit(rowmul(left[i], transitions[symbol]), i, [symbol])",
         "            visit([G() for _ in range(n)], i, [symbol])",
         ['verify.py', '--suite', 'core']),
        ('erase-source-absolute-phase', 'models.py',
         "        exponent = recipe['phase']",
         "        exponent = 0",
         ['source_control.py']),
        ('drop-dirty-return-check', 'check_certificate.py',
         "            need(not sum((rows[i][k]*right[k][j] for k in range(n)), G()), 'all returned channels')",
         "            need(True, 'all returned channels')",
         ['return_control.py'])]
    results = []
    for name, filename, old, new, args in cases:
        for optimized in (False, True):
            with tempfile.TemporaryDirectory(prefix='finite-memory-mutant-') as folder:
                out = Path(folder)
                for f in ('exact.py', 'certify.py', 'check_certificate.py', 'models.py', 'verify.py',
                          'SOURCE-FIXTURE.json'):
                    (out/f).write_bytes((ROOT/f).read_bytes())
                target = out/filename
                text = target.read_text()
                need(text.count(old) == 1, 'unique mutation site: '+name)
                target.write_text(text.replace(old, new, 1))
                (out/'bad-problem.json').write_text(json.dumps(changed))
                (out/'bad-certificate.json').write_text(json.dumps(bad))
                (out/'return_control.py').write_text(
                    "from exact import load\nfrom check_certificate import check\n"
                    "try:\n    check(load('bad-problem.json'),load('bad-certificate.json'))\n"
                    "except ValueError:\n    pass\n"
                    "else:\n    raise ValueError('mutant accepted false dirty return')\n")
                (out/'source_control.py').write_text(
                    "from exact import load,need\nfrom certify import certify\n"
                    "from models import native_frontend\n"
                    "for row in native_frontend(load('SOURCE-FIXTURE.json')):\n"
                    "    for block in row:\n"
                    "        need(certify(block.problem())['kind']=='all_positive_widths',"
                    " 'mutant changed source endpoint phase')\n")
                command = [sys.executable, '-B', '-X', 'pycache_prefix='+str(out/'no-cache')]
                if optimized:
                    command.append('-O')
                run = subprocess.run(command+args, cwd=out, capture_output=True, text=True, timeout=30,
                                     env={'PATH': ''})
                need(run.returncode != 0 and 'ValueError' in run.stderr, 'semantic mutation survived: '+name)
                results.append({'mutation': name, 'optimized': optimized,
                                'diagnostic': run.stderr.strip().splitlines()[-1]})
    print(json.dumps({'status': 'PASS_FINITE_MEMORY_SEMANTIC_MUTATIONS', 'checks': results},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
