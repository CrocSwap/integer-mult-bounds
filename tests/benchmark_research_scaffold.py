"""Opt-in generator benchmark with exact five-file output equality; no timing gate.

Reuses the existing batch reader by Arham-Tahir64 (#1595); the earlier streamed
reader is by woklerx (#1452). Prepared by ywz65 with OpenAI Codex assistance.
Apache-2.0. Temporary shared clones require the pinned base in local Git history.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BASE = '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2'
INVENTORY = 'research/u8-e4-gap-fill/SOURCES.json'
sys.path.insert(0, str(ROOT / 'scripts'))
import new_research_package as current
import research_package as package


def benchmark(pairs):
    old_source = package.git(ROOT, 'show', BASE + ':scripts/new_research_package.py')
    namespace = {'__name__': 'pinned_generator'}
    exec(compile(old_source, 'pinned_new_research_package.py', 'exec'), namespace)
    inventory = package.git(ROOT, 'show', BASE + ':' + INVENTORY)
    sources = sorted(json.loads(inventory)['files'])
    names = sorted(set(sources + ['docs/research/agent-task-catalog.json',
                                  'certificates/selected-result.json']))
    measurements = []
    with tempfile.TemporaryDirectory() as directory:
        roots = {}
        for mode in ('before', 'after'):
            root = Path(directory) / mode
            subprocess.run(['git', 'clone', '--shared', '--no-checkout', str(ROOT), str(root)],
                           check=True, capture_output=True)
            package.git(root, 'symbolic-ref', 'HEAD', 'refs/heads/benchmark')
            package.git(root, 'update-ref', 'HEAD', BASE)
            roots[mode] = root
            # Fixture preparation is excluded from measurements. Read one blob
            # at a time; finish the iterator to check the Git process exit.
            for index, (_, data) in enumerate(package.git_blobs(root, [BASE + ':' + n for n in names])):
                target = root / names[index]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        for sample in range(pairs):
            outputs = {}
            for mode in (('before', 'after') if sample % 2 == 0 else ('after', 'before')):
                create = namespace['create'] if mode == 'before' else current.create
                commands, real = [], subprocess.Popen
                def tracked(argv, *args, **kwargs):
                    commands.append(argv)
                    return real(argv, *args, **kwargs)
                start = time.perf_counter()
                with patch.object(subprocess, 'Popen', side_effect=tracked):
                    target = create(roots[mode], 'benchmark-' + str(sample),
                                    'bit-new-register-model', 'Benchmark fixture', sources)
                measurements.append({'sample': sample, 'mode': mode,
                                     'seconds': time.perf_counter() - start,
                                     'git_processes': len(commands)})
                outputs[mode] = {p.name: p.read_bytes() for p in target.iterdir()}
            if outputs['before'] != outputs['after']:
                raise RuntimeError('generated package bytes differ')
    return {'base': BASE, 'inventory': INVENTORY,
            'inventory_sha256': hashlib.sha256(inventory).hexdigest(),
            'old_generator_sha256': hashlib.sha256(old_source).hexdigest(),
            'explicit_sources': len(sources), 'pinned_sources': len(names),
            'python': sys.version, 'platform': sys.platform,
            'git': package.git(ROOT, '--version').decode().strip(),
            'all_five_files_equal_in_every_pair': True, 'measurements': measurements,
            'scope': 'Package generation only; host timing, no mathematical replay or performance guarantee.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    args = parser.parse_args()
    if args.pairs < 1:
        parser.error('pairs must be positive')
    print(json.dumps(benchmark(args.pairs), indent=2))
