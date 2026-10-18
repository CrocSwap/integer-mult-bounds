# SPDX-License-Identifier: Apache-2.0
"""Exercise the actual checker, its geometric hypotheses and failure paths."""

import importlib.util
import json
import marshal
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SPEC = importlib.util.spec_from_file_location('joint_endpoint_under_test', PACKAGE / 'verify.py')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
MARKER = 'PASS_P104_JOINT_ENDPOINT cheap=232 broad=191 bound=235 states=34 pairs=1156'


def run(root, *options):
    command = [sys.executable, '-I', '-O', '-Werror', '-B',
               str(root / 'research/p104-joint-endpoint-obstruction/verify.py'), *options]
    return subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)


def export(root):
    destination = root / 'research/p104-joint-endpoint-obstruction'
    destination.mkdir(parents=True)
    for name in ('verify.py', 'RESULT.json', 'SOURCES.json'):
        shutil.copyfile(PACKAGE / name, destination / name)
    for row in json.loads((PACKAGE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            target = root / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['path'], target)
    return destination


class Behavior(unittest.TestCase):
    def test_cli_and_recomputed_receipt(self):
        result = run(ROOT)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, MARKER))
        emitted = run(ROOT, '--emit')
        self.assertEqual(emitted.returncode, 0, emitted.stderr)
        data = json.loads(emitted.stdout)
        self.assertEqual(data['certificate']['minimum_conditional_union_bound'], 235)
        self.assertEqual(data['geometry']['mutual_edges'], 4368)

    def test_degree_hypothesis_is_essential(self):
        candidates = V.states()
        weaker = min(a[4] + b[4] - V.overlap_cap(a, b, pp=5)
                     for a in candidates for b in candidates)
        self.assertEqual(weaker, 225)
        self.assertLessEqual(weaker, 232)
        data = V.calculate()['geometry']
        ae = [tuple(row) for row in data['arrival_endpoints']]
        ae[V.classes(ae)[2][0]] = (44, 29)
        with self.assertRaisesRegex(ValueError, 'R gap'):
            V.classes(ae)

    def test_false_mutual_graph_facts_reject(self):
        module, word, fixture = V.inputs()
        paths = module['paths'](word)
        (aa, normals), (dd, labels) = module['endpoint_data'](paths, module['ports'](fixture))
        ag = V.classes(module['census'](aa, normals))
        dg = V.classes(module['census'](dd, labels))
        arrival = [{s for s in range(104) if labels[s] in row} for row in aa]
        departure = [{t for t in range(104) if normals[t] in row} for row in dd]
        self.assertEqual(V.degree_facts(arrival, departure, ag, dg)['qq_edges'], 0)
        s, t = dg[1][0], ag[1][0]
        arrival[t].add(s)
        departure[s].add(t)
        with self.assertRaisesRegex(ValueError, 'Q-Q'):
            V.degree_facts(arrival, departure, ag, dg)
        arrival[t].remove(s)
        departure[s].remove(t)
        s = dg[0][0]
        t = next(t for t in ag[0] if s not in arrival[t] or t not in departure[s])
        arrival[t].add(s)
        departure[s].add(t)
        with self.assertRaisesRegex(ValueError, 'P-P'):
            V.degree_facts(arrival, departure, ag, dg)

    def test_git_free_export_is_read_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            export(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = run(root)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, MARKER))
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(after, before)

    def test_source_rejection_precedes_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            export(root)
            marker = root / 'executed'
            (root / V.GEOMETRY).write_text(f'open({str(marker)!r}, "w").write("bad")\n')
            result = run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('input SHA256', result.stderr)
            self.assertFalse(marker.exists())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            export(root)
            (root / V.WORD).write_text('{}')
            result = run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('input SHA256', result.stderr)

    def test_authenticated_source_ignores_a_valid_poisoned_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            export(root)
            path = root / V.GEOMETRY
            stat = path.stat()
            code = compile("raise RuntimeError('poisoned cache executed')", str(path), 'exec')
            payload = (importlib.util.MAGIC_NUMBER + struct.pack('<III', 0,
                       int(stat.st_mtime) & 0xFFFFFFFF, stat.st_size) + marshal.dumps(code))
            for optimization in {str(sys.flags.optimize), '1'}:
                cache = Path(importlib.util.cache_from_source(
                    str(path), optimization=optimization if optimization != '0' else ''))
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_bytes(payload)
            spec = importlib.util.spec_from_file_location('poison_control', path)
            module = importlib.util.module_from_spec(spec)
            with self.assertRaisesRegex(RuntimeError, 'poisoned cache executed'):
                spec.loader.exec_module(module)
            result = run(root)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, MARKER))

    def test_receipt_types_and_duplicate_keys_reject(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = export(root) / 'RESULT.json'
            data = json.loads(target.read_text())
            data['geometry']['qq_edges'] = False
            target.write_text(json.dumps(data))
            result = run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('typed receipt equality', result.stderr)
            target.write_text('{"geometry": {}, "geometry": {}}')
            result = run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('duplicate JSON key', result.stderr)


if __name__ == '__main__':
    unittest.main()
