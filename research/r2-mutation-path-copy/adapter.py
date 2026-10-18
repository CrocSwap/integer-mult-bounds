#!/usr/bin/env python3
"""Source-specific mutation isolation for the retained PR3202 R2 audit.

Tekalign (@tekuuu), substantial OpenAI Codex assistance, Apache-2.0.
Original controls: 24kHandsome1201. Checked marshal baseline: jackmgaller/#1939.
This is not a general replacement for deepcopy.
"""
import ast
import copy
import marshal
import pickle
import time

CANON = 'CANONICAL-WORD.json.gz'
PROGRAM = 'LOCAL-PROGRAMS.json.gz'
RECIPES = 'CLIFFORD-RECIPES.json'
ADAPTERS = 'RESIDUAL-ADAPTERS.json'
W = [256, 128, 64, 34, 17, 11, 4]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def fixture_guard(value):
    # Trusted in-memory JSON trees only. No pickle data is ever loaded.
    # Compare complete bytes within one process: no hash acceptance or portable
    # pickle certificate is involved. All actual payload comparisons use ==.
    return pickle.dumps(value, protocol=5)


def fork_path(value, path, deep_leaf=True):
    """Copy ancestors of one write footprint; leave all other cells shared."""
    need(type(value) in (list, dict), 'path container')
    if not path:
        return copy.deepcopy(value) if deep_leaf else value.copy()
    key, *rest = path
    result = value.copy()
    result[key] = fork_path(value[key], rest, deep_leaf)
    return result


def plan(name, word, data):
    """Literal write footprints of the pinned sixteen mutation functions."""
    if name == 'missing dirty restoration':
        return 'word', ['restore'], False
    if name == 'extra fan-in observer':
        return 'word', ['restore', 180], True
    if name == 'post wrappers before cleanup':
        # The original mutation splices the outer list, never edits its events.
        return 'data', [PROGRAM, 'forward'], False
    event_plans = {
        'forward fan-in sign': ('forward', lambda e: e[:1] == ['scalar'] and
                               e[1] == ['add', ['L', 40], ['L', 54], -2, 1]),
        'dual fan-in sign': ('backward', lambda e: e[:1] == ['scalar'] and
                            e[1] == ['add', ['L', 54], ['L', 40], 2, 1]),
        'rank-two child undercharge': ('forward', lambda e:
                                      e[:3] == ['climb', 'cleanup_tail', 54] and e[-1] == 2),
        'tail phase substitution': ('forward', lambda e: e == ['phase', 'cleanup_tail']),
        'wrapper side': ('forward', lambda e: e[:2] == ['residual_adapter', 'post']),
        'dual wrapper owner': ('backward', lambda e: e[:2] == ['residual_adapter', 'pre']),
        'source exit frame': ('forward', lambda e: e[:3] == ['adapter', 'new_to_old', 40]),
        'prefix wrong source frame': ('forward', lambda e: e[0] == 'climb' and e[3] != 0),
    }
    if name in event_plans:
        orientation, select = event_plans[name]
        index = next(i for i, event in enumerate(data[PROGRAM][orientation]) if select(event))
        return 'data', [PROGRAM, orientation, index], True
    if name in ('native global phase', 'native translation', 'native child rank'):
        wid = data[CANON]['frames'].index(W)
        index = next(i for i, rec in enumerate(data[RECIPES]['children'])
                     if (rec['old'], rec['new']) == (wid, 1))
        return 'data', [RECIPES, 'children', index], True
    if name in ('residual global phase', 'residual translation'):
        key = sorted(data[ADAPTERS]['recipes'])[0]
        return 'data', [ADAPTERS, 'recipes', key], True
    raise ValueError('unrecognized pinned mutation: ' + name)


