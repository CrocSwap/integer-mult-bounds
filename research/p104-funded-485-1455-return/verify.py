# SPDX-License-Identifier: Apache-2.0
"""Reproduce the funded485/1455 construction in a fresh isolated copy.

Each registered stage compares its fresh mathematical receipts with the frozen
ones. Only explicitly named runtime measurements are omitted from comparison.
No generated receipt in the publication directory is overwritten.
"""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from fractions import Fraction
from collections import Counter
from io import BytesIO
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def require(ok, label):
    if not ok:
        raise ValueError(label)


def integrity():
    manifest = read(HERE / 'PACKAGE-MANIFEST.json')
    names = [row['path'] for row in manifest['files']]
    require(len(names) == len(set(names)), 'Unique package inventory')
    for row in manifest['files']:
        path = HERE / row['path']
        require(path.resolve().is_relative_to(HERE) and path.is_file()
                and not path.is_symlink(), 'Regular inventoried file')
        raw = path.read_bytes()
        require((len(raw), sha256(raw).hexdigest()) == (row['size'], row['sha256']),
                'Exact package bytes: ' + row['path'])
    return names


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def ceiling(root):
    signed = read(root / 'producer54/validation_signed/RESULT.json')
    native = read(root / 'producer54/validation_native/NATIVE-RESULT.json')
    invoice = signed['price']['after']
    invoice = dict(invoice, P={int(k): v for k, v in invoice['P'].items()},
                   T={int(k): v for k, v in invoice['T'].items()})
    local = dict(native['native'])
    local['paid'] = {int(k): v for k, v in local['paid'].items()}
    certificate = read(HERE / 'CEILING.json')
    cap = 145
    remainder = Counter(invoice['P'])
    fixed = Counter({rank: 17 * count for rank, count in local['paid'].items()})
    remainder.subtract(fixed)
    require(all(count >= 0 and rank <= cap for rank, count in remainder.items()),
            'Nonnegative exact ambient145 remainder')
    mass = sum(rank * count for rank, count in remainder.items())
    relaxed = Counter(invoice['T'])
    relaxed.subtract(fixed)
    relaxed[cap] -= Fraction(mass, cap)
    lo, hi = map(Fraction, certificate['raw_ceiling'])
    claim, end = Fraction(signed['claim']), Fraction(1, 32)
    require(0 < claim < lo < hi <= end, 'Strict claimed headroom')
    tariff = tariff_module(root)
    # The exact derivative bound is the retained7161 packing argument.
    # Verify the supplied bracket directly instead of repeating its search.
    derivative = (0, 0)
    for rank, count in relaxed.items():
        term = tariff.mul(tariff.power(rank, end if count >= 0 else 0), tariff.log(rank))
        derivative = tariff.add(derivative, tariff.smul(term, -count))
    require(derivative[1] < 0, 'Uniform directed decrease of packing relaxation')
    require(tariff.moment(relaxed, lo)[0] > 0 > tariff.moment(relaxed, hi)[1],
            'Both directed packing bracket endpoints')
    answer = dict(ambient_cap=cap, remainder_rank_mass=mass,
                  raw_ceiling=[str(lo), str(hi)],
                  claimed_fraction=[str(claim / hi), str(claim / lo)])
    return json.loads(json.dumps(answer, default=str))


def tariff_module(root):
    """Read the actual frozen tariff through its authenticated archive chain.

    The native and signed stages still reconstruct the complete source. A pure
    tariff calculation needs the same module bytes, without old constructors.
    """
    pin = read(root / 'TARIFF-SOURCE.json')
    name = pin['source_root']
    path = root / name
    require(path.resolve().is_relative_to(root), 'In-root tariff source archive')
    raw = path.read_bytes()
    for entry in pin['chain']:
        require(entry['archive'] == name and sha256(raw).hexdigest() == entry['archive_sha256'],
                'Exact containing tariff archive')
        member = entry['member']
        if name.endswith('.zip'):
            with zipfile.ZipFile(BytesIO(raw)) as archive:
                info = archive.getinfo(member)
                require(not info.is_dir(), 'Regular tariff member')
                raw = archive.read(info)
        else:
            with tarfile.open(fileobj=BytesIO(raw)) as archive:
                info = archive.getmember(member)
                require(info.isfile(), 'Regular tariff member')
                raw = archive.extractfile(info).read()
        require(sha256(raw).hexdigest() == entry['member_sha256'], 'Exact tariff member bytes')
        name = member
    require(name.endswith('/interval_gate.py') and sha256(raw).hexdigest() == pin['sha256'],
            'Actual native-source tariff identity')
    target = root / 'derived-tariff.py'
    target.write_bytes(raw)
    return load('funded_ceiling_tariff', target)


def compare(root, name, ignored=()):
    actual, expected = read(root / name), read(HERE / name)
    for key in ignored:
        actual.pop(key, None)
        expected.pop(key, None)
    require(actual == expected, 'Every mathematical receipt field: ' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['core', 'native', 'signed', 'frontier'], required=True)
    args = parser.parse_args()
    require(__debug__, 'Assertions are mathematical checks; run without -O')
    names = integrity()
    with TemporaryDirectory(prefix='funded-485-1455-') as temporary:
        root = Path(temporary) / 'package'
        for name in names:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / name, target)

        def run(script):
            print('RUN', script, flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(root / script)], cwd=root, check=True)

        if args.stage == 'core':
            run('producer54/run_core.py')
            run('producer54/validation_native/owned_contract.py')
            for name in ['producer54/reroute/INDEPENDENT-RESULT.json',
                         'producer54/reroute/ADVERSARIAL.json', 'producer54/reroute/GRID.json',
                         'producer54/validation_native/LOCAL-OWNED-CONTRACT.json']:
                compare(root, name)
            result = read(root / 'producer54/reroute/RESULT.json')
            frozen = read(HERE / 'producer54/reroute/RESULT.json')
            for key, value in frozen.items():
                if key not in ('status', 'native_seconds', 'native_result'):
                    require(result[key] == value, 'Core emission field: ' + key)
            require(not result['native_result']['bad_inputs'], 'Every public adjoint input')
        elif args.stage == 'native':
            run('producer54/validation_native/run.py')
            compare(root, 'producer54/validation_native/NATIVE-RESULT.json', ('timings',))
        elif args.stage == 'signed':
            run('producer54/validation_signed/run.py')
            compare(root, 'producer54/validation_signed/RESULT.json', ('timings', 'elapsed_seconds'))
        else:
            run('producer54/finalise.py')
            compare(root, 'producer54/APPLICATION.json')
            require(ceiling(root) == read(HERE / 'CEILING.json'), 'Fresh fixed-profile packing ceiling')
    integrity()
    print('PASS_FUNDED_485_1455_' + args.stage.upper(), flush=True)


if __name__ == '__main__':
    main()
