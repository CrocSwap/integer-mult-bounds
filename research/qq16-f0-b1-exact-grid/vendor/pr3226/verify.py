#!/usr/bin/env python3
"""Conservative finite F0 native grid/range certificate. Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Native semantics and the pair-first lowering are credited in README.md.
This interpreter propagates bounds, not sampled payload values.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIM = 512
FIELDS = 712
MEMBERS = {
    "slots/local/CLIFFORD-RECIPES.json":
        "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731",
    "slots/local/RESIDUAL-ADAPTERS.json":
        "383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for pin in pins["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == pin["sha256"],
                 "Source hash: " + pin["path"])
    packet = json.loads(gzip.decompress(
        (ROOT / "research/joint-query/certificate.json.gz").read_bytes()))
    program = packet["programs"]["F_0"]
    need(program[0][:3] == ["retained_core", "forward", 0], "F0 retained core")
    events = list(packet["core_words"]["forward"])
    for wrapper in program[1:]:
        need(wrapper[0] in ("private_sweep", "cover_sweep"), "F0 wrapper")
        events.extend(wrapper[2])
    objects = []
    with tarfile.open(ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz") as tf:
        for name, sha in MEMBERS.items():
            found = [x for x in tf.getmembers() if x.name == name]
            need(len(found) == 1 and found[0].isfile(), "Unique source member")
            need(found[0].size < 12_000_000, "Bounded source member")
            raw = tf.extractfile(found[0]).read()
            need(hashlib.sha256(raw).hexdigest() == sha, "Member hash: " + name)
            objects.append(json.loads(raw))
    return events, packet, *objects


def reg(token):
    need(isinstance(token, list) and len(token) == 2, "Register token")
    kind, index = token
    need(kind in ("L", "C") and type(index) is int, "Register type")
    need(0 <= index < (704 if kind == "L" else 8), "Register index")
    return index + (704 if kind == "C" else 0)


def valuation(n):
    need(type(n) is int and n != 0, "Nonzero integer valuation")
    n = abs(n)
    return (n & -n).bit_length() - 1


def dyadic(coefficient):
    c = Fraction(coefficient)
    need(c.denominator & (c.denominator - 1) == 0, "Dyadic coefficient")
    return c


@dataclass(frozen=True)
class Bound:
    """|component| <= magnitude M h; component in h 2^-grid Z.

    A zero bound has grid zero by convention. Grid exponents may be negative.
    """
    magnitude: Fraction
    grid: int = 0

    def __post_init__(self):
        need(isinstance(self.magnitude, Fraction) and self.magnitude >= 0,
             "Nonnegative rational magnitude")
        need(type(self.grid) is int, "Integer grid exponent")
        need(self.magnitude != 0 or self.grid == 0, "Canonical zero")

    def scale(self, c):
        c = dyadic(c)
        if not c or not self.magnitude:
            return ZERO
        return Bound(self.magnitude * abs(c),
                     self.grid + c.denominator.bit_length() - 1
                     - valuation(c.numerator))

    def plus(self, other):
        if not self.magnitude:
            return other
        if not other.magnitude:
            return self
        return Bound(self.magnitude + other.magnitude, max(self.grid, other.grid))

    def record(self):
        return [str(self.magnitude), self.grid]


ZERO = Bound(Fraction(0))
UNIT = Bound(Fraction(1))


def ceil_log2(value):
    need(value > 0, "Positive logarithm input")
    n, d = value.numerator, value.denominator
    k = n.bit_length() - d.bit_length()
    power = Fraction(1 << k) if k >= 0 else Fraction(1, 1 << -k)
    return k if value <= power else k + 1


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            k = row.bit_length() - 1
            if k not in basis:
                basis[k] = row
                break
            row ^= basis[k]
    return len(basis)


def check_monomial(m):
    """Signed component permutation, including all 9 active coordinates."""
    need(set(m) == {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"},
         "Monomial fields")
    a, q, z = (m[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4"))
    need(len(a) == len(q) == len(z) == 9, "Nine-axis monomial")
    need(all(type(x) is int and 0 <= x < DIM for x in a + q), "Binary rows")
    need(all(type(x) is int and 0 <= x < 4 for x in z), "Quarter turns")
    need(type(m["offset"]) is int and 0 <= m["offset"] < DIM, "Offset")
    need(type(m["phase"]) is int and 0 <= m["phase"] < 4, "Global phase")
    need(binary_rank(a) == 9, "Invertible monomial")


class Envelope:
    def __init__(self):
        self.max_grid = 0
        self.max_range = Fraction(1)
        self.grid_site = [-1, "entry"]
        self.range_site = [-1, "entry"]
        self.observations = 0
        self.event = -1
        self.cost = Counter()
        self.trace = hashlib.sha256()
        self.validated_monomials = set()

    def observe(self, value, stage):
        self.observations += 1
        if value.magnitude and value.grid > self.max_grid:
            self.max_grid = value.grid
            self.grid_site = [self.event, stage]
        if value.magnitude > self.max_range:
            self.max_range = value.magnitude
            self.range_site = [self.event, stage]
        self.trace.update(canonical([self.event, stage, value.record()]) + b"\n")
        return value

    def multiply(self, value, c):
        """Integer constant product first, exact binary division second.

        Shift/add partial products have no larger magnitude than |numerator|
        times the input; their grids are no finer than the input.
        """
        c = dyadic(c)
        need(c != 0, "Nonzero source coefficient")
        n, d = c.numerator, c.denominator
        self.cost["constant_product_calls"] += 2 * DIM
        self.cost["constant_product_component_copies"] += abs(n).bit_count() * 2 * DIM
        self.cost["constant_product_additions"] += (abs(n).bit_count()-1) * 2 * DIM
        self.cost["constant_product_left_shifts"] += (
            abs(n).bit_count() - (abs(n) & 1)) * 2 * DIM
        self.cost["constant_product_negations"] += (n < 0) * 2 * DIM
        self.cost["constant_product_right_shifts"] += (d > 1) * 2 * DIM
        partial = Bound(value.magnitude * abs(n), value.grid) if value.magnitude else ZERO
        self.observe(partial, "constant-partials")
        product = self.observe(value.scale(n), "constant-numerator")
        return self.observe(product.scale(Fraction(1, d)), "constant-result")

    def line(self, value):
        self.cost["native_gaussian_lines"] += 1
        self.cost["native_real_additions"] += 8 * (DIM // 2)
        self.cost["native_exact_halvings"] += 4 * (DIM // 2)
        self.cost["native_pair_component_copies"] += 8 * (DIM // 2)
        pair = self.observe(value.plus(value), "native-pair")
        cross = self.observe(pair.plus(pair), "native-cross")
        return self.observe(cross.scale(Fraction(1, 2)), "native-halved")

    def mono(self, value, m):
        key = digest(m)
        if key not in self.validated_monomials:
            check_monomial(m)
            self.validated_monomials.add(key)
        self.cost["monomial_calls"] += 1
        # Write the signed permutation to one buffer and copy it back.
        self.cost["monomial_component_copies"] += 4 * DIM
        self.cost["monomial_component_negations_upper_bound"] += 2 * DIM
        return self.observe(value, "monomial")

    def recipe(self, value, r):
        rank = r["rank"]
        need(type(rank) is int and 0 <= rank <= 9, "Native rank")
        self.cost["native_recipe_calls"] += 1
        if rank:
            value = self.mono(value, r["right"])
            for _ in range(rank):
                value = self.line(value)
        else:
            need(r["right"] is None, "Rank-zero right monomial")
        return self.mono(value, r["left"])


def audit(data=None):
    events, packet, recipes, residuals = data or load()
    need(Counter(e[0] for e in events) == {
        "scalar": 21025, "climb": 3486, "adapter": 1090,
        "residual_adapter": 480, "phase": 10, "native_line": 8}, "F0 event inventory")
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    need(len(children) == len(recipes["children"]), "Unique child recipes")
    need(len(adapters) == len(recipes["endpoint_adapters"]), "Unique adapters")
    e = Envelope()
    state = [UNIT] * 704 + [ZERO] * 8
    cut_hash = hashlib.sha256()
    for index, event in enumerate(events):
        e.event = index
        kind = event[0]
        if kind == "scalar":
            gate = event[1]
            dst = reg(gate[1])
            if gate[0] == "clear":
                need(dst >= 704, "Private CLEAR only")
                state[dst] = ZERO
                e.cost["clear_component_writes"] += 2 * DIM
            elif gate[0] == "scale":
                state[dst] = e.multiply(state[dst], Fraction(gate[2], gate[3]))
            else:
                need(gate[0] == "add", "Scalar kind")
                src = reg(gate[2])
                term = e.multiply(state[src], Fraction(gate[3], gate[4]))
                state[dst] = e.observe(state[dst].plus(term), "scalar-add")
                e.cost["scalar_real_additions"] += 2 * DIM
        elif kind == "climb":
            _, _, dst, old, new, _ = event
            need(type(dst) is int and 0 <= dst < 704, "Climb field")
            state[dst] = e.recipe(state[dst], children[old, new])
        elif kind == "adapter":
            _, direction, dst, _ = event
            need(direction in ("old_to_new", "new_to_old") and 0 <= dst < 704,
                 "Adapter direction/field")
            if direction == "old_to_new" and dst < 112:
                a = adapters["source", dst]
                need(a["rank"] == 0 and a["right"] is None, "Monomial source adapter")
                state[dst] = e.mono(state[dst], a["left"])
            elif direction == "new_to_old" and 112 <= dst < 224:
                a = adapters["target", dst-112]
                need(a["rank"] == 0 and a["right"] is None, "Monomial target adapter")
                state[dst] = e.mono(state[dst], a["left"])
            else:
                e.cost["adapter_identity_labels"] += 1
        elif kind == "residual_adapter":
            direction, dst, a = event[1:4]
            need(direction in ("pre", "post") and 224 <= dst < 704,
                 "Residual direction/field")
            b = event[4] if len(event) == 5 else 1
            key = str(a) if b == 1 else f"{a}:{b}"
            state[dst] = e.mono(state[dst], residuals["recipes"][key][
                "right" if direction == "pre" else "left"])
        elif kind == "native_line":
            dst = reg(event[1])
            state[dst] = e.recipe(state[dst], packet["native_line_recipes"][event[2]]["recipe"])
        else:
            need(kind == "phase", "Unknown event")
            e.cost["phase_labels"] += 1
            continue
        e.observe(state[dst], "completed-event")
        cut_hash.update(canonical([index, dst, state[dst].record()]) + b"\n")
    b = ceil_log2(e.max_range)
    e.cost["final_owned_scratch_clear_writes"] = 2 * DIM + 12
    return {
        "schema_version": 1,
        "status": "PASS_QQ16_NATIVE_GRID_ENVELOPE",
        "scope": "Finite literal F0 reference, all 704 bounded input fields, private fields zero",
        "events": len(events), "event_sha256": digest(events),
        "grid_guard": e.max_grid, "grid_site": e.grid_site,
        "range_power_of_two": b, "range_site": e.range_site,
        "max_range_exact": str(e.max_range),
        "signed_width_P_plus": e.max_grid + b + 1,
        "primitive_bound_observations": e.observations,
        "primitive_bound_sha256": e.trace.hexdigest(),
        "completed_bound_sha256": cut_hash.hexdigest(),
        "final_bounds_sha256": digest([x.record() for x in state]),
        "validated_distinct_monomials": len(e.validated_monomials),
        "direct_cost": dict(sorted(e.cost.items())),
        "logical_payload_words": 2 * DIM * FIELDS,
        "additional_scratch_words_upper_bound": 2 * DIM + 12,
        "supplier_admission": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", type=Path, help="Exclusively create a receipt")
    args = p.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "Receipt mismatch")
    print(result["status"], "events=" + str(result["events"]),
          "grid_guard=" + str(result["grid_guard"]),
          "range_bits=" + str(result["range_power_of_two"]),
          "signed_width=P+" + str(result["signed_width_P_plus"]))


if __name__ == "__main__":
    main()
