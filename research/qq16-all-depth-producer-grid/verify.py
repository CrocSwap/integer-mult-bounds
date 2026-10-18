"""Symbolic tensor-depth envelope of the literal QQ16 producer. Apache-2.0."""

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction

import binding

need = binding.require


def valuation(n):
    need(type(n) is int and n != 0, "nonzero integer")
    n = abs(n)
    return (n & -n).bit_length() - 1


@dataclass(frozen=True)
class Bound:
    """Magnitude <= M*2**(a*(lambda-1)); grid <= g+b*(lambda-1)."""

    magnitude: Fraction
    grid: int = 0
    a: int = 0
    b: int = 0

    def __post_init__(self):
        need(type(self.magnitude) is Fraction and self.magnitude >= 0, "magnitude")
        need(all(type(x) is int for x in (self.grid, self.a, self.b)), "integer guards")
        need(self.a >= 0 and self.b >= 0, "nonnegative slopes")
        need(self.magnitude != 0 or (self.grid, self.a, self.b) == (0, 0, 0), "zero")

    def plus(self, other):
        if not self.magnitude:
            return other
        if not other.magnitude:
            return self
        return Bound(
            self.magnitude + other.magnitude,
            max(self.grid, other.grid),
            max(self.a, other.a),
            max(self.b, other.b),
        )

    def scale(self, c):
        c = Fraction(c)
        need(c.denominator & (c.denominator - 1) == 0, "dyadic coefficient")
        if not c or not self.magnitude:
            return ZERO
        return Bound(
            self.magnitude * abs(c),
            self.grid + c.denominator.bit_length() - 1 - valuation(c.numerator),
            self.a,
            self.b,
        )

    def record(self):
        return [str(self.magnitude), self.grid, self.a, self.b]


ZERO = Bound(Fraction(0))
UNIT = Bound(Fraction(1))


class Envelope:
    def __init__(self):
        self.max_grid, self.max_range = 0, Fraction(1)
        self.max_a = self.max_b = 0
        self.observations = 0
        self.event = -1
        self.cost = Counter()
        self.trace, self.one_trace = hashlib.sha256(), hashlib.sha256()
        self.monomials = set()

    def observe(self, value, stage):
        self.observations += 1
        if value.magnitude:
            self.max_grid = max(self.max_grid, value.grid)
            self.max_range = max(self.max_range, value.magnitude)
            self.max_a, self.max_b = max(self.max_a, value.a), max(self.max_b, value.b)
        record = [self.event, stage, value.record()]
        self.trace.update(binding.canonical(record) + b"\n")
        record[2] = value.record()[:2]
        self.one_trace.update(binding.canonical(record) + b"\n")
        return value

    def multiply(self, value, c):
        c = Fraction(c)
        need(c != 0 and c.denominator & (c.denominator - 1) == 0, "nonzero dyadic")
        n, d = c.numerator, c.denominator
        self.cost["constant_product_calls"] += 1024
        self.cost["constant_product_component_copies"] += abs(n).bit_count() * 1024
        self.cost["constant_product_additions"] += (abs(n).bit_count() - 1) * 1024
        self.cost["constant_product_left_shifts"] += (
            abs(n).bit_count() - (abs(n) & 1)
        ) * 1024
        self.cost["constant_product_negations"] += (n < 0) * 1024
        self.cost["constant_product_right_shifts"] += (d > 1) * 1024
        partial = (
            Bound(value.magnitude * abs(n), value.grid, value.a, value.b)
            if value.magnitude
            else ZERO
        )
        self.observe(partial, "constant-partials")
        product = self.observe(value.scale(n), "constant-numerator")
        return self.observe(product.scale(Fraction(1, d)), "constant-result")

    def line(self, value):
        self.cost["native_gaussian_lines"] += 1
        self.cost["native_real_additions"] += 2048
        self.cost["native_exact_halvings"] += 1024
        self.cost["native_pair_component_copies"] += 2048
        if not value.magnitude:
            pair = cross = result = ZERO
        else:
            a, b = value.a + 1, value.b + 1
            pair = Bound(2 * value.magnitude, value.grid, a, b)
            cross = Bound(4 * value.magnitude, value.grid, a, b)
            result = Bound(2 * value.magnitude, value.grid + 1, a, b)
        self.observe(pair, "native-pair")
        self.observe(cross, "native-cross")
        return self.observe(result, "native-halved")

    def mono(self, value, m):
        key = binding.digest(m)
        if key not in self.monomials:
            binding.monomial(m)
            self.monomials.add(key)
        self.cost["monomial_calls"] += 1
        self.cost["monomial_component_copies"] += 2048
        self.cost["monomial_component_negations_upper_bound"] += 1024
        return self.observe(value, "monomial")

    def recipe(self, value, row):
        rank = row["rank"]
        need(type(rank) is int and 0 <= rank <= 9, "native rank")
        self.cost["native_recipe_calls"] += 1
        if rank:
            value = self.mono(value, row["right"])
            for _ in range(rank):
                value = self.line(value)
        else:
            need(row["right"] is None, "rank-zero right monomial")
        return self.mono(value, row["left"])


