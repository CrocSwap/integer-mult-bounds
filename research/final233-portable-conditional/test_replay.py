import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("compact_replay", HERE / "replay.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CompactTests(unittest.TestCase):
    def test_local_integrity_reports_external_missing(self):
        manifest, objects, missing = mod.check()
        self.assertTrue(missing)
        self.assertEqual(len(manifest["entries"]), 59)
        self.assertTrue(objects)

    def test_reject_path_traversal_and_absolute_paths(self):
        for path in ("../escape", "/absolute", "C:/absolute", "a\\b"):
            with self.assertRaises(ValueError):
                mod.safe(HERE, path)

    def test_existing_work_is_not_overwritten(self):
        manifest, objects, _ = mod.check()
        with tempfile.TemporaryDirectory() as work:
            with self.assertRaises(ValueError):
                mod.materialize(Path(work), manifest, objects, None)

    def test_missing_external_does_not_start_materialization(self):
        manifest, objects, missing = mod.check()
        self.assertTrue(missing)
        self.assertTrue(any(e["storage"] == "external" for e in manifest["entries"]))

if __name__ == "__main__":
    unittest.main()
