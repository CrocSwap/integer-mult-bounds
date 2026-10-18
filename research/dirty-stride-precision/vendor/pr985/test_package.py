"""Check relocation, exact receipts, and faults at the solver boundary."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent

LOAD = r'''
import importlib.util, pathlib, sys
p = pathlib.Path(sys.argv[1])
s = importlib.util.spec_from_file_location('replay', p/'verify.py')
v = importlib.util.module_from_spec(s)
s.loader.exec_module(v)
'''

PROBE = LOAD+r'''
v.generic_check(8)
d, F = v.d, v.F
fs = [(False, (F(1, 4), F(1, 8)), F(1)),
      (True, (F(1, 3), F(1, 9)), F(1)),
      (False, (F(-1, 5), F(1, 7)), F(1))]
originals = [v.values(7, 96, 36+7*j) for j in range(4)]
banks = [v.Bank(a) for a in originals]
tau = (F(3, 5), F(4, 5))
d.compose(banks[0], banks[1], fs, banks[2:], tau, F(1, 2), 96, 3)
d.need(banks[0].values == originals[0] and [a.values for a in banks[2:]] == originals[2:], 'product restoration')
c = v.load(p/'vendor/pr628/check.py', 'probe628')
q = [d.ONE]
for inside, b, scale in fs:
    rho = b if inside else d.div(d.ONE, b)
    new = [d.ZERO]*(len(q)+1)
    for j, value in enumerate(q):
        new[j] = d.sub(new[j], d.mul(rho, value))
        new[j+1] = d.add(new[j+1], value)
    q = new
exact = c.matrix_solve(originals[0], c.phased_polynomial(q, tau), 3)
net = [d.sub(a, b) for a, b in zip(banks[1].values, originals[1])]
bound = d.execution_bound(len(fs), 1, F(1, 2), 4, 96)
d.need(all(d.norm2(d.sub(a, b)) <= bound**2 for a, b in zip(net, exact)), 'mixed factor output')
d.compose(banks[0], banks[1], fs, banks[2:], tau, F(1, 2), 96, 3, -1)
d.need([a.values for a in banks] == originals, 'product inverse')
print('PASS_BOUNDARY_PROBE')
'''


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(args, reason=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B']+args,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if reason is None:
        need(result.returncode == 0, result.stdout+'\n'+result.stderr)
    else:
        need(result.returncode != 0 and reason in result.stderr,
             'wrong rejection: '+str(args)+'\n'+result.stdout+'\n'+result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutations-only', action='store_true', help='Run the short fault checks only.')
    args = parser.parse_args()
    controls = []
    with tempfile.TemporaryDirectory(prefix='dirty stride checks ') as tmp:
        root = Path(tmp)
        package = root/'standalone package'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        run(['-c', PROBE, str(package)])
        source = package/'dirty_stride.py'
        original = source.read_text()
        inverse_probe = PROBE.replace('originals =', 'fs = fs[:2]\noriginals =', 1)
        mutations = [
            ('missing_source_undo', '    causal(source, target, stride, geometry, undo=True)\n',
             '', 'source restoration', PROBE),
            ('unpaired_closure', 'closure(source, target, stride, geometry, -1, level)',
             'closure(source, target, stride, geometry, 1, level)', 'source restoration', PROBE),
            ('wrong_closure_stride', '(-source.length) % stride, geometry',
             'source.length % stride, geometry', 'leaf error', PROBE),
            ('missing_inner_shift', 'm, -stride if inside else 0, meter)',
             'm, 0, meter)', 'mixed factor output', PROBE),
            ('missing_closure_transport', '    swap(borrowed, carrier)\n',
             '', 'leaf error', PROBE),
            ('expansive_power_rounding', 'result = trunc(mul(',
             'result = rnd(mul(', 'power does not increase the norm', LOAD+'v.power_check()\n'),
            ('wrong_inverse_order',
             '            run(z, dst, mid, hi, level+1, 1)\n            run(src, z, lo, mid, level+1, 1)\n            run(z, dst, mid, hi, level+1, -1)\n            run(src, z, lo, mid, level+1, -1)',
             '            run(src, z, lo, mid, level+1, -1)\n            run(z, dst, mid, hi, level+1, -1)\n            run(src, z, lo, mid, level+1, 1)\n            run(z, dst, mid, hi, level+1, 1)',
             'product inverse', inverse_probe),
        ]
        for name, old, new, reason, probe in mutations:
            need(old in original, 'missing mutation site: '+name)
            source.write_text(original.replace(old, new))
            run(['-c', probe, str(package)], reason)
            source.write_text(original)
            controls.append(name)

        vendor = package/'vendor/pr846/stride.py'
        raw = vendor.read_bytes()
        vendor.write_bytes(raw+b'\n')
        run(['-c', LOAD+'v.pins()\n', str(package)], 'source SHA256')
        vendor.write_bytes(raw)
        controls.append('source_drift')

        occupied = root/'occupied.json'
        occupied.write_bytes(b'keep these bytes\n')
        run([str(package/'verify.py'), '--write', str(occupied)], 'output already exists')
        need(occupied.read_bytes() == b'keep these bytes\n', 'existing output changed')
        controls.append('existing_output')

        if args.mutations_only:
            print('PASS_DIRTY_STRIDE_MUTATIONS controls='+str(len(controls)))
            return

        expected_file = package/'EXPECTED.json'
        expected = expected_file.read_bytes()
        changed = json.loads(expected)
        need(type(changed['costs'][0]['length']) is int and changed['costs'][0]['length'] == 1,
             'integer-to-Boolean control fixture')
        changed['costs'][0]['length'] = True
        expected_file.write_text(json.dumps(changed))
        run([str(package/'verify.py')], 'exact receipt mismatch')
        expected_file.write_bytes(expected)
        controls.append('certificate_integer_to_boolean')

        for path in package.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        regenerated = root/'regenerated.json'
        run([str(package/'verify.py'), '--write', str(regenerated)])
        need(regenerated.read_bytes() == expected, 'standalone receipt differs')
        need(source.read_text() == original, 'mutated source was not restored')
        print('PASS_DIRTY_STRIDE_PACKAGE relocation=1 regeneration=1 controls='+str(len(controls)))
        print(json.dumps(dict(controls=controls, receipt_sha256=hashlib.sha256(expected).hexdigest()), sort_keys=True))


if __name__ == '__main__':
    main()
