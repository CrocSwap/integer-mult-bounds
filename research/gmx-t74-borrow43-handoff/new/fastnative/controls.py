#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Rejection controls at source, word, emitted recipe and receipt boundaries."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import random

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, need, source_bytes
from compare import compare


def evaluator_check():
    """Finite differential check against this snapshot's original dense algebra.

    Seed2, dimensions1..5, twelve length20 circuits per dimension, every input
    basis column. Covers all five gate kinds, both C signs and adjoints. This
    supplements the predecessor proof; it is not a full formal proof.
    """
    from stage import module
    source_bytes(HERE / 'vendor')
    algebra = module('clifford_exact', HERE / 'vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py')
    tables = module('test_exact_tables', HERE / 'vendor/accelerators/tables.py')
    sparse = module('test_exact_sparse', HERE / 'vendor/accelerators/sparse_state.py')
    rng = random.Random(2)
    columns = 0
    for n in range(1, 6):
        for _ in range(12):
            op = algebra.ident(n)
            for j in range(20):
                if j % 5 == 0:
                    rows = [1 << i for i in range(n)]
                    if n > 1:
                        for _ in range(2 * n):
                            a, b = rng.sample(range(n), 2)
                            rows[a] ^= rows[b]
                    gate = algebra.perm(n, rows)
                elif j % 5 == 1:
                    rows = [0] * n
                    for a in range(n):
                        for b in range(a, n):
                            if rng.randrange(2):
                                rows[a] |= 1 << b
                                rows[b] |= 1 << a
                    alpha = [((rows[i] >> i) & 1) + 2 * rng.randrange(2) for i in range(n)]
                    gate = algebra.diag(n, rows, alpha)
                elif j % 5 == 2:
                    gate = algebra.cgate(n, rng.randrange(1 << n), rng.choice((-1, 1)))
                elif j % 5 == 3:
                    gate = algebra.xgate(n, rng.randrange(1 << n))
                else:
                    gate = algebra.ident(n)
                    gate.circuit.append(('phase', rng.randrange(4)))
                op = op.then(gate)
            for candidate in (op, op.adjoint()):
                for basis in range(1 << n):
                    need(candidate.zero_state(basis) == sparse.zero_state(candidate, tables, basis),
                         'dense/sparse exact state mismatch')
                    columns += 1
    print('PASS_T74_EXACT_STATE_DIFFERENTIAL', columns, 'columns')


