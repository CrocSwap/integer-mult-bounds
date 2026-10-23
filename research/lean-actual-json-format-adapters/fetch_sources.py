#!/usr/bin/env python3
"""Materialize the manifest's exact public/local sources in fresh scratch; never run Lean."""
from pathlib import Path
from urllib.request import urlopen
import argparse
import hashlib
import json
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path, help='published package directory containing SOURCE_MANIFEST.json and sources/')
    parser.add_argument('scratch', type=Path, help='new, nonexistent scratch directory')
    args = parser.parse_args()
    package = args.package.resolve()
    manifest = json.loads((package / 'SOURCE_MANIFEST.json').read_text())
    local = {x['module']: x for x in manifest['new_modules']}
    public = {x['module']: x for x in manifest['public_prerequisites']}
    order = manifest['topological_order']
    assert len(local) == 4 and len(public) == 9 and not (local.keys() & public.keys())
    assert len(order) == 13 and len(set(order)) == 13
    assert set(order) == local.keys() | public.keys()
    position = {name: i for i, name in enumerate(order)}
    for name, imports in manifest['research_imports'].items():
        assert all(position[dep] < position[name] for dep in imports)
    scratch = args.scratch.resolve()
    scratch.mkdir(parents=False, exist_ok=False)
    source_dir = scratch / 'src'
    source_dir.mkdir()
    fetched = []
    for name in order:
        if name in local:
            entry = local[name]
            path = package / entry['path']
            assert path.resolve().is_relative_to(package)
            data = path.read_bytes()
        else:
            entry = public[name]
            assert re.fullmatch(r'[0-9a-f]{40}', entry['head'])
            assert entry['repository'] == 'jamesyc/integer-mult-bounds'
            assert not entry['path'].startswith('/') and '..' not in Path(entry['path']).parts
            url = f"https://raw.githubusercontent.com/{entry['repository']}/{entry['head']}/{entry['path']}"
            with urlopen(url, timeout=60) as response:
                data = response.read()
        assert len(data) == entry['bytes'], f'{name}: byte count mismatch'
        assert hashlib.sha256(data).hexdigest() == entry['sha256'], f'{name}: SHA256 mismatch'
        imports = [word for line in data.decode('utf-8').splitlines() if line.startswith('import ')
                   for word in line[len('import '):].split()]
        research = [word for word in imports if word in position]
        assert research == manifest['research_imports'][name], f'{name}: research imports changed'
        assert all(word in position or word in manifest['official_import_roots'] for word in imports), f'{name}: unexpected import'
        with (source_dir / f'{name}.lean').open('xb') as handle:
            handle.write(data)
        fetched.append({'module': name, 'bytes': len(data), 'sha256': entry['sha256']})
    (scratch / 'module-order.txt').write_text(''.join(name + '\n' for name in order))
    (scratch / 'SOURCE_READBACK.json').write_text(json.dumps(fetched, indent=2) + '\n')
    print(f'Verified {len(fetched)} exact sources in {source_dir}; no compiler was run.')


if __name__ == '__main__':
    main()
