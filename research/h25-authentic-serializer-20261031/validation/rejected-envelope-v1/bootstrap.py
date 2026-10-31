"""Run a fixed target in the same interpreter as effective runtime checks.

This module is entered only from the inclusive observer. All imports and checks
here are inside that boundary. Runtime manifests are independently frozen, never
learned from a successful target or amended after a failure.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gzip
import hashlib
import importlib
import json
import os
from effective import capture, unchanged
import zlib
from custody import check_snapshot, need, pin, read_json, safe, same, write_json


def mappings():
    paths = set()
    for line in Path('/proc/self/maps').read_text().splitlines():
        row = line.split(maxsplit=5)
        if len(row) == 6 and row[5].startswith('/'):
            need(not row[5].endswith(' (deleted)'), 'deleted runtime mapping')
            paths.add(str(Path(row[5]).resolve()))
    return paths


def callable_bindings():
    import _json
    import _hashlib
    selected = {'gzip.GzipFile': gzip.GzipFile, 'zlib.decompressobj': zlib.decompressobj,
                'zlib.crc32': zlib.crc32, 'json.loads': json.loads, 'json.dumps': json.dumps,
                '_json.make_scanner': _json.make_scanner, '_json.make_encoder': _json.make_encoder,
                'hashlib.sha256': hashlib.sha256, '_hashlib.openssl_sha256': _hashlib.openssl_sha256}
    names = {name: {'module': getattr(obj, '__module__', None),
                    'qualname': getattr(obj, '__qualname__', getattr(obj, '__name__', None)),
                    'type_module': type(obj).__module__, 'type_name': type(obj).__name__}
             for name, obj in selected.items()}
    return selected, names


def closure(runtime, package, entry, main_path=None):
    # Source-bound lazy initialization is paid setup before effective sealing.
    # tempfile's first gettempdir/name-sequence otherwise legitimately rebinds
    # globals during the first target mkdtemp and creates false drift.
    import tempfile
    need(tempfile.gettempdir() == '/tmp', 'unexpected effective temp directory')
    tempfile._get_candidate_names()
    need(all(name in sys.builtin_module_names for name in runtime['required_builtin_modules']),
         'required actual builtin provider missing')
    need(Path(sys.executable).resolve() == Path(runtime['executable']), 'interpreter mismatch')
    need(sys.version == runtime['python_version'], 'interpreter version mismatch')
    need(sys.flags.isolated == 1 and sys.flags.dont_write_bytecode == 1 and sys.flags.no_site == 1, 'isolated -B -S required')
    need(zlib.__spec__.origin == 'built-in' and 'zlib' in sys.builtin_module_names,
         'actual builtin zlib provider required; no fictional extension')
    need(gzip.zlib is zlib, 'gzip provider differs')
    need(runtime['builtin_zlib_provider'] == runtime['executable'], 'builtin provider pin differs')
    for filename, expected in sorted(runtime['files'].items()):
        same(Path(filename), expected)
    observed = {}
    for name, module in sorted(tuple(sys.modules.items())):
        if module is None:
            continue
        filename = getattr(module, '__file__', None)
        if filename is None:
            spec = getattr(module, '__spec__', None)
            origin = getattr(spec, 'origin', None)
            need(origin in ('built-in', 'frozen') and
                 (origin == 'frozen' or name in sys.builtin_module_names), 'unsealed no-file module: ' + name)
            continue
        actual = str(Path(filename).resolve())
        if name == '__main__':
            expected = str(Path(main_path or __file__).resolve())
        elif name == 'o03_entry':
            expected = str(entry)
        elif actual.startswith(str(package) + '/'):
            relative = str(Path(actual).relative_to(package))
            need(relative in runtime['package_modules'].values(), 'undeclared package module: ' + name)
            need(name in runtime['package_modules'], 'unsealed package module alias: ' + name)
            expected = str(package / runtime['package_modules'][name])
        else:
            expected = runtime['module_paths'].get(name)
        need(actual == expected, 'unexpected runtime module origin: ' + name + '=' + actual)
        observed[name] = actual
    actual_maps = mappings()
    need(actual_maps <= set(runtime['mapped_files']), 'unsealed mapped files: ' + repr(sorted(actual_maps - set(runtime['mapped_files']))))
    need(runtime['linked_libz'] in actual_maps, 'actual linked libz missing')
    objects, descriptors = callable_bindings()
    need(descriptors == runtime['callable_bindings'], 'selected implementation binding mismatch')
    return {'module_origins': observed, 'mapped_files': sorted(actual_maps),
            'builtin_zlib_provider': runtime['builtin_zlib_provider'], 'linked_libz': runtime['linked_libz'],
            'selected_callable_bindings': descriptors}, objects


def main():
    need(len(sys.argv) == 3, 'bootstrap requires request and exact request digest')
    request = read_json(Path(sys.argv[1]), sys.argv[2])
    runtime = read_json(Path(request['runtime_manifest']), request['runtime_sha256'])
    package = safe(Path(request['package_custody']['root']))
    entry = safe(package / request['entry'])
    need(request['entry'] in request['package_custody']['files'], 'unsealed target entry')
    check_snapshot(request['package_custody'])
    report = {'schema': 'o03-effective-runtime-v1', 'status': 'STARTED', 'errors': []}
    before_objects = None
    effective_before = None
    try:
        # Freeze imports used by all execution branches, including conditional helpers.
        for filename, expected in runtime['files'].items():
            same(Path(filename), expected)
        for name in runtime['preload_modules']:
            importlib.import_module(name)
        # Import the entry without running its guarded main, then freeze actual
        # effective package bindings and execute exactly its reviewed main().
        sys.path.insert(0, str(entry.parent))
        sys.path.insert(1, str(package / 'loader'))
        spec = importlib.util.spec_from_file_location('o03_entry', entry)
        entry_module = importlib.util.module_from_spec(spec)
        sys.modules['o03_entry'] = entry_module
        spec.loader.exec_module(entry_module)
        report['before'], before_objects = closure(runtime, package, entry)
        effective_before = capture(dict(sys.modules))
        report['effective_before'] = effective_before
        sys.argv = [str(entry), *request['argv']]
        entry_module.main()
        report['target_returned'] = True
    except SystemExit as error:
        report['target_exit'] = error.code
        if error.code not in (0, None):
            report['errors'].append({'type': 'SystemExit', 'message': str(error.code)})
    except BaseException as error:
        report['errors'].append({'type': type(error).__name__, 'message': str(error)})
    finally:
        try:
            report['after'], after_objects = closure(runtime, package, entry)
            report['effective_after'] = capture(dict(sys.modules))
            need(effective_before is not None, 'effective before seal absent')
            unchanged(effective_before, report['effective_after'])
            need(before_objects is not None and all(after_objects[k] is v for k, v in before_objects.items()),
                 'callable rebound during target')
            check_snapshot(request['package_custody'])
        except BaseException as error:
            report['errors'].append({'check': 'after', 'type': type(error).__name__, 'message': str(error)})
        report['status'] = 'PASS' if not report['errors'] else 'STOP'
        write_json(Path(request['runtime_report']), report)
    need(report['status'] == 'PASS', 'effective runtime/target failure')


if __name__ == '__main__':
    main()
