"""Fresh native PR433 phases, signed R758, geometry, primitives and composition.

Usage: python -B verify.py NEW_OUTPUT [--signed SIGNED_VALIDATION_PACKAGE]
Prepared with OpenAI Codex assistance. Original source notices remain intact.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import subprocess
import sys

if not __debug__ or sys.version_info < (3, 12):
    raise SystemExit('Python 3.12+ with assertions required')
sys.dont_write_bytecode = True
import compose
import native_restore
import science
import signed_bit

HERE = Path(__file__).resolve().parent
KAPPA = '44834598090331144184841/40000000000000000000000000'


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def inventory(directory, count):
    directory = Path(directory)
    manifest = directory / 'MANIFEST.sha256'
    rows = [line.split(None, 1) for line in manifest.read_text().splitlines()]
    entries = {name.strip().removeprefix('./'): want for want, name in rows}
    assert len(entries) == len(rows) == count - 1
    assert 'MANIFEST.sha256' not in entries
    assert not any(p.is_symlink() for p in directory.rglob('*'))
    for name in entries:
        p = Path(name)
        assert not p.is_absolute() and '..' not in p.parts
    actual = {p.relative_to(directory).as_posix(): digest(p)
              for p in directory.rglob('*') if p.is_file() and p != manifest}
    assert actual == entries
    return digest(manifest)


def check_sources(signed):
    source = read(HERE / 'SOURCE.json')
    inventory(HERE, source['package_file_count'])
    pin = source['signed_dependency']
    assert inventory(signed, pin['file_count']) == pin['manifest_sha256']
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--signed', type=Path,
                        default=HERE.parent / 'e8-bit-signed-validation')
    args = parser.parse_args()
    out = args.output.resolve()
    signed = args.signed.resolve()
    assert not out.exists()
    assert not out.is_relative_to(HERE) and not out.is_relative_to(signed)
    for path in (HERE, out, signed, Path(sys.executable).resolve()):
        assert not any(c.isspace() for c in str(path))
    assert os.environ.get('E8_HAMMING_GZIP_OS19') != '1'
    check_sources(signed)
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
    for key in list(env):
        if key in ('PYTHONOPTIMIZE', 'PR315', 'B3_OUT', 'E8_HAMMING_GZIP_OS19') or key.startswith(('CX_', 'COMPLEX_')):
            env.pop(key, None)
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
    checks = []

    def run(name, argv):
        print('CHECK', name, flush=True)
        logpath = out / (name + '.log')
        with logpath.open('w') as log:
            subprocess.run([sys.executable, '-B', *map(str, argv)], env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        checks.append(dict(name=name, log_sha256=digest(logpath)))

    native = native_restore.restore(HERE, out / 'native')
    run('native433-full-phases', [native['pr433'] / 'verify.py', out / 'full', '--replay-phases'])
    run('literal-complex-primitives', [HERE / 'primitive_audit.py', out / 'full/split-centres',
                                      out / 'PRIMITIVE-REVIEW.json'])
    print('CHECK fresh-signed-R758-and-geometry', flush=True)
    signed_bit.run(HERE, native['pr433'], native['pr386'], out / 'full', signed, out / 'signed')
    complex_science = science.complex_science(out / 'full', out / 'PRIMITIVE-REVIEW.json')
    write(out / 'COMPLEX-SCIENCE.json', complex_science)
    assembly = compose.run(native['pr433'], native['pr386'], out / 'full', out / 'signed',
                           out / 'PRIMITIVE-REVIEW.json', out / 'composition')
    assert assembly['kappa'] == KAPPA
    validation = dict(status='PASS_FRESH_SPLIT433_SIGNED_R758_COMPLETE_COMPOSITION',
                      kappa=KAPPA, complex_b=assembly['complex_b'], bit_c=assembly['bit_c'],
                      native_source_index_sha256=digest(HERE / 'native-source-index.json'),
                      complete_complex_science_sha256=digest(out / 'COMPLEX-SCIENCE.json'),
                      complete_signed_bit_science_sha256=digest(out / 'signed/SCIENCE.json'),
                      exact_composition_science_sha256=digest(out / 'composition/SCIENCE.json'),
                      scope=assembly['scope'])
    assert validation == read(HERE / 'EXPECTED.json')
    write(out / 'VALIDATION.json', validation)
    check_sources(signed)
    native_check = native_restore.check(HERE, out / 'native')
    receipt = dict(status=validation['status'], kappa=KAPPA,
                   complex_b=validation['complex_b'], bit_c=validation['bit_c'],
                   package_manifest_sha256=digest(HERE / 'MANIFEST.sha256'),
                   validation_sha256=digest(out / 'VALIDATION.json'),
                   fresh_native_result_sha256=digest(out / 'full/RESULT.json'),
                   fresh_signed_bit_receipt_sha256=digest(out / 'signed/RECEIPT.json'),
                   fresh_complex_primitive_receipt_sha256=digest(out / 'PRIMITIVE-REVIEW.json'),
                   native_inventory=native_check, all_frozen_sources_unchanged=True,
                   checks=checks, scope=assembly['scope'])
    write(out / 'RECEIPT.json', receipt)
    print(receipt['status'], KAPPA, flush=True)


if __name__ == '__main__':
    main()
