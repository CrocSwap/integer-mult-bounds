import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pysat.formula import CNF

import generate


class GenerationTests(unittest.TestCase):
    def test_binary_proof_writer_on_real_tiny_unsat(self):
        cnf = CNF(from_clauses=[[1, 2], [1, -2], [-1, 2], [-1, -2]])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'run'
            with patch.object(sys, 'argv', ['generate.py', str(output)]), \
                    patch.object(generate, 'build_instance', return_value=(cnf, None)), \
                    patch.object(generate, 'audit_counter_bridge'), \
                    contextlib.redirect_stdout(io.StringIO()):
                generate.main()
            receipt = json.loads((output / 'generation.json').read_text())
            self.assertEqual((receipt['variables'], receipt['clauses']), (2, 4))
            self.assertGreater((output / 'proof.bdrat').stat().st_size, 0)
            self.assertEqual((output / 'instance.cnf').read_text().splitlines()[0], 'p cnf 2 4')

    def test_nonempty_directory_and_version_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'existing').touch()
            for version in ['1.9.dev15', 'other']:
                with patch.object(sys, 'argv', ['generate.py', directory]), \
                        patch.object(generate, 'version', return_value=version), \
                        self.assertRaises(SystemExit):
                    generate.main()

    def test_sat_does_not_produce_exclusion(self):
        cnf = CNF(from_clauses=[[1]])
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sys, 'argv', ['generate.py', str(Path(directory) / 'run')]), \
                    patch.object(generate, 'build_instance', return_value=(cnf, None)), \
                    patch.object(generate, 'audit_counter_bridge'), \
                    self.assertRaises(SystemExit):
                generate.main()
            self.assertFalse((Path(directory) / 'run/proof.bdrat').exists())


if __name__ == '__main__':
    unittest.main()
