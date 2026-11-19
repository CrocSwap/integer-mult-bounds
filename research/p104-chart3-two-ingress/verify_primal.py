#!/usr/bin/env python3
"""Check the 126 two-ingress exclusions directly on the pinned primal graph."""

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
Q = Fraction
HEAD = "89a67c404226d51028e135de2b9169e9020d57af"
WORD = "c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb"
LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
WORD_ARCHIVE = "fde0f7eaa3749d0934a9fc0d6320074f021cd722ed6753f3a59a62fb5b221949"
LAYOUT_ARCHIVE = "b0f3ebc5710e469f3e8fc5ce159cbba048b563944182b50993431ef94f4fedbf"


def read_pinned(name, archive_digest, payload_digest):
    raw = (HERE / "source" / name).read_bytes()
    require(sha256(raw).hexdigest() == archive_digest, f"bad compressed source pin for {name}")
    payload = gzip.decompress(raw)
    require(sha256(payload).hexdigest() == payload_digest, f"bad source payload pin for {name}")
    return json.loads(payload)


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def add_scaled(dst, row, coefficient):
    for index, value in row.items():
        updated = dst.get(index, 0) + coefficient * value
        if updated:
            dst[index] = updated
        else:
            dst.pop(index, None)


class NativeGraph:
    def __init__(self, word, layout):
        self.word = word
        self.schedule = word["schedule"]
        self.order = {key: clock for clock, key in enumerate(self.schedule)}
        self.routes = {key: (start, end) for key, start, end in word["moves"]}
        self.forms = {
            key: {symbol: Fraction(value) for symbol, value in row}
            for key, row in word["forms"]
        }
        self.terminals = {
            word["first_output"] + i: chart for i, chart in enumerate(word["final"])
        }
        self.primary = defaultdict(list)
        for i, chart in enumerate(word["initial"]):
            self.primary[chart].append(~i)
        self.arrivals = defaultdict(list)
        for key, (_, chart) in self.routes.items():
            self.arrivals[chart].append(key)

        require(layout["frames"] == word["frames"], "word and layout charts")
        require(layout["public"] == len(word["initial"]) == len(self.terminals) == 1289,
                "1289 arbitrary inputs and outputs")
        require(len(self.routes) == len(word["moves"]) == 5709, "complete MOVE roster")
        require(len(self.order) == len(self.schedule) == len(self.forms) == len(word["forms"])
                == 6998, "complete ordered form roster")
        require(set(self.order) == self.routes.keys() | self.terminals.keys() == self.forms.keys()
                and self.routes.keys().isdisjoint(self.terminals), "each form is one send or terminal")
        for key in self.schedule:
            owner = self.routes[key][0] if key in self.routes else self.terminals[key]
            local_stock = set(self.stock(owner, key))
            require(self.forms[key].keys() <= local_stock, f"noncausal or nonlocal source at {key}")

    def stock(self, chart, before):
        previous = [key for key in self.arrivals[chart] if self.order[key] < self.order[before]]
        return sorted(self.primary[chart] + previous)

    def pulse_columns(self, keys):
        responses = {}
        for key in self.schedule:
            row = {key: Fraction(1)} if key in keys else {}
            for symbol, q in self.forms[key].items():
                if symbol in responses:
                    add_scaled(row, responses[symbol], q)
            if row:
                responses[key] = row
        return responses


def add_mod(dst, src, gain, prime):
    for key, value in src.items():
        value = (dst.get(key, 0) + gain * value) % prime
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def reduce_mod(row, pivots, prime, stop_on_unpivoted=False):
    remaining, outside = row.copy(), {}
    while remaining:
        key = min(remaining)
        if key in pivots:
            add_mod(remaining, pivots[key], -remaining[key], prime)
        elif stop_on_unpivoted:
            return remaining
        else:
            outside[key] = remaining.pop(key)
    return outside


E, F, P, RECEIVER = 97760, 95681, 99128, 3
PRIME = 65521


