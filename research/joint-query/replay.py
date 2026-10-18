"""Verify the frozen QQ16 local joint-query words from pinned sources."""

from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json


HERE = Path(__file__).resolve().parent
PAYLOAD_SHA256 = '2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef'
SOURCE_LOADER_SHA256 = 'd23924511e3aed41e5e64511ca70126a636d91c8aa02e656cb61d6ceca1fe0a0'
CODE = ('source_data.py', 'verify_scalar.py', 'verify_native.py', 'verify_ordered.py', 'replay.py')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode('utf-8')
    path.write_bytes(raw)
    return sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(sha256((HERE / 'source_data.py').read_bytes()).hexdigest() == SOURCE_LOADER_SHA256,
         'The unchanged reviewed source loader')
    raw = gzip.decompress((HERE / 'certificate.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD_SHA256, 'The frozen base QQ16 certificate')
    packet = json.loads(raw)
    need(packet['schema'] == 'conserved-qq16-full-cover-native-words-v1', 'The certificate schema')
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for name, entry in manifest['evidence'].items():
        need(sha256((HERE / name).read_bytes()).hexdigest() == entry['sha256'], 'Evidence pin: ' + name)
    source = load_module('source_data')
    scalar = load_module('verify_scalar')
    native = load_module('verify_native')
    ordered = load_module('verify_ordered')
    data = source.reconstruct(args.repo)
    blocks = scalar.rebuild(data['R'])
    scalar_result = scalar.verify(data, packet, blocks)
    native_result = native.verify(data, packet, blocks, scalar.scalar_cost)
    ordered_result = ordered.verify(data['R'])
    args.out.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, value in (('CLEAN-J-CHECKS.json', data['checks']),
                        ('SCALAR-CHECKS.json', scalar_result),
                        ('NATIVE-CHECKS.json', native_result),
                        ('ORDERED-CHECKS.json', ordered_result)):
        outputs[name] = write_json(args.out / name, value)
    report = {
        'status': 'PASS_PORTABLE_QQ16_LOCAL_JOINT_QUERY',
        'source_base': source.BASE, 'source_archive_sha256': source.ARCHIVE_SHA256,
        'certificate_payload_sha256': PAYLOAD_SHA256,
        'source_manifest_sha256': sha256((HERE / 'SOURCES.json').read_bytes()).hexdigest(),
        'code_sha256': {name: sha256((HERE / name).read_bytes()).hexdigest() for name in CODE},
        'outputs': outputs,
        'native_cases': 37, 'common_chart_input_columns_per_orientation': 712,
        'exact_new_native_gaussian_columns': native_result['exact_gaussian_kernel_columns'],
        'inherited': ['The bridge proof for the retained core at each owner',
                      'The original child kernels and recursive native contract'],
        'not_checked': ['An implementation of the algebraic inverse in output native frames',
                        'Global controller closure or an endpoint decoder',
                        'New child and helper hosting', 'Stream and address implementation costs',
                        'Recursive precision and the complete supplier invoice', 'A new kappa bound'],
    }
    write_json(args.out / 'REPLAY.json', report)
    print(report['status'])
    print('37 native cases; 712 scalar input columns per orientation; 16384 exact new native columns.')
    print('B: scalar 214986, native mass 5546. F: scalar 211210, native mass 5530.')
    print('Local construction only. The complete supplier and kappa calculation are not established.')


if __name__ == '__main__':
    main()
