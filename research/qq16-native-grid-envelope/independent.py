#!/usr/bin/env python3
"""Integer-only second derivation of every grid/range observation.

Imports no primary or predecessor implementation. Apache-2.0.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from collections import Counter
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, text):
    if not ok:
        raise ValueError(text)


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj):
    return hashlib.sha256(encode(obj)).hexdigest()


def normalize_coefficient(n, d):
    require(n != 0 and d != 0, "Nonzero coefficient")
    n, d = abs(n), abs(d)
    common = gcd(n, d)
    n, d = n // common, d // common
    require(d & (d-1) == 0, "Power-of-two denominator")
    return n, d


def scale(pair, n, d=1):
    if not pair[0]:
        return (0, 0)
    n, d = normalize_coefficient(n, d)
    shift = d.bit_length()-1
    while n % 2 == 0:
        n //= 2
        shift -= 1
    return pair[0] * n, pair[1] + shift


def add(left, right):
    if not left[0]:
        return right
    if not right[0]:
        return left
    g = max(left[1], right[1])
    return ((left[0] << (g-left[1])) + (right[0] << (g-right[1])), g)


def text_pair(pair):
    n, g = pair
    if g < 0:
        n <<= -g
        g = 0
    while g and n % 2 == 0:
        n //= 2
        g -= 1
    return str(n) if g == 0 else str(n) + "/" + str(1 << g)


def greater(left, right):
    g = max(left[1], right[1])
    return (left[0] << (g-left[1])) > (right[0] << (g-right[1]))


def register(token):
    return token[1] + (704 if token[0] == "C" else 0)


class IntegerLedger:
    def __init__(self):
        self.trace = hashlib.sha256()
        self.max_range = (1, 0)
        self.max_grid = 0
        self.range_site = self.grid_site = [-1, "entry"]
        self.count = 0
        self.event = -1
        self.lines = self.monomials = self.recipes = 0

    def mark(self, pair, stage):
        self.count += 1
        if pair[0] and pair[1] > self.max_grid:
            self.max_grid = pair[1]
            self.grid_site = [self.event, stage]
        if greater(pair, self.max_range):
            self.max_range = pair
            self.range_site = [self.event, stage]
        self.trace.update(encode([self.event, stage, [text_pair(pair), pair[1]]]) + b"\n")
        return pair

    def coefficient(self, pair, n, d):
        n, d = normalize_coefficient(n, d)
        self.mark((pair[0]*n, pair[1]) if pair[0] else (0, 0), "constant-partials")
        product = self.mark(scale(pair, n), "constant-numerator")
        return self.mark(scale(product, 1, d), "constant-result")

    def monomial(self, pair):
        self.monomials += 1
        return self.mark(pair, "monomial")

    def recipe(self, pair, recipe):
        self.recipes += 1
        rank = recipe["rank"]
        if rank:
            pair = self.monomial(pair)
            for _ in range(rank):
                pair_sum = self.mark(add(pair, pair), "native-pair")
                cross = self.mark(add(pair_sum, pair_sum), "native-cross")
                pair = self.mark(scale(cross, 1, 2), "native-halved")
                self.lines += 1
        return self.monomial(pair)


def audit():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for p in sources["files"]:
        if p["usage"] == "input":
            require(hashlib.sha256((ROOT / p["path"]).read_bytes()).hexdigest() == p["sha256"],
                    "Independent input hash")
    packet = json.loads(gzip.decompress((ROOT / "research/joint-query/certificate.json.gz").read_bytes()))
    with tarfile.open(ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz") as tf:
        recipes = json.load(tf.extractfile("slots/local/CLIFFORD-RECIPES.json"))
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    events = packet["core_words"]["forward"][:]
    for entry in packet["programs"]["F_0"][1:]:
        events += entry[2]
    field = [(1, 0)] * 704 + [(0, 0)] * 8
    ledger = IntegerLedger()
    cut_digest = hashlib.sha256()
    coefficients = []
    adds = clears = labels = 0
    for i, op in enumerate(events):
        ledger.event = i
        if op[0] == "phase":
            continue
        if op[0] == "scalar":
            gate = op[1]
            dest = register(gate[1])
            if gate[0] == "clear":
                field[dest] = (0, 0)
                clears += 1
            else:
                n, d = gate[-2:]
                coefficients.append((n, d))
                if gate[0] == "scale":
                    field[dest] = ledger.coefficient(field[dest], n, d)
                else:
                    source = register(gate[2])
                    term = ledger.coefficient(field[source], n, d)
                    field[dest] = ledger.mark(add(field[dest], term), "scalar-add")
                    adds += 1
        elif op[0] == "climb":
            dest = op[2]
            field[dest] = ledger.recipe(field[dest], children[op[3], op[4]])
        elif op[0] == "native_line":
            dest = register(op[1])
            field[dest] = ledger.recipe(field[dest], packet["native_line_recipes"][op[2]]["recipe"])
        elif op[0] == "residual_adapter":
            dest = op[2]
            field[dest] = ledger.monomial(field[dest])
        elif op[0] == "adapter":
            dest = op[2]
            if (op[1] == "old_to_new" and dest < 112) or (
                    op[1] == "new_to_old" and 112 <= dest < 224):
                field[dest] = ledger.monomial(field[dest])
            else:
                labels += 1
        else:
            raise ValueError("Unexpected F0 operation")
        ledger.mark(field[dest], "completed-event")
        cut_digest.update(encode([i, dest, [text_pair(field[dest]), field[dest][1]]]) + b"\n")
    cost = Counter()
    for n0, d0 in coefficients:
        n, d = normalize_coefficient(n0, d0)
        cost["constant_product_calls"] += 1024
        cost["constant_product_component_copies"] += 1024 * n.bit_count()
        cost["constant_product_additions"] += 1024 * (n.bit_count()-1)
        cost["constant_product_left_shifts"] += 1024 * (n.bit_count()-(n & 1))
        cost["constant_product_negations"] += 1024 * ((n0 < 0) != (d0 < 0))
        cost["constant_product_right_shifts"] += 1024 * (d > 1)
    cost.update({
        "scalar_real_additions": 1024*adds,
        "clear_component_writes": 1024*clears,
        "native_gaussian_lines": ledger.lines,
        "native_real_additions": 2048*ledger.lines,
        "native_exact_halvings": 1024*ledger.lines,
        "native_pair_component_copies": 2048*ledger.lines,
        "native_recipe_calls": ledger.recipes,
        "monomial_calls": ledger.monomials,
        "monomial_component_copies": 2048*ledger.monomials,
        "monomial_component_negations_upper_bound": 1024*ledger.monomials,
        "adapter_identity_labels": labels,
        "phase_labels": sum(e[0] == "phase" for e in events),
        "final_owned_scratch_clear_writes": 1036,
    })
    result = json.loads((HERE / "RESULT.json").read_text())
    expected = {
        "events": len(events), "event_sha256": sha(events),
        "grid_guard": ledger.max_grid, "grid_site": ledger.grid_site,
        "max_range_exact": text_pair(ledger.max_range), "range_site": ledger.range_site,
        "primitive_bound_observations": ledger.count,
        "primitive_bound_sha256": ledger.trace.hexdigest(),
        "completed_bound_sha256": cut_digest.hexdigest(),
        "final_bounds_sha256": sha([[text_pair(p), p[1]] for p in field]),
        "direct_cost": dict(cost),
    }
    n, g = ledger.max_range
    expected["range_power_of_two"] = n.bit_length() - (n & (n-1) == 0) - g
    expected["signed_width_P_plus"] = expected["range_power_of_two"] + ledger.max_grid + 1
    for key, value in expected.items():
        require(result[key] == value, "Independent disagreement: " + key)
    print("PASS_QQ16_NATIVE_GRID_INTEGER_RECURRENCE observations=" + str(ledger.count))
    return expected


if __name__ == "__main__":
    audit()
