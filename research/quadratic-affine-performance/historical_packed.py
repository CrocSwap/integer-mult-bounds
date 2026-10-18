#!/usr/bin/env python3
"""Authenticated historical PR752 replay alongside the PR1076 production engine.

Douglas Colkitt, with OpenAI Codex assistance; Apache-2.0.
Curtis Dransfield's original package and its frozen pins remain unchanged.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = 'research/quadratic-affine-packed/SOURCES.json'
SUCCESS = 'PASS_QUADRATIC_AFFINE_DIFFERENTIAL all_frozen_rows_equal=true cases=12'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, name):
    p = PurePosixPath(name)
    require(bool(p.parts) and not p.is_absolute() and '..' not in p.parts
            and ':' not in name and '\\' not in name, 'Unsafe input path')
    f = root.joinpath(*p.parts)
    require(not f.is_symlink(), 'Symlink input')
    return f


def historical_blob(root, base, name):
    return subprocess.check_output(['git', 'show', base + ':' + name], cwd=root)


def materialize(root, destination, config, fetch=historical_blob):
    require(not destination.exists(), 'Snapshot already exists')
    raw = safe(root, MANIFEST).read_bytes()
    require(digest(raw) == config['manifest_sha256'], 'Changed predecessor manifest')
    manifest = json.loads(raw)
    require(manifest['base_commit'] == config['base_commit'], 'Changed historical base')
    require(set(config['accepted_live']) <= set(manifest['files']), 'Unknown live replacement')
    data = {}
    for name, pin in manifest['files'].items():
        live = safe(root, name).read_bytes()
        if digest(live) == pin:
            data[name] = live
        else:
            require(digest(live) in config['accepted_live'].get(name, []),
                    'Unrecognized live source: ' + name)
            old = fetch(root, config['base_commit'], name)
            require(digest(old) == pin, 'Changed historical blob: ' + name)
            data[name] = old
    require(MANIFEST in config['package_files'], 'Manifest not in copied package')
    for name, pin in config['package_files'].items():
        require(name not in data, 'Overlapping historical/package input')
        raw = safe(root, name).read_bytes()
        require(digest(raw) == pin, 'Changed predecessor package: ' + name)
        data[name] = raw
    destination.mkdir(parents=True)
    for name, raw in data.items():
        f = safe(destination, name)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(raw)
    expected = {name: digest(raw) for name, raw in data.items()}
    verify_unchanged(destination, expected)
    return expected


def verify_unchanged(root, expected):
    for name, pin in expected.items():
        f = safe(root, name)
        require(f.is_file() and digest(f.read_bytes()) == pin, 'Changed replay input: ' + name)


def check_completion(code, output):
    require(code == 0 and output.splitlines()[-1:] == [SUCCESS],
            'Incomplete historical replay')


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled for inherited checks')
    config = json.loads((HERE / 'HISTORICAL-PACKED.json').read_text())
    with tempfile.TemporaryDirectory(prefix='quadratic-affine-history-') as tmp:
        root = Path(tmp) / 'snapshot'
        expected = materialize(ROOT, root, config)
        p = subprocess.run([sys.executable, '-B', 'research/quadratic-affine-packed/verify.py'],
                           cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(p.stdout, end='', flush=True)
        verify_unchanged(root, expected)
        check_completion(p.returncode, p.stdout)
    print('PASS_AUTHENTICATED_HISTORICAL_PACKED_REPLAY unchanged_pins=true')


if __name__ == '__main__':
    main()