def replay():
    graph = NativeGraph(read_pinned("WORD.json.gz", WORD_ARCHIVE, WORD),
                        read_pinned("LAYOUT.json.gz", LAYOUT_ARCHIVE, LAYOUT))
    first = graph.word["first_output"]
    raw = (EVIDENCE / "SCREEN.json").read_bytes()
    saved = json.loads(raw)
    probe_bytes = (HERE / "WITNESSES.json").read_bytes()
    require(saved["source"]["head"] == HEAD and saved["source"]["word_sha256"] == WORD
            and saved["source"]["layout_sha256"] == LAYOUT
            and sha256(probe_bytes).hexdigest() == saved["source"]["probe_input_sha256"],
            "bound receipt source and frozen probes")
    inputs = json.loads(probe_bytes)
    require(not graph.arrivals[RECEIVER] and not [k for k, c in graph.terminals.items() if c == RECEIVER]
            and len(graph.primary[RECEIVER]) == 908, "adjoint chart 3 is a saturated terminal sink")
    successor = defaultdict(list)
    for k, local in graph.forms.items():
        for d in local:
            successor[d].append(k)

    def bank(chart):
        return sorted({k for k, (a, _) in graph.routes.items() if a == chart}
                      | {~(k - first) for k, c in graph.terminals.items() if c == chart})

    def held(chart, prohibited):
        permitted = []
        for key in bank(chart):
            nodes, visited = [key] if key >= 0 else [], set()
            while nodes:
                k = nodes.pop()
                if k in prohibited:
                    break
                if k not in visited:
                    visited.add(k)
                    nodes.extend(successor[k])
            else:
                permitted.append(key)
        return permitted

    def reverse(initial, mod=False):
        if mod:
            values = defaultdict(dict, {first + i: {i: 1} for i in range(len(graph.terminals))})
        else:
            values = defaultdict(Q, {first + i: q for i, q in initial.items()})
        for k in reversed(graph.schedule):
            for d, q in graph.forms[k].items():
                if mod:
                    add_mod(values[d], values[k], q.numerator * pow(q.denominator, -1, PRIME), PRIME)
                elif values[k]:
                    values[d] += values[k] * q
        return lambda key: values[first + ~key if key < 0 else key]

    A, U, V = (held(c, {E, F}) for c in (3, 768, 508))
    require(len(A) == 907 and set(bank(3)) == set(A) | {F}
            and set(A) == set(saved["source_banks"]["receiver"])
            and set(U) == set(saved["source_banks"]["rank_six"])
            and set(V) == set(saved["source_banks"]["first_recoded"]), "complete saved bank census")
    q, r = [reverse({i: Q(v) for i, v in inputs[k]["coordinates"]}) for k in ("r14_pulse", "r15_pulse")]
    require(q(F) == r(F) == -960 and all(not q(k) for k in A + U)
            and all(not r(k) for k in A + V), "both exact rational adjoint pulses")
    mod = reverse({}, mod=True)

    def rank(keys):
        pivots = {}
        for key in keys:
            row = reduce_mod(mod(key), pivots, PRIME, stop_on_unpivoted=True)
            if row:
                j = min(row)
                inv = pow(row[j], -1, PRIME)
                pivots[j] = {i: v * inv % PRIME for i, v in row.items()}
        return len(pivots)

    proofs = [saved["rank_six_intersection"], saved["first_recoded_intersection"]]
    relations = []
    for proof, stock in zip(proofs, (U, V), strict=True):
        chosen = set(proof["chosen_source"])
        missing = {item["omitted"] for item in proof["exact_dependencies"]}
        require(chosen <= set(stock) and missing == set(stock) - chosen, "all nonbasis source atoms covered")
        rhs_support = set()
        for relation in proof["exact_dependencies"]:
            row = {int(k): Q(v) for k, v in relation["source_expression"].items()}
            rhs = {int(k): -Q(v) for k, v in relation["receiver_expression"].items()}
            omitted = relation["omitted"]
            require(row.keys() <= chosen | {omitted} and row[omitted] == 1 and rhs.keys() <= set(A),
                    "triangular exact decomposition")
            rhs_support.update(rhs)
            row.update(rhs)
            relations.append(row)
        require(rhs_support == set(proof["receiver_support"]), "complete exact intersection support")
    support = set().union(*(row.keys() for row in relations))
    pulses = graph.pulse_columns({first + ~d if d < 0 else d for d in support})
    require(all(sum(q * pulses.get(k, {}).get(first + ~d if d < 0 else d, 0) for d, q in row.items()) == 0
                for k in graph.terminals for row in relations), "all published rational source relations")
    ranks = [rank(A), *(rank(A + proof["chosen_source"]) for proof in proofs)]
    require(ranks == [907, 910, 909], "alternate modular independent minors")
    require(set(proofs[0]["receiver_support"]) == {P}, "only the old 99128 direction at chart 768")
    V_support = set(proofs[1]["receiver_support"])
    sites = {}
    for k in A:
        if k == P:
            continue
        chart = graph.routes[k][1]
        available = held(chart, {E, F, k})
        if any(q(j) for j in available):
            sites[k] = [(q(j), r(j)) for j in available if q(j) or r(j)]
    require(set(sites) == set(inputs["saved_first_pulse_roster"]["paid_slots"]), "regenerated complete shortlist")
    counts = Counter()
    for k, responses in sites.items():
        a, b = responses[0]
        equal_nonzero = a == b or any(a*d != b*c for c, d in responses)
        if equal_nonzero:
            require(k not in V_support, "chart 508 cannot supply the extra preserved direction")
        counts["exact quotient rank at most two" if equal_nonzero else "exact probe exclusion"] += 1
    require(counts == saved["quotient_outcomes"], "independent classification of all 126 cases")
    return {"status": "PASS_R16_126_SCOPED_EXCLUSIONS", "source": saved["source"],
            "source_receipt_sha256": sha256(raw).hexdigest(), "ranks": ranks,
            "independent_receiver_directions_required": 908, "fixed_receiver_directions": 905,
            "outcomes": counts, "second_intersection_support": sorted(V_support)}


if __name__ == "__main__":
    verified = replay()
    reproduced = json.dumps(verified, indent=2, sort_keys=True) + "\n"
    require(reproduced.encode() == (EVIDENCE / "REVIEW-PRIMAL.json").read_bytes(),
            "exact independent primal replay receipt differs")
    print(verified["status"])
