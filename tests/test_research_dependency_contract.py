"""Metadata acceptance and execution share the same dependency contract."""
import json
import sys
import unittest
from unittest.mock import patch

import test_research_onboarding as fixtures

package = fixtures.package


class DependencyContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.PackageTests('runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        _, self.manifest = self.fixture.ready()
        self.path = self.fixture.target / 'VERIFY.json'

    @unittest.skipUnless(sys.version_info[:2] == (3, 12), 'generic replay uses Python 3.12')
    def test_omitted_and_empty_requirements_replay_without_dependency_install(self):
        for missing in (True, False):
            for install in (True, False):
                with self.subTest(missing=missing, install=install):
                    self.manifest['requirements'] = []
                    if missing:
                        del self.manifest['requirements']
                    self.path.write_text(json.dumps(self.manifest))
                    before = self.path.read_bytes()
                    (self.fixture.target / 'verify.py').write_text('assert 6*7 == 42\n')
                    with patch.object(package.importlib.metadata, 'version',
                                      side_effect=AssertionError('no dependency should be queried')):
                        package.run_package(self.fixture.root, 'research/fixture', install=install)
                    self.assertEqual(self.path.read_bytes(), before)
                    (self.fixture.target / 'verify.py').write_text('raise SystemExit(7)\n')
                    with self.assertRaisesRegex(ValueError, 'exited 7'):
                        package.run_package(self.fixture.root, 'research/fixture', install=install)

    def test_conflicting_distribution_pins_fail_metadata_validation(self):
        for requirements in (['numpy==1.26.4', 'numpy==2.0.0'],
                             ['sympy==1.13.3', 'sympy==1.14.0']):
            with self.subTest(requirements=requirements):
                self.manifest['requirements'] = requirements
                self.path.write_text(json.dumps(self.manifest))
                with self.assertRaisesRegex(ValueError, 'one version per dependency'):
                    package.validate(self.fixture.root, 'research/fixture')
        self.manifest['requirements'] = ['numpy==1.26.4', 'sympy==1.13.3']
        self.path.write_text(json.dumps(self.manifest))
        _, validated = package.validate(self.fixture.root, 'research/fixture')
        self.assertEqual(validated['requirements'], self.manifest['requirements'])


if __name__ == '__main__':
    unittest.main()
