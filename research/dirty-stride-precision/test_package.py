"""Check faults, source binding, and a read-only standalone replay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent

LOAD = r'''
import importlib.util, pathlib, sys
p = pathlib.Path(sys.argv[1])
s = importlib.util.spec_from_file_location('probe', p/'verify.py')
v = importlib.util.module_from_spec(s)
s.loader.exec_module(v)
d, b, F = v.d, v.b, v.F
'''

SOURCE = LOAD+r'''
x0, y0 = v.v.values(12, 64, 36), v.v.values(12, 64, 71)
x, y = v.v.Bank(x0), v.v.Bank(y0)
d.lift(x, y, (F(3,10), F(2,5)), F(1,2), 64, 5)
d.need(x.values == x0, 'source restoration')
'''

KERNEL = LOAD+r'''
fs = [(True, (F(1,4), F(1,8)), F(3)),
      (False, (F(1,3), F(1,9)), F(1))]
q = [d.ONE]
for inside, coefficient, scale in fs:
    root = coefficient if inside else d.div(d.ONE, coefficient)
    new = [d.ZERO]*(len(q)+1)
    for j, value in enumerate(q):
        new[j] = d.sub(new[j], d.mul(root, value))
        new[j+1] = d.add(new[j+1], value)
    q = new
q = [tuple(z/3 for z in pair) for pair in q]
state = dict(radix=3, embedding=0, q=q,
             certificate=dict(factorization_inverse_error_bound='0'))
budget = b.choose(2, 3, F(1,2), 1000, 4, 128, 16)
v.execute_kernel(state, fs, F(1,2), budget, 5, 2, (F(3,5), F(4,5)))
'''

POWER = LOAD+r'''
root = (F(3,10), F(2,5))
exact = d.mul(root, root)
d.need(d.norm2(d.power(root, 2, 4, d.Meter())) <= d.norm2(exact), 'power norm guard')
'''

EXTINCTION = LOAD+r'''
beta, bits = F(1,4096), 64
depth = d.effective_depth(beta, bits)
d.need(d.power((1-beta,F(0)), 1 << depth, bits, d.Meter()) == d.ZERO,
       'exact coefficient extinction')
'''

LEGACY_READS = LOAD+r'''
arrays = [v.Bank(v.v.values(12, 64, salt)) for salt in (36,71)]
v.run_counted(lambda: v.v.d.lift(*arrays, (F(3,10),F(2,5)), F(1,2), 64, 5), arrays)
'''


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def run(args, reason=None, cwd=None):
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    result = subprocess.run([sys.executable, '-I', '-O', '-B']+args, cwd=cwd,
                            env=env, text=True, capture_output=True)
    if reason is None:
        need(result.returncode == 0, result.stdout+'\n'+result.stderr)
    else:
        need(result.returncode != 0 and reason in result.stderr,
             'wrong failure: '+reason+'\n'+result.stdout+'\n'+result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutations-only', action='store_true')
    args = parser.parse_args()
    controls = []
    with tempfile.TemporaryDirectory(prefix='dirty precision checks ') as tmp:
        root = Path(tmp)
        package = root/'standalone package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for probe in (SOURCE, KERNEL, POWER, EXTINCTION):
            run(['-c', probe, str(package)])
        run(['-c', LEGACY_READS, str(package)], 'literal indexed access charge')
        controls.append('legacy_validation_rereads')
        source = package/'dirty_stride.py'
        original = source.read_text()
        inverse_word = ('            run(z, dst, mid, hi, level+1, 1)\n'
                        '            run(src, z, lo, mid, level+1, 1)\n'
                        '            run(z, dst, mid, hi, level+1, -1)\n'
                        '            run(src, z, lo, mid, level+1, -1)')
        wrong_word = ('            run(src, z, lo, mid, level+1, -1)\n'
                      '            run(z, dst, mid, hi, level+1, -1)\n'
                      '            run(src, z, lo, mid, level+1, 1)\n'
                      '            run(z, dst, mid, hi, level+1, 1)')
        mutations = [
            ('source_undo', '    causal(source, target, stride, geometry, undo=True)\n',
             '', SOURCE, 'source restoration'),
            ('closure_inverse', 'closure(source, target, stride, geometry, -1, level)',
             'closure(source, target, stride, geometry, 1, level)', SOURCE, 'source restoration'),
            ('nearest_power', 'result = trunc(mul(', 'result = rnd(mul(', POWER, 'power norm guard'),
            ('false_extinction', 'return ceil_log2(1/beta) + bits.bit_length()',
             'return 0', EXTINCTION, 'exact coefficient extinction'),
            ('inverse_order', inverse_word, wrong_word, KERNEL, 'complete word inverse'),
            ('inner_shift', 'm, -stride if inside else 0, meter)',
             'm, 0, meter)', KERNEL, 'new kernel execution error'),
            ('validation_reread', "need(rnd(datum, bits) == datum, 'fixed grid data')",
             "need(rnd(data[i], bits) == data[i], 'fixed grid data')",
             KERNEL, 'literal indexed access charge'),
        ]
        for name, old, new, probe, reason in mutations:
            need(old in original, 'missing fault site: '+name)
            source.write_text(original.replace(old, new))
            run(['-c', probe, str(package)], reason)
            controls.append(name)
        source.write_text(original)
        budget = package/'budget.py'
        original_budget = budget.read_text()
        for name, old, new, reason in (
            ('local_error_power', 'local = 5*g+', 'local = 3*g+', 'independent local bound'),
            ('inverse_guard', 'prefix+magnitude_bits+8*g+2*ell+16',
             'prefix+magnitude_bits+7*g+2*ell+16', 'inverse preimage integer guard'),
        ):
            need(old in original_budget, 'missing budget fault site')
            budget.write_text(original_budget.replace(old, new))
            run(['-c', LOAD+'v.budget_checks()\n', str(package)], reason)
            controls.append(name)
        budget.write_text(original_budget)
        dependency = package/'vendor/pr985/dirty_stride.py'
        dependency.write_bytes(dependency.read_bytes()+b'\n')
        run(['-c', LOAD+'v.pins()\n', str(package)], 'source SHA256')
        controls.append('dependency_drift')
        shutil.copyfile(HERE/'vendor/pr985/dirty_stride.py', dependency)
        occupied = root/'occupied.json'
        occupied.write_text('keep\n')
        run([str(package/'verify.py'), '--write', str(occupied)], 'output already exists')
        need(occupied.read_text() == 'keep\n', 'existing output preserved')
        controls.append('output_overwrite')
        receipt = None
        if not args.mutations_only:
            output = root/'regenerated.json'
            try:
                for item in package.rglob('*'):
                    item.chmod(0o555 if item.is_dir() else 0o444)
                package.chmod(0o555)
                result = run([str(package/'verify.py'), '--write', str(output)], cwd=root)
                need(output.read_bytes() == (HERE/'EXPECTED.json').read_bytes(),
                     'standalone exact receipt')
                receipt = hashlib.sha256(output.read_bytes()).hexdigest()
                print(result.stdout, end='')
            finally:
                package.chmod(0o755)
                for item in package.rglob('*'):
                    item.chmod(0o755 if item.is_dir() else 0o644)
        print(json.dumps(dict(controls=controls, read_only_relocation=receipt is not None,
                              receipt_sha256=receipt), sort_keys=True))
    print('PASS_DIRTY_STRIDE_PRECISION_PACKAGE controls=%d relocation=%d' %
          (len(controls), not args.mutations_only))


if __name__ == '__main__':
    main()
