#!/usr/bin/env python3
"""Replay frozen checks against authenticated historical inputs in a temporary copy.

Dennis, with substantial OpenAI Codex assistance; Apache-2.0.
The checkers, their pins, and the live selected record remain unchanged.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INPUTS = Path(__file__).with_name('historical-ci-inputs')
# Each replacement must also match the unchanged predecessor manifest.
CONFIG = {
    'r420': {
        'manifest': 'research/r420-two-sided-basis/SOURCES.json',
        'field': 'files',
        'path': 'certificates/selected-result.json',
        'input': 'selected-result.json',
        'sha256': 'b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53',
        'commands': [['research/r420-two-sided-basis/verify.py'],
                     ['-m', 'unittest', 'discover', '-s', 'research/r420-two-sided-basis', '-p', 'test_*.py']],
    },
    'reconciliation92': {
        'manifest': 'research/community-reconciliation92-audit/MANIFEST.json',
        'field': 'integrated_files',
        'preserve_prefix': True,
        'path': 'Makefile',
        'input': 'Makefile',
        'sha256': 'ea8830dd79da493e2d75baf753d733ff7efbcf2b4794afe41fae0ac8f3055646',
        'commands': [['research/community-reconciliation92-audit/verify.py']],
    },
    'split-skip': {
        'manifest': 'research/split-skip/SOURCE.json',
        'field': 'files',
        'path': 'scripts/audit_fused_block.py',
        'input': 'audit_fused_block.py',
        'sha256': '2afb83ca8e5f193ca8a4c242becf267ad1d9dc2578ba238b820e98d5185f6288',
        'commands': [['research/split-skip/producer.py', '--work-dir', 'build/split-skip',
                      '--output', 'build/split-skip-receipt.json'],
                     ['research/split-skip/witness.py'],
                     ['research/split-skip/independent_arithmetic.py'],
                     ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_split_skip.py', '-v']],
    },
}


# Keep PR53's frozen source pin intact while replaying against the reviewed
# successor of the faster exclusion support-mask checker. Original exact bytes
# are retained by the linked baseline package (Wentao Li / VictorLiwentao).
# Dennis with substantial OpenAI Codex assistance; Apache-2.0.
CONFIG['skip-clones'] = {
    'manifest': 'research/skip-clones/SOURCE.json',
    'field': 'files',
    'path': 'scripts/exclusion_circuit.py',
    'input_from_root': True,
    'input': 'research/exclusion-embedding-masks/baseline.py',
    'sha256': 'b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0',
    'accepted_live_sha256': [
        'f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3',
    ],
    'additional_inputs': [{
        'manifest': 'research/skip-clones/SOURCE.json', 'field': 'files',
        'path': 'scripts/partial_swap/shared.py', 'input_from_root': True,
        'input': 'research/partial-swap-digest/baseline.py',
        'sha256': '81e9af92cdf38243a540cdcff2062778e449467848d444da37a9553c12ca4c34',
        # Wentao Li's retained digest and initialization successors.
        'accepted_live_sha256': [
            'b27c8bfe1de3f7d2d5fb19ac742adf11597c2aaa7add68430443119997e646e8',
            '7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c',
        ],
    }],
    'commands': [
        ['research/skip-clones/producer.py'],
        ['research/skip-clones/witness.py', '--output',
         'research/skip-clones/certificate.json'],
        ['-m', 'unittest', 'discover', '-s', 'tests',
         '-p', 'test_skip_clones.py', '-v'],
    ],
}
CONFIG['skip-clones-tests'] = {
    **CONFIG['skip-clones'],
    'commands': [CONFIG['skip-clones']['commands'][-1]],
}


# The split-skip manifest binds five historical helpers. Restore each exact
# dependency, retaining Wentao Li's optimized live successors unchanged.
CONFIG['split-skip']['accepted_live_sha256'] = [
    '6fe64f886309d9154e33a3d67a16e8714cebc424a7a248b3080f8cab7d94179b',
]
CONFIG['split-skip']['additional_inputs'] = [
    {**CONFIG['skip-clones'], 'manifest': 'research/split-skip/SOURCE.json'},
    {**CONFIG['skip-clones']['additional_inputs'][0],
     'manifest': 'research/split-skip/SOURCE.json'},
    {
        'manifest': 'research/split-skip/SOURCE.json', 'field': 'files',
        'path': 'scripts/audit_sparse_fusion.py', 'input_from_root': True,
        'input': 'research/sparse-fusion-orbits-production/baseline.py',
        'sha256': 'bbaa32f9786f083409e363b081bfb7a1e597c8d32e4183c13a4105c2170934ce',
        'accepted_live_sha256': [
            '6d1997fba802a8fc41099996b29e3add5d2b4f904da02548a98bed32c50aa773',
        ],
    },
    {
        'manifest': 'research/split-skip/SOURCE.json', 'field': 'files',
        'path': 'scripts/shared_point_circuit.py', 'input_from_root': True,
        'input': 'research/shared-point-digest/baseline.py',
        'sha256': 'c9bb7a5df92d260a4e3ad532b53e26936730d7c93f7facfb0784957c1e81c8ba',
        'accepted_live_sha256': [
            'f5abbf6d61f3c10349416a3e1a1ed038bbd1279ed223367f2df549de46dd7ea5',
            # PR2054: checked frame-containment cache and initialization successor.
            '360d9bffc0f55315fe294789b72c71c79e0991524555b3a5f42a2ca504d7da95',
        ],
    },
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(root, name):
    path = PurePosixPath(name)
    require(bool(path.parts) and not path.is_absolute() and '..' not in path.parts
            and '\\' not in name and ':' not in name, 'Unsafe repository path')
    return root.joinpath(*path.parts)


def authenticated_input(root, config, inputs=INPUTS):
    manifest = json.loads(safe_path(root, config['manifest']).read_bytes())
    entry = manifest[config['field']].get(config['path'])
    if isinstance(entry, dict):
        require(entry.get('representation') == 'bytes', 'Expected exact byte representation')
        entry = entry.get('sha256')
    require(entry == config['sha256'], 'Missing or changed predecessor source pin')
    # A replay must not hide an unrelated live source mutation.
    if 'accepted_live_sha256' in config:
        live = hashlib.sha256(safe_path(root, config['path']).read_bytes()).hexdigest()
        require(live in (config['sha256'], *config['accepted_live_sha256']),
                'Unrecognized live source update: ' + config['path'])
    input_root = root if config.get('input_from_root') else inputs
    data = safe_path(input_root, config['input']).read_bytes()
    require(hashlib.sha256(data).hexdigest() == entry, 'Changed historical input')
    if config.get('preserve_prefix'):
        require(data.endswith(b'\n') and safe_path(root, config['path']).read_bytes().startswith(data),
                'Historical Makefile prefix changed')
    return data


def tracked_paths(root):
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root)
    return [p.decode('utf-8') for p in raw.split(b'\0') if p]


def input_configs(config):
    """Each replacement has an explicit pin in the same predecessor manifest."""
    result = [config]
    result.extend(dict(item, manifest=config['manifest'], field=config['field'])
                  for item in config.get('additional_inputs', []))
    require(len({item['path'] for item in result}) == len(result),
            'Duplicate historical replacement')
    return result


def materialize(root, destination, config, paths, inputs=INPUTS):
    """Copy tracked working bytes only; never share writable links with the checkout."""
    replacements = [(item, authenticated_input(root, item, inputs))
                    for item in input_configs(config)]
    for item, _ in replacements:
        require(item['path'] in paths and item['manifest'] in paths,
                'Historical input or manifest is not tracked')
        if item.get('input_from_root'):
            require(item['input'] in paths, 'Historical baseline is not tracked')
    require(not destination.exists(), 'Replay destination already exists')
    destination.mkdir(parents=True)
    expected = {}
    for name in paths:
        source = safe_path(root, name)
        require(not source.is_symlink() and source.is_file(), 'Non-file tracked source: ' + name)
        target = safe_path(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        expected[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    for item, data in replacements:
        safe_path(destination, item['path']).write_bytes(data)
        expected[item['path']] = item['sha256']
    # Authenticate every replacement again before executing any checker.
    for item, _ in replacements:
        authenticated_input(destination, item, inputs)
    return expected


def verify_unchanged(snapshot, expected):
    """Retain the original CI reproducibility gate inside the isolated replay tree."""
    for name, digest in expected.items():
        target = safe_path(snapshot, name)
        require(target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest,
                'Replay changed tracked artifact: ' + name)


@contextmanager
def replay_tree(package, root=ROOT):
    """Yield an isolated historical checkout, checking tracked bytes on exit.

    The tracked tree is several GB. Keep the copy on the checkout's build
    filesystem, rather than consuming a memory-backed /tmp in concurrent tests.
    """
    config = CONFIG[package]
    paths = tracked_paths(root)
    scratch = root / 'build'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='historical-ci-', dir=scratch) as temporary:
        snapshot = Path(temporary) / 'repo'
        expected = materialize(root, snapshot, config, paths)
        try:
            yield snapshot
        finally:
            verify_unchanged(snapshot, expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', choices=CONFIG)
    parser.add_argument('--native', action='store_true', help='also run R420 C++ checks (requires C++17/Boost)')
    args = parser.parse_args()
    require(not args.native or args.package == 'r420', '--native applies only to r420')
    config = CONFIG[args.package]
    print('REPLAY_HISTORICAL_CHECK', args.package, 'copying tracked inputs', flush=True)
    with replay_tree(args.package) as snapshot:
        commands = list(config['commands'])
        if args.native:
            commands.append(['research/r420-two-sided-basis/native.py'])
        for command in commands:
            subprocess.run([sys.executable, '-B'] + command, cwd=snapshot, check=True)
    print('PASS_HISTORICAL_CHECK', args.package, 'input_sha256=' + config['sha256'], flush=True)


if __name__ == '__main__':
    main()
