"""Separate numeric-depth rational interpreter. Apache-2.0.

Shares only authenticated loading/word expansion, not the symbolic Bound,
Envelope or dispatcher. Explicitly repeats each Gaussian line lambda times.
"""

import hashlib
import json
from fractions import Fraction

import binding

need = binding.require
ZERO = (Fraction(0), 0)
UNIT = (Fraction(1), 0)


def add(x, y):
    if not x[0]:
        return y
    if not y[0]:
        return x
    return x[0] + y[0], max(x[1], y[1])


def scaled(x, c):
    c = Fraction(c)
    need(c.denominator & (c.denominator - 1) == 0, "dyadic")
    if not x[0] or not c:
        return ZERO
    n = abs(c.numerator)
    trailing = (n & -n).bit_length() - 1
    return x[0] * abs(c), x[1] + c.denominator.bit_length() - 1 - trailing


class Numeric:
    def __init__(self, depth):
        need(type(depth) is int and 1 <= depth <= 8, "bounded numeric control depth")
        self.depth = depth
        self.grid = 0
        self.magnitude = Fraction(1)
        self.native_lines = 0

    def visit(self, x):
        if x[0]:
            self.grid = max(self.grid, x[1])
            self.magnitude = max(self.magnitude, x[0])
        return x

    def coefficient(self, x, c):
        c = Fraction(c)
        self.visit(scaled(x, abs(c.numerator)))
        self.visit(scaled(x, c.numerator))
        return self.visit(scaled(x, c))

    def recipe(self, x, row):
        if row["rank"]:
            binding.monomial(row["right"])
        binding.monomial(row["left"])
        for _ in range(row["rank"] * self.depth):
            pair = self.visit(add(x, x))
            cross = self.visit(add(pair, pair))
            x = self.visit(scaled(cross, Fraction(1, 2)))
            self.native_lines += 1
        return x


def run_events(events, state, numeric, packet, children, adapters, residuals, offset):
    cut = hashlib.sha256()
    for index, event in enumerate(events):
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate = event[1]
            dest = binding.reg(gate[1])
            if gate[0] == "clear":
                need(dest >= 704, "private clear")
                state[dest] = ZERO
            elif gate[0] == "scale":
                state[dest] = numeric.coefficient(
                    state[dest], Fraction(gate[2], gate[3])
                )
            else:
                need(gate[0] == "add", "scalar addition")
                term = numeric.coefficient(
                    state[binding.reg(gate[2])], Fraction(gate[3], gate[4])
                )
                state[dest] = numeric.visit(add(state[dest], term))
        else:
            dest = (
                binding.reg(event[1])
                if kind in ("cover_map", "native_line")
                else event[2]
            )
            if kind == "climb":
                state[dest] = numeric.recipe(state[dest], children[event[3], event[4]])
            elif kind == "native_line":
                state[dest] = numeric.recipe(
                    state[dest], packet["native_line_recipes"][event[2]]["recipe"]
                )
            elif kind == "adapter":
                if event[1] == "old_to_new" and dest < 112:
                    binding.monomial(adapters["source", dest]["left"])
                if event[1] == "new_to_old" and 112 <= dest < 224:
                    binding.monomial(adapters["target", dest - 112]["left"])
            elif kind == "residual_adapter":
                key = (
                    str(event[3])
                    if len(event) == 4 or event[4] == 1
                    else f"{event[3]}:{event[4]}"
                )
                binding.monomial(
                    residuals["recipes"][key]["right" if event[1] == "pre" else "left"]
                )
            else:
                need(kind == "cover_map", "native event")
        numeric.visit(state[dest])
        cut.update(
            binding.canonical(
                [offset + index, dest, [str(state[dest][0]), state[dest][1]]]
            )
            + b"\n"
        )
    return cut.hexdigest()


def replay(depth, data, reset=False):
    packet, recipes, residuals = data
    children = {(x["old"], x["new"]): x for x in recipes["children"]}
    adapters = {(x["role"], x["port"]): x for x in recipes["endpoint_adapters"]}
    state = [UNIT] * 704 + [ZERO] * 8
    numeric = Numeric(depth)
    stages, offset = {}, 0
    for name in ("F_0", "B_1_2"):
        if reset and name == "B_1_2":
            state = [UNIT] * 704 + [ZERO] * 8
        events = binding.expand(packet, name)
        cut = run_events(
            events, state, numeric, packet, children, adapters, residuals, offset
        )
        stages[name] = {
            "completed_sha256": cut,
            "final_sha256": binding.digest([[str(x[0]), x[1]] for x in state]),
        }
        offset += len(events)
    need(all(x == ZERO for x in state[704:]), "private return zero")
    return {
        "depth": depth,
        "grid": numeric.grid,
        "max_range": str(numeric.magnitude),
        "native_lines": numeric.native_lines,
        "stages": stages,
    }


def audit():
    data = binding.load()
    binding.cover_maps(data[0])
    expected = json.loads(binding.read(binding.HERE / "RESULT.json", 65536))
    rows = [replay(depth, data) for depth in (1, 2, 3, 8)]
    old = json.loads(binding.read(binding.HERE / "vendor/PR3270-RESULT.json", 65536))
    for name, row in rows[0]["stages"].items():
        need(
            row["completed_sha256"] == old["stages"][name]["completed_bound_sha256"],
            "one-layer cuts",
        )
        need(
            row["final_sha256"] == old["stages"][name]["final_bounds_sha256"],
            "one-layer state",
        )
    for row in rows:
        depth = row["depth"]
        need(
            row["grid"] <= 71 + expected["grid_slope"] * (depth - 1),
            "numeric grid bound",
        )
        need(
            Fraction(row["max_range"])
            < 1 << (143 + expected["range_slope"] * (depth - 1)),
            "numeric range bound",
        )
        need(row["native_lines"] == 11076 * depth, "tensor line count")
    need(rows[1]["grid"] > 71, "one-layer grid cannot certify two-layer envelope")
    costs = old["direct_cost"]
    native = sum(
        costs[k]
        for k in (
            "native_real_additions",
            "native_exact_halvings",
            "native_pair_component_copies",
        )
    )
    need(
        native == 512 * expected["tensor_linear_wordops_per_N"],
        "native operation density",
    )
    need(
        expected["tensor_linear_wordops_per_N"]
        + expected["tensor_constant_wordops_per_N"]
        == 483082,
        "total density",
    )
    return rows


if __name__ == "__main__":
    rows = audit()
    print("PASS_QQ16_NUMERIC_DEPTH_CONTROLS", [(r["depth"], r["grid"]) for r in rows])
