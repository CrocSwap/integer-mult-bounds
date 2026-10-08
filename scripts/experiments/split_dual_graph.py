"""PR59 split-pair groups composed with the PR55 dual-suffix layout.

Original source files and notices remain byte-identical. This provider selects
only the two small group vectors and PR55's native fold/layout orders. PR59's
paid clones and recorded point/strip/total permutations are not consumed.
Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLIT = ROOT / 'references/frame-compiler/pr59'
SUFFIX = ROOT / 'references/frame-compiler/pr55'
EXPECTED_CONFIGS = {
    23: dict(groups=[1, 3, 2], total_mode='reverse', top_mode='input', deep_mode='asc'),
    25: dict(groups=[1, 2, 2], total_mode='desc', top_mode='input', deep_mode='support_desc'),
}


def checked_manifest(directory):
    manifest = json.loads((directory / 'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        assert sha256((directory / name).read_bytes()).hexdigest() == digest, name
    if 'shared_dependency_manifest' in manifest:
        path = directory / manifest['shared_dependency_manifest']
        assert sha256(path.read_bytes()).hexdigest() == manifest['shared_dependency_manifest_sha256']
    return manifest


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _private_modules():
    checked_manifest(SPLIT)
    checked_manifest(SUFFIX)
    for name in ('scripts/partial_swap/paired.py', 'scripts/partial_swap/shared.py',
                 'scripts/exclusion_circuit.py'):
        assert (SPLIT / name).read_bytes() == (ROOT / 'references/frame-compiler/pr48' / name).read_bytes()
    previous_path = sys.path[:]
    absent = object()
    previous_skip = sys.modules.get('skip_graph', absent)
    try:
        base = _load('split_dual_private_base', SPLIT / 'research/skip-strips/skip_graph.py')
        sys.modules['skip_graph'] = base
        split = _load('split_dual_private_split', SPLIT / 'research/split-skip/split_graph.py')
        suffix = _load('split_dual_private_suffix', SUFFIX / 'research/skip-suffix/skip_graph.py')
        assert split.base is base
        return base, split, suffix
    finally:
        sys.path[:] = previous_path
        if previous_skip is absent:
            sys.modules.pop('skip_graph', None)
        else:
            sys.modules['skip_graph'] = previous_skip


_base, _split, _suffix = _private_modules()


def configuration(h):
    if type(h) is not int or h not in EXPECTED_CONFIGS:
        raise ValueError('Only the certified dimensions 23 and 25 are supported')
    config = json.loads((ROOT / f'research/split-dual/config-{h}.json').read_text())
    if (type(config) is not dict or config != EXPECTED_CONFIGS[h]
            or any(type(choice) is not int for choice in config['groups'])):
        raise ValueError('The certified graph configuration changed')
    return config


def graph(h):
    config = configuration(h)
    previous = _base.skip_prefix
    try:
        _base.skip_prefix = _suffix.skip_suffix
        return _split.graph(h, config=config)
    finally:
        _base.skip_prefix = previous
