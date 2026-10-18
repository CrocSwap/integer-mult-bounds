#!/usr/bin/env python3
"""Independent literal replay. Imports no constructor or predecessor code."""
from collections import Counter, deque
from array import array
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import random

ROOT = Path(__file__).resolve().parent
BASE = "47481c89fd30a43f8f882eb4b391e89c29273fd0"
PREDECESSOR = "da2cd0dd2229e08b61b174a8835a2c2bb99d2230"
S = (1, 0, 1, -1, 0, -1)
R = (1, 0, -1, -1, 0, 1)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic(k):
    return type(k) is int and k != 0 and abs(k) & (abs(k)-1) == 0


def word_check(word):
    need(type(word) is list, "word is not a list")
    for op in word:
        need(op == "X" or dyadic(op), "query alphabet")


def symbolic(word):
    # Track coefficients of independent incoming x and y directly, with
    # exponents as integers. This does not use the walk's prefix-tap formula.
    x, y = {0}, set()
    for op in word:
        if op == "X":
            y.symmetric_difference_update({0})
        else:
            x = {e+op for e in x}
            y = {e+op for e in y}
    return x, y


def endpoint_check(word, indices):
    word_check(word)
    expected = {sign*(1 << j) for j in indices for sign in [-1, 1]}
    need(symbolic(word) == ({0}, expected), "Laurent endpoint/restoration")


def components(indices):
    # Reconstruct the required-vertex graph from differences, rather than
    # using the constructor's consecutive-index partition.
    vertices = {sign*(1 << j) for j in indices for sign in [-1, 1]}
    unseen = set(vertices)
    groups = []
    while unseen:
        todo = [min(unseen)]
        unseen.remove(todo[0])
        group = []
        while todo:
            v = todo.pop()
            group.append(v)
            neighbors = {w for w in unseen if dyadic(v-w)}
            unseen.difference_update(neighbors)
            todo.extend(neighbors)
        groups.append(sorted(group))
    return sorted(groups)


def lowerings_check(lowerings):
    need(type(lowerings) is dict, "lowerings table")
    for key, events in lowerings.items():
        need(str(int(key)) == key and dyadic(int(key)), "lowering key")
        counts = Counter()
        for op in events:
            need(type(op) is list and op, "native event")
            counts[op[0]] += 1
            if op[0] == "C":
                need(op == ["C", 0, 5], "ordinary child fields")
            else:
                need(op[0] == "A" and len(op) == 4, "affine event schema")
                _, t, d, controls = op
                need(type(t) is int and 0 <= t < 6, "affine target")
                a = F(d)
                need(dyadic(a.numerator) and dyadic(a.denominator), "all-odd diagonal unit")
                seen = set()
                for i, coefficient in controls:
                    need(type(i) is int and 0 <= i < t and i not in seen, "ordered affine control")
                    seen.add(i)
                    need(dyadic(F(coefficient).denominator), "dyadic control denominator")
        need(counts == {"A": 6, "C": 1}, "six affines and one paid child")


def prepared(events, modulus=None, inverse=False):
    if modulus is not None:
        need(type(modulus) is int and modulus >= 3 and modulus % 2 == 1,
             "odd ADDRESS modulus")

    def coefficient(s):
        a = F(s)
        return a if modulus is None else a.numerator * pow(a.denominator, -1, modulus) % modulus

    out = []
    for op in reversed(events) if inverse else events:
        if op[0] == "C":
            out.append(tuple(op))
        else:
            _, t, diagonal, controls = op
            d = F(diagonal)
            cs = [(i, F(v)) for i, v in controls]
            if inverse:
                cs = [(i, -v/d) for i, v in cs]
                d = 1/d
            out.append(("A", t, coefficient(d), [(i, coefficient(v)) for i, v in cs]))
    return out


def native(events, z, modulus=None):
    z = list(z)
    for op in events:
        if op[0] == "C":
            _, i, j = op
            z[i], z[j] = z[j], z[i]
        else:
            _, t, d, cs = op
            z[t] = d*z[t] + sum(v*z[i] for i, v in cs)
            if modulus is not None:
                z[t] %= modulus
    return tuple(z)


def formula(k, z, modulus=None):
    a = F(k, 4) if modulus is None else k*pow(4, -1, modulus) % modulus
    dot = sum(v*w for v, w in zip(R, z))
    out = tuple(v+a*s*dot for v, s in zip(z, S))
    return out if modulus is None else tuple(v % modulus for v in out)