def checked_marshal_function(raw):
    """Execute the unchanged credited function, without its CLI monkeypatch."""
    tree = ast.parse(raw)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name == 'checked_deepcopy']
    need(len(nodes) == 1, 'unique credited marshal function')
    namespace = {'marshal': marshal, '_original_deepcopy': copy.deepcopy,
                 'STATS': {'marshal': 0, 'fallback': 0}}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'PR1939/checked_deepcopy', 'exec'), namespace)
    return namespace['checked_deepcopy'], namespace['STATS']


class Harness:
    def __init__(self, mode, marshal_source, differential=False):
        need(mode in ('deepcopy', 'marshal', 'paths'), 'copy mode')
        self.mode, self.differential = mode, differential
        self.marshal_copy, self.marshal_stats = checked_marshal_function(marshal_source)
        self.copy_seconds = 0.0
        self.providers = {}
        self.current = None
        self._original_guard = None

    def begin(self, tag, word, data):
        need(self.current is None and tag not in self.providers, 'provider lifecycle')
        self.current = tag
        self._original_guard = fixture_guard([word, data])
        self.providers[tag] = {'mutants': [], 'write_footprints': [], 'original_unchanged': False}

    def copy(self, name, word, data):
        start = time.perf_counter()
        root, path, deep = plan(name, word, data)
        self.providers[self.current]['write_footprints'].append(
            {'name': name, 'root': root, 'path': path, 'deep_leaf': deep})
        if self.mode == 'paths':
            result = ((fork_path(word, path, deep), data) if root == 'word'
                      else (word, fork_path(data, path, deep)))
        else:
            copier = copy.deepcopy if self.mode == 'deepcopy' else self.marshal_copy
            result = copier(word), copier(data)
        self.copy_seconds += time.perf_counter() - start
        return result

    def observe(self, name, mutate, w, d, word, data):
        need(self.current is not None, 'mutant outside provider')
        if self.differential:
            # Original mutation callable, complete original deepcopy, full equality.
            expected_w, expected_d = copy.deepcopy(word), copy.deepcopy(data)
            mutate(expected_w, expected_d)
            need(w == expected_w and d == expected_d, 'complete mutant differs: ' + name)
        self.providers[self.current]['mutants'].append(name)

    def end(self, tag, word, data):
        need(self.current == tag, 'provider end order')
        row = self.providers[tag]
        need(fixture_guard([word, data]) == self._original_guard, 'original fixture mutated')
        need(len(row['mutants']) == 16 and len(set(row['mutants'])) == 16, 'complete mutant inventory')
        row['original_unchanged'] = True
        self.current = None
        self._original_guard = None


def replace_once(text, old, new):
    need(text.count(old) == 1, 'unique source hook: ' + old[:60])
    return text.replace(old, new)


def transform_audit(raw):
    text = raw.decode()
    text = replace_once(text, '        w, d = copy.deepcopy(word), copy.deepcopy(data)',
                        '        w, d = _copy_mutant(name, word, data)')
    text = replace_once(text, '        mutate(w, d)',
                        '        mutate(w, d)\n        _observe_mutant(name, mutate, w, d, word, data)')
    text = replace_once(text, '        data = artifacts(blobs, tag, data_path)',
                        '        data = artifacts(blobs, tag, data_path)\n        _begin_provider(tag, word, data)')
    text = replace_once(text, "        providers[tag]['rejected_controls'] = failure_controls(kernel, word, data)",
                        "        providers[tag]['rejected_controls'] = failure_controls(kernel, word, data)\n"
                        '        _end_provider(tag, word, data)')
    return text.encode()


def transform_replay(raw):
    text = raw.decode()
    point = "        changed = text.replace(anchor, anchor + '\\n    _install_comparator(kernel)').encode()"
    text = replace_once(text, point, point + '\n        changed = _transform_audit(changed)')
    point = '        verifier._install_comparator = install'
    text = replace_once(text, point, point + '\n        verifier._copy_mutant = _harness.copy'
                        '\n        verifier._observe_mutant = _harness.observe'
                        '\n        verifier._begin_provider = _harness.begin'
                        '\n        verifier._end_provider = _harness.end')
    return text.encode()
