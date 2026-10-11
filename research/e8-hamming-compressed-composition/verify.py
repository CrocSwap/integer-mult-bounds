"""Fresh PR431 Hamming supplier and compressed signed R822 composition.

Usage: python -B verify.py NEW_OUTPUT. Python3.12+, assertions and C++17 required.
Prepared with OpenAI Codex assistance; inherited notices and conditions apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
import os
import subprocess
import sys

if not __debug__ or sys.version_info < (3, 12):
    raise SystemExit('Python3.12+ with assertions required')
sys.dont_write_bytecode = True
import compose
import native_restore
import science

HERE = Path(__file__).resolve().parent
NAMES = {'bit': 'e8-bit-helper-reuse', 'bit-parent': 'e8-bit-seven-stage',
         'signed': 'e8-bit-signed-validation'}
KAPPA = '211395063483155587916079/200000000000000000000000000'


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


def check_sources(paths):
    source = read(HERE / 'SOURCE.json')
    inventory(HERE, source['package_file_count'])
    for name, pin in source['dependencies'].items():
        assert inventory(paths[name], pin['file_count']) == pin['manifest_sha256']
    return source


def transport_controls(fresh):
    spec = importlib.util.spec_from_file_location('inactive_gzip_transport', HERE / 'sitecustomize.py')
    module = importlib.util.module_from_spec(spec)
    original = gzip.compress
    spec.loader.exec_module(module)
    assert gzip.compress is original
    tested = []
    for part in ('baseline', 'changed'):
        root = fresh / part / 'work/complex-network/hamming'
        for name in ('FULL-WORD.json.gz', 'CANONICAL-WORD.json.gz', 'GLOBAL-TEMPLATE.json.gz'):
            raw = (root / name).read_bytes()
            assert raw[9] == 19
            for platform in (3, 19, 255):
                simulated = raw[:9] + bytes([platform]) + raw[10:]
                normalized = module.normalize_zero_mtime_header(simulated, 0)
                assert normalized == raw and normalized[:9] == simulated[:9] and normalized[10:] == simulated[10:]
                assert gzip.decompress(normalized) == gzip.decompress(simulated)
            tested.append(dict(file=part + '/' + name, native_sha256=sha256(raw).hexdigest(),
                               payload_sha256=sha256(gzip.decompress(raw)).hexdigest()))
    for timestamp in (None, 1, 123456789):
        raw = gzip.compress(b'nonzero and default timestamp control', mtime=timestamp)
        assert module.normalize_zero_mtime_header(raw, timestamp) == raw
    bad = bytearray(gzip.compress(b'wrong timestamp', mtime=0)); bad[4] = 1
    try:
        module.normalize_zero_mtime_header(bytes(bad), 0)
    except AssertionError:
        pass
    else:
        raise AssertionError('Inconsistent zero-mtime header admitted')
    return dict(status='PASS_NATIVE431_GZIP_HEADER_TRANSPORT_ONLY', source_sha256=digest(HERE / 'sitecustomize.py'),
                checked_native_outputs=tested, simulated_os_bytes=[3, 19, 255],
                nonzero_and_none_mtime_unchanged=True, malformed_timestamp_rejected=True,
                scope='Only gzip header byte9 for mtime0 outputs. Deflate, CRC, ISIZE and decoded data remain identical. Native compressed-byte assertions remain mandatory; arbitrary future zlib payload equivalence is not claimed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    for name, dirname in NAMES.items():
        parser.add_argument('--' + name, type=Path, default=HERE.parent / dirname)
    args = parser.parse_args()
    out = args.output.resolve()
    paths = {name: getattr(args, name.replace('-', '_')).resolve() for name in NAMES}
    assert not out.exists()
    for path in (HERE, *paths.values()):
        assert not out.is_relative_to(path)
    for path in (HERE, out, *paths.values(), Path(sys.executable).resolve()):
        assert not any(c.isspace() for c in str(path))
    assert os.environ.get('E8_HAMMING_GZIP_OS19') != '1', 'Transport activates only in the native Hamming child tree'
    source = check_sources(paths)
    out.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0')
    for key in list(env):
        if key in ('PYTHONOPTIMIZE', 'PR315', 'B3_OUT', 'E8_HAMMING_GZIP_OS19') or key.startswith(('CX_', 'COMPLEX_')):
            env.pop(key, None)
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env.get('PATH', '')
    checks = []

    def run(name, argv, child_env=None):
        print('CHECK', name, flush=True)
        with (out / (name + '.log')).open('w') as log:
            subprocess.run([sys.executable, '-B', *map(str, argv)], env=child_env or env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        checks.append(dict(name=name, log_sha256=digest(out / (name + '.log'))))

    native = native_restore.restore(HERE, out / 'native')
    run('fresh-frozen-R822-parent', [paths['bit'] / 'verify.py', out / 'bit-replay', '--parent', paths['bit-parent']])
    parent = read(out / 'bit-replay/RECEIPT.json')
    assert parent['status'] == 'PASS_SOURCE_BOUND_CONDITIONAL_E8_HELPER_REUSE_AND_ASSEMBLY'
    assert parent['extension_manifest_sha256'] == source['dependencies']['bit']['manifest_sha256']
    hamming_env = dict(env, E8_HAMMING_GZIP_OS19='1')
    hamming_env['PYTHONPATH'] = str(HERE) + os.pathsep + env.get('PYTHONPATH', '')
    run('native431-complete', [native['pr431'] / 'verify.py', out / 'complex'], hamming_env)
    transport = transport_controls(out / 'complex')
    write(out / 'GZIP-TRANSPORT.json', transport)
    hamming = out / 'complex/changed/work/complex-network/hamming'
    run('literal-complex-primitives', [HERE / 'primitive_audit.py', hamming, out / 'PRIMITIVE-REVIEW.json'])
    run('compressed-signed-R822', [HERE / 'compressed_bit.py', HERE, native['pr386'], native['pr370'],
                                 out / 'bit-replay', paths['signed'], out / 'bit'])
    bit = read(out / 'bit/RECEIPT.json')
    assert bit['status'] == 'PASS_PORTABLE_FRESH_R822_COMPRESSED_SIGNED_SUPPLIER'
    assert bit['science_sha256'] == digest(out / 'bit/SCIENCE.json')
    complex_science = science.complex_science(out / 'complex', out / 'PRIMITIVE-REVIEW.json')
    write(out / 'COMPLEX-SCIENCE.json', complex_science)
    assembly = compose.run(out / 'complex', out / 'bit', native['pr425'] / 'work/pr361/code/engines',
                           out / 'PRIMITIVE-REVIEW.json', out / 'composition')
    assert assembly['kappa'] == KAPPA
    validation = dict(status='PASS_FRESH_HAMMING431_COMPRESSED_SIGNED_R822', kappa=KAPPA,
                      complex_b=assembly['complex_b'], bit_c=assembly['bit_c'],
                      bit_word_raw_sha256=bit['word_raw_sha256'], native_source_index_sha256=digest(HERE / 'native-source-index.json'),
                      complete_complex_science_sha256=digest(out / 'COMPLEX-SCIENCE.json'),
                      complete_bit_science_sha256=digest(out / 'bit/SCIENCE.json'),
                      exact_composition_science_sha256=digest(out / 'composition/SCIENCE.json'),
                      gzip_transport_sha256=digest(out / 'GZIP-TRANSPORT.json'),
                      scope=assembly['scope'])
    assert validation == read(HERE / 'EXPECTED.json')
    write(out / 'VALIDATION.json', validation)
    check_sources(paths)
    native_check = native_restore.check(HERE, out / 'native')
    receipt = dict(status=validation['status'], kappa=KAPPA, complex_b=validation['complex_b'], bit_c=validation['bit_c'],
                   package_manifest_sha256=digest(HERE / 'MANIFEST.sha256'), validation_sha256=digest(out / 'VALIDATION.json'),
                   fresh_R822_parent_receipt_sha256=digest(out / 'bit-replay/RECEIPT.json'),
                   fresh_native431_result_sha256=digest(out / 'complex/RESULT.json'),
                   fresh_compressed_bit_receipt_sha256=digest(out / 'bit/RECEIPT.json'),
                   fresh_complex_primitive_receipt_sha256=digest(out / 'PRIMITIVE-REVIEW.json'),
                   native_inventory=native_check, all_frozen_sources_unchanged=True, checks=checks,
                   scope=assembly['scope'])
    write(out / 'RECEIPT.json', receipt)
    print(receipt['status'], KAPPA, flush=True)


if __name__ == '__main__':
    main()
