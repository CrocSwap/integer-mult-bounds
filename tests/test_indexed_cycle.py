"""Physical and exact-arithmetic controls for the aligned split/pair witness."""
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT/'scripts/experiments'
sys.path.insert(0, str(EXPERIMENTS))
from binary_frame_profile_prepare import prepare
from binary_frame_replay import replay
from binary_frame_math import moment


class SplitPairControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = {h: json.loads(gzip.decompress((ROOT/f'certificates/indexed-cycle-word-{h}.json.gz').read_bytes()))
                     for h in (23,25)}

    def reject_mutation(self, mutate, checker='both'):
        for h, original in self.words.items():
            with self.subTest(h=h), tempfile.TemporaryDirectory() as directory:
                changed = deepcopy(original)
                mutate(changed)
                path = Path(directory)/'word.json'
                path.write_text(json.dumps(changed, separators=(',', ':'))+'\n')
                with self.assertRaises((AssertionError, ValueError, IndexError, KeyError)):
                    if checker != 'transitions':
                        replay(path)
                    if checker != 'replay':
                        prepare(path, Path(directory)/'transitions.bin')

    def test_selected_words_pass_independent_replay(self):
        recorded = json.loads((ROOT/'certificates/indexed-cycle-compiler.json').read_text())
        for h in (23,25):
            with self.subTest(h=h):
                actual = replay(ROOT/f'certificates/indexed-cycle-word-{h}.json.gz')
                self.assertEqual(json.loads(json.dumps(actual)), recorded['axes'][str(h)]['replay'])

    def test_omitted_literal_xor_is_rejected(self):
        self.reject_mutation(lambda word: word['ops'].pop(0))

    def test_self_xor_is_rejected(self):
        def mutate(word):
            word['ops'][0][1] = word['ops'][0][0]
        self.reject_mutation(mutate, 'replay')

    def test_non_nested_operation_frame_is_rejected(self):
        def mutate(word):
            narrow = next(i for i,(core,cover) in enumerate(word['frames']) if core == cover)
            operation = next(op for op in word['ops'] if word['frames'][op[2]][0] != word['frames'][op[2]][1])
            operation[2] = narrow
        self.reject_mutation(mutate)

    def test_aliased_terminal_role_is_rejected(self):
        def mutate(word):
            word['outputs'][1][0] = word['outputs'][0][0]
        self.reject_mutation(mutate, 'replay')

    def test_missing_copied_center_is_rejected(self):
        def mutate(word):
            index = next(i for i,(_,_,_,target) in enumerate(word['outputs']) if len(target) == 1)
            word['outputs'].pop(index)
        self.reject_mutation(mutate)

    def test_omitted_transition_cannot_reduce_paid_profile(self):
        self.reject_mutation(lambda word: word['events'].pop(0), 'transitions')

    def test_understated_physical_width_is_rejected(self):
        def mutate(word):
            word['R'] -= 1
        self.reject_mutation(mutate)

    def test_complete_pr79_profile_fails_new_bit_saving(self):
        from split_pair_arithmetic import refine
        previous = json.loads((ROOT/'references/frame-compiler/pr79/certificates/balanced-split-kappa.json').read_text())['bit']
        current = json.loads((ROOT/'certificates/indexed-cycle-kappa.json').read_text())
        result = refine.exact_moment(previous['m'], previous['W'], {int(t): n for t,n in previous['child_multiplicities'].items()}, Fraction(current['bit_saving']))
        self.assertGreater(result['lower'], 1)
        self.assertGreater(Fraction(current['kappa']), Fraction(current['comparison']['pr79_kappa']))

    def test_private_import_preserves_path_and_arithmetic_module(self):
        import indexed_cycle_graph as provider
        import split_pair_arithmetic as arithmetic
        sentinel = object()
        existing = sys.modules.get('refine', sentinel)
        previous_path = sys.path[:]
        graph, schedule = provider._private_modules()
        refine, audit = arithmetic.private_arithmetic()
        self.assertIs(audit.refine, refine)
        self.assertIs(sys.modules.get('refine', sentinel), existing)
        self.assertEqual(sys.path, previous_path)

    def test_failed_graph_build_restores_original_providers(self):
        import indexed_cycle_graph as provider
        previous_class, previous_points = provider._graph.circuit_class, provider._graph.alternating_points
        with patch.object(provider._graph, 'graph', side_effect=RuntimeError('deliberate graph failure')):
            with self.assertRaises(RuntimeError):
                provider.graph(23)
        self.assertIs(provider._graph.circuit_class, previous_class)
        self.assertIs(provider._graph.alternating_points, previous_points)

    def test_failed_compilation_restores_engine_graph_and_schedule(self):
        import indexed_cycle_compiler as producer
        previous_graph, previous_build = producer.ENGINES[23].graph, producer.ENGINES[23].build
        missing = object()
        runtime = {name:getattr(producer.ENGINES[23],name,missing) for name in ('PENDING_COST','ORACLE_EXE','ORACLE_INPUT','oracles','OUTPUT_MODE')}
        with patch.object(producer.ENGINES[23], 'compile_', side_effect=RuntimeError('deliberate compiler failure')):
            with self.assertRaises(RuntimeError):
                producer.compile_axis(23)
        self.assertIs(producer.ENGINES[23].graph, previous_graph)
        self.assertIs(producer.ENGINES[23].build, previous_build)
        for name,value in runtime.items():
            self.assertIs(getattr(producer.ENGINES[23],name,missing),value)

    def test_uncertified_configurations_are_rejected(self):
        import indexed_cycle_graph as provider
        wrong_anchor = deepcopy(provider.EXPECTED_CONFIGS[23]); wrong_anchor['anchor'] = False
        boolean_group = deepcopy(provider.EXPECTED_CONFIGS[23]); boolean_group['groups'][0] = True
        changed_schedule = deepcopy(provider.EXPECTED_CONFIGS[23]); changed_schedule['schedule'] = 'reverse-node'
        wrong_coarse = deepcopy(provider.EXPECTED_CONFIGS[23]); wrong_coarse['coarse'] = 'row'
        omitted_completion = deepcopy(provider.EXPECTED_CONFIGS[23]); omitted_completion['future_completion'] = False
        extra_exchanges = deepcopy(provider.EXPECTED_CONFIGS[23]); extra_exchanges['carry_exchange_passes'] = 4
        wrong_route = deepcopy(provider.EXPECTED_CONFIGS[23]); wrong_route['output_mode'] = 'route-late'
        wrong_permutation = deepcopy(provider.EXPECTED_CONFIGS[23]); wrong_permutation['coordinate_permutation'][0] = True
        extra_cycles = deepcopy(provider.EXPECTED_CONFIGS[23]); extra_cycles['carry_two_cycle_passes'] = 4
        for changed in (wrong_anchor, boolean_group, changed_schedule, wrong_coarse, omitted_completion, extra_exchanges,wrong_route,wrong_permutation,extra_cycles):
            with self.subTest(configuration=changed), patch.object(provider.json, 'loads', return_value=changed):
                with self.assertRaises(ValueError):
                    provider.configuration(23)
        for dimension in (True, 22, 24, '23'):
            with self.subTest(dimension=dimension), self.assertRaises(ValueError):
                provider.configuration(dimension)

    def test_recursive_weighted_exclusions_and_contraction(self):
        import indexed_cycle_graph as provider
        for h in (23,25):
            block_sizes = []
            parent = provider._graphs[h].circuit_class(h)
            selected = provider.split_class(parent, provider.configuration(h)['groups'])
            case = self
            class Audited(selected):
                def grouping(self, points):
                    groups = super().grouping(points)
                    case.assertEqual([x for group in groups for x in group], list(points))
                    case.assertLess(len(groups), len(points))
                    return groups

                def _block(self, points, edges, weights, level):
                    def expected(omitted):
                        values = [value for pair,value in edges.items() if not set(pair) & omitted]
                        values += [value for point,value in weights.items() if point not in omitted]
                        support = 0
                        for value in values:
                            case.assertEqual(support & self.support[value], 0)
                            support |= self.support[value]
                        return support
                    total, single, pairs = super()._block(points, edges, weights, level)
                    case.assertEqual(self.support[total], expected(set()))
                    case.assertEqual(set(single), set(points))
                    for a in points:
                        case.assertEqual(self.support[single[a]], expected({a}))
                    case.assertEqual(set(pairs), set(combinations(points,2)))
                    for a,b in combinations(points,2):
                        case.assertEqual(self.support[pairs[a,b]], expected({a,b}))
                    block_sizes.append(len(points))
                    return total, single, pairs
            local = Audited(h-1)
            block_sizes.clear()
            local.pair(list(range(h-1)))
            self.assertEqual(max(block_sizes), h-1)
            self.assertIn(2,block_sizes)
            self.assertTrue(all(2<=n<=h-1 for n in block_sizes))

    def test_next_fine_grid_points_and_old_assembly_controls_reject(self):
        from split_pair_arithmetic import refine
        current = json.loads((ROOT/'certificates/indexed-cycle-kappa.json').read_text())
        bit = current['bit']; saving = Fraction(current['bit_saving']); kappa = Fraction(current['kappa'])
        grid = Fraction(1,10**18)
        rows = {int(t): n for t,n in bit['child_multiplicities'].items()}
        self.assertLess(refine.exact_moment(bit['m'],bit['W'],rows,saving)['upper'], 1)
        self.assertGreater(refine.exact_moment(bit['m'],bit['W'],rows,saving+grid)['lower'], 1)
        for label, variant in (
                ('next_kappa', dict(kappa=kappa+grid)),
                ('zero_backoff', dict(h=Fraction())),
                ('original_prefix', dict(original_prefix=True)),
                ('old_guard', dict(old_guard=True)),
                ('old_exposures', dict(old_exposures=True))):
            call = dict(a_bit=saving, kappa=kappa, h=Fraction(1,10**12));call.update(variant)
            with self.subTest(control=label), self.assertRaises(refine.balanced.InvalidAssembly):
                refine.balanced.assembly(current['finite_bridge'], **call)

    def test_mass_preserving_profile_mutation_is_rejected(self):
        from indexed_cycle_compose import check_sources
        profile_path = ROOT/'certificates/indexed-cycle-profiles-23.json'
        changed = json.loads(profile_path.read_text())
        before = sum(t*n for t,n in enumerate(changed['blocks']))
        changed['blocks'][2] += 3; changed['blocks'][3] -= 2
        self.assertTrue(all(n >= 0 for n in changed['blocks']))
        self.assertEqual(before, sum(t*n for t,n in enumerate(changed['blocks'])))
        forged = (json.dumps(changed)+'\n').encode()
        original = Path.read_bytes
        def read_bytes(path):
            return forged if path == profile_path else original(path)
        with patch.object(Path, 'read_bytes', read_bytes), self.assertRaisesRegex(AssertionError, 'indexed-cycle-profiles-23'):
            check_sources()

    def test_missing_profile_pin_is_rejected(self):
        from indexed_cycle_compose import check_sources
        manifest_path = ROOT/'research/indexed-cycle/SOURCE.json'
        manifest = json.loads(manifest_path.read_text());manifest['files'].pop('certificates/indexed-cycle-profiles-23.json')
        original = Path.read_text
        def read_text(path, *args, **kwargs):
            return json.dumps(manifest) if path == manifest_path else original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read_text), self.assertRaisesRegex(AssertionError, 'Incomplete'):
            check_sources()

    def test_all_threshold_dependent_bridge_fields_are_checked(self):
        from indexed_cycle_compose import finite_bridge, validate_bridge
        expected = finite_bridge(131795727)
        self.assertTrue(validate_bridge(expected, 131795727))
        for section,key in (('bit','wire_bits'),('rows','coefficient'),('rows','degree'),('rows','degree_gap'),('rows','suffix_slope')):
            changed = deepcopy(expected)
            changed[section][key] = Fraction(changed[section][key])+1
            with self.subTest(field=section+'.'+key), self.assertRaisesRegex(AssertionError, 'Stale finite bridge'):
                validate_bridge(changed, 131795727)

    def test_optimized_python_is_rejected_by_every_new_entry(self):
        for name in ('indexed_cycle_graph.py', 'indexed_cycle_engine.py', 'indexed_cycle_compiler.py', 'split_pair_arithmetic.py', 'indexed_cycle_compose.py', 'verify_indexed_cycle.py'):
            with self.subTest(entry=name):
                result = subprocess.run([sys.executable, '-O', str(EXPERIMENTS/name), '--help'], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Assertions must remain enabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
