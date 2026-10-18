"""Reject semantic faults and replay a relocated read-only package."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def probe(folder, expression):
    program = (
        "import importlib.util,sys; from pathlib import Path; "
        "p=Path(sys.argv[1]); s=importlib.util.spec_from_file_location('fault_check',p/'verify.py'); "
        "v=importlib.util.module_from_spec(s); sys.modules[s.name]=v; s.loader.exec_module(v); "
        +expression)
    return subprocess.run([sys.executable, '-I', '-O', '-B', '-c', program, str(folder)],
                          text=True, capture_output=True, timeout=600)


def main():
    old = (HERE/'vendor/pr1038/chirp.py').read_text()
    new = (HERE/'chirp.py').read_text()
    difference = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                             fromfile='PR1038/chirp.py', tofile='chirp.py', n=0))
    need(difference == (HERE/'DERIVATION.diff').read_text(), 'exact wrapper derivation')
    cases = [
        ('wrong_second_difference', 'phase_stream.py',
         'omega = seed_coefficients(2*a, modulus, state_bits+8, meter)',
         'omega = seed_coefficients(a, modulus, state_bits+8, meter)',
         'v.phase_case(5,17,12,33)', 'ratio state drift'),
        ('wrong_emitted_state', 'phase_stream.py',
         'return chart(self.value, self.phase.bits, self.phase.meter)',
         'return chart(self.ratio, self.phase.bits, self.phase.meter)',
         'v.phase_case(5,17,12,33)', 'phase quadrant'),
        ('stale_reverse_chart', 'phase_stream.py',
         'self.value = rotate(self.value, coefficients, p.state_bits, True, p.meter)',
         'self.value = rotate(self.value, chart(p.seed, p.state_bits, p.meter), p.state_bits, True, p.meter)',
         'v.phase_case(5,17,12,33)', 'phase state cleanup'),
        ('missing_guard_bits', 'phase_stream.py',
         'state_bits = bits+2*(length+1).bit_length()+20', 'state_bits = bits',
         'v.phase_case(1,31,2,65)', 'phase coefficient accuracy'),
        ('uncleared_series', 'phase_stream.py', 'sine -= sine_term', 'sine -= 0',
         'v.phase_case(5,17,12,33)', 'Taylor cleanup'),
        ('wrong_dirty_source_inverse', 'chirp.py',
         'phase_pass(x, phase, False)', 'phase_pass(x, phase, True)',
         'v.word_case(5,2,-3,10,2**40)', 'dirty source restoration'),
        ('wrong_seed_erase', 'phase_stream.py',
         'self.seed = rotate(self.seed, first, self.state_bits, True, self.meter)',
         'self.seed = rotate(self.seed, first, self.state_bits, False, self.meter)',
         'v.phase_case(5,17,12,33)', 'phase preparation cleanup'),
    ]
    with tempfile.TemporaryDirectory(prefix='dirty-fast-phase-controls-') as temp:
        root = Path(temp)
        for name, filename, before, after, expression, expected in cases:
            folder = root/name
            shutil.copytree(HERE, folder)
            path = folder/filename
            source = path.read_text()
            need(before in source, 'missing fault site: '+name)
            path.write_text(source.replace(before, after, 1))
            result = probe(folder, expression)
            need(result.returncode != 0 and 'ValueError: '+expected+'\n' in result.stderr,
                 'wrong fault rejection: '+name+'\n'+result.stdout+result.stderr)
            print('REJECT '+name+': '+expected, flush=True)
            shutil.rmtree(folder)
        folder = root/'source_corruption'
        shutil.copytree(HERE, folder)
        source = folder/'vendor/pr1038/oracle.py'
        source.write_bytes(source.read_bytes()+b'\n')
        result = probe(folder, 'v.pins()')
        need(result.returncode != 0 and 'ValueError: source SHA256: vendor/pr1038/oracle.py\n'
             in result.stderr, 'source corruption rejection')
        print('REJECT source_corruption: source SHA256', flush=True)
        shutil.rmtree(folder)
        relocated = root/'relocated'
        shutil.copytree(HERE, relocated)
        for path in relocated.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(relocated/'verify.py')],
                                cwd=root, capture_output=True, text=True, timeout=600)
        need(result.returncode == 0, 'relocated receipt replay\n'+result.stdout+result.stderr)
        print(result.stdout.strip(), flush=True)
    print('PASS_FAST_PHASE_PACKAGE controls=8 relocation=1 derivation=1')


if __name__ == '__main__':
    main()