def invoice_check(word, invoice, lowerings):
    word_check(word)
    actual = Counter()
    powers = Counter()
    for op in word:
        if op == "X":
            actual["xor_scans"] += 1
        else:
            need(str(op) in lowerings, "missing native lowering")
            powers[str(op)] += 1
            for event in lowerings[str(op)]:
                actual["children" if event[0] == "C" else "affines"] += 1
    expected = dict(actual, query_multiplicities=dict(powers))
    need(invoice == expected, "literal complete invoice")
    for name in ["children", "affines", "xor_scans"]:
        need(type(invoice[name]) is int, "invoice integer type")
    need(all(type(v) is int for v in invoice["query_multiplicities"].values()),
         "multiplicity integer type")


def source_check():
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    need(sources["format"] == "dyadic-query-runs-sources-v1", "source format")
    need(sources["base_commit"] == BASE and sources["assignment_seed"] == 55,
         "base and assignment")
    need(len(sources["immutable_inputs"]) == 11, "complete retained source inventory")
    seen = set()
    for item in sources["immutable_inputs"]:
        need(item["commit"] == PREDECESSOR, "predecessor head")
        local = item["local"]
        need(local.startswith("vendor/") and ".." not in Path(local).parts and local not in seen,
             "source path/inventory")
        seen.add(local)
        data = (ROOT / local).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256: " + local)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == item["git_blob"], "source Git blob: " + local)
    # The predecessor's retained source manifest also binds its original
    # transitive inputs to their actual original commits and byte digests.
    ancestor = json.loads((ROOT / "vendor/pr840-SOURCES.json").read_text())
    for item in ancestor["immutable_inputs"]:
        data = (ROOT / item["local"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "ancestral source digest")
    return len(seen), len(ancestor["immutable_inputs"])


def invert_word(word):
    return ["X" if op == "X" else -op for op in reversed(word)]


def pack(coords, radices):
    result = 0
    for v, m in zip(coords, radices):
        result = result*m+v
    return result


def full_permutations(modulus, lowerings):
    # Physical order (H0, spectator, H1,H2,D0, spectator,D1,D2),
    # with two binary spectator fields. Every address is enumerated.
    coords = list(product(range(modulus), repeat=6))
    radices = (modulus, 2, modulus, modulus, modulus, 2, modulus, modulus)
    slots = [[pack((z[0], a, z[1], z[2], z[3], b, z[4], z[5]), radices)
              for a, b in product(range(2), repeat=2)] for z in coords]
    U = 4*len(coords)
    literal, direct = {}, {}
    comparisons = 0
    for key, events in lowerings.items():
        p, ref = [0]*U, [0]*U
        ops = prepared(events, modulus)
        for i, z in enumerate(coords):
            got = native(ops, z, modulus)
            expected = formula(int(key), z, modulus)
            need(got == expected, "full ADDRESS push map")
            comparisons += 1
            j = pack(got, (modulus,)*6)
            e = pack(expected, (modulus,)*6)
            for src, dst, correct in zip(slots[i], slots[j], slots[e]):
                p[src], ref[src] = dst, correct
        need(len(set(p)) == U, "native permutation is bijective")
        literal[int(key)], direct[int(key)] = p, ref
    return U, literal, direct, comparisons


def push(data, permutation):
    out = bytearray(len(data))
    for src, dst in enumerate(permutation):
        out[dst] = data[src]
    return out


def xor(a, b):
    return bytearray(x ^ y for x, y in zip(a, b))


def execute(word, state, permutations):
    x, y, z = (bytearray(row) for row in state)
    for op in word:
        x = xor(x, y) if op == "X" else push(x, permutations[op])
    return x, y, z


def adverse_controls(data):
    import copy
    controls = []

    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
            return
        raise ValueError("negative control accepted: " + name)

    case = data["cases"][54]
    word, indices = case["word"], case["indices"]
    rejects("omitted final return", lambda: endpoint_check(word[:-1], indices))
    missing = list(word)
    missing.remove("X")
    rejects("omitted source tap", lambda: endpoint_check(missing, indices))
    changed = list(word)
    changed[0] *= -1
    rejects("wrong query sign", lambda: endpoint_check(changed, indices))
    rejects("VALUE-address confusion", lambda: endpoint_check([True, "X", -1], [0]))
    rejects("source query outside alphabet", lambda: word_check(["QY"]))
    for field in ["children", "affines", "xor_scans"]:
        bill = copy.deepcopy(case["invoice"])
        bill[field] -= 1
        rejects("unpaid " + field, lambda bill=bill: invoice_check(word, bill, data["lowerings"]))
    table = copy.deepcopy(data["lowerings"])
    table["1"] = [op for op in table["1"] if op[0] != "C"]
    rejects("removed native child", lambda: lowerings_check(table))
    table = copy.deepcopy(data["lowerings"])
    table["1"][0][3][0][0] = 5
    rejects("control after target", lambda: lowerings_check(table))
    table = copy.deepcopy(data["lowerings"])
    table["1"][0][2] = "3"
    rejects("nonunit at odd radix", lambda: lowerings_check(table))
    bad_events = copy.deepcopy(data["lowerings"]["1"])
    bad_events[0][3][0][1] = "1"
    basis = (1, 0, 0, 0, 0, 0)
    rejects("scalar-valid wrong native sign", lambda: need(
        native(prepared(bad_events), basis) == formula(1, basis), "native endpoint"))
    rejects("even radix admission", lambda: prepared(data["lowerings"]["1"], 4))

    # Two positive scope controls: the endpoint is valid but the lower-bound
    # hypothesis changes. They must not be reported as failed constructions.
    unrestricted = [-4, "X", 3, "X", 2, "X", 3, "X", -4]
    need(symbolic(unrestricted) == ({0}, {-4, -1, 1, 4}), "nondyadic scope endpoint")
    need(sum(type(op) is int for op in unrestricted) == 5, "nondyadic query count")
    rejects("nondyadic shortcut", lambda: word_check(unrestricted))
    aliased = set()
    for e in [-2, -1, 1, 2]:
        aliased.symmetric_difference_update({e % 3})
    need(not aliased, "modulus-three cancellation scope control")
    # A legal but longer construction is evidence of correctness, not
    # evidence of optimality: the separate-pair seed baseline has 15 queries.
    endpoint_check(case["baseline"], indices)
    rejects("valid nonoptimal invoice", lambda: need(
        case["baseline_invoice"]["children"] == 2*len(indices)+len(components(indices)),
        "restricted optimum"))
    return controls, ["nondyadic five-query endpoint", "modulus-three zero target"]


def finite_walk_census():
    # A separate shortest-walk experiment, not the universal proof: allow
    # every dyadic edge with both endpoints in [-32,32], and any off-support
    # visits. Track all eight possible required vertices simultaneously.
    bound = 32
    width = 2*bound+1
    required = sorted(sign*(1 << j) for j in range(4) for sign in [-1, 1])
    bits = {v: 1 << i for i, v in enumerate(required)}
    steps = [sign*(1 << j) for j in range(7) for sign in [-1, 1]]
    distances = array("i", [-1])*(width*(1 << len(required)))
    distances[bound] = 0
    todo = deque([bound])
    states = edges = 0
    while todo:
        key = todo.popleft()
        mask, offset = divmod(key, width)
        position = offset-bound
        states += 1
        for step in steps:
            target = position+step
            if -bound <= target <= bound:
                edges += 1
                newmask = mask | bits.get(target, 0)
                nxt = newmask*width+target+bound
                if distances[nxt] == -1:
                    distances[nxt] = distances[key]+1
                    todo.append(nxt)
    minima = []
    for selection in range(1, 16):
        indices = [j for j in range(4) if selection & (1 << j)]
        required_mask = sum(bits[sign*(1 << j)] for j in indices for sign in [-1, 1])
        candidates = [distances[mask*width+bound] for mask in range(256)
                      if mask & required_mask == required_mask and distances[mask*width+bound] >= 0]
        best = min(candidates)
        need(best == 2*len(indices)+len(components(indices)), "independent finite walk minimum")
        minima.append([selection, best])
    return {"position_interval": [-bound, bound], "max_dyadic_step": 64,
            "indices": list(range(4)), "reachable_states": states,
            "directed_edges_examined": edges, "completed_selections": minima,
            "scope": "Complete bounded walk census; universal bound is the written proof."}


def verify():
    source_count, ancestor_count = source_check()
    data = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(data["format"] == "dyadic-query-runs-v1" and data["assignment_seed"] == 55,
         "certificate identity")
    need(data["domain"] == {"indices": list(range(6)), "masks": [1, 63]}, "complete domain")
    cases = data["cases"]
    need([case["mask"] for case in cases] == list(range(1, 64)), "every declared mask once")
    lowerings_check(data["lowerings"])
    query_total = baseline_total = 0
    graph_records = []
    for case in cases:
        expected_indices = [j for j in range(6) if case["mask"] & (1 << j)]
        need(case["indices"] == expected_indices, "mask/indices binding")
        groups = components(expected_indices)
        for name, bill in [("word", "invoice"), ("baseline", "baseline_invoice")]:
            word = case[name]
            endpoint_check(word, expected_indices)
            endpoint_check(invert_word(word), expected_indices)
            invoice_check(word, case[bill], data["lowerings"])
        optimum = 2*len(expected_indices)+len(groups)
        need(case["invoice"]["children"] == optimum, "graph lower bound attained")
        need(case["invoice"]["xor_scans"] == 2*len(expected_indices), "tap lower bound attained")
        need(case["baseline_invoice"]["children"] == 3*len(expected_indices), "pair baseline count")
        query_total += optimum
        baseline_total += case["baseline_invoice"]["children"]
        graph_records.append([case["mask"], groups, optimum])
    rational = modular = 0
    moduli = [3, 5, 7, 9, 15, 25, 27, 49, 81]
    for key, events in data["lowerings"].items():
        for modulus in [None]+moduli:
            fwd = prepared(events, modulus)
            inv = prepared(events, modulus, inverse=True)
            for column in range(6):
                basis = tuple(int(i == column) for i in range(6))
                result = native(fwd, basis, modulus)
                need(result == formula(int(key), basis, modulus), "native matrix column")
                need(native(inv, result, modulus) == basis, "literal native inverse")
                need(native(inv, basis, modulus) == formula(-int(key), basis, modulus),
                     "inverse push direction")
                if modulus is None:
                    rational += 1
                else:
                    modular += 1
    negative, positive = adverse_controls(data)
    walk_census = finite_walk_census()
    rng = random.Random(55)
    full_cases = address_points = 0
    stream_hash = hashlib.sha256()
    for modulus in [3, 5]:
        U, literal, direct, checked = full_permutations(modulus, data["lowerings"])
        address_points += checked
        for case in cases:
            state = tuple(bytearray(rng.getrandbits(1) for _ in range(U)) for _ in range(3))
            expected = bytearray(state[0])
            for j in case["indices"]:
                for sign in [-1, 1]:
                    expected = xor(expected, push(state[1], direct[sign*(1 << j)]))
            for name in ["word", "baseline"]:
                out = execute(case[name], state, literal)
                need(out == (expected, state[1], state[2]), "full dirty VALUE endpoint")
                restored = execute(invert_word(case[name]), out, literal)
                need(restored == state, "full dirty inverse restoration")
                for row in out+restored:
                    stream_hash.update(row)
                full_cases += 1
    seed = cases[54]
    return {"format": "dyadic-query-runs-evidence-v1", "cases": len(cases),
            "rational_columns": rational, "modular_columns": modular,
            "odd_moduli": moduli, "full_address_moduli": [3, 5],
            "native_address_comparisons": address_points,
            "spectator_configurations_per_address": 4,
            "dirty_forward_cases": full_cases, "dirty_inverse_cases": full_cases,
            "dirty_execution_sha256": stream_hash.hexdigest(),
            "graph_records_sha256": hashlib.sha256(json.dumps(graph_records).encode()).hexdigest(),
            "all_cases_fused_queries": query_total, "all_cases_baseline_queries": baseline_total,
            "seed_indices": seed["indices"], "seed_invoice": seed["invoice"],
            "seed_baseline_invoice": seed["baseline_invoice"],
            "rejection_controls": negative, "positive_scope_controls": positive,
            "independent_bounded_walk_census": walk_census,
            "source_files": source_count, "ancestral_source_files": ancestor_count}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    result = verify()
    evidence = ROOT / "EVIDENCE.json"
    if args.write_evidence:
        evidence.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    else:
        need(result == json.loads(evidence.read_text()), "complete evidence receipt mismatch")
    print("PASS_DYADIC_QUERY_RUNS cases=63 seed=55 children=15->12 affines=90->72 XOR=10")
    print("dirty_forward={dirty_forward_cases} dirty_inverse={dirty_inverse_cases} "
          "rational_columns={rational_columns} modular_columns={modular_columns}".format(**result))
