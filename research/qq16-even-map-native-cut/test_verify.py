#!/usr/bin/env python3
"""Boundary, arithmetic and exported-receipt controls; standard library only."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_cut", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def character(rows, odd):
    """Separate scalar evaluator, without the production evaluate helper."""
    result = []
    for row in rows:
        out = {}
        for (column, (_, shift)), (real, imag) in row.items():
            sign = -1 if odd and shift.bit_count() % 2 else 1
            old = out.get(column, (Q(0), Q(0)))
            out[column] = (old[0] + sign*real, old[1] + sign*imag)
        result.append({key: value for key, value in out.items() if value != (0, 0)})
    return result


def real_minor(rows, row_ids, column_ids):
    lo, hi = character(rows, False), character(rows, True)
    a, b = [], []
    for i in row_ids:
        pairs = [(hi[i].get(j, (0, 0))[0] - lo[i].get(j, (0, 0))[0],
                  hi[i].get(j, (0, 0))[1] - lo[i].get(j, (0, 0))[1]) for j in column_ids]
        a.append([Q(x) for x, _ in pairs])
        b.append([Q(y) for _, y in pairs])
    return [x + [-y for y in z] for x, z in zip(a, b)] + [z + x for x, z in zip(a, b)]


def rational_rank_det(matrix):
    """Real rational elimination, independent of Gaussian determinant code."""
    a, rank, determinant = deepcopy(matrix), 0, Q(1)
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        if pivot != rank:
            a[pivot], a[rank] = a[rank], a[pivot]
            determinant = -determinant
        value = a[rank][col]
        determinant *= value
        for i in range(rank+1, len(a)):
            scale = a[i][col] / value
            if scale:
                a[i] = [x-scale*y for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank, determinant if rank == len(a) else Q(0)


class CutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = v.load_packet()
        cls.original = cls.packet["programs"]["B_1_2"][:80]
        cls.upper = v.construct(cls.packet)
        cls.target = v.replay(cls.packet, cls.original, v.physical_shear(cls.packet))
        cls.actual = v.replay(cls.packet, cls.upper)

    def test_independent_realified_rank_and_determinant(self):
        rows = [x for t in v.T for x in (t, 112+t)] + v.A
        cols = [x for a, t in zip(v.A, v.T) for x in (a, t)] + [112+a for a in v.A]
        self.assertEqual(rational_rank_det(real_minor(self.target, rows, cols)), (48, Q(4096**2)))
        baseline = v.replay(self.packet, self.original)
        self.assertEqual(rational_rank_det(real_minor(baseline, v.T+v.A, v.T+[112+a for a in v.A]))[0], 32)

    def test_projection_is_insufficient_for_full_operator(self):
        bad = deepcopy(self.upper)
        event = deepcopy(self.original[8])
        event[1] = ["L", 224]
        bad.append(event)
        damaged = v.replay(self.packet, bad)
        self.assertNotEqual(damaged[224], self.target[224])
        for odd in (False, True):
            self.assertEqual(character(damaged, odd), character(self.target, odd))
        with self.assertRaises(ValueError):
            v.typed(self.packet, bad)

    def test_all_fields_and_arbitrary_private_input(self):
        self.assertEqual(self.actual, self.target)
        unit = v.identity()
        self.assertEqual(self.actual[224:704], unit[224:704])
        self.assertEqual(self.actual[704], {})
        self.assertEqual(self.actual[705:], unit[705:])
        bad = deepcopy(self.upper)
        del bad[0][2][0]
        damaged = v.replay(self.packet, bad)
        self.assertNotEqual(damaged, self.target)
        self.assertTrue(any(column == 704 for row in damaged[:224] for column, _ in row))
        bad = deepcopy(self.upper)
        del bad[0][2][-1]
        with self.assertRaises(ValueError):
            v.typed(self.packet, bad)

    def test_map_class_and_actual_native_recipe(self):
        name = self.original[8][2]
        bad = deepcopy(self.packet)
        bad["map_registry"][name]["payload_translation_at_identity_owner"] ^= 1
        with self.assertRaisesRegex(ValueError, "even payload"):
            v.invariants(bad)
        bad = deepcopy(self.packet)
        bad["map_registry"][name]["action"] = "payload-only action"
        with self.assertRaisesRegex(ValueError, "owner/payload"):
            v.invariants(bad)
        bad = deepcopy(self.packet)
        bad["map_registry"][name]["owner_right_matrix_columns"] = list(v.AXES)
        bad["map_registry"][name]["owner_right_matrix_columns"][0] ^= 2
        with self.assertRaisesRegex(ValueError, "orthogonal"):
            v.invariants(bad)
        self.assertEqual(v.physical_check(self.packet), 8192)
        bad = deepcopy(self.packet)
        bad["native_line_recipes"]["inverse_21"]["recipe"]["left"]["phase"] += 1
        with self.assertRaisesRegex(ValueError, "Gaussian column"):
            v.physical_check(bad)

    def test_literal_invoice_and_illegal_fields(self):
        def invoice(word):
            flat = list(v.flatten(word))
            adds = [e for e in flat if e[0] == "scalar" and e[1][0] == "add"]
            clears = sum(e[0] == "scalar" and e[1][0] == "clear" for e in flat)
            unit = sum(e[1][4] == 1 for e in adds)
            half = sum(e[1][4] == 2 for e in adds)
            self.assertEqual(unit+half, len(adds))
            return (sum(e[0] == "native_line" for e in flat), sum(e[0] == "cover_map" for e in flat),
                    unit, half, clears, 8*unit+10*half+2*clears)
        self.assertEqual(invoice(self.original), (16, 64, 16, 32, 16, 480))
        self.assertEqual(invoice(self.upper), (24, 64, 40, 32, 32, 704))
        for token in (["L", True], ["L", 704], ["C", 8], ["Q", 0]):
            with self.subTest(token=token), self.assertRaises(ValueError):
                v.register(token)
        bad = deepcopy(self.upper)
        bad[0][2][3][2] = "unknown_native"
        with self.assertRaises(KeyError):
            v.typed(self.packet, bad)

    def test_strict_json_types(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1.0}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                v.load_json(raw)
        self.assertNotEqual(v.exact({"x": False}), v.exact({"x": 0}))

    def test_single_layer_replay_does_not_prove_tensor_replay(self):
        # On two odd Fourier modes, C tensor C has eigenvalue i*i=-1.
        # The simultaneous shift of both modes is +1, so alpha I+beta(T tensor T)
        # instead has eigenvalue +1. The complete replay must retain its lambda=1 scope.
        alpha, beta = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
        odd = [1, -1, -1, 1]
        c = [[alpha, beta], [beta, alpha]]
        actual = [v.ZERO]*4
        for i in range(4):
            for j in range(4):
                coefficient = v.mul(c[i//2][j//2], c[i%2][j%2])
                actual[i] = v.add(actual[i], (odd[j]*coefficient[0], odd[j]*coefficient[1]))
        simultaneous = [v.add((alpha[0]*odd[i], alpha[1]*odd[i]),
                              (beta[0]*odd[i ^ 3], beta[1]*odd[i ^ 3])) for i in range(4)]
        self.assertEqual(actual, [(-x, Q(0)) for x in odd])
        self.assertEqual(simultaneous, [(x, Q(0)) for x in odd])
        self.assertNotEqual(actual, simultaneous)

    def test_free_noncommuting_endpoint_and_wrong_order(self):
        target = v.free_replay(self.original, sheared=True)
        self.assertEqual(v.free_replay(self.upper), target)
        bad = deepcopy(self.upper)
        bad[0][2][3], bad[0][2][4] = bad[0][2][4], bad[0][2][3]
        damaged = v.free_replay(bad)
        self.assertNotEqual(damaged, target)
        # Subtracting before converting the source leaves the bare source word.
        self.assertEqual(damaged[112+v.T[0]][(v.A[0], ())], Q(-1))
        self.assertNotIn((v.A[0], ()), target[112+v.T[0]])

    def test_relocated_cli_and_corruption_controls(self):
        with tempfile.TemporaryDirectory(prefix="qq16-cut-tests-") as temp:
            root = Path(temp) / "repo"
            package = root / "research" / "cut"
            package.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                shutil.copy2(HERE / name, package / name)
            packet_path = root / v.PACKET
            packet_path.parent.mkdir(parents=True)
            shutil.copy2(v.ROOT / v.PACKET, packet_path)
            def run(*args, optimized=False):
                command = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
                return subprocess.run(command + [str(package / "verify.py"), *map(str, args)],
                                      capture_output=True, text=True, timeout=120)
            self.assertEqual(run(optimized=True).returncode, 0)
            receipt = (package / "RESULT.json").read_text()
            result = json.loads(receipt)
            result["exact"]["minor_det"][1] = False
            (package / "RESULT.json").write_text(json.dumps(result))
            self.assertIn("type-exact frozen RESULT", run().stderr)
            (package / "RESULT.json").write_text('{"status":"stale",' + receipt.lstrip()[1:])
            self.assertIn("duplicate JSON key", run().stderr)
            (package / "RESULT.json").write_text(receipt)
            source = (package / "SOURCES.json").read_text()
            stale = json.loads(source); stale["base_commit"] = "0"*40
            (package / "SOURCES.json").write_text(json.dumps(stale))
            self.assertIn("source base", run().stderr)
            (package / "SOURCES.json").write_text(source)
            raw = packet_path.read_bytes()
            packet_path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            self.assertIn("source SHA", run().stderr)
            packet_path.write_bytes(raw)
            output = Path(temp) / "fresh.json"
            self.assertEqual(run("--write-result", output).returncode, 0)
            self.assertEqual(json.loads(output.read_text()), json.loads(receipt))
            before = output.read_bytes()
            self.assertIn("fresh external output only", run("--write-result", output).stderr)
            self.assertEqual(output.read_bytes(), before)
            self.assertIn("fresh external output only", run("--write-result", package / "new.json").stderr)
            self.assertFalse((package / "new.json").exists())


if __name__ == "__main__":
    unittest.main()
