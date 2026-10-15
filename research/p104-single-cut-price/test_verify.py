#!/usr/bin/env python3
"""Semantic controls for the P104 price certificate. Apache-2.0."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("price_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class PriceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = v.model.load_source()
        cls.graph = v.model.build(cls.w)
        cls.saved = json.loads((HERE / "CERTIFICATE.json").read_text())

    def test_positive_and_expanded_oracle(self):
        result = v.verify()
        self.assertEqual(result["cost"], 864)
        self.assertEqual(result["expanded"]["layers"], 1427)
        self.assertEqual(result["expanded"]["register_unit_edges"], 399680)
        self.assertEqual(result["expanded"]["capacity_penalty"], 72)

    def test_capacity_conservation_cost_and_type(self):
        graph = self.graph
        source_edge = next(i for i, e in enumerate(graph.edges) if e[4] == "source")
        paid_edge = next(i for i, (e, f) in enumerate(zip(graph.edges, self.saved["paid"]["flow"]))
                         if e[4] == "paid" and f)
        cases = []
        c = copy.deepcopy(self.saved["paid"])
        c["flow"][source_edge] = graph.edges[source_edge][2] + 1
        cases.append((c, "flow capacity"))
        c = copy.deepcopy(self.saved["paid"])
        c["flow"][paid_edge] -= 1
        cases.append((c, "flow conservation"))
        c = copy.deepcopy(self.saved["paid"])
        c["cost"] -= 1
        cases.append((c, "stated cost"))
        c = copy.deepcopy(self.saved["paid"])
        c["flow"][source_edge] = True
        cases.append((c, "integer certificate"))
        for c, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(v.Invalid, message):
                v.certificate(graph, c)

    def test_dual_and_unpriced_contact(self):
        c = copy.deepcopy(self.saved["paid"])
        c["potential"][self.graph.cut_nodes["0x1"]] += 1
        with self.assertRaisesRegex(v.Invalid, "reduced cost"):
            v.certificate(self.graph, c)
        graph = copy.deepcopy(self.graph)
        i = next(i for i, (e, f) in enumerate(zip(graph.edges, c["flow"])) if e[4] == "paid" and f)
        graph.edges[i][3] -= 1
        c = copy.deepcopy(self.saved["paid"])
        c["graph_sha256"] = graph.fingerprint()  # Bypass hashing: test mathematical rejection.
        c["cost"] -= c["flow"][i]
        with self.assertRaisesRegex(v.Invalid, "forward reduced cost"):
            v.certificate(graph, c)
        p = self.saved["paid"]["potential"].copy()
        p[self.graph.cut_nodes["0x1"]] += 1
        with self.assertRaisesRegex(v.Invalid, "expanded paid arc"):
            v.expanded_dual(self.w, self.graph, p)

    def test_maximality_and_cut_binding(self):
        # Removing all flows still gives a feasible, zero-cost min-cost flow of
        # value zero; it must not be accepted as the baseline maximum.
        graph = v.model.build(self.w, paid=False)
        c = copy.deepcopy(self.saved["baseline"])
        c["flow"] = [0] * len(graph.edges)
        c["value"] = 0
        with self.assertRaisesRegex(v.Invalid, "flow is not maximum"):
            v.certificate(graph, c)
        moved = v.model.build(self.w, cut=2430)
        with self.assertRaisesRegex(v.Invalid, "graph binding"):
            v.certificate(moved, self.saved["paid"])

    def test_frame_legality_and_equivalent_bases(self):
        rank_bad = copy.deepcopy(self.w)
        event = next(e for e in rank_bad["program"] if e[0] == "transport")
        event[4] += 1
        with self.assertRaisesRegex(v.Invalid, "transport rank"):
            v.model.build(rank_bad)
        nonnested = copy.deepcopy(self.w)
        event = next(e for e in nonnested["program"] if e[0] == "transport" and e[2])
        a = v.model.span(tuple(event[2]))
        event[3] = [next(x for x in range(1, 512) if not (a >> x & 1))]
        with self.assertRaisesRegex(v.Invalid, "nonnested transport"):
            v.model.build(nonnested)
        wrong_add = copy.deepcopy(self.w)
        event = next(e for e in wrong_add["program"] if e[0] == "add")
        event[-1] = [1] if not event[-1] else []
        with self.assertRaisesRegex(v.Invalid, "common frame"):
            v.model.build(wrong_add)
        equivalent = copy.deepcopy(self.w)
        frames = list(equivalent["initial_frames"].values()) + list(equivalent["final_frames"].values())
        for e in equivalent["program"]:
            frames += [e[2], e[3]] if e[0] == "transport" else [e[-1]]
        for f in frames:
            f.reverse()
            if f:
                f.append(f[0])
        graph = v.model.build(equivalent)
        self.assertEqual(graph.fingerprint(), self.graph.fingerprint())
        self.assertEqual(v.expanded_dual(equivalent, graph, self.saved["paid"]["potential"])
                         ["capacity_penalty"], 72)

    def test_source_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.json"
            path.write_bytes((v.model.ROOT / v.model.SOURCE).read_bytes() + b"\n")
            with self.assertRaisesRegex(v.Invalid, "source hash"):
                v.model.load_source(path)
            path = Path(temp) / "receipt.json"
            c = copy.deepcopy(self.saved)
            c["paid"]["frontier"][9][1] = 8
            path.write_text(json.dumps(c))
            with self.assertRaisesRegex(v.Invalid, "frontier receipt"):
                v.verify(path)

    def test_optimizer_rerouting_and_no_overwrite(self):
        spec = importlib.util.spec_from_file_location("price_solve", HERE / "solve.py")
        solver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solver)
        g = v.model.Graph()
        for i in range(4):
            g.node(i, 1, 1)
        # Greedy first path costs 0; a residual cancellation is needed to reach
        # optimum 2 instead of committing to the second path of cost 100.
        for u, target, cost in [(0, 2, 0), (0, 3, 0), (2, 4, 0), (2, 5, 1),
                                 (3, 4, 1), (3, 5, 100), (4, 1, 0), (5, 1, 0)]:
            g.edge(u, target, 1, cost)
        solved = solver.optimize(g, requested=2)
        self.assertEqual((solved["value"], solved["cost"]), (2, 2))
        v.certificate(g, solved)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "existing.json"
            path.write_text("preserve me")
            run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "solve.py"),
                                  "--write", str(path)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(path.read_text(), "preserve me")


if __name__ == "__main__":
    unittest.main()
