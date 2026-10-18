#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export exact public Git source packages and check their frozen manifests."""
import argparse
import io
import subprocess
import tarfile
from pathlib import Path
from full_replay import check_source
from verify import P, read, require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True, help='An existing repository checkout')
    parser.add_argument('--out', type=Path, required=True, help='A new directory')
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    pins = read(P / 'PREDECESSORS.json')
    remote = 'https://github.com/' + pins['repository'] + '.git'
    for pr, pin in pins['sources'].items():
        commit = pin['commit']
        available = subprocess.run(['git', '-C', str(args.repo), 'cat-file', '-e', commit + '^{commit}'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not available:
            subprocess.run(['git', '-C', str(args.repo), 'fetch', '--no-tags', remote, commit], check=True)
        data = subprocess.check_output(['git', '-C', str(args.repo), 'archive', commit,
                                        pin['package'], 'LICENSE', 'NOTICE'])
        root = output / ('pr' + pr)
        root.mkdir()
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for item in archive:
                relative = Path(item.name)
                require(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe archive path')
                if item.isdir():
                    continue
                require(item.isfile(), 'Unexpected non-file source object')
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(item).read())
        check_source(root, pin)
        print('PASS_IMMUTABLE_SOURCE_EXPORT', pr, commit, flush=True)


if __name__ == '__main__':
    main()
