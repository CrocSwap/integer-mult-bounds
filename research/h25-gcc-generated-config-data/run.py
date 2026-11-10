"""Thin export integrity and pure-test entry point; package-local inputs only."""
from pathlib import Path
import hashlib
import importlib
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "SOURCE-ORIGIN.json").read_text())
for row in manifest["copied_files"]:
    path = ROOT / row["path"]
    if path.is_symlink() or not path.is_file():
        raise SystemExit("nonregular export input: " + row["path"])
    body = path.read_bytes()
    if len(body) != row["bytes"] or hashlib.sha256(body).hexdigest() != row["sha256"]:
        raise SystemExit("export byte identity mismatch: " + row["path"])
core = ROOT / "unit03/gcc"
sys.path.insert(0, str(core))
module = importlib.import_module("test_configured_data_v1")
for name in ("configured_data_v1", "generated_config_v1", "test_configured_data_v1"):
    if Path(sys.modules[name].__file__).resolve().parent != core:
        raise SystemExit("nonlocal module: " + name)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.testsRun != 29 or not result.wasSuccessful():
    raise SystemExit(1)
print("PASS_EXPORTED_BYTE_IDENTITIES_AND_29_PURE_CONTROLS")