def scalar(envelope, state, gate):
    dest = binding.reg(gate[1])
    if gate[0] == "clear":
        need(dest >= 704, "owned clear only")
        state[dest] = ZERO
        envelope.cost["clear_component_writes"] += 1024
    elif gate[0] == "scale":
        state[dest] = envelope.multiply(state[dest], Fraction(gate[2], gate[3]))
    else:
        need(gate[0] == "add", "scalar kind")
        source = binding.reg(gate[2])
        term = envelope.multiply(state[source], Fraction(gate[3], gate[4]))
        state[dest] = envelope.observe(state[dest].plus(term), "scalar-add")
        envelope.cost["scalar_real_additions"] += 1024
    return dest


def native(envelope, state, event, packet, children, adapters, residuals):
    kind = event[0]
    dest = binding.reg(event[1]) if kind in ("native_line", "cover_map") else event[2]
    need(type(dest) is int and 0 <= dest < 712, "native field")
    if kind == "climb":
        state[dest] = envelope.recipe(state[dest], children[event[3], event[4]])
    elif kind == "native_line":
        state[dest] = envelope.recipe(
            state[dest], packet["native_line_recipes"][event[2]]["recipe"]
        )
    elif kind == "adapter":
        direction = event[1]
        if direction == "old_to_new" and dest < 112:
            state[dest] = envelope.mono(state[dest], adapters["source", dest]["left"])
        elif direction == "new_to_old" and 112 <= dest < 224:
            state[dest] = envelope.mono(
                state[dest], adapters["target", dest - 112]["left"]
            )
        else:
            envelope.cost["adapter_identity_labels"] += 1
    elif kind == "residual_adapter":
        direction, _, a = event[1:4]
        b = event[4] if len(event) == 5 else 1
        key = str(a) if b == 1 else f"{a}:{b}"
        state[dest] = envelope.mono(
            state[dest],
            residuals["recipes"][key]["right" if direction == "pre" else "left"],
        )
    else:
        need(kind == "cover_map" and event[2] in packet["map_registry"], "cover map")
        envelope.cost["full_cover_maps"] += 1
        envelope.cost["cover_component_transfers"] += 2048
        envelope.observe(state[dest], "cover-uniform-bound")
    return dest


