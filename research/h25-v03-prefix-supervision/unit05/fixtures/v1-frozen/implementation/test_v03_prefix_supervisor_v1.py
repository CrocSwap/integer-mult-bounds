"""Pure fixtures for newly authored functions; no archived module import.

These tests establish local predicates and error retention only. Synthetic
states are never evidence of Popen, kernel cleanup, source admission or C05.
"""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest


def new_function(path, name, globals_map):
    source = Path(path).read_text(encoding='utf-8')
    tree = ast.parse(source, feature_version=(3, 12))
    matches = [node for node in tree.body
               if type(node) is ast.FunctionDef and node.name == name]
    if len(matches) != 1:
        raise ValueError('unique newly authored function required')
    module = ast.Module(body=matches, type_ignores=[])
    scope = dict(globals_map)
    exec(compile(module, '<new-function-pure-fixture>', 'exec'), scope)
    return scope[name]


class Stop(RuntimeError):
    pass


def need(condition, message):
    if condition is not True:
        raise Stop(message)


class AccessorTests(unittest.TestCase):
    def setUp(self):
        self.owner = {
            'primary': [None], 'quarantine': [False],
            'pending': [False], 'iterator_uncertain': [False],
            'native_errors': [None] * 4,
        }
        self.state = {
            'parent_pid': 10, 'unknown_owner': self.owner,
            'primary': [None], 'secondary': [None] * 16,
            'overflow': [None], 'phase': 'CLOSED',
            'quarantine': False, 'acquisition_in_flight': False,
            'io_uncertain': False,
            'root': (11, 10, 11, 11, 123, 'Z', 0),
            'returncode': 1, 'closure_confirmed': True,
            'final_rows': (), 'after_root': set(), 'reaped': [],
            'fds': [7], 'fd_attempted': [True], 'fd_closed': [True],
            'rows': [(11, 10, 11, 11, 123, 'Z', 0)],
            'count': 1, 'groups': {(11, 11)},
        }
        self.token = object()
        self.rows = {}
        self.census_calls = 0

        def state(token):
            need(token is self.token, 'synthetic token mismatch')
            return self.state

        def fresh(value):
            owner = value['unknown_owner']
            need(not owner['quarantine'][0] and
                 not owner['pending'][0] and
                 not owner['iterator_uncertain'][0],
                 'synthetic uncertainty')

        def census(value):
            self.census_calls += 1
            return self.rows

        self.call = new_function(
            'parent_domain_v1.py', 'prefix_exit1_terminal_facts',
            {'_state': state, '_GETPID': lambda: 10,
             '_fresh_acquisition': fresh, '_census': census,
             '_TYPE': type, 'schema': SimpleNamespace(need=need)})

    def test_intact_exit1_predicate(self):
        result = self.call(self.token)
        self.assertEqual(result['returncode'], 1)
        self.assertIs(result['production_completion'], False)
        self.assertIs(
            result['refusal_semantics_authenticated_by_this_function'], False)
        self.assertEqual(self.census_calls, 1)

    def test_other_exit_dispositions(self):
        for value in (0, 2, -9, True, 1.0):
            with self.subTest(value=repr(value)):
                self.setUp()
                self.state['returncode'] = value
                with self.assertRaises(Stop):
                    self.call(self.token)
                self.assertEqual(self.census_calls, 0)

    def test_unclosed_fd(self):
        self.state['fd_closed'][0] = False
        with self.assertRaises(Stop):
            self.call(self.token)

    def test_late_owned_child(self):
        self.rows = {12: (12, 10, 12, 12, 456, 'R', 1)}
        with self.assertRaises(Stop):
            self.call(self.token)

    def test_existing_primary_identity(self):
        first = RuntimeError('first')
        self.owner['primary'][0] = first
        try:
            self.call(self.token)
        except BaseException as caught:
            self.assertIs(caught, first)
        else:
            self.fail('earlier primary was accepted')
        self.assertEqual(self.census_calls, 0)

    def test_local_primary_identity(self):
        first = RuntimeError('local first')
        self.state['primary'][0] = first
        try:
            self.call(self.token)
        except BaseException as caught:
            self.assertIs(caught, first)
            self.assertIs(self.owner['primary'][0], first)
        else:
            self.fail('local primary was replaced')

    def test_invalid_early_call_keeps_cleanup_phase(self):
        self.state['phase'] = 'RUNNING'
        with self.assertRaises(Stop):
            self.call(self.token)
        self.assertEqual(self.state['phase'], 'RUNNING')
        self.assertTrue(self.owner['quarantine'][0])


class SourceStructureTests(unittest.TestCase):
    def test_supervisor_has_no_mint_call(self):
        source = Path('v03_prefix_supervisor_v1.py').read_text()
        tree = ast.parse(source)
        forbidden = {
            'ParentEpoch', 'ParentCompletion', 'reserve_producer',
            'accept_completed_producer', 'commit_exports',
            '_EPOCH_COMPLETION', '_EPOCH_ACCEPT',
        }
        names = {node.id for node in ast.walk(tree)
                 if type(node) is ast.Name}
        attributes = {node.attr for node in ast.walk(tree)
                      if type(node) is ast.Attribute}
        self.assertFalse(forbidden & (names | attributes))

    def test_complete_observer_selected(self):
        source = Path('v03_prefix_supervisor_v1.py').read_text()
        self.assertIn("'corroborate_complete_refusal'", source)
        self.assertNotIn("'corroborate_raw_refusal'", source)

    def test_source_gates_remain_none(self):
        tree = ast.parse(Path('v03_prefix_supervisor_v1.py').read_text())
        required = {
            'CONFIGURATION', 'SOURCE_REVIEW', 'STAGE_APPROVAL',
            'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL',
        }
        found = {}
        for node in tree.body:
            if type(node) is ast.Assign and len(node.targets) == 1:
                target = node.targets[0]
                if type(target) is ast.Name and target.id in required:
                    found[target.id] = ast.literal_eval(node.value)
        self.assertEqual(found, {name: None for name in required})


if __name__ == '__main__':
    unittest.main()
