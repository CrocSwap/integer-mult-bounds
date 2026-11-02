"""Trusted metadata-only mode restoration for this exact source export.

No target imports, compilation, tests or execution. Authenticate this helper
against the publication commit before use. No concurrent filesystem mutation
is supported; this is not an atomic filesystem snapshot or runtime admission.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat

MANIFEST_SHA256 = '159a85d5fd9c06d80c30635a7be27ef102be5943c75cff144cbe05bed85edd7e'
MANIFEST_BYTES = 10376
HERE = Path(__file__).absolute().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def checked_path(root, name):
    relative = Path(name)
    require(not relative.is_absolute() and bool(relative.parts) and
            '..' not in relative.parts and str(relative) == name,
            'Unsafe source path: ' + name)
    current = root
    require(not current.is_symlink(), 'Symlink source root')
    for part in relative.parts:
        current = current / part
        require(not current.is_symlink(), 'Symlink source ancestry: ' + name)
    require(current.is_file(), 'Missing source: ' + name)
    require(stat.S_ISREG(current.stat().st_mode), 'Nonregular source: ' + name)
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', required=True,
                        help='Restore authenticated declared modes after checking all bytes')
    parser.parse_args()
    require(not any(path.is_symlink() for path in (HERE, *HERE.parents)),
            'Symlink package ancestry')
    manifest = checked_path(HERE, 'component/SOURCE-PINS.json')
    raw = manifest.read_bytes()
    require(len(raw) == MANIFEST_BYTES and hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256,
            'Accepted manifest identity changed')
    pins = json.loads(raw)
    require(pins['schema'] == 'inventory-component-source-pins-v1' and
            len(pins['package']) == 11 and len(pins['external']) == 36,
            'Manifest schema/census changed')
    rows = [('component/SOURCE-PINS.json',
             {'sha256': MANIFEST_SHA256, 'bytes': MANIFEST_BYTES, 'mode': 0o664})]
    rows += [('component/' + name, info) for name, info in sorted(pins['package'].items())]
    for name, info in sorted(pins['external'].items()):
        require('/runtime/' not in name and
                (name.startswith('outputs/h25-bookkeeping-swarm-20261028/stages/v4/') or
                 name in ('outputs/h25-data-handling-20261028/areas/hashing-traces/API.md',
                          'outputs/h25-data-handling-20261028/areas/hashing-traces/inventory_controls.py')),
                'External path outside accepted source scope')
        rows.append(('workspace/' + name, info))
    component = HERE / 'component'
    entries = list(component.rglob('*'))
    require(not any(path.is_symlink() for path in entries), 'Component symlink')
    require({str(path.relative_to(component)) for path in entries if path.is_file()} ==
            set(pins['package']) | {'SOURCE-PINS.json'}, 'Component file census changed')
    authenticated = []
    for name, info in rows:
        require(info['mode'] in (0o444, 0o664), 'Unexpected declared source mode')
        path = checked_path(HERE, name)
        payload = path.read_bytes()
        require(len(payload) == info['bytes'] and hashlib.sha256(payload).hexdigest() == info['sha256'],
                'Source identity changed: ' + name)
        authenticated.append((path, info))
    # All file bytes authenticate before the first mutation. Only these exact
    # 48 declared files are touched; original workspace and review files are not.
    for path, info in authenticated:
        path.chmod(info['mode'])
    for path, info in authenticated:
        require(stat.S_IMODE(path.stat().st_mode) == info['mode'], 'Mode restoration failed')
        payload = path.read_bytes()
        require(len(payload) == info['bytes'] and hashlib.sha256(payload).hexdigest() == info['sha256'],
                'Source identity changed during restoration')
    print(json.dumps({'status': 'DECLARED_SOURCE_MODES_RESTORED', 'files': len(authenticated),
                      'manifest_sha256': MANIFEST_SHA256, 'target_execution': False}, sort_keys=True))


if __name__ == '__main__':
    main()
