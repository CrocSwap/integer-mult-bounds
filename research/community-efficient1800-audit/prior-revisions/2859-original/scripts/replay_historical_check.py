#!/usr/bin/env python3
"""Replay frozen checks against authenticated historical inputs in a temporary copy.

Dennis, with substantial OpenAI Codex assistance; Apache-2.0.
The checkers, their pins, and the live selected record remain unchanged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
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
        'utf8': True,
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
        'commands': [['research/split-skip/witness.py'],
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


# The split-skip manifest binds three historical helpers. Restore each exact
# dependency, retaining Wentao Li's two optimized live successors unchanged.
CONFIG['split-skip']['accepted_live_sha256'] = [
    '6fe64f886309d9154e33a3d67a16e8714cebc424a7a248b3080f8cab7d94179b',
]
CONFIG['split-skip']['additional_inputs'] = [
    {**CONFIG['skip-clones'], 'manifest': 'research/split-skip/SOURCE.json'},
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


# Reconciliation92 predates reviewed worker-budget/cancellation successors.
# Replay the immutable runner recorded by its unchanged integrated-file manifest.
CONFIG['reconciliation92']['additional_inputs'] = [{
    'manifest': 'research/community-reconciliation92-audit/MANIFEST.json',
    'field': 'integrated_files', 'path': 'scripts/run_parallel.py',
    'input': 'run_parallel.py',
    'sha256': 'f046e98e4c296fde954b93b466b7f359be0c05c287d96943e016f0b850587387',
    'accepted_live_sha256': [
        'a49e763573343a6a068b0c48c8ff422756be5a8f55902b2385fa8d13cc951fda',
    ],
}]

# The second scheduler verifier has the same frozen reconciliation boundary.
CONFIG['reconciliation92']['additional_inputs'].append({
    'manifest': 'research/community-reconciliation92-audit/MANIFEST.json',
    'field': 'integrated_files', 'path': 'scripts/verify_parallel.py',
    'input': 'verify_parallel.py',
    'sha256': '7751bcdd2df3c98798b1855050646744404f24d015eb4cd2b4af84bfb591cdc3',
    'accepted_live_sha256': [
        '22b0e66b878c886d52aaa69d233fdcaa4194cc947cab0191ca3dabee5980d6ad',
        '45f5a2a8bccd62052421f20e56ad2f1f098fc44335c2a14aebf3179aa3749d89',
    ],
})

# The state benchmark executes the historical helper via its cold-interface
# checker. Use UTF-8 mode in child interpreters without changing frozen bytes.
CONFIG['tooling-exact'] = {
    'utf8': True,
    'manifest': 'research/clifford-state-performance/SOURCE.json',
    'field': 'files', 'path': 'scripts/verify_hpe_lean_binding.py',
    'input': 'verify_hpe_lean_binding.py',
    'sha256': '52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03',
    'accepted_live_sha256': [
        '2fe5aac5828b1fdb79ff5e9ba87faef4db77e0c9339f362a1775b498a6d59e13',
    ],
    'commands': [
        ['research/clifford-state-performance/test_state.py'],
        ['research/gram-prefix-performance/verify.py'],
        ['research/gram-prefix-performance/test_kernel.py', '--mutations'],
        ['-I', 'research/r420-geometry-cache/verify.py'],
        ['-I', 'research/owner-footprint-bitsets/verify.py'],
        ['-I', 'research/owner-footprint-bitsets/test_masks.py'],
        ['-I', '-O', 'research/owner-footprint-bitsets/test_masks.py'],
    ],
}


# Older complete graph variants include singleton/pair output targets. Their
# unchanged contracts require the original generic target digest, whereas the
# live optimized base-class benchmark remains on its reviewed three-target code.
LEGACY_SHARED = {
    'manifest': 'research/skip-clones/SOURCE.json', 'field': 'files',
    'path': 'scripts/partial_swap/shared.py', 'input_from_root': True,
    'input': 'research/partial-swap-digest/baseline.py',
    'sha256': '81e9af92cdf38243a540cdcff2062778e449467848d444da37a9553c12ca4c34',
    'accepted_live_sha256': ['7290bd639600aecff11941d3faf95c9ce95589125cc6a7f7440fb86af7a0f17c'],
}
CONFIG['skip-clones']['additional_inputs'] = [dict(LEGACY_SHARED)]
CONFIG['skip-clones-tests']['additional_inputs'] = [dict(LEGACY_SHARED)]
CONFIG['split-skip']['additional_inputs'] += [
    {**LEGACY_SHARED, 'manifest': 'research/split-skip/SOURCE.json'},
    {'manifest': 'research/split-skip/SOURCE.json', 'field': 'files',
      'path': 'scripts/audit_sparse_fusion.py', 'input': 'audit_sparse_fusion.py',
      'sha256': 'bbaa32f9786f083409e363b081bfb7a1e597c8d32e4183c13a4105c2170934ce',
      'accepted_live_sha256': ['6d1997fba802a8fc41099996b29e3add5d2b4f904da02548a98bed32c50aa773']},
]
CONFIG['split-skip']['commands'].insert(0, [
    'research/split-skip/producer.py', '--work-dir', 'build/split-skip',
    '--output', 'build/split-skip-receipt.json'])

for family in ('community', 'producers', 'strips', 'pair'):
    CONFIG['legacy-' + family] = {**LEGACY_SHARED, 'commands': [],
                                  'make_target': 'verify-' + family}
CONFIG['legacy-producers']['additional_inputs'] = [{
    'manifest': 'scripts/historical-ci-inputs/partial-swap-context.json',
    'field': 'files', 'path': 'certificates/partial-swap-network.json',
    'input': 'partial-swap-network.json',
    'sha256': 'f3c4be597b2f2136da4ae2cc80c7454f63c90aa01f84e5b8131cee4dd55de815',
    'accepted_live_sha256': ['2b19ed45b6207647017f6ee9f87f41df484981822fe555d088e5c1185dc7c62a'],
}]

# Retain every original unittest command, isolating only frozen family tests.
for slug in ('copied-fixed', 'copied-fixed-reversed', 'skip-strips',
             'skip-suffix', 'pair-assembly'):
    key = 'legacy-test-' + slug
    CONFIG[key] = {**LEGACY_SHARED, 'commands': [
        ['-m', 'unittest', 'discover', '-s', 'tests',
         '-p', 'test_' + slug.replace('-', '_') + '.py', '-v']]}
CONFIG['legacy-test-split-skip'] = {**CONFIG['split-skip'],
    'commands': [CONFIG['split-skip']['commands'][-1]]}


# The current ledger checker authenticates immutable review contexts, including
# helpers that subsequently gained reviewed production optimizations.
CONFIG['tooling-ledger'] = {
    **CONFIG['tooling-exact'],
    'manifest': 'research/community-hyperplane599-audit/SOURCE.json',
    'field': 'source_files',
    'commands': [['scripts/verify_pr_reconciliation.py']],
    'additional_inputs': [{
        'manifest': 'research/community-k492-audit/SOURCE.json',
        'field': 'source_files',
        'path': 'research/complex-k492-owner-repair/code/hpe_audit_and_transport.py',
        'input': 'k492_hpe_audit_and_transport.py',
        'sha256': 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
        'accepted_live_sha256': ['d777db4abe316594df5cd3dc1269b42f4af4a8c87d4d0df500d32655e3775b87'],
    }],
}


CONFIG['tooling-ledger']['additional_inputs'].extend([{'manifest': 'research/community-frontier741-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '681', 'files'],
  'path': 'research/complex-factory5-resynthesis/SOURCE-PINS.json',
  'input': 'ledger-frontier741-SOURCE-PINS.json',
  'sha256': '79e00db34b721dc38830a7816f3126a09615d49c12f1b6a630147f1f50378f63',
  'accepted_live_sha256': ['9581d53e525c4f7f7a6e9bd96c02814cb3ab7be7734c5de3c42cc74042df8718']},
 {'manifest': 'research/community-frontier741-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '681', 'files'],
  'path': 'research/complex-factory5-resynthesis/verify.py',
  'input': 'ledger-frontier741-verify.py',
  'sha256': 'edbae43b68c0e4f65978a2f9b9a739867128f4ef19d8bbe81d06ed2e5bc165f1',
  'accepted_live_sha256': ['90c917080f577f24390b1ba8ab059e052314eb0cee2cccb2e4321bcc2c6cf74a']},
 {'manifest': 'research/community-frontier741-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '681', 'files'],
  'path': 'research/supplier-circuit-consolidation/SOURCES.json',
  'input': 'ledger-frontier741-SOURCES.json',
  'sha256': 'ef2568aac251c94d86736936b9d8c7507d224b129da2907d1bc6a1c2b5546742',
  'accepted_live_sha256': ['ad8665bf62453b4597f798aeeec1fa9d145413dbb725f11893a5345ba5a4ee4b']},
 {'manifest': 'research/community-frontier741-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '695', 'files'],
  'path': 'docs/ci-verification.md',
  'input': 'ledger-frontier741-ci-verification.md',
  'sha256': 'a854022e0e1d5d4db4d60e586be3ea56005013ef14a1fc06d02bc06e8529c4b0',
  'accepted_live_sha256': ['ae5bcac684ce2188632f38dee8ed46ebdc9588f490401505aa1cac33c55d84db']},
 {'manifest': 'research/community-frontier890-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '853', 'files'],
  'path': 'scripts/verify_complex741_parallel.py',
  'input': 'ledger-frontier890-verify_complex741_parallel.py',
  'sha256': '616cff67233958647dd1e6f33dcc5ffc6132df68e0e1230dc768e820d00155a1',
  'accepted_live_sha256': ['f368e6ed6461806107ab425cbe15f5c6dc9056a2bd29a90ed75d22791744c61b']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '921', 'files'],
  'path': 'scripts/run_isolated_tests.py',
  'input': 'ledger-batch932-run_isolated_tests.py',
  'sha256': '96ea543e6c707424afe247e77bd86c82152f90fc76a0773c4232145da5cdf8d1',
  'accepted_live_sha256': ['fdc022f70e42a9b5a2be8c6c3645cfdc211c6dffdffac68904b2945b1cdc3e5a', 'f569b1c287252c698b4d59bc1bd0f013159e772cc3be64e26c4eab8eb99d0478']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '921', 'files'],
  'path': 'tests/test_isolated_test_runner.py',
  'input': 'ledger-batch932-test_isolated_test_runner.py',
  'sha256': '628391b6abfbc8674ceec1751867a4392f2cc0b5b66886243e139af86cf355ac',
  'accepted_live_sha256': ['5c2a715a66c0c87fd672ce46889cb878dd7017a8bfa0c44395b340306b1b5382']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '903', 'files'],
  'path': 'research/data-corner-performance/README.md',
  'input': 'ledger-batch932-README.md',
  'sha256': 'eaa548973e42e1ca6695fb3d6a8ae3c738ff29a5c4ccd053c9bf44f6eacb545c',
  'accepted_live_sha256': ['6e8b28070731ab42fca90519f16eb17f9a19b86362b2b8533fa2ddcb2bdd6e0c']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '903', 'files'],
  'path': 'research/data-corner-performance/SOURCE.json',
  'input': 'ledger-batch932-SOURCE.json',
  'sha256': 'ceda6f692682d98f7a4bc258717764ea2b549304b5808ba380f7ee48783dcb53',
  'accepted_live_sha256': ['513628ac6fc4941c7bf2f9b890099ed163d9f2521f4461d3f42f07773d04eef1']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '903', 'files'],
  'path': 'research/data-corner-performance/replay.py',
  'input': 'ledger-batch932-replay.py',
  'sha256': 'ce7cceeabb816d4a70aaa6352d5ba0432ac7dea4f66f903e3af4fa91aa44c822',
  'accepted_live_sha256': ['eb96c629a8732216fc1bf6243ada832d0041b467ede3af7a70e07783900694ba']},
 {'manifest': 'research/community-batch932-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '903', 'files'],
  'path': 'research/data-corner-performance/test_replay.py',
  'input': 'ledger-batch932-test_replay.py',
  'sha256': '5f134d0cf4e3c4b79e0aa274117523582badbe8e6431554832f0277bb644724e',
  'accepted_live_sha256': ['0c7ab29c0f5628ec1943501f79f6144d2d474efd837c44dbb9ee5dd97b569ad1']},
 {'manifest': 'research/community-batch1047-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '1035', 'files'],
  'path': 'research/p112-free-sink-audit97/README.md',
  'input': 'ledger-batch1047-README.md',
  'sha256': 'c792fc8f5de0c784049904c6febf3eed9b20e2462b30dc643c72730470d72b79',
  'accepted_live_sha256': ['6924c590eaa9a954d986153fa417c3f1ee074bcb194a42c79e1e37cb69f2cd4a']},
 {'manifest': 'research/community-batch1047-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '1035', 'files'],
  'path': 'research/p112-free-sink-audit97/independent.py',
  'input': 'ledger-batch1047-independent.py',
  'sha256': '46806efe1ee7744c810a69981d471b42dfceaa336fee226991c55ba1edfd129f',
  'accepted_live_sha256': ['c77cf3dd1234c26cfb7df2d356752721e8b1b37169f20543678fe2f4d07a53f8']},
 {'manifest': 'research/community-batch1099-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '1017', 'files'],
  'path': 'research/r439-omission-atlas-seed81/README.md',
  'input': 'ledger-batch1099-README.md',
  'sha256': '6fc756df2aa0afe5b63985c1a5b4878659a3387250092e9ae5167f3316d5de9f',
  'accepted_live_sha256': ['812fabd455a7d1f77331e59d57150f28ff8ddc6ff47f9a54c5b24970f6dcc00a']},
 {'manifest': 'research/community-batch1099-audit/CONTENT-COVERAGE.json',
  'field': ['pull_requests', '1017', 'files'],
  'path': 'research/r439-omission-atlas-seed81/verify.py',
  'input': 'ledger-batch1099-verify.py',
  'sha256': '127d7679fb26e264018548a1301b2f0f437d834eb1f0ffa215556243077ff866',
  'accepted_live_sha256': ['6c3c94b01e3db5fb6d9e45eda4f60628252de1fab218e6e8233cc7949afd8966']}])


CONFIG['tooling-ledger']['additional_inputs'].append({'manifest': 'research/community-batch970-audit/CONTENT-COVERAGE.json',
 'field': ['pull_requests', '959', 'files'],
 'path': 'scripts/verify_selected_result.py',
 'input': 'ledger-batch970-verify_selected_result.py',
 'sha256': 'd7fd929726b326aeeaf0a3996475adec88eee9aac09ae0bebeeaa0bc1fc8f199',
 'accepted_live_sha256': ['c0cc23a8534d91c8d272195315c725213f13279815750ffdef055ec3adfbe911']})

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
    fields = config['field']
    pins = manifest
    for key in ([fields] if isinstance(fields, str) else fields):
        pins = pins[key]
    if isinstance(pins, list):
        matches = [item['integrated_sha256'] for item in pins
                   if item.get('integrated_path') == config['path']
                   and item.get('integrated_sha256')]
        require(len(matches) == 1, 'Missing or duplicate predecessor source pin')
        entry = matches[0]
    else:
        entry = pins.get(config['path'])
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
    catalog = root / '.historical-ci-tracked.json'
    if catalog.is_file():
        raw = catalog.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == os.environ.get('HISTORICAL_CI_CATALOG_SHA256'),
                'Changed historical tracked-input catalog')
        paths = json.loads(raw)
        require(isinstance(paths, list) and len(paths) == len(set(paths)),
                'Invalid historical tracked-input catalog')
        for name in paths:
            require(safe_path(root, name).is_file(), 'Missing historical tracked input')
        return paths
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root)
    return [p.decode('utf-8') for p in raw.split(b'\0') if p]


def materialize(root, destination, config, paths, inputs=INPUTS):
    """Copy tracked working bytes only; never share writable links with the checkout."""
    configurations = [config, *config.get('additional_inputs', [])]
    replacements = {}
    for entry in configurations:
        require(entry['path'] not in replacements, 'Duplicate historical replacement')
        data = authenticated_input(root, entry, inputs)
        require(entry['path'] in paths and entry['manifest'] in paths,
                'Historical input or manifest is not tracked')
        if entry.get('input_from_root'):
            require(entry['input'] in paths, 'Historical baseline is not tracked')
        replacements[entry['path']] = data
    require(not destination.exists(), 'Replay destination already exists')
    destination.mkdir(parents=True)
    expected = {}
    for name in paths:
        source = safe_path(root, name)
        require(not source.is_symlink() and source.is_file(), 'Non-file tracked source: ' + name)
        target = safe_path(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Hash the same bytes we write, without reopening every destination.
        # Keep independent writable files and the final verify_unchanged gate.
        data = source.read_bytes()
        require(target.write_bytes(data) == len(data), 'Incomplete replay copy: ' + name)
        expected[name] = hashlib.sha256(data).hexdigest()
        del data  # Release this file before reading the next, possibly large, input.
    for entry in configurations:
        safe_path(destination, entry['path']).write_bytes(replacements[entry['path']])
        expected[entry['path']] = entry['sha256']
    # Authenticate every replacement again before executing any checker.
    for entry in configurations:
        authenticated_input(destination, entry, inputs)
    return expected


def verify_unchanged(snapshot, expected):
    """Retain the original CI reproducibility gate inside the isolated replay tree."""
    for name, digest in expected.items():
        target = safe_path(snapshot, name)
        require(target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest,
                'Replay changed tracked artifact: ' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', choices=CONFIG)
    parser.add_argument('--native', action='store_true', help='also run R420 C++ checks (requires C++17/Boost)')
    args = parser.parse_args()
    require(not args.native or args.package == 'r420', '--native applies only to r420')
    config = CONFIG[args.package]
    paths = tracked_paths(ROOT)
    with tempfile.TemporaryDirectory(prefix='historical-ci-') as temporary:
        snapshot = Path(temporary) / 'repo'
        print('REPLAY_HISTORICAL_CHECK', args.package, 'copying tracked inputs', flush=True)
        expected = materialize(ROOT, snapshot, config, paths)
        commands = list(config['commands'])
        if args.native:
            commands.append(['research/r420-two-sided-basis/native.py'])
        # Retain assert-based historical checks, including nested interpreters.
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        # A ledger replay invokes reconciliation92 recursively. Carry the full
        # original tracked inventory into Git-free child copies, authenticating
        # its exact bytes rather than rediscovering only a subset of the tree.
        catalog = json.dumps(paths, ensure_ascii=True).encode('ascii')
        (snapshot / '.historical-ci-tracked.json').write_bytes(catalog)
        env['HISTORICAL_CI_CATALOG_SHA256'] = hashlib.sha256(catalog).hexdigest()
        if config.get('utf8'):
            env['PYTHONUTF8'] = '1'
        for command in commands:
            subprocess.run([sys.executable, '-B'] + command, cwd=snapshot, env=env, check=True)
        if config.get('make_target'):
            subprocess.run(['make', config['make_target']], cwd=snapshot, env=env, check=True)
        verify_unchanged(snapshot, expected)
    print('PASS_HISTORICAL_CHECK', args.package, 'input_sha256=' + config['sha256'], flush=True)


if __name__ == '__main__':
    main()
