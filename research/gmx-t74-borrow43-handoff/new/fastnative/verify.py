#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Fresh complete native replay against the pinned PR2751 reference outputs."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, need, sha, source_bytes
from compare import canonical, normalized


def main():
    need(__debug__, 'assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=('base', 'extra'), default='base')
    parser.add_argument('--relocate', action='store_true', help='replay a Git-free copy in a path with spaces')
    args = parser.parse_args()
    if args.relocate:
        with tempfile.TemporaryDirectory(prefix='t74-relocate-') as temporary:
            root = Path(temporary)
            package = root / 'package with spaces'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            need(not (root / '.git').exists(), 'Git-free relocation')
            subprocess.run([sys.executable, '-I', '-B', str(package / 'verify.py'),
                            '--provider', args.provider], cwd=root, check=True)
        print('PASS_T74_NATIVE_FAST_GIT_FREE_RELOCATION', args.provider)
        return
    source_bytes(HERE / 'vendor')
    word = HERE / f'fixtures/WORD-{args.provider}.json.gz'
    pins = json.loads((HERE / 'PINS.json').read_text())
    need(sha(word.read_bytes()) == pins[word.relative_to(HERE).as_posix()], 'fixture digest')
    expected = json.loads((HERE / 'EXPECTED.json').read_text())[args.provider]
    with tempfile.TemporaryDirectory(prefix='t74-native-fast-') as temporary:
        work = Path(temporary) / 'replay'
        subprocess.run([sys.executable, '-I', '-B', str(HERE / 'run_native.py'),
                        str(word), str(work)], check=True)
        local = work / 'native/local'
        output = normalized(local)
        need(sha(canonical(output)) == expected['normalized_sha256'], 'all native outputs match reference')
        need(sha((local / 'CLIFFORD-RECIPES.json').read_bytes()) == expected['recipe_bytes_sha256'], 'recipe bytes')
        need(output['WARP-RECIPE-CHECKS.json'] == expected['coverage'], 'independent warp coverage')
        if args.provider == 'base':
            from controls import check
            check(local)
    print('PASS_T74_NATIVE_FAST_REFERENCE_AND_CONTROLS', args.provider)


if __name__ == '__main__':
    main()
