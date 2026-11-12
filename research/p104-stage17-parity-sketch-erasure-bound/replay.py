"""Authenticate and replay the exact stage-17 five-parity capacity bound."""
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, stderr, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def unique(items):
    out = dict(items)
    if len(items) != len(out):
        raise ValueError('duplicate JSON key')
    return out


def data(name):
    file = (ROOT / name).resolve()
    assert file.is_relative_to(ROOT) and file.relative_to(ROOT).as_posix() == name
    return file.read_bytes()


def read(name):
    return loads(data(name), object_pairs_hook=unique)


def authenticate():
    for name, digest in read('LOCAL-PINS.json').items():
        raw = data(name)
        assert sha256(raw).hexdigest() == digest, name
        if name.endswith('.json'):
            loads(raw, object_pairs_hook=unique)
    for name, prov in read('PROVENANCE.json')['files'].items():
        raw = data(name)
        assert sha256(raw).hexdigest() == prov['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == prov['git_blob']


def copy(name, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data(name))


def execute(path, arguments, receipt=None):
    result = run([executable, '-I', '-B', str(path), *map(str, arguments)], capture_output=True, timeout=22)
    if receipt is None:
        assert result.returncode == 1 and b'AssertionError' in result.stderr and not result.stdout
        return None
    if result.returncode:
        stderr.write(result.stderr.decode(errors='replace'))
    result.check_returncode()
    assert result.stdout == data(receipt), receipt
    return loads(result.stdout, object_pairs_hook=unique)


def compare(a, b):
    assert a['clocks'] == b['clocks'] == [4646, 4660]
    assert a['width'] == b['f'] == 2 and a['parity_cap'] == 5
    assert a['polar_rank'] == b['bits'] == 16
    assert a['restricted_rank_lower'] == b['restricted_polar_rank'] == 6
    assert a['control_probes'] == b['sketch_probes']
    assert a['control_max_fraction'] == b['max_phase_fraction'] == '9/16'
    assert b['extremal_cosets'] == [30] and b['exact_control_min_displacement'] == 65280
    assert b['universal_required_displacement'] == '57344'
    assert a['normalized_core_fixed_fraction'] == b['core_fixed_fraction'] == '32769/131072'
    assert a['core_capacity_per_volume_upper'] == b['core_capacity_fraction_upper'] == '3/4'
    assert a['required_volume_lower'] == b['required_volume_lower'] == '7/6'
    assert Q(b['affordability_upper']) <= Q(a['funded_volume_upper']) < Q('1.003')
    assert Q(a['gross_upper']) < Q('-20.798')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    authenticate()
    with TemporaryDirectory(prefix='p104-parity-sketch-') as directory:
        temp = Path(directory)
        lead = temp / 'round215/lead/parity_sketch.py'
        for source, dest in (
            ('engines/lead.py', lead),
            ('inputs/CALLER.json', temp / 'lead/inputs/CALLER.json'),
            ('inputs/PROJECTOR.json', temp / 'round214/lead/inputs/PROJECTOR.json'),
            ('inputs/pricing.py', temp / 'round214/lead/inputs/pricing.py'),
        ):
            copy(source, dest)
        a = execute(lead, [], 'receipts/R215-LEAD.json')
        independent = ROOT / 'engines/independent.py'
        b = execute(independent, [ROOT], 'receipts/R215-INDEPENDENT.json')
        compare(a, b)
        for name in b['pins']:
            copy(name, temp / 'mutant' / name)
        wrong = read('inputs/CALLER.json')
        wrong['events'][4646][3] = [16]
        (temp / 'mutant/inputs/CALLER.json').write_text(dumps(wrong))
        execute(independent, [temp / 'mutant'])
    print('PASS_P104_STAGE17_PARITY_SKETCH_ERASURE_BOUND')


if __name__ == '__main__':
    main()
