#!/usr/bin/env python3
"""Behavioral controls for the completed-stage error bridge. Apache-2.0."""

import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZERO = (Q(0),) * 4


def plus(*terms):
    result = list(ZERO)
    for coefficient, vector in terms:
        for owner in range(4):
            result[owner] += coefficient * vector[owner]
    return tuple(result)


def route(stage, port, vector):
    if not stage:
        return vector
    pair = ((0, 1) if port % 2 else (1, 2)) if stage == 1 else (
        (2, 3) if port % 3 else (0, 2))
    result = list(vector)
    result[pair[0]], result[pair[1]] = result[pair[1]], result[pair[0]]
    return tuple(result)


class Numeric:
    """Direct source equations on four noncommuting toy cover owners."""

    def __init__(self, packet, word):
        self.word = word
        self.a, self.t, self.u = (packet[name] for name in
                                  ("A_ports", "T_ports", "U_ports"))
        self.r = [{int(p): Q(c) for p, c in row.items()} for row in packet["R_rows"]]
        self.k = [{int(p): Q(c) for p, c in row.items()} for row in packet["K_rows"]]

    def query(self, vector, stage, ports):
        return [plus(*[(c, route(stage, p, vector[p]))
                       for p, c in row.items() if p in ports]) for row in self.r]

    def section(self, query, stage, port):
        return route(stage, port, plus(*[(c, query[k]) for k, c in self.k[port].items()]))

    def f0(self, fields):
        x, y = fields[:112], fields[112:]
        f, c = self.query(x, 0, range(112)), self.query(x, 0, self.t)
        out_x = []
        for p in range(112):
            section = self.section(c if p in self.a else f, 0, p)
            out_x.append(plus((1, x[p]), (-1, section)) if p in self.u else section)
        out_y = [plus((1, y[p]), (1, out_x[p])) if p in self.u else
                 plus((1, x[p]), (1, y[p]), (-1, out_x[p])) for p in range(112)]
        return out_x + out_y

    def b1(self, fields):
        x, y = fields[:112], fields[112:]
        query = self.query(y, 2, self.u + self.t)
        u = [plus((1, y[p]), (1, self.section(query, 2, p))) if p in self.a
             else y[p] for p in range(112)]
        a, b = self.query(x, 1, self.t), self.query(u, 1, range(112))
        out_x, out_y = [], []
        for p in range(112):
            ka, kb = self.section(a, 1, p), self.section(b, 1, p)
            if p in self.u:
                xp, yp = plus((1, x[p]), (-1, y[p])), plus((1, y[p]), (1, ka))
            elif p in self.a:
                xp, yp = plus((1, x[p]), (1, y[p]), (-1, u[p])), u[p]
            else:
                xp = plus((1, kb), (12, ka))
                yp = plus((1, u[p]), (-1, kb), (-11, ka))
            out_x.append(xp)
            out_y.append(yp)
        return out_x + out_y

    def decode(self, fields, suffix=False, word=None):
        names = "ZW" if suffix else "XY"
        state = {f"{c}{p}": fields[i * 112 + p]
                 for i, c in enumerate(names) for p in range(112)}
        events = self.word[2741:] if suffix else self.word
        for event in events if word is None else word:
            op = event[0]
            if op == "clear":
                state[event[1]] = ZERO
            elif op == "add":
                state[event[1]] = plus((1, state[event[1]]),
                                      (Q(event[3]), state[event[2]]))
            elif op == "map":
                state[event[1]] = route(event[2], event[3], state[event[1]])
        return [state[f"{c}{p}"] for c in "ZW" for p in range(112)]


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = runpy.run_path(str(HERE / "verify.py"))
        cls.packet, cls.word = cls.subject["sources"]()
        cls.numeric = Numeric(cls.packet, cls.word)

    def test_exact_noncommuting_producer(self):
        v = [tuple(Q(((p + 3) * (o + 5)) % 17 - 8, 8) for o in range(4))
             for p in range(224)]
        got = self.numeric.decode(self.numeric.b1(self.numeric.f0(v)))
        self.assertEqual(got, v)
        sample = tuple(map(Q, (1, 2, 3, 4)))
        self.assertEqual(route(1, 0, route(2, 0, sample)), tuple(map(Q, (3, 1, 2, 4))))
        self.assertEqual(route(2, 0, route(1, 0, sample)), tuple(map(Q, (2, 3, 1, 4))))

    def test_coherent_stage_faults(self):
        original = [tuple(Q((-1)**(p + o)) for o in range(4)) for p in range(224)]
        ef = [tuple(Q((-1)**(p + 2 * o), 256) for o in range(4)) for p in range(224)]
        eb = [tuple(Q((-1)**(2 * p + o), 8192) for o in range(4)) for p in range(224)]
        first = [plus((1, a), (1, b)) for a, b in zip(self.numeric.f0(original), ef)]
        second = [plus((1, a), (1, b)) for a, b in zip(self.numeric.b1(first), eb)]
        decoded = self.numeric.decode(second)
        error = [plus((1, a), (-1, b)) for a, b in zip(decoded, original)]
        expected = [plus((1, a), (1, b)) for a, b in zip(
            self.numeric.decode(ef, suffix=True), self.numeric.decode(eb))]
        self.assertEqual(error, expected)
        self.assertLessEqual(max(abs(c) for row in error for c in row), Q(3491, 8192))
        self.assertEqual(Q(49, 256) + Q(1923, 8192) + Q(1, 2), Q(7587, 8192))

    def test_sharp_witness_and_scalar_mutation(self):
        rows, _ = self.subject["replay"](self.word[2741:], self.subject["OUTPUTS"])
        witness = [ZERO for _ in range(224)]
        for (i, path), c in rows[112].items():
            self.assertEqual(path, ())
            witness[i] = (Q(1 if c > 0 else -1),) * 4
        self.assertEqual(self.numeric.decode(witness, suffix=True)[112], (Q(49),) * 4)
        altered = [event[:] for event in self.word[2741:]]
        altered[-16][3] = "1"  # W0 += Z0 instead of W0 -= Z0.
        self.assertEqual(altered[-16][:3], ["add", "W0", "Z0"])
        self.assertNotEqual(self.numeric.decode(witness, suffix=True, word=altered)[112],
                            (Q(49),) * 4)

    def test_state_failures(self):
        replay, names = self.subject["replay"], self.subject["OUTPUTS"]
        for word in ([['add', 'F0', 'Z0', '1']], [['clear', 'X0', 'current']],
                     [['begin', 's', 8], ['clear', 'F0', 'q'],
                      ['add', 'F0', 'Z0', '1'], ['end', 's', 8]]):
            with self.subTest(word=word), self.assertRaises(ValueError):
                replay(word, names)
        rows, _ = replay([['clear', 'Z0', 'current']], names)
        self.assertEqual(rows[0], {})
        self.assertEqual(rows[1], {(1, ()): Q(1)})

    def test_capacities_and_geometry(self):
        row = {(0, ()): Q(1)}
        for token in range(4):
            row = self.subject["mapped"](row, token)
        with self.assertRaisesRegex(ValueError, "degree capacity"):
            self.subject["mapped"](row, 4)
        with self.assertRaisesRegex(ValueError, "coefficient capacity"):
            self.subject["add"]({}, {(0, ()): Q(2**33)}, Q(1))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.subject["decode"]('{"x":1,"x":2}')
        packet = dict(self.packet, A_ports=self.packet["A_ports"][:-1])
        with self.assertRaisesRegex(ValueError, "partition"):
            self.subject["geometry"](packet)

    def test_cli_export_and_corruption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research/qq16-producer-defect-transfer"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            inventory = json.loads((HERE / "SOURCES.json").read_bytes())
            for item in inventory["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(HERE.parents[1] / item["path"], target)
            self.assert_cli(package, 'verify.py', True, optimized=True)
            original_receipt = (package / 'RESULT.json').read_bytes()
            refused = subprocess.run(
                [sys.executable, '-Werror', '-I', '-B', str(package / 'verify.py'), '--write'],
                capture_output=True, text=True, timeout=90, check=False)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn('FileExistsError', refused.stderr)
            self.assertEqual((package / 'RESULT.json').read_bytes(), original_receipt)
            source = root / 'research/qq16-line-normalized-decoder/WORD.json'
            source.write_bytes(source.read_bytes() + b' ')
            self.assert_cli(package, 'verify.py', False, message='source drift')
            receipt = json.loads((package / 'RESULT.json').read_bytes())
            receipt['operators']['F0'][0]['l1'] = '0'
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            self.assert_cli(package, 'independent.py', False, optimized=True)
            receipt = json.loads(original_receipt)
            receipt['operators']['F0'][0]['row'] = False
            (package / 'RESULT.json').write_text(json.dumps(receipt))
            self.assert_cli(package, 'independent.py', False, optimized=True)

    def assert_cli(self, package, script, success, optimized=False, message=None):
        command = [sys.executable, '-Werror', '-I', '-B']
        if optimized:
            command.append('-O')
        result = subprocess.run(command + [str(package / script)], capture_output=True,
                                text=True, timeout=90, check=False)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_QQ16_PRODUCER_DEFECT_TRANSFER', result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0)
            if message:
                self.assertIn(message, result.stderr)


if __name__ == '__main__':
    unittest.main()
