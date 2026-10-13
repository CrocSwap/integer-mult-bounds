#!/usr/bin/env python3
"""End-to-end fixture and mutation tests against the published PR582 package.

  python3 tests/run_tests.py --checkout REPO_AT_PR582 --work NEW_DIR \
      --source multicold=DIR --source structural_gain=DIR --source larger_gain=DIR --source joint_prefix=DIR

REPO_AT_PR582 is a checkout of PR582 (commit 747ec97, research/complex-571-free4f). The run takes about half an hour
on three cores: two full replays (generate and strict verify) and four short mutation runs.

fixture   Start from examples/pr582/WITNESS.json alone (inputs: pinned sources, geometry, typed build chains,
          PLAN/OWNERS by hash). `spec.py generate` builds every provider word from the pinned sources and writes
          EXPECTED.json. That must equal the expected values of PR582's published spec. `spec.py check` must pass,
          and a strict `verify.py` run from scratch must reproduce kappa 0.001601486955392486 exactly.
mutations Each changes one value and must make verify.py FAIL at the named check: an expected profile count, a
          dispatch entry, an owner role (OWNERS re-pinned) and a kernel coefficient (recipe re-pinned).
"""
import argparse, copy, gzip, hashlib, json, shutil, subprocess, sys
from fractions import Fraction
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1]
EXAMPLE = TOOL / 'examples/pr582/WITNESS.json'
KAPPA = '0.001601486955392486'
results = []


def read(p): return json.loads(Path(p).read_bytes())


def write(p, x): Path(p).write_text(json.dumps(x, indent=1) + '\n', newline='\n')


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def report(name, ok, detail=''):
    results.append(dict(test=name, ok=ok, detail=detail))
    print('%s %s %s' % ('PASS' if ok else 'FAIL', name, detail), flush=True)


def tool(script, *args, log):
    with open(log, 'w') as f:
        code = subprocess.call([sys.executable, '-B', str(TOOL / script), *map(str, args)], stdout=f, stderr=subprocess.STDOUT)
    return code, Path(log).read_text()


