"""Review controls for the explicitly composed PR2100/PR2117 source pins."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'research' / name / 'verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CombinedPins(unittest.TestCase):
    def test_ternary_full_payload_and_companion_source(self):
        m = load('ternary-frame-cleared-cache')
        rel = 'certificates/ternary-side.json'
        base = json.loads(m.git_show(rel))
        live = json.loads((ROOT / rel).read_bytes())
        m.check_pin_payload(live, base)
        for key, value in [('unexpected', 1), ('status', 'forged')]:
            bad = json.loads(json.dumps(live)); bad[key] = value
            with self.assertRaises(ValueError): m.check_pin_payload(bad, base)
        bad = json.loads(json.dumps(live))
        companion = 'scripts/experiments/disjoint_tensor.py'
        bad['source_sha256'][companion] = '0' * 64
        with self.assertRaises(ValueError): m.check_pin_payload(bad, base)
        with tempfile.TemporaryDirectory() as t, patch.object(m, 'ROOT', Path(t)):
            f = Path(t) / companion; f.parent.mkdir(parents=True); f.write_bytes(b'changed source')
            with self.assertRaises(ValueError): m.check_pin_payload(live, base)

    def test_disjoint_full_payload_and_companion_source(self):
        m = load('disjoint-tensor-frame-unions')
        bases = {rel: m.git_show(rel) for rel in m.PINNED_CERTIFICATES}
        with tempfile.TemporaryDirectory() as t, patch.object(m, 'ROOT', Path(t)), patch.object(m, 'git_show', side_effect=bases.__getitem__):
            for rel in m.PINNED_CERTIFICATES:
                f = Path(t) / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes((ROOT / rel).read_bytes())
            companion = 'scripts/experiments/ternary_side.py'
            f = Path(t) / companion; f.parent.mkdir(parents=True); f.write_bytes((ROOT / companion).read_bytes())
            m.check_certificate_pin_discipline()
            c = Path(t) / 'certificates/ternary-side.json'; original = c.read_bytes()
            bad = json.loads(original); bad['unreviewed_field'] = 1; c.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): m.check_certificate_pin_discipline()
            bad = json.loads(original); bad['source_sha256'][companion] = '0' * 64; c.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): m.check_certificate_pin_discipline()
            c.write_bytes(original); f.write_bytes(b'changed source')
            with self.assertRaises(ValueError): m.check_certificate_pin_discipline()

if __name__ == '__main__':
    unittest.main()
