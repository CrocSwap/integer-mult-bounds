"""Review controls for the explicitly composed PR2100/PR2117 source pins."""
import importlib.util
import json
from hashlib import sha256
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

def check_disjoint_composed_pins(module):
    """Compose accepted disjoint/ternary/central/mixed-point updates exactly.

    Preserve the complete original baseline payload. The frozen disjoint package
    predates the independent central-factor production update; no historical
    verifier or baseline is rewritten. Dennis with OpenAI Codex assistance.
    """
    for relative in module.PINNED_CERTIFICATES:
        baseline = json.loads(module.git_show(relative))
        live = json.loads((module.ROOT / relative).read_bytes())
        restored = json.loads(json.dumps(live))
        allowed = {'scripts/experiments/disjoint_tensor.py': module.OPTIMIZED_SHA256}
        if relative == 'certificates/ternary-side.json':
            allowed['scripts/experiments/ternary_side.py'] = 'eba4acc6f44c5d56aa8d225266a4a951fc1f1cb84819cdc104e1847578403878'
        if relative == 'certificates/dyadic-central-factor.json':
            allowed['scripts/experiments/complex_centers.py'] = '39cfcf869dc4a00dd30a1e91efb986074371621dad14b390cf1053f6aeea79bf'
        if relative == 'certificates/parity-side.json':
            allowed['scripts/experiments/mixed_point_circuit.py'] = 'cc98eeada267814fa2c0bc5f3ebb844f614d667c74d16d80d7ef29b1f90e0aa5'
        if baseline['source_sha256']['scripts/experiments/disjoint_tensor.py'] != module.ORIGINAL_SHA256:
            raise ValueError('Unexpected base disjoint source pin')
        for source, digest in allowed.items():
            if (live['source_sha256'][source] != digest
                    or sha256((module.ROOT / source).read_bytes()).hexdigest() != digest):
                raise ValueError('Unreviewed composed source pin: ' + source)
            restored['source_sha256'][source] = baseline['source_sha256'][source]
        if restored != baseline:
            raise ValueError('Changed fields beyond reviewed composed source pins: ' + relative)


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
            f = Path(t) / companion; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(b'changed source')
            with self.assertRaises(ValueError): m.check_pin_payload(live, base)

    def test_disjoint_full_payload_and_companion_source(self):
        m = load('disjoint-tensor-frame-unions')
        bases = {rel: m.git_show(rel) for rel in m.PINNED_CERTIFICATES}
        with tempfile.TemporaryDirectory() as t, patch.object(m, 'ROOT', Path(t)), patch.object(m, 'git_show', side_effect=bases.__getitem__):
            for rel in m.PINNED_CERTIFICATES:
                f = Path(t) / rel; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes((ROOT / rel).read_bytes())
            for source in ('scripts/experiments/disjoint_tensor.py', 'scripts/experiments/complex_centers.py', 'scripts/experiments/mixed_point_circuit.py'):
                dependency = Path(t) / source; dependency.parent.mkdir(parents=True, exist_ok=True)
                dependency.write_bytes((ROOT / source).read_bytes())
            companion = 'scripts/experiments/ternary_side.py'
            f = Path(t) / companion; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes((ROOT / companion).read_bytes())
            check_disjoint_composed_pins(m)
            c = Path(t) / 'certificates/ternary-side.json'; original = c.read_bytes()
            bad = json.loads(original); bad['unreviewed_field'] = 1; c.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): check_disjoint_composed_pins(m)
            bad = json.loads(original); bad['source_sha256'][companion] = '0' * 64; c.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): check_disjoint_composed_pins(m)
            c.write_bytes(original)
            central = Path(t) / 'scripts/experiments/complex_centers.py'
            central_original = central.read_bytes(); central.write_bytes(b'unreviewed central successor')
            with self.assertRaises(ValueError): check_disjoint_composed_pins(m)
            central.write_bytes(central_original)
            f.write_bytes(b'changed source')
            with self.assertRaises(ValueError): check_disjoint_composed_pins(m)

if __name__ == '__main__':
    unittest.main()