def published_expected(spec):
    """PR582's single SPEC.json mapped onto EXPECTED.json (without witness_sha256). The one deliberate difference:
    SCALAR-FRAME-AUDIT.json records seconds, was never compared, and is no longer listed."""
    build = {}
    for pid, d in spec['build']['providers'].items():
        steps = [{k: s[k] for k in ('input_content_sha256', 'output_content_sha256', 'omission_controls', 'rank5_controls', 'joint_negative_controls') if k in s}
                 for s in d['steps']]
        build[pid] = dict(base_content_sha256=d['base']['content_sha256'], steps=steps, word_content_sha256=d['word_content_sha256'])
    providers = copy.deepcopy(spec['providers'])
    for p in providers.values():
        p['artifacts'].pop('SCALAR-FRAME-AUDIT.json')
    glob = {k: v for k, v in spec['expected'].items() if k != 'gain_baseline_kappa'}
    return dict(schema='witness-expected/1', build=build, providers=providers, **{'global': glob})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--checkout', type=Path, required=True, help='repository checkout at PR582')
    ap.add_argument('--work', type=Path, required=True, help='new directory for all test outputs')
    ap.add_argument('--source', action='append', required=True, metavar='NAME=DIR')
    ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    pkg = (a.checkout / 'research/complex-571-free4f').resolve()
    W = a.work.resolve()
    W.mkdir(parents=True)
    src = [x for s in a.source for x in ('--source', s)]
    published = read(pkg / 'data/SPEC.json')

    # fixture: WITNESS.json alone -> build everything -> EXPECTED.json
    out = W / 'generated'
    code, log = tool('spec.py', 'generate', '--package', pkg, '--witness', EXAMPLE, '--work', W / 'generate', '--out-dir', out,
                     '--jobs', a.jobs, *src, log=W / 'generate.log')
    if code:
        report('fixture: spec.py generate from WITNESS.json alone', False, log[-3000:])
        return finish(W)
    report('fixture: generate leaves the declarative WITNESS.json unchanged', read(out / 'WITNESS.json') == read(EXAMPLE))
    expected = read(out / 'EXPECTED.json')
    want = published_expected(published)
    differ = sorted(k for k in want if expected.get(k) != want[k])
    report('fixture: generated EXPECTED.json = published expected values', not differ and expected['witness_sha256'] == sha(out / 'WITNESS.json'),
           'differs: %s' % differ if differ else '')

    code, log = tool('spec.py', 'check', '--package', pkg, '--witness', out / 'WITNESS.json', '--expected', out / 'EXPECTED.json', *src, log=W / 'check.log')
    report('fixture: spec.py check', code == 0 and 'CHECK OK' in log, log.strip().splitlines()[-1] if log.strip() else '')

    strict = W / 'strict'
    code, log = tool('verify.py', '--package', pkg, '--witness', out / 'WITNESS.json', '--expected', out / 'EXPECTED.json', '--work', strict,
                     '--jobs', a.jobs, *src, log=W / 'strict.log')
    kappa = read(strict / 'RESULT.json')['kappa_decimal'] if code == 0 else None
    report('fixture: strict verify from scratch reproduces kappa', code == 0 and kappa == KAPPA and Fraction(kappa) == Fraction(KAPPA), 'kappa %s' % kappa)
    if code:
        return finish(W)

    # mutations reuse the strict run's frozen558 replay and localized providers; every build step still reruns
    reuse = ['--reuse-baseline', strict / 'baseline558']
    for pid in read(out / 'WITNESS.json')['build']['providers']:
        reuse += ['--reuse-local', '%s=%s' % (pid, strict / (pid + '-local'))]

    def mutant(name, marker, mutate):
        """mutate(witness, expected, package_dir or None) edits copies; a package copy holds data/ without its MANIFEST."""
        d = W / ('mutant-' + name)
        p = d / 'package'
        shutil.copytree(pkg / 'data', p / 'data')
        w, e = read(out / 'WITNESS.json'), read(out / 'EXPECTED.json')
        mutate(w, e, p)
        write(d / 'WITNESS.json', w)
        e['witness_sha256'] = sha(d / 'WITNESS.json')
        write(d / 'EXPECTED.json', e)
        code, log = tool('verify.py', '--package', p, '--witness', d / 'WITNESS.json', '--expected', d / 'EXPECTED.json', '--work', d / 'run',
                         '--jobs', a.jobs, *src, *reuse, log=d / 'verify.log')
        report('mutation must fail: ' + name, code != 0 and marker in log, 'exit %d; expected %r in %s' % (code, marker, d / 'verify.log'))

    def profile(w, e, p):
        k = sorted(e['global']['global_profile'])[0]
        e['global']['global_profile'][k] += 1
    mutant('profile-count', 'SPEC MISMATCH global.global_profile', profile)

    def dispatch(w, e, p):
        w['dispatch'][0][2] = sorted(set(w['build']['providers']) - {w['dispatch'][0][2]})[0]
    mutant('dispatch-entry', 'PLAN dispatch differs from witness dispatch', dispatch)

    def owner(w, e, p):
        f = p / 'data/OWNERS.json.gz'
        roles = json.loads(gzip.decompress(f.read_bytes()))
        roles[0]['family'] += 1
        f.write_bytes(gzip.compress(json.dumps(roles, separators=(',', ':')).encode(), mtime=0))
        w['data']['owners_sha256'] = sha(f)
    mutant('owner-role', 'emit-controller failed', owner)

    def kernel(w, e, p):
        step = next(s for s in w['build']['providers']['ck']['steps'] if s['type'] == 'greedy_kernels')
        f = p / step['recipe'].split(':', 1)[1]
        r = read(f)
        gate = r['kernels'][0]['gates'][0]
        gate['coefficient'] = str(-Fraction(gate['coefficient']))
        write(f, r)
        step['recipe_sha256'] = sha(f)
    mutant('kernel-coefficient', 'ck-step0-greedy_kernels-construction failed', kernel)
    return finish(W)


def finish(W):
    write(W / 'TEST-RESULTS.json', results)
    print('%d/%d passed' % (sum(r['ok'] for r in results), len(results)))
    sys.exit(0 if all(r['ok'] for r in results) else 1)


if __name__ == '__main__':
    main()
