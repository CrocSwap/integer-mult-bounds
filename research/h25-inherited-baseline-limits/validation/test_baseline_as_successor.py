"""Pure changed-boundary controls; no baseline/candidate module is imported.

The selected production helper, child-limit assignment/callback, and launch
field expressions execute with the original pure schema predicate and an inert
setrlimit recorder. This does not test native launch, ownership or workload fit.
"""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

ROUND = Path(__file__).resolve().parents[1]
SOURCE = ROUND / 'implementation/baseline/baseline_owner_v1.py'
SCHEMA = ROUND / 'review/INPUT-epoch_schema_v5.py.txt'


def selected_definition(text, name):
    rows = [node for node in ast.parse(text).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name]
    if len(rows) != 1 or rows[0].decorator_list:
        raise ValueError('one exact undecorated production definition required')
    return rows[0]


def execute_nodes(nodes, namespace):
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(module, '<selected-production-source>', 'exec'), namespace)


def read_subject():
    source = SOURCE.read_text()
    namespace = {'_TYPE': type, '_STR': str, '_LEN': len}
    schema = SCHEMA.read_text()
    execute_nodes([selected_definition(schema, 'EpochStop'),
                   selected_definition(schema, 'need')], namespace)
    selected = {'schema': SimpleNamespace(need=namespace['need'])}
    execute_nodes([selected_definition(source, 'root_address_space_limits')], selected)
    return source, selected['root_address_space_limits'], namespace['EpochStop']


def finite_oracle(inherited, upper):
    """Independent finite feasible-set maximum: hard first, then soft."""
    candidates = []
    for hard in range(upper + 1):
        for soft in range(hard + 1):
            if inherited[1] != -1 and hard > inherited[1]:
                continue
            if inherited[0] != -1 and soft > inherited[0]:
                continue
            candidates.append((soft, hard))
    return max(candidates, key=lambda row: (row[1], row[0]))


class BaselineASControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, function, cls.stop = read_subject()
        cls.calculate = staticmethod(function)
        cls.tree = ast.parse(cls.source)

    def test_selected_production_helper_against_independent_finite_oracle(self):
        checked = 0
        for upper in range(1, 9):
            for hard in [-1, *range(9)]:
                softs = [-1, *range(9)] if hard == -1 else range(hard + 1)
                for soft in softs:
                    with self.subTest(upper=upper, soft=soft, hard=hard):
                        actual = self.calculate((soft, hard), upper)
                        self.assertEqual(actual, finite_oracle((soft, hard), upper))
                        checked += 1
        self.assertEqual(checked, 440)

    def test_real_scale_lower_limits_and_zero_soft_are_preserved(self):
        mib = 1024 ** 2
        for inherited, requested, expected in [
            ((-1, -1), 1024*mib, (1024*mib, 1024*mib)),
            ((256*mib, 256*mib), 1024*mib, (256*mib, 256*mib)),
            ((128*mib, 256*mib), 1024*mib, (128*mib, 256*mib)),
            ((192*mib, 192*mib), 1024*mib, (192*mib, 192*mib)),
            ((256*mib, 256*mib), 64*mib, (64*mib, 64*mib)),
            ((0, -1), 1024*mib, (0, 1024*mib)),
            ((0, 0), 1024*mib, (0, 0)),
        ]:
            with self.subTest(inherited=inherited, requested=requested):
                self.assertEqual(self.calculate(inherited, requested), expected)

    def test_invalid_types_and_order_fail_with_original_schema_stop(self):
        for inherited, requested in [
            ((1, 2), True), ((1, 2), 0), ((1, 2), -1),
            ((1, 2), 1024**3+1), ((1, 2), 1.0),
            ([1, 2], 1), ((1,), 1), ((1, 2, 3), 1),
            ((True, 2), 1), ((1, False), 1), ((-2, 2), 1),
            ((1, -2), 1), ((3, 2), 1), ((-1, 2), 1),
        ]:
            with self.subTest(inherited=inherited, requested=requested):
                with self.assertRaises(self.stop):
                    self.calculate(inherited, requested)

    def test_actual_child_callback_installs_selected_tuple_without_parent_set(self):
        assignments = [node for node in ast.walk(self.tree)
                       if isinstance(node, ast.Assign)
                       and ast.unparse(node.targets[0]) == '(setter, kind, limits)']
        self.assertEqual(len(assignments), 1)
        callbacks = [node for node in ast.walk(self.tree)
                     if isinstance(node, ast.FunctionDef) and node.name == 'child_limit']
        self.assertEqual(len(callbacks), 1)
        calls = []
        installed = self.calculate((128*1024**2, 256*1024**2), 1024**3)
        namespace = {'_SETRLIMIT': lambda kind, limits: calls.append((kind, limits)),
                     'resource': SimpleNamespace(RLIMIT_AS=9),
                     'run': {'installed_root_address_space_limits': installed}}
        execute_nodes([assignments[0], callbacks[0]], namespace)
        self.assertEqual(calls, [])
        namespace['child_limit']()
        self.assertEqual(calls, [(9, (128*1024**2, 256*1024**2))])

    def test_actual_launch_fields_keep_requested_and_installed_distinct(self):
        launches = [node.value for node in ast.walk(self.tree)
                    if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'launch' for t in node.targets)]
        self.assertEqual(len(launches), 1)
        values = {key.value: value for key, value in zip(launches[0].keys, launches[0].values)}
        namespace = {'row': {'address_space_bytes': 1024**3},
                     'run': {'inherited_address_space_limits': (128*1024**2, 256*1024**2),
                             'installed_root_address_space_limits': (128*1024**2, 256*1024**2)}}
        wanted = ('address_space_bytes', 'inherited_address_space_limits',
                  'installed_root_address_space_limits', 'lower_inherited_AS_preserved')
        observed = {}
        for key in wanted:
            expression = ast.fix_missing_locations(ast.Expression(values[key]))
            observed[key] = eval(compile(expression, '<production-launch-field>', 'eval'), namespace)
        self.assertEqual(observed, {
            'address_space_bytes': 1024**3,
            'inherited_address_space_limits': [128*1024**2, 256*1024**2],
            'installed_root_address_space_limits': [128*1024**2, 256*1024**2],
            'lower_inherited_AS_preserved': True})

    def test_new_parent_drift_predicate_rejects_changed_limit(self):
        predicates = [node for node in ast.walk(self.tree)
                      if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                      and any(isinstance(arg, ast.Constant)
                              and arg.value == 'parent address-space limit drift'
                              for arg in node.value.args)]
        self.assertEqual(len(predicates), 1)
        unused, unused_fn, stop = read_subject()
        original = (256*1024**2, 256*1024**2)
        for current, succeeds in [(original, True), ((128*1024**2, 256*1024**2), False)]:
            namespace = {'_GETRLIMIT': lambda unused_kind: current,
                         'resource': SimpleNamespace(RLIMIT_AS=9),
                         'run': {'inherited_address_space_limits': original},
                         'schema': SimpleNamespace(need=lambda value, reason:
                             None if value is True else (_ for _ in ()).throw(stop(reason)))}
            if succeeds:
                execute_nodes(predicates, namespace)
            else:
                with self.assertRaises(stop):
                    execute_nodes(predicates, namespace)

    def test_protocol_binding_is_new_and_original_launch_bound_is_retained(self):
        lineage = json.loads((ROUND / 'implementation/SOURCE-LINEAGE.json').read_text())
        protocol_sha = lineage['amended_protocol_sha256']
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), lineage['source_sha256'])
        assignments = {node.targets[0].id: node.value.value for node in self.tree.body
                       if isinstance(node, ast.Assign) and len(node.targets) == 1
                       and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant)}
        self.assertEqual(assignments['PROTOCOL_SHA'], protocol_sha)
        validate = selected_definition(self.source, 'validate_launch_contract')
        self.assertIn("row['rss_bytes'] == row['address_space_bytes'] == 1024 ** 3",
                      ast.unparse(validate))
        for gate in ('SOURCE_REVIEW', 'RUNTIME_CONFIGURATION', 'STAGE_APPROVAL',
                     'COMMAND_APPROVAL', 'FUNDING', 'EXECUTION_APPROVAL'):
            self.assertIsNone(assignments[gate])


if __name__ == '__main__':
    unittest.main(verbosity=2)