def reject(argv, message):
    result = subprocess.run([sys.executable, '-I', '-B', *map(str, argv)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
    text = result.stdout.decode(errors='replace')
    need(result.returncode != 0 and message in text, 'expected rejection: ' + message + '\n' + text[-2000:])


def check(local):
    evaluator_check()
    controls = []
    with tempfile.TemporaryDirectory(prefix='t74-negative-') as temporary:
        root = Path(temporary)
        # Authenticate before loading even the first vendored import. A sentinel
        # would be created if tampered code were executed before rejection.
        for mutation in ('digest', 'extra', 'missing', 'symlink'):
            vendor = root / mutation
            shutil.copytree(HERE / 'vendor', vendor)
            target = vendor / 'accelerators/tables.py'
            if mutation == 'digest':
                sentinel = root / 'EXECUTED'
                target.write_text('from pathlib import Path\nPath(' + repr(str(sentinel)) + ').touch()\n')
                message = 'source digest'
            elif mutation == 'extra':
                (vendor / 'unlisted.py').write_text('raise RuntimeError("unlisted")\n')
                message = 'complete source path inventory'
            elif mutation == 'missing':
                target.unlink()
                message = 'complete source path inventory'
            else:
                target.unlink()
                target.symlink_to(HERE / 'vendor/accelerators/tables.py')
                message = 'source symlink'
            reject([HERE / 'stage.py', '--vendor', vendor, '--script', 'bw_phases.py', root / 'unused'], message)
            controls.append('source:' + mutation)
        need(not (root / 'EXECUTED').exists(), 'tampered source executed')
        package = root / 'changed fixture package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        fixture = package / 'fixtures/WORD-base.json.gz'
        fixture.write_bytes(fixture.read_bytes() + b'changed')
        unused = root / 'benchmark-must-not-start'
        reject([package / 'benchmark.py', '--pairs', 1, '--work', unused], 'fixture digest')
        need(not unused.exists(), 'invalid benchmark fixture created outputs')
        controls.append('benchmark-fixture')
        for script in ('run_native.py', 'stage.py', 'verify.py'):
            reject(['-O', HERE / script], 'assertions must remain enabled')
            controls.append('optimized:' + script)
        existing = root / 'existing'
        existing.mkdir()
        (existing / 'preserve').write_text('do not overwrite')
        reject([HERE / 'run_native.py', HERE / 'fixtures/WORD-base.json.gz', existing], 'fresh work directory required')
        need(list(existing.iterdir()) == [existing / 'preserve'] and
             (existing / 'preserve').read_text() == 'do not overwrite', 'existing output changed')
        controls.append('existing-output')

        word = json.loads(gzip.decompress((HERE / 'fixtures/WORD-base.json.gz').read_bytes()))
        for mutation in ('singular-warp', 'paid-profile'):
            bad = copy.deepcopy(word)
            if mutation == 'singular-warp':
                bad['warps'][0][2][1] = bad['warps'][0][2][0]
                message = 'non-invertible G'
            else:
                key = next(iter(bad['report']['local_profile']))
                bad['report']['local_profile'][key] += 1
                message = 'paid profile differs'
            path = root / (mutation + '.json')
            path.write_text(json.dumps(bad))
            for engine in ('reference', 'sparse'):
                out = root / (mutation + '-' + engine)
                reject([HERE / 'run_native.py', path, out, '--engine', engine], 'stage failed')
                log = out / ('reference-driver.log' if engine == 'reference' else 'native-bw_transport.py.log')
                need(message in log.read_text(), 'wrong rejection reason for ' + str(out))
                need(not (out / 'RESULT.json').exists(), 'failed native run wrote success')
                controls.append('word:' + mutation + ':' + engine)

        # Exercise the independent checker on mutated FILES, in addition to its
        # thirteen retained internal matrix-mutation controls in every full run.
        for mutation in ('phase', 'missing-class'):
            out = root / ('recipe-' + mutation)
            shutil.copytree(local, out)
            path = out / 'CLIFFORD-RECIPES.json'
            recipes = json.loads(path.read_text())
            if mutation == 'phase':
                left = recipes['warps'][0]['left']
                left['phase'] = (left['phase'] + 1) % 4
                message = 'warp recipe is not the exact column product'
            else:
                recipes['warps'].pop()
                message = 'recipe classes differ'
            path.write_text(json.dumps(recipes))
            reject([HERE / 'vendor/native/new/code/borrow/bw_check_recipes.py', out], message)
            controls.append('recipe-file:' + mutation)

        for mutation in ('coverage', 'missing-file', 'container-binding'):
            out = root / ('receipt-' + mutation)
            shutil.copytree(local, out)
            if mutation == 'missing-file':
                (out / 'LOCAL-CHECKS.json').unlink()
                message = 'complete native output inventory'
            else:
                path = out / 'WARP-RECIPE-CHECKS.json'
                receipt = json.loads(path.read_text())
                if mutation == 'coverage':
                    receipt['controls_rejected'].pop()
                    message = 'native outputs differ'
                else:
                    receipt['canonical_word_sha256'] = '0' * 64
                    message = 'canonical container binding'
                path.write_text(json.dumps(receipt))
            try:
                compare(local, out)
            except ValueError as error:
                need(message in str(error), 'wrong comparison failure')
            else:
                raise AssertionError('altered native outputs accepted: ' + mutation)
            controls.append('comparison:' + mutation)
    print('PASS_T74_NATIVE_FAST_BOUNDARY_CONTROLS', len(controls), json.dumps(controls))
    return controls


if __name__ == '__main__':
    need(__debug__, 'assertions must remain enabled')
    source_bytes(HERE / 'vendor')
    check(Path(sys.argv[1]))
