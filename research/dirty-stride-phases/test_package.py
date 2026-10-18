"""Reject concrete source faults and replay the package after relocation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v = load(HERE/'verify.py', 'package_verifier')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reject(name, action, expected):
    try:
        action()
    except ValueError as error:
        need(str(error) in expected, name+': wrong rejection: '+str(error))
        return dict(name=name, rejected=str(error))
    raise ValueError(name+': mutation was accepted')


def main():
    source = (HERE/'chirp.py').read_text()
    phase_case = lambda module: v.check_phase_case(module, 7, 1, 64, (F(17, 4), F(-33, 8)))
    leaf_case = lambda module: v.check_leaf_case(module, 8, 3, -3, 16, 2**40)
    faults = [
        ('wrong_machin_weight', '((5, 16), (239, -4))', '((5, 15), (239, -4))',
         phase_case, {'phase coefficient accuracy'}),
        ('short_shear_precision', 'real_round(tangent, self.bits+8)', 'real_round(tangent, 8)',
         phase_case, {'phase coefficient accuracy'}),
        ('wrong_forward_shear', 'imag += real_round(sine*real, bits)', 'imag -= real_round(sine*real, bits)',
         phase_case, {'rotation accuracy'}),
        ('wrong_reverse_shear', 'imag -= real_round(sine*real, bits)', 'imag += real_round(sine*real, bits)',
         phase_case, {'rotation exact inverse'}),
        ('linear_phase_stream', 'difference = (difference+2*phase.numerator) % phase.modulus',
         'difference = (difference+phase.numerator) % phase.modulus',
         leaf_case, {'phased leaf accuracy'}),
        ('unrestored_source', '    phase_pass(x, phase, False)', '    phase_pass(x, phase, True)',
         leaf_case, {'leaf source restoration'}),
        ('wrong_target_phase', '    phase_pass(y, phase, False)', '    phase_pass(y, phase, True)',
         leaf_case, {'phased leaf accuracy'}),
        ('unpaid_phase_read', '        meter.access(data, i)\n        value = rotate',
         '        value = rotate', leaf_case, {'paid data accesses'}),
        ('lost_quadratic_sign', 'return cls(numerator % modulus,', 'return cls((-numerator) % modulus,',
         leaf_case, {'phased leaf accuracy'}),
    ]
    controls = []
    with tempfile.TemporaryDirectory(prefix='dirty-phase-controls-') as temporary:
        root = Path(temporary)
        for index, (name, old, new, check, errors) in enumerate(faults):
            need(old in source, 'mutation anchor: '+name)
            package = root/name
            (package/'vendor/pr985').mkdir(parents=True)
            shutil.copyfile(HERE/'dirty_stride.py', package/'dirty_stride.py')
            (package/'chirp.py').write_text(source.replace(old, new, 1))
            module = load(package/'chirp.py', 'fault_'+str(index))
            controls.append(reject(name, lambda: check(module), errors))
        # The mathematical verifier must reject an incorrect borrowed-array inverse.
        package = root/'wrong_child_inverse'
        (package/'vendor/pr985').mkdir(parents=True)
        (package/'chirp.py').write_text(source)
        prior = (HERE/'dirty_stride.py').read_text()
        old = 'run(src, z, lo, mid, level+1, -1)'
        need(old in prior, 'child inverse anchor')
        (package/'dirty_stride.py').write_text(prior.replace(old, 'run(src, z, lo, mid, level+1, 1)', 1))
        module = load(package/'chirp.py', 'fault_child')
        controls.append(reject('wrong_child_inverse', lambda: v.check_kernel_case(module, 2, 5, 2, 13),
                               {'kernel source and scratch restoration', 'phased kernel accuracy'}))
        # Check content binding separately from all semantic fault checks above.
        package = root/'binding'
        shutil.copytree(HERE, package)
        pin = package/'vendor/pr985/dirty_stride.py'
        pin.write_bytes(pin.read_bytes()+b'\n')
        relocated = load(package/'verify.py', 'binding_verifier')
        controls.append(reject('source_bytes', relocated.pins,
                               {'source SHA256: vendor/pr985/dirty_stride.py'}))
        # A noninteger schema value must not compare equal to its integer value.
        receipt = json.loads((HERE/'EXPECTED.json').read_text())
        altered = dict(receipt, schema=True)
        need(v.canonical(receipt) != v.canonical(altered), 'typed receipt comparison')
        controls.append(dict(name='boolean_receipt', rejected='typed receipt mismatch'))
        clean = root/'standalone'
        shutil.copytree(HERE, clean)
        before = {str(path.relative_to(clean)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in clean.rglob('*') if path.is_file()}
        for path in clean.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        output = root/'regenerated.json'
        completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(clean/'verify.py'), '--write', str(output)],
                                   cwd=root, text=True, capture_output=True, timeout=600)
        need(completed.returncode == 0, 'relocated replay: '+completed.stdout+completed.stderr)
        need(output.read_bytes() == (HERE/'EXPECTED.json').read_bytes(), 'relocated full receipt')
        after = {str(path.relative_to(clean)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in clean.rglob('*') if path.is_file()}
        need(before == after, 'read-only package changed')
    print(json.dumps(dict(controls=controls, relocated_read_only_replay=True, byte_identical_receipt=True), sort_keys=True))
    print('PASS_DIRTY_PHASE_PACKAGE controls='+str(len(controls))+' relocation=1 regeneration=1')


if __name__ == '__main__':
    main()
