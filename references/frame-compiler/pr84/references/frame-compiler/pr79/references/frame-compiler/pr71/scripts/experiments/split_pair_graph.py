"""Split-pair recursion on PR65's preserved interval/pair graph and schedules.

PR62 interval strips/core-aware assembly: Avi Eisenberg. PR63 ranked-frame
composition: Dominik Scholz. PR65 region order: Rohan Arun. The [1,1,2]
group vector was selected by Chafik Boukhalfa with OpenAI Codex assistance,
using the split-pair operation introduced in Rohan Garg's PR59. All original
sources and notices remain unchanged in the pinned contributor archive.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'references/frame-compiler/pr65'
EXPECTED_CONFIGS = {
    23: dict(groups=[1, 1, 2], schedule='cover-core', anchor=True),
    25: dict(groups=[1, 1, 2], schedule='reverse-node', anchor=True),
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
    checked_manifest(BASELINE)
    inherited = ROOT / 'references/frame-compiler/pr48'
    checked_manifest(inherited)
    for name in ('scripts/partial_swap/paired.py', 'scripts/partial_swap/shared.py',
                 'scripts/exclusion_circuit.py'):
        assert (BASELINE / name).read_bytes() == (inherited / name).read_bytes()
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(inherited / 'scripts'))
        graph = _load('split_pair_private_graph', BASELINE / 'research/pair-assembly/pair_graph.py')
        schedule = _load('split_pair_private_schedule', BASELINE / 'research/reordered-rank-pair/verify.py')
        # Imported aliases may preexist in a test process; verify their bytes.
        for module_name, relative in (
                ('partial_swap.paired', 'scripts/partial_swap/paired.py'),
                ('partial_swap.shared', 'scripts/partial_swap/shared.py'),
                ('exclusion_circuit', 'scripts/exclusion_circuit.py')):
            assert Path(sys.modules[module_name].__file__).read_bytes() == (inherited / relative).read_bytes()
        return graph, schedule
    finally:
        sys.path[:] = previous_path


_graph, _schedule = _private_modules()


def configuration(h):
    if type(h) is not int or h not in EXPECTED_CONFIGS:
        raise ValueError('Only the certified dimensions 23 and 25 are supported')
    config = json.loads((ROOT / f'research/split-pair/config-{h}.json').read_text())
    if (type(config) is not dict or config != EXPECTED_CONFIGS[h]
            or any(type(choice) is not int for choice in config['groups'])
            or type(config['anchor']) is not bool):
        raise ValueError('The certified graph configuration changed')
    return config


def split_class(parent, choices):
    class SplitPair(parent):
        def grouping(self, points):
            groups = super().grouping(points)
            choice = choices[self._level] if self._level < len(choices) else 0
            if len(points) > 3 and choice:
                index = {1: 0, 2: (len(groups)-1)//2, 3: len(groups)-1}[choice]
                if len(groups[index]) == 2:
                    groups[index:index+1] = [[point] for point in groups[index]]
            assert all(len(group) in (1, 2) for group in groups)
            assert len(groups) < len(points)
            assert sorted(point for group in groups for point in group) == sorted(points)
            return groups
    return SplitPair


def graph(h):
    config = configuration(h)
    original = _graph.circuit_class
    previous_points = _graph.alternating_points
    try:
        _graph.circuit_class = lambda dimension: split_class(original(dimension), config['groups'])
        if config['anchor']:
            def anchored_points(dimension, common):
                points = previous_points(dimension, common)
                pairs = [(a, a+1) for a in range(0, dimension-1, 2) if common not in (a, a+1)]
                chosen = min(pairs)
                result = list(chosen) + [x for x in points if x not in chosen]
                assert sorted(result) == [x for x in range(dimension) if x != common]
                return result
            _graph.alternating_points = anchored_points
        return _graph.graph(h)
    finally:
        _graph.circuit_class = original
        _graph.alternating_points = previous_points


def ordered_build(original, h):
    mode = configuration(h)['schedule']
    if mode == 'original':
        return original
    return _schedule.reordered_build(original, mode)
