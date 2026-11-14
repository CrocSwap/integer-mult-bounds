#!/usr/bin/env python3
"""Authenticate retained sources and reconstruct the published candidate.

Hao Yan (@FanPUYen), substantial OpenAI Codex assistance. Apache-2.0.
The other registered commands establish the separate mathematical obligations.
"""
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import zipfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    versions = json.loads((HERE / 'SOURCE-VERSIONS.json').read_bytes())
    paths = set()
    for row in versions['files']:
        path = HERE / row['path']
        require(row['path'] not in paths, 'duplicate source manifest path')
        paths.add(row['path'])
        require(not path.is_symlink() and path.resolve().is_relative_to(HERE / 'retained'),
                'retained source path')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'immutable retained source: ' + row['path'])
    present = {p.relative_to(HERE).as_posix() for p in (HERE / 'retained').rglob('*')
               if p.is_file() and '__pycache__' not in p.parts}
    require(paths == present, 'source manifest covers every retained file')
    # These convenience copies are authenticated members of the unchanged
    # published7603 archive, not new Git-history dependencies.
    with zipfile.ZipFile(HERE / 'retained/two-contractions/published/replay.zip') as archive:
        for row in versions['files']:
            if 'archive_member' in row:
                require(archive.read(row['archive_member']) == (HERE / row['path']).read_bytes(),
                        'published archive member: ' + row['path'])
    builder = runpy.run_path(str(HERE / 'build.py'))
    candidate = json.loads(gzip.decompress((HERE / 'data/word.json.gz').read_bytes()))
    require(candidate == builder['build_word'](), 'exact constructed word')
    require(json.loads((HERE / 'data/invoice-new.json').read_bytes()) == builder['invoice'](),
            'exact reconstructed complete invoice')
    # Compressed container bytes are not a cross-environment equality test.
    alternate = gzip.compress(json.dumps(candidate).encode(), compresslevel=1, mtime=123)
    require(alternate != (HERE / 'data/word.json.gz').read_bytes(), 'different gzip control')
    require(json.loads(gzip.decompress(alternate)) == candidate, 'same mathematical word')
    print(json.dumps({'status': 'PASS_ROLE315_SOURCE_AND_CONSTRUCTION',
                      'retained_files': len(paths), 'events': len(candidate['program']),
                      'candidate_canonical_sha256': hashlib.sha256(json.dumps(
                          candidate, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                      'gzip_payload_equality_control': True}, indent=2))


if __name__ == '__main__':
    main()
