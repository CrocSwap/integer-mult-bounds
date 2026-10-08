"""Adversarial controls for pinned whole-chain, original-envelope cloning."""
from collections import Counter
from copy import copy, deepcopy
from pathlib import Path
from fractions import Fraction as Q
from unittest.mock import patch
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT/'research/skip-clones'
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('skip_clones_tests_module', HERE/'cloned_graph.py')
clones = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clones)


class WholeChainCloneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.axes = {}
        cls.real_supports = staticmethod(clones.scalar_supports)
        cls.support_cache = {}
        for h in (23, 25):
            base = clones.base_graph(h)
            document = clones.read(HERE/f'clone-jobs-{h}.json')
            base_digest = clones.digest(base)
            stages = []
            current = base
            # Cache only previously verified immutable graph instances. Mutated
            # result graphs still receive the real finite scalar check.
            def cached(circuit, verify_outputs=True):
                key = id(circuit)
                if verify_outputs and key in cls.support_cache:
                    return cls.support_cache[key]
                result = cls.real_supports(circuit, verify_outputs)
                if verify_outputs:
                    cls.support_cache[key] = result
                return result
            with patch.object(clones, 'scalar_supports', cached):
                cached(current)
                for stage in document['rounds']:
                    result = clones.replay_round(current, stage)
                    stages.append((current, stage, result))
                    current = result
            cls.axes[h] = (base, document, current, stages, base_digest)
        cls.base, cls.document, _, _, _ = cls.axes[23]
        cls.stage = cls.document['rounds'][0]

    def reject(self, document, message):
        original = type(self).real_supports
        supports = self.support_cache[id(self.base)]
        def checked(circuit, verify_outputs=True):
            if circuit is self.base and verify_outputs:
                return supports
            return original(circuit, verify_outputs)
        with patch.object(clones, 'scalar_supports', checked):
            with self.assertRaisesRegex(ValueError, message):
                clones.replay_round(self.base, document)

    def test_invalid_parent_and_provider_are_rejected(self):
        for field in ('parent', 'provider'):
            for bad in (True, -1, len(self.base.args), 1):
                stage = deepcopy(self.stage)
                if field == 'parent':
                    stage['jobs'][0]['parent'] = bad
                else:
                    stage['jobs'][0]['providers'][0] = bad
                with self.subTest(field=field, bad=bad):
                    self.reject(stage, 'Invalid integer|Out-of-range|Inactive or source gate')

    def test_provider_capacity_and_matching_collisions_are_rejected(self):
        stage = deepcopy(self.stage)
        stage['jobs'][0]['providers'][1] = stage['jobs'][0]['providers'][0]
        self.reject(stage, 'Providers must be distinct')
        stage = deepcopy(self.stage)
        stage['matching_before'].append(stage['matching_before'][0][:])
        self.reject(stage, 'Prior matching collision')
        stage = deepcopy(self.stage)
        stage['jobs'].append(deepcopy(stage['jobs'][0]))
        self.reject(stage, 'Conflicting clone parent|Provider capacity already used|Clone chains collide')

    def test_named_provider_operand_must_partition_the_parent_exactly(self):
        stage = deepcopy(self.stage)
        job = stage['jobs'][0]
        provider, old_child = job['providers'][0], job['source_children'][0]
        # The replacement remains an actual operand of its named provider;
        # only the required disjoint partition of the parent is broken.
        job['source_children'][0] = next(x for x in self.base.args[provider] if x != old_child)
        self.reject(stage, 'Clone partition does not equal parent with disjoint sources')

    def test_clone_replaces_the_whole_continuation_chain(self):
        position = next(i for i, job in enumerate(self.stage['jobs']) if len(job['chain']) > 1)
        for mutation in ('prefix_only', 'duplicate_use', 'boolean_use'):
            stage = deepcopy(self.stage)
            chain = stage['jobs'][position]['chain']
            if mutation == 'prefix_only':
                chain.pop()
            elif mutation == 'duplicate_use':
                chain.append(chain[-1])
            else:
                chain[0] = True
            with self.subTest(mutation=mutation):
                self.reject(stage, 'Clone must replace one whole continuation chain')

    def test_wrong_first_chain_use_and_stale_graph_pins_are_rejected(self):
        stage = deepcopy(self.stage)
        stage['jobs'][0]['first'] = stage['matching_before'][0][1]
        self.reject(stage, 'Clone must start an actual parent chain')
        for key, message in (('source_graph_sha256', 'Clone source graph differs from pin'),
                             ('output_graph_sha256', 'Clone output graph differs from pin')):
            stage = deepcopy(self.stage)
            stage[key] = '0'*64
            with self.subTest(key=key):
                self.reject(stage, message)

    def test_declared_addition_and_role_counts_cannot_override_actual_graph(self):
        for h, (_, _, result, _, _) in self.axes.items():
            altered = copy(result)
            altered.additions -= 1
            with self.subTest(h=h), self.assertRaisesRegex(ValueError, 'Wrong addition count'):
                type(self).real_supports(altered, verify_outputs=False)

    def test_original_scalar_frames_are_preserved_in_every_round(self):
        for h, (base, _, _, stages, original_digest) in self.axes.items():
            self.assertEqual(clones.digest(base), original_digest)
            for old, stage, result in stages:
                old_support = self.support_cache[id(old)]
                new_support = self.support_cache[id(result)]
                expected = Counter((old_support[n], old.core[n], old.union[n]) for n in old.active)
                expected.update((old_support[job['parent']], old.core[job['parent']],
                                 old.union[job['parent']]) for job in stage['jobs'])
                actual = Counter((new_support[n], result.core[n], result.union[n]) for n in result.active)
                with self.subTest(h=h, source=stage['source_graph_sha256']):
                    self.assertEqual(actual, expected)
                    self.assertEqual(clones.digest(result), stage['output_graph_sha256'])

    def test_rebuilt_finite_fixtures_have_expected_clone_and_role_counts(self):
        # These are independent expected values, not values read from the
        # fixture under test. Old pre-clone fixtures must fail this control.
        for h, expected_clones, expected_roles in ((23, 253, 32693), (25, 353, 43056)):
            base, document, result, _, _ = self.axes[h]
            original = clones.read(HERE/f'original-{h}.json')
            scalar = clones.read(HERE/f'scalar-{h}.json')
            profile = clones.read(HERE/f'profiles-{h}.json')
            with self.subTest(h=h):
                self.assertEqual(sum(len(r['jobs']) for r in document['rounds']), expected_clones)
                self.assertEqual(result.clone_count, expected_clones)
                self.assertEqual(result.additions, base.additions+expected_clones)
                self.assertEqual(scalar['cloned_additions'], expected_clones)
                self.assertEqual(scalar['circuit_sha256'], clones.digest(result))
                self.assertEqual(original['c'], result.additions)
                self.assertEqual(original['q'], len(result.outputs))
                self.assertEqual(original['R'], original['c']+original['q']-original['matched'])
                self.assertEqual(original['R'], expected_roles)
                self.assertEqual(profile['R'], expected_roles)
                self.assertEqual(profile['rank_sum'], sum(t*n for t, n in enumerate(profile['blocks'])))




class SkipCloneCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        specification = importlib.util.spec_from_file_location('skip_clone_witness_tests', HERE/'witness.py')
        cls.witness = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(cls.witness)
        cls.result = cls.witness.run()

    def test_exact_certificate_and_strict_pr53_improvement(self):
        w, result = self.witness, self.result
        self.assertEqual(w.js(result), w.read(HERE/'certificate.json'))
        self.assertGreater(result['kappa'], Q(4498144, 10**11))
        self.assertEqual(len(result['assembly']['constraints']), 47)
        self.assertEqual(len(result['assembly']['margins']), 7)
        self.assertTrue(all(value > 0 for value in result['assembly']['constraints'].values()))
        self.assertTrue(all(value > result['kappa'] for value in result['assembly']['margins'].values()))
        self.assertLess(result['bit']['upper'], 1)

    def test_profile_mass_and_compensated_negative_blocks_rejected(self):
        w = self.witness
        original_read = w.read
        for mutation in ('negative_blocks', 'synchronized_rank_sum'):
            def changed_read(path):
                row = deepcopy(original_read(path))
                if mutation == 'negative_blocks' and Path(path).name == 'profiles-25.json':
                    row['blocks'][1] += 2*(row['blocks'][2]+1)
                    row['blocks'][2] = -1
                elif mutation == 'synchronized_rank_sum' and Path(path).name in ('profiles-25.json', 'original-25.json'):
                    row['rank_sum'] += 1
                return row
            with self.subTest(mutation=mutation), patch.object(w, 'read', changed_read), self.assertRaises(ValueError):
                w.profile()

    def test_clone_jobs_and_graph_code_require_current_source_pins(self):
        import clone_io
        original_read = clone_io.read
        for missing in ('cloned_graph.py', 'clone-jobs-23.json'):
            def missing_pin(path):
                row = deepcopy(original_read(path))
                if Path(path).name == 'SOURCE.json':
                    row['files'].pop('research/skip-clones/'+missing)
                return row
            with self.subTest(missing=missing), patch.object(clone_io, 'read', missing_pin), self.assertRaises(ValueError):
                clone_io.check_sources(clone_io.CERTIFICATE_INPUTS)
        original_bytes = Path.read_bytes
        def stale_bytes(path):
            return original_bytes(path)+(b' changed' if path == HERE/'cloned_graph.py' else b'')
        with patch.object(Path, 'read_bytes', stale_bytes), self.assertRaises(ValueError):
            clone_io.check_sources(clone_io.CERTIFICATE_INPUTS)


if __name__ == '__main__':
    unittest.main()
