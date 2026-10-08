"""Indexed two-cycle compilation with PR74 node order on anchored multi-split recursion from PR65's preserved interval/pair graph.

PR62 interval strips/core-aware assembly: Avi Eisenberg. PR63 ranked-frame
composition: Dominik Scholz. PR65 region order: Rohan Arun. The [4,1,1] and [1,4,1]
group vectors were selected by Chafik Boukhalfa with OpenAI Codex assistance,
using the balanced-split operation introduced in Rohan Garg's PR59. Balanced row/column parenthesization comes from eumemic PR69; row and half-plane choices were selected with OpenAI Codex assistance. Thomas DiFiore PR74 supplies node order and coordinate relabeling; Rohan Arun PR78 supplies the coordinate-flag search idea. All original
sources and notices remain unchanged in the pinned contributor archive.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from hashlib import sha256
import ast
import types
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'references/frame-compiler/pr65'
EXPECTED_CONFIGS = {23: {'anchor': True, 'carry_exchange_passes': 3, 'carry_two_cycle_passes': 3, 'coarse': 'half', 'coordinate_permutation': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 0], 'future_completion': True, 'groups': [4, 1, 1], 'output_mode': 'baseline', 'pending_next_use_cost': True, 'schedule': 'natural'}, 25: {'anchor': True, 'carry_exchange_passes': 3, 'carry_two_cycle_passes': 3, 'coarse': 'half', 'coordinate_permutation': [2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 21, 23, 24, 0], 'future_completion': True, 'groups': [1, 4, 1], 'output_mode': 'route-late', 'pending_next_use_cost': True, 'schedule': 'natural'}}


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


def _private_modules(h=23):
    checked_manifest(BASELINE)
    inherited = ROOT / 'references/frame-compiler/pr48'
    checked_manifest(inherited)
    for name in ('scripts/partial_swap/paired.py', 'scripts/partial_swap/shared.py',
                 'scripts/exclusion_circuit.py'):
        assert (BASELINE / name).read_bytes() == (inherited / name).read_bytes()
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(inherited / 'scripts'))
        donor = ROOT/'references/frame-compiler/pr69'
        checked_manifest(donor)
        tree = ast.parse((donor/'scripts/experiments/balanced_coarse_compiler.py').read_text())
        constants = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
                     if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id in ('BEFORE', 'AFTER')}
        path = BASELINE/'research/pair-assembly/pair_graph.py'
        source = path.read_text()
        assert source.count(constants['BEFORE']) == 1
        replacement = constants['AFTER']
        column = 'columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]'
        assert replacement.count(column) == 1
        assert h in (23,25)
        replacement = replacement.replace(column, 'columns = ([self.total([e(a,b) for a in groups[i]]) for b in groups[j]] if i+j < ng-1 else [self.total([e(a,b) for b in groups[j]]) for a in groups[i]])')
        graph = types.ModuleType('indexed_cycle_private_graph_'+str(h))
        graph.__file__ = str(path)
        exec(compile(source.replace(constants['BEFORE'], replacement), str(path)+':balanced_coarse', 'exec'), graph.__dict__)
        schedule = _load('indexed_cycle_private_schedule', BASELINE / 'research/reordered-rank-pair/verify.py')
        # Imported aliases may preexist in a test process; verify their bytes.
        for module_name, relative in (
                ('partial_swap.paired', 'scripts/partial_swap/paired.py'),
                ('partial_swap.shared', 'scripts/partial_swap/shared.py'),
                ('exclusion_circuit', 'scripts/exclusion_circuit.py')):
            assert Path(sys.modules[module_name].__file__).read_bytes() == (inherited / relative).read_bytes()
        return graph, schedule
    finally:
        sys.path[:] = previous_path


_graph, _schedule = _private_modules(23)
_graph25, _ = _private_modules(25)
_graphs = {23: _graph, 25: _graph25}


def configuration(h):
    if type(h) is not int or h not in EXPECTED_CONFIGS:
        raise ValueError('Only the certified dimensions 23 and 25 are supported')
    config = json.loads((ROOT / f'research/indexed-cycle/config-{h}.json').read_text())
    if (type(config) is not dict or config != EXPECTED_CONFIGS[h]
            or any(type(choice) is not int for choice in config['groups'])
            or any(type(config[key]) is not bool for key in ('anchor','future_completion','pending_next_use_cost'))
            or any(type(config[key]) is not int for key in ('carry_exchange_passes','carry_two_cycle_passes'))
            or any(type(i) is not int for i in config['coordinate_permutation'])):
        raise ValueError('The certified graph configuration changed')
    return config


def split_class(parent, choices):
    class SplitPair(parent):
        def grouping(self, points):
            groups = super().grouping(points)
            choice = choices[self._level] if self._level < len(choices) else 0
            if len(points) > 3 and choice:
                first,mid,last = 0,(len(groups)-1)//2,len(groups)-1
                requested = {1:[first],2:[mid],3:[last],4:[first,mid],5:[first,last],6:[mid,last],7:[first,mid,last],8:[first,first+1],9:[last-1,last]}[choice]
                chosen=[]
                for k in requested:
                    if k not in chosen and 0<=k<len(groups) and len(groups[k])==2 and len(groups)+len(chosen)+1<len(points):
                        chosen.append(k)
                for k in sorted(chosen, reverse=True):
                    groups[k:k+1] = [[point] for point in groups[k]]
            assert all(len(group) in (1, 2) for group in groups)
            assert len(groups) < len(points)
            assert sorted(point for group in groups for point in group) == sorted(points)
            return groups
    return SplitPair


def graph(h):
    config = configuration(h)
    _graph = _graphs[h]
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
        from indexed_cycle_nodeops import reorder
        return reorder(_graph.graph(h))
    finally:
        _graph.circuit_class = original
        _graph.alternating_points = previous_points
