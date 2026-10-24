"""Native Windows launch regressions for lossless Unicode command transport.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Retains ywz65's gated Job Object and the isolated runner's ownership contract.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import research_package as package
import run_isolated_tests as isolated
sys.path.pop(0)

RECORDER = """import json, sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps(sys.argv[3:]), encoding='ascii')
raise SystemExit(int(sys.argv[2]))
"""


def windows_units(argv):
    """Count the actual Windows quoting, UTF-16 surrogate pairs and final NUL."""
    return len(subprocess.list2cmdline(argv).encode("utf-16-le", "surrogatepass")) // 2 + 1


@unittest.skipUnless(sys.platform == "win32", "requires native Windows process creation")
class WindowsUnicodeArgvTests(unittest.TestCase):
    def round_trip(self, arguments, supervisor=False, exit_code=0):
        with tempfile.TemporaryDirectory(prefix="unicode argv ") as tmp:
            root = Path(tmp)
            receipt = root / "argv.json"
            argv = [sys.executable, "-I", "-S", "-c", RECORDER,
                    str(receipt), str(exit_code), *arguments]
            # Establish that this same fixture is a valid native command first.
            self.assertLess(windows_units(argv), 16000)
            direct = subprocess.run(argv, cwd=root, capture_output=True, timeout=10)
            self.assertEqual(direct.returncode, exit_code, direct.stderr)
            self.assertEqual(json.loads(receipt.read_text(encoding="ascii")), arguments)
            receipt.unlink()

            if supervisor:
                command = isolated.windows_module_command(argv, sys.executable, root / "cache")
                result = subprocess.run(command, cwd=root, env=dict(os.environ),
                                        capture_output=True, timeout=15)
                self.assertEqual(result.returncode, exit_code, result.stderr)
            elif exit_code:
                with self.assertRaisesRegex(ValueError, f"verification command exited {exit_code}"):
                    package.run_python_replay(argv, root, 10)
            else:
                # Exercise the registered interpreter/cache/ownership path.
                package.run_python_replay(argv, root, 10)
            self.assertEqual(json.loads(receipt.read_text(encoding="ascii")), arguments)

    def test_registered_bmp_argument_fits_and_round_trips(self):
        self.round_trip(["\u03ba" * 6000])

    def test_registered_supplementary_argument_fits_and_round_trips(self):
        self.round_trip(["\U0001f600" * 3500])

    def test_isolated_supervisor_bmp_argument_fits_and_round_trips(self):
        self.round_trip(["\u03ba" * 6000], supervisor=True)

    def test_isolated_supervisor_supplementary_argument_fits_and_round_trips(self):
        self.round_trip(["\U0001f600" * 3500], supervisor=True)

    def test_quotes_empty_arguments_and_unicode_are_preserved(self):
        arguments = ["", "two words", 'quote"\\tail\\', "\u03ba\n\t\U0001f600",
                     "e\u0301", "\u00e9", "literal \\u03ba", "\ud800", "\udfff"]
        for supervisor in (False, True):
            with self.subTest(supervisor=supervisor):
                self.round_trip(arguments, supervisor=supervisor)

    def test_long_unicode_failure_status_is_preserved(self):
        for supervisor in (False, True):
            with self.subTest(supervisor=supervisor):
                self.round_trip(["\u03ba" * 6000], supervisor=supervisor, exit_code=7)


if __name__ == "__main__":
    unittest.main()
