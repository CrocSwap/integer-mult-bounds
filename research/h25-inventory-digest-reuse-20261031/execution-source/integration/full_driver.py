"""Fixed inventory component operations under unchanged parent guard.

Source/runtime/external custody repeats after success or failure. Trusted local
CPython host, no hostile concurrent mutation or whole-H25 attestation claim.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

STAGE = Path(__file__).resolve().parents[1]
PACKAGE = STAGE / 'package'
WORKSPACE = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
PACKAGE_SHA256 = '159a85d5fd9c06d80c30635a7be27ef102be5943c75cff144cbe05bed85edd7e'
LOCAL = ('component_consumer', 'reference', 'candidate', 'inventory_controls', 'digest_controls')
ENV = {'PYTHONHASHSEED': '0', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC',
       'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1', 'PYTHONSAFEPATH': '1'}
LANES = {'inventory-controls': 'controls', 'inventory-baseline': 'baseline',
         'inventory-candidate': 'candidate'}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def small(path):
    with path.open('rb') as stream:
        raw = stream.read(1048577)
    need(len(raw) <= 1048576, 'Custody metadata exceeded1MiB')
    return raw


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def file_pin(path):
    need(path.is_absolute() and path.resolve() == path, 'Pin path must be resolved absolute')
    before = path.lstat()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb', buffering=0) as stream:
        opened = os.fstat(stream.fileno())
        need(stat.S_ISREG(opened.st_mode), 'Pin is not a regular file')
        count, hasher = 0, hashlib.sha256()
        while count < opened.st_size:
            raw = stream.read(min(1048576, opened.st_size - count))
            need(bool(raw), 'Pinned file ended early')
            hasher.update(raw)
            count += len(raw)
        after = os.fstat(stream.fileno())
    need(identity(before) == identity(opened) == identity(after) == identity(path.lstat()),
         'Pinned file changed while hashing')
    return {'bytes': count, 'sha256': hasher.hexdigest()}


def payload_pin(path, pin):
    need(file_pin(path) == {'bytes': pin['bytes'], 'sha256': pin['sha256']} and
         stat.S_IMODE(path.stat().st_mode) == pin['mode'], 'Payload changed: ' + str(path))


def origins(runtime):
    observed = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, '__file__', None)
        if filename is None:
            continue
        actual = str(Path(filename).resolve())
        if name == '__main__':
            expected = str(Path(__file__).resolve())
        elif name in LOCAL:
            expected = str(PACKAGE / (name + '.py'))
        else:
            expected = runtime['module_paths'].get(name)
        need(actual == expected, 'Unadmitted file-backed module origin: ' + name)
        observed[name] = actual
    return observed


def package_pins():
    package_raw = small(PACKAGE / 'SOURCE-PINS.json')
    need(hashlib.sha256(package_raw).hexdigest() == PACKAGE_SHA256, 'Inventory manifest changed')
    package = json.loads(package_raw)
    need(package['schema'] == 'inventory-component-source-pins-v1', 'Package schema differs')
    need(len(package['package']) == 11 and len(package['external']) == 36,
         'Package/external source count differs')
    return package


def custody(anchor):
    need(small(STAGE / 'RUNTIME-PINS.sha256') == anchor, 'Runtime anchor changed')
    expected_runtime = anchor.decode('ascii').strip()
    need(len(expected_runtime) == 64 and all(c in '0123456789abcdef' for c in expected_runtime),
         'Malformed parent runtime anchor')
    runtime_raw = small(STAGE / 'RUNTIME-PINS.json')
    need(hashlib.sha256(runtime_raw).hexdigest() == expected_runtime,
         'Runtime manifest differs from independent parent anchor')
    runtime = json.loads(runtime_raw)
    need(runtime['schema'] == 'inventory-finite-runtime-pins-v1', 'Runtime schema differs')
    need(runtime['python_version'] == sys.version and
         runtime['executable_realpath'] == str(Path(sys.executable).resolve()) == '/usr/bin/python3.12',
         'Interpreter differs from parent runtime')
    need(runtime['environment'] == ENV and all(os.environ.get(k) == v for k, v in ENV.items()),
         'Finite environment differs')
    need(not any(name in os.environ for name in
         ('PYTHONPATH', 'PYTHONOPTIMIZE', 'PYTHONINSPECT', 'PYTHONSTARTUP', 'PYTHONPYCACHEPREFIX')),
         'Forbidden Python startup environment')
    need(sys.flags.no_user_site == 1 and sys.flags.safe_path and sys.dont_write_bytecode,
         'Required finite startup flags absent')
    package = package_pins()
    actual_paths = set()
    for path in PACKAGE.rglob('*'):
        need(not path.is_symlink(), 'Symlink in frozen inventory package')
        if path.is_file():
            actual_paths.add(str(path.relative_to(PACKAGE)))
    need(actual_paths == set(package['package']) | {'SOURCE-PINS.json'}, 'Package file census changed')
    for relative, pin in sorted(package['package'].items()):
        payload_pin(PACKAGE / relative, pin)
    for relative, pin in sorted(package['external'].items()):
        path = Path(relative)
        need(not path.is_absolute() and '..' not in path.parts, 'Unsafe external source path')
        payload_pin(WORKSPACE / path, pin)
    for filename, pin in sorted(runtime['files'].items()):
        need(file_pin(Path(filename)) == pin, 'Runtime file changed: ' + filename)
    return {'runtime_manifest_sha256': expected_runtime, 'runtime_file_count': len(runtime['files']),
            'inventory_manifest_sha256': PACKAGE_SHA256, 'inventory_payload_files': len(package['package']),
            'external_source_files': len(package['external']), 'immutable_workspace': str(WORKSPACE),
            'module_origins': origins(runtime), 'assumptions': runtime['assumptions']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lanes', choices=tuple(LANES), required=True)
    parser.add_argument('--finite-only', action='store_true')
    args = parser.parse_args()
    need(args.finite_only, 'This adapter admits only fixed inventory operations')
    mode = LANES[args.lanes]
    need(sys.flags.optimize in ((0, 1) if mode == 'controls' else (0,)), 'Undeclared optimization mode')
    need(args.output.is_absolute() and args.output.resolve() == args.output, 'Resolved absolute output required')
    need(not args.output.exists() and not args.output.is_relative_to(STAGE), 'Fresh output outside stage required')
    # Reject overlap before creating anything. No source file or parent is used
    # as scratch; the parent separately freezes this exact output binding.
    package = package_pins()
    need(all(not args.output.is_relative_to((WORKSPACE / relative).parent)
             for relative in package['external']), 'Output overlaps external source root')
    args.output.mkdir(parents=True)
    scratch = args.output / 'component' / 'scratch'
    boundary = {'scope': 'Inventory-only finite host; no full H25/caller/native/publication speedup',
                'mode': mode, 'fixture_files': None if mode == 'controls' else 32,
                'fixture_bytes': None if mode == 'controls' else 453700,
                'inventory_calls': None if mode == 'controls' else 128,
                'python_version': sys.version, 'executable': sys.executable,
                'executable_realpath': str(Path(sys.executable).resolve()),
                'optimization': sys.flags.optimize, 'no_user_site': sys.flags.no_user_site,
                'safe_path': sys.flags.safe_path, 'dont_write_bytecode': sys.dont_write_bytecode,
                'environment': {key: os.environ.get(key) for key in ENV}, 'status': 'STARTED'}
    primary, post_error, anchor = None, None, None
    try:
        anchor = small(STAGE / 'RUNTIME-PINS.sha256')
        boundary['before'] = custody(anchor)
        need(not any(name in sys.modules for name in LOCAL), 'Component module preloaded')
        sys.path.insert(0, str(PACKAGE))
        import component_consumer
        need(Path(component_consumer.__file__).resolve() == PACKAGE / 'component_consumer.py',
             'Actual consumer source differs')
        receipt = component_consumer.run(mode, WORKSPACE, args.output / 'component')
        expected_status = ('INVENTORY_COMPONENT_CONTROLS_RETURNED' if mode == 'controls'
                           else 'INVENTORY_REPRESENTATIVE_COMPONENT_RETURNED')
        need(receipt['status'] == expected_status and receipt['cleanup_complete'] is True,
             'Component return/cleanup was not accepted')
        need(receipt['mode'] == mode and receipt['optimization'] == sys.flags.optimize,
             'Component mode changed')
        boundary['component_status'] = receipt['status']
        boundary['status'] = 'FINITE_INVENTORY_COMPONENT_RETURNED'
    except BaseException as error:
        primary = error
        boundary['status'] = 'PRIMARY_ERROR'
        boundary['primary_error_type'] = type(error).__name__
        raise
    finally:
        try:
            need(anchor is not None, 'Runtime anchor was not obtained')
            boundary['after'] = custody(anchor)
        except BaseException as error:
            post_error = error
            boundary['postcheck_error_type'] = type(error).__name__
            if primary is None:
                boundary['status'] = 'POSTCHECK_ERROR'
        try:
            boundary['component_cleanup'] = {'scratch_path': str(scratch),
                                             'scratch_exists_after': scratch.exists(),
                                             'component_directory_exists': (args.output / 'component').exists()}
            need(not scratch.exists(), 'Component scratch cleanup incomplete')
        except BaseException as error:
            boundary['cleanup_error_type'] = type(error).__name__
            if post_error is None:
                post_error = error
            if primary is None:
                boundary['status'] = 'POSTCHECK_ERROR'
        try:
            raw = (json.dumps(boundary, sort_keys=True, indent=2) + '\n').encode('utf-8')
            path = args.output / 'adapter-boundary.json'
            path.write_bytes(raw)
            need(path.read_bytes() == raw, 'Adapter boundary readback differs')
        except BaseException:
            if primary is None and post_error is None:
                raise
        if primary is None and post_error is not None:
            raise post_error
    print(json.dumps({'status': boundary['status'], 'mode': mode,
                      'optimization': sys.flags.optimize}, sort_keys=True))


if __name__ == '__main__':
    main()
