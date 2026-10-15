#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export two exact public Git packages, retaining source bytes and notices."""
import argparse
import io
import subprocess
import tarfile
from pathlib import Path
from common import HERE, check_source, read, require

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    pins = read(HERE / 'PREDECESSORS.json')
    for number, pin in pins['sources'].items():
        commit = pin['commit']
        have = subprocess.run(['git', '-C', str(args.repo), 'cat-file', '-e', commit + '^{commit}'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not have:
            subprocess.run(['git', '-C', str(args.repo), 'fetch', '--no-tags',
                            'https://github.com/' + pins['repository'] + '.git', commit], check=True)
        data = subprocess.check_output(['git', '-C', str(args.repo), 'archive', commit,
                                        pin['package'], 'LICENSE', 'NOTICE'])
        root = output / ('pr' + number)
        root.mkdir()
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for item in archive:
                name = Path(item.name)
                require(not name.is_absolute() and '..' not in name.parts, 'Unsafe archive path')
                if item.isdir():
                    continue
                require(item.isfile(), 'Unexpected source object')
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.extractfile(item).read())
        check_source(root / pin['package'], number)
        print('PASS_IMMUTABLE_SOURCE_EXPORT', number, commit, flush=True)

if __name__ == '__main__':
    main()
