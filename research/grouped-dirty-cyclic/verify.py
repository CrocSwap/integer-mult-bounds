"""Offline source-bound replay; standard library, Python 3.11 or later."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys

P = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)


def require(value, message):
    if not value:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: '+key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=str)


def bindings(authoring=False):
    manifest = P/'MANIFEST.json'
    require(manifest.exists() or authoring, 'missing package manifest')
    require(not any(path.is_symlink() for path in P.rglob('*')), 'package symlink')
    if manifest.exists():
        record = read_json(manifest)
        require(set(record) == {'files'} and type(record['files']) is dict, 'manifest schema')
        files = record['files']
        actual = {str(path.relative_to(P)) for path in P.rglob('*') if path.is_file() and path != manifest}
        require(set(files) == actual, 'package file coverage')
        for name, sha in files.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'relative package path')
            require(type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha), 'manifest hash type')
            require(hashlib.sha256((P/name).read_bytes()).hexdigest() == sha, 'package hash: '+name)
    sources = read_json(P/'SOURCE-PINS.json')
    require(len(sources['sources']) == 14, 'source inventory')
    require(len({row['path'] for row in sources['sources']}) == 14, 'unique source inventory')
    for row in sources['sources']:
        name = row['path']
        require(not Path(name).is_absolute() and '..' not in Path(name).parts, 'relative source path')
        raw = (P/name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: '+name)
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
                'source Git blob: '+name)
    return dict(files=14, source_pins_sha256=hashlib.sha256((P/'SOURCE-PINS.json').read_bytes()).hexdigest())


def modules():
    sys.path.insert(0, str(P))
    names = ['real_reference', 'gaussian', 'weighted', 'grouped', 'budgets', 'certified', 'controls', 'kernel_bridge']
    loaded = {}
    for name in names:
        loaded[name] = importlib.import_module(name)
        require(Path(loaded[name].__file__).resolve() == P/(name+'.py'), 'local implementation binding: '+name)
    return loaded


def calculate():
    loaded = modules()
    result = dict(status='PASS_GROUPED_DIRTY_CYCLIC', kappa='unchanged')
    for name in ['budgets', 'certified', 'weighted', 'grouped', 'controls', 'kernel_bridge']:
        result[name] = loaded[name].main()
    result['scope'] = ('Four higher-order classical cyclic inverse calls with one arbitrary dirty connector, '
                       'cubic data precision and an explicitly paid scalar solve/preparation term. '
                       'No bit-reversible arithmetic, common-label, full transform, or multiplication-exponent claim.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='authoring: create a fresh receipt, never overwrite')
    parser.add_argument('--out', type=Path, help='verify the committed receipt and write a fresh copy')
    parser.add_argument('--bindings-only', action='store_true', help='package/source checks; no mathematics replay')
    args = parser.parse_args()
    require(sum(bool(v) for v in (args.write, args.out, args.bindings_only)) <= 1, 'choose one mode')
    destination = args.write or args.out
    if destination:
        require(not destination.exists(), 'output already exists')
        require(not destination.resolve().is_relative_to(P), 'output must be outside the source package')
    pins = bindings(authoring=args.write is not None)
    if args.bindings_only:
        print('PASS_GROUPED_BINDINGS sources='+str(pins['files']))
        return
    result = calculate()
    result['sources'] = pins
    if not args.write:
        require(canonical(result) == canonical(read_json(P/'EXPECTED.json')), 'mathematical receipt mismatch')
    if destination:
        with destination.open('x') as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True, default=str)+'\n')
    print('PASS_GROUPED_DIRTY_CYCLIC real=160 weighted=40 mixed=120 kernels=48 budgets=2313 controls=16 kappa=unchanged')


if __name__ == '__main__':
    main()
