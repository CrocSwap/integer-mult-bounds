#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Load the minimal immutable predecessor closure without Git or network access."""
from contextlib import contextmanager
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def checked_bytes(raw, expected, label):
    require(hashlib.sha256(raw).hexdigest() == expected, 'source hash: ' + label)
    return raw


def module(name, path):
    spec = importlib.util.spec_from_file_location('p104_composition_' + name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


@contextmanager
def predecessor():
    inventory = json.loads((HERE / 'SOURCES.json').read_text())
    pin, = inventory['archives']
    raw = checked_bytes((HERE / pin['path']).read_bytes(), pin['sha256'], pin['path'])
    expected = {m['path']: m for m in pin['members']}
    require(len(expected) == len(pin['members']) == 11, 'predecessor member inventory')
    with tempfile.TemporaryDirectory(prefix='p104-coalesced-reuse-') as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
            members = archive.getmembers()
            require(len(members) == len(expected) and {m.name for m in members} == set(expected),
                    'archive member coverage')
            for member in members:
                path = PurePosixPath(member.name)
                require(member.isfile() and not path.is_absolute() and '..' not in path.parts,
                        'unsafe archive member')
                data = checked_bytes(archive.extractfile(member).read(),
                                     expected[member.name]['sha256'], member.name)
                target = root / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        for entry in inventory['files']:
            if entry['usage'] != 'input':
                continue
            data = checked_bytes((ROOT / entry['path']).read_bytes(), entry['sha256'], entry['path'])
            target = root / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        yield root / 'research/p104-interleaved-search'