def run_stage(events, state, envelope, packet, children, adapters, residuals, offset):
    one_cut, symbolic_cut = hashlib.sha256(), hashlib.sha256()
    for index, event in enumerate(events):
        envelope.event = offset + index
        if event[0] == "phase":
            envelope.cost["phase_labels"] += 1
            continue
        dest = (
            scalar(envelope, state, event[1])
            if event[0] == "scalar"
            else native(envelope, state, event, packet, children, adapters, residuals)
        )
        envelope.observe(state[dest], "completed-event")
        one_cut.update(
            binding.canonical([offset + index, dest, state[dest].record()[:2]]) + b"\n"
        )
        symbolic_cut.update(
            binding.canonical([offset + index, dest, state[dest].record()]) + b"\n"
        )
    return {
        "events": len(events),
        "event_sha256": binding.digest(events),
        "one_layer_completed_sha256": one_cut.hexdigest(),
        "symbolic_completed_sha256": symbolic_cut.hexdigest(),
        "one_layer_final_sha256": binding.digest([x.record()[:2] for x in state]),
        "symbolic_final_sha256": binding.digest([x.record() for x in state]),
    }


def check_one_layer(envelope, stages):
    old = json.loads(binding.read(binding.HERE / "vendor/PR3270-RESULT.json", 65536))
    need(envelope.cost == old["direct_cost"], "one-layer operation inventory")
    need(
        envelope.one_trace.hexdigest() == old["primitive_bound_sha256"],
        "one-layer primitive trace",
    )
    need(
        envelope.observations == old["primitive_bound_observations"],
        "observation count",
    )
    need(
        (envelope.max_grid, str(envelope.max_range)) == (71, old["max_range_exact"]),
        "one-layer maxima",
    )
    for name, row in stages.items():
        prior = old["stages"][name]
        need(
            row["one_layer_completed_sha256"] == prior["completed_bound_sha256"],
            "one-layer cuts",
        )
        need(
            row["one_layer_final_sha256"] == prior["final_bounds_sha256"],
            "one-layer states",
        )
    need(envelope.max_range < 1 << 143, "strict range bound")


def audit():
    packet, recipes, residuals = binding.load()
    cover_count = binding.cover_maps(packet)
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    need(len(children) == len(recipes["children"]), "unique children")
    need(len(adapters) == len(recipes["endpoint_adapters"]), "unique adapters")
    state = [UNIT] * 704 + [ZERO] * 8
    envelope = Envelope()
    stages, offset = {}, 0
    for name in ("F_0", "B_1_2"):
        events = binding.expand(packet, name)
        stages[name] = run_stage(
            events, state, envelope, packet, children, adapters, residuals, offset
        )
        offset += len(events)
    need(all(x == ZERO for x in state[704:]), "private return zero")
    envelope.cost["final_owned_scratch_clear_writes"] = 1036
    check_one_layer(envelope, stages)
    return {
        "status": "PASS_QQ16_ALL_DEPTH_PRODUCER_GRID",
        "events": offset,
        "stages": stages,
        "grid_intercept_at_one": 71,
        "grid_slope": envelope.max_b,
        "range_bits_at_one": 143,
        "range_slope": envelope.max_a,
        "signed_width_P_plus_at_one": 215,
        "signed_width_slope": envelope.max_a + envelope.max_b,
        "primitive_observations": envelope.observations,
        "symbolic_trace_sha256": envelope.trace.hexdigest(),
        "one_layer_trace_sha256": envelope.one_trace.hexdigest(),
        "direct_cost_at_one": dict(sorted(envelope.cost.items())),
        "tensor_linear_wordops_per_N": 10 * 11076,
        "tensor_constant_wordops_per_N": 483082 - 10 * 11076,
        "cover_transfers_per_N": 2112,
        "storage_words_per_N": 1426,
        "scalar_scratch_words": 12,
        "distinct_cover_maps_checked": cover_count,
        "payload_dimension": "N=2^(73*lambda), every integer lambda>=1",
        "physical_routing_priced": False,
        "supplier_admission": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    result = audit()
    if args.output:
        with open(args.output, "x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads(binding.read(binding.HERE / "RESULT.json", 65536))
        need(
            binding.canonical(result) == binding.canonical(expected), "receipt mismatch"
        )
    print(
        result["status"],
        "grid slope",
        result["grid_slope"],
        "width slope",
        result["signed_width_slope"],
    )


if __name__ == "__main__":
    main()
