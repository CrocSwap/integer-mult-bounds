#!/usr/bin/env python3
"""Independent backward Gaussian-pair polynomial audit of the literal caller.

Reverse FUNCTIONAL pullback is not inversion or Hermitian conjugation. The
classical quotient-polynomial method and our earlier6361 reverse audit retain
their credit; no author, peer, predecessor or local scientific code is loaded.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parent
FROZEN = {
    "SOURCE-PINS.json": "c74239713cbebdea38f0cca551a17606617878a83c82d4ef0a5cb689e8ce9cb0",
    "verify_local.py": "1cff5ecc5af60a97aca7ddc425f56a2abdf42fa8def6a64b9bf9abed8d9f08d9",
    "oracle_local.py": "e6191d69f80612ba6b51e8d2963ebc80fe77f35c163ae4e526eefa05b6bce393",
    "LOCAL-RESULT.json": "cb82b5ff7ccb32971ef839974f9d43461f89d8bd738409e5c3577aa0aa9f2894",
    "LOCAL-ORACLE.json": "ea0bcc77e8a1b9a21e24c35a318f7523b4867272d294fc73c57967e44fb9c7eb",
    "PROOF.md": "a40f40fe7812d5e7503178a1789c7f84f9d70fd4ba49f24f0612877c3b025820",
    "sources/CONTROLLER.json": "4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c",
    "sources/NOTICE": "b6026dd901f3cb2e6ec6d5f7b32a38aa998005c8a1df93392151ca1766d45b33",
    "sources/ROOT.json": "2f25684c24ae0e1d10d4f8f29430aed3cef584f82c8ae840e82be0a72baa048d",
    "sources/algebra-source.py": "02eb3380715294334710edd3273f267dc048264555bd60fefb86022bc9eda835",
    "sources/author-caller-reverse.py": "6435f092e7f435aa30db3877237056cc00fcb206fd8c87a3bddf380dbb7e80e9",
    "sources/controller-source.py": "e5671c66a4091f1b482a750baf5bedf9ac0750e577efbe3c5b3d2860d2fa8edc",
    "sources/headroom-NOTICE": "87d3cf335599cec76ede9e68e58fa13b077e823004aab60ad17b22196cdc3747",
    "sources/normalization-PROOF.md": "68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9",
    "sources/upstream-PROOF.md": "bfbe0b872f6ff14c858bff47c6e3ac0bb8e43bc8eeaec20253744e3f44720fcd",
}
BLOBS = {
    "CONTROLLER.json": "4f7d7a2f13b13966b10c7b583d28d1bed210364c",
    "ROOT.json": "b59f1ea89aca17f0a76131743c12f2c724421df8",
    "upstream-PROOF.md": "510bf9dba012949ea0f37d9e087ce8778b1951d0",
    "NOTICE": "03e4ac5937424ed9f0ae0e4b33d6b0df0c9ec8d9",
    "controller-source.py": "393524f903b44be54884475d11200f06ce1dfddb",
    "algebra-source.py": "a06d6f641685e96b2f150ea6b741930a9ec037f8",
    "normalization-PROOF.md": "f910b5fbf9a9d519fa7d7c7503de51df5a796368",
    "author-caller-reverse.py": "be84e58dc5c1836261441c1a58d4ffe51315c23f",
    "headroom-NOTICE": "081d5cea1467c7cecfe35a37608963dda4e483b7",
}
CAPS = {"seconds": 120, "terms_per_cell": 10000, "terms_per_functional": 100000,
        "maximum_RSS_bytes": 512*1024*1024}
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
UNIT = (0,)*19


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(raw):
    def unique(items):
        answer = {}
        for key, value in items:
            require(key not in answer, "Duplicate JSON member")
            answer[key] = value
        return answer
    def bad(value):
        raise ValueError("Nonfinite JSON value " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticate():
    data = {}
    for name, sha in FROZEN.items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Frozen scientific sha256 mismatch: " + name)
        if name.startswith("sources/"):
            short = name[len("sources/"):]
            require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == BLOBS[short],
                    "Source Git blob mismatch: " + short)
            if short in ("CONTROLLER.json", "ROOT.json"):
                data[short] = decode(raw)
    return data


def rational(value):
    require(type(value) in (str, int), "Exact rational string/integer coefficient")
    return F(value)


def zadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def zmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


class Budget:
    def __init__(self):
        self.started = time.monotonic()

    def check(self):
        require(time.monotonic()-self.started <= CAPS["seconds"], "Explicit endpoint time cap exceeded")
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss_bytes = int(rss) if sys.platform == "darwin" else int(rss)*1024
        require(rss_bytes <= CAPS["maximum_RSS_bytes"], "Explicit endpoint memory cap exceeded")


class Polynomials:
    def __init__(self, budget):
        self.budget = budget
        self.max_cell_terms = 0
        self.max_functional_terms = 0
        self.max_stage_exponent = 0

    def checked(self, poly):
        require(len(poly) <= CAPS["terms_per_cell"], "Explicit per-cell polynomial term cap")
        self.max_cell_terms = max(self.max_cell_terms, len(poly))
        return poly

    def add(self, a, b):
        out = dict(a)
        for key, value in b.items():
            total = zadd(out.get(key, ZERO), value)
            if total != ZERO:
                out[key] = total
            else:
                out.pop(key, None)
        return self.checked(out)

    def scale(self, poly, coefficient):
        if coefficient == ZERO:
            return {}
        return self.checked({key: zmul(value, coefficient) for key, value in poly.items()})

    def shift(self, poly, q=0, stages=()):
        out = {}
        for key, value in poly.items():
            exponents = list(key)
            exponents[0] = (exponents[0]+q) % 4
            for stage in stages:
                exponents[stage] += 1
                self.max_stage_exponent = max(self.max_stage_exponent, exponents[stage])
            new_key = tuple(exponents)
            require(new_key not in out, "Injective unrestricted-stage monomial shift")
            out[new_key] = value
        return self.checked(out)

    def normalizer(self, poly, sign):
        # Same factor as the forward complex-linear map, NOT its conjugate.
        a, b = (F(1, 2), F(sign, 2)), (F(1, 2), F(-sign, 2))
        return self.add(self.scale(poly, a), self.scale(self.shift(poly, q=2), b))

    def observe(self, functional):
        terms = sum(map(len, functional))
        require(terms <= CAPS["terms_per_functional"], "Explicit full-functional polynomial term cap")
        self.max_functional_terms = max(self.max_functional_terms, terms)
        self.budget.check()


def typed_events(controller, fixed_count=True):
    require(type(controller) is dict and set(controller) == {"schema", "roles", "stages", "ambient_rank", "nodes", "events", "diagonal"}, "Controller object schema")
    require(controller["schema"] == "mixed-projector-query-root/2" and type(controller["roles"]) is int and controller["roles"] == 34
            and type(controller["stages"]) is int and controller["stages"] == 18
            and type(controller["ambient_rank"]) is int and controller["ambient_rank"] == 153, "Fixed role/stage/ambient dimensions")
    events = controller["events"]
    require(type(events) is list and (not fixed_count or len(events) == 570), "Fixed literal570-event count")
    ops = []
    for event in events:
        require(type(event) is list and event and type(event[0]) is str, "Event list/opcode")
        op = event[0]
        arity = {"ADD": 4, "SCALE": 3, "SWAP": 3, "LOCAL": 4, "QUERY": 4, "Q_POWER": 3, "LAMBDA": 3, "IDLE": 4, "IDLE_ONE": 3}
        require(op in arity and len(event) == arity[op], "Typed ordinary/native opcode arity")
        if op == "LOCAL":
            require(type(event[1]) is int and 1 <= event[1] <= 18, "Distinct-domain native stage identifier")
            roles = event[2:4]
        elif op in ("ADD", "SWAP", "QUERY", "IDLE"):
            roles = event[1:3]
        else:
            roles = [event[1]]
        require(all(type(r) is int and 0 <= r < 34 for r in roles) and len(roles) == len(set(roles)), "Distinct active caller roles")
        if op in ("ADD", "SCALE"):
            c = rational(event[-1])
            require(op != "SCALE" or c != 0, "Invertible ordinary scale")
            ops.append((op, tuple(roles), c))
        elif op in ("QUERY", "LAMBDA"):
            sign = event[-1]
            require(type(sign) is int and sign in (-1, 1), "Typed query/normalizer sign")
            ops.append((op, tuple(roles), sign))
        elif op == "Q_POWER":
            require(type(event[2]) is int and event[2] in (-2, 2), "Ordinary central translation exponent")
            ops.append((op, tuple(roles), event[2]))
        elif op == "LOCAL":
            ops.append((op, tuple(roles), event[1]))
        elif op in ("IDLE", "IDLE_ONE"):
            stages = event[-1]
            require(type(stages) is list and stages and all(type(s) is int and 1 <= s <= 18 for s in stages)
                    and stages == sorted(set(stages)), "Distinct formal whole-idle stages")
            ops.append((op, tuple(roles), tuple(stages)))
        else:
            ops.append((op, tuple(roles), None))
    if fixed_count:
        require(sorted(value for op, _roles, value in ops if op == "LOCAL") == list(range(1, 19)), "Every source native stage exactly once")
    return tuple(ops)


def expected_targets(root, controller):
    require(type(root) is dict and root["schema"] == "mixed-projector-query-root/2"
            and type(root["fields"]) is int and root["fields"] == 6, "Independent ROOT schema")
    masks = root["masks"]
    require(type(masks) is list and len(masks) == 6 and all(type(row) is list and len(row) == 4
            and all(type(b) is int and b in (0, 1) for b in row) for row in masks), "Independent six root masks")
    children = root["children"]
    require(type(children) is list and len(children) == 4, "Four binary child topologies")
    next_stage, next_role = 1, 6
    nodes = []
    def label(tree):
        nonlocal next_stage
        if type(tree) is int:
            require(tree == 1, "Binary native leaf literal1")
            stage = next_stage; next_stage += 1
            return [stage], None
        require(type(tree) is list and len(tree) == 2, "Binary tree arity")
        left, right = label(tree[0]), label(tree[1])
        return left[0]+right[0], (left, right)
    trees = [label(tree) for tree in children]
    require(next_stage == 19 and [len(t[0]) for t in trees] == root["child_sizes"] == [7, 2, 2, 7], "Independent18-stage allocation")
    targets = [None]*34
    def walk(tree, sign):
        nonlocal next_role
        stages, descendants = tree
        if descendants is None:
            return
        a, b = next_role, next_role+1
        next_role += 2
        nodes.append({"roles": [a, b], "stages": stages, "exponent": sign})
        for role, q in ((a, -sign), (b, sign)):
            targets[role] = (q % 4,) + tuple(int(stage in stages) for stage in range(1, 19))
        walk(descendants[0], -sign)
        walk(descendants[1], sign)
    for tree in trees:
        walk(tree, 1)
    for role, mask in enumerate(masks):
        stages = [s for bit, tree in zip(mask, trees) if bit for s in tree[0]]
        targets[role] = (3,) + tuple(int(stage in stages) for stage in range(1, 19))
    require(next_role == 34 and len(nodes) == 14 and all(term is not None for term in targets), "Every arbitrary input has an independently specified node/root target")
    require(canonical(nodes) == canonical(controller["nodes"]), "Literal node declaration matches independent ROOT tree")
    diagonal = controller["diagonal"]
    require(type(diagonal) is list and len(diagonal) == 34 and all(type(row) is list and len(row) == 20
            and all(type(x) is int for x in row) and row[1] == 0 for row in diagonal), "Source diagonal dummy0 schema")
    require([(row[0] % 4,)+tuple(row[2:]) for row in diagonal] == targets, "Source header independently ROOT/tree bound")
    return targets


def pullback_all(ops, budget):
    algebra = Polynomials(budget)
    rows = []
    reverse = tuple(reversed(ops))
    for output in range(34):
        weights = [{} for _ in range(34)]
        weights[output] = {UNIT: ONE}
        for step, (op, roles, value) in enumerate(reverse):
            if op == "ADD":
                d, s = roles
                weights[s] = algebra.add(weights[s], algebra.scale(weights[d], (value, F(0))))
            elif op == "SCALE":
                r = roles[0]
                weights[r] = algebra.scale(weights[r], (value, F(0)))
            elif op == "SWAP":
                a, b = roles
                weights[a], weights[b] = weights[b], weights[a]
            elif op == "QUERY":
                d, s = roles
                weights[s] = algebra.add(weights[s], algebra.shift(weights[d], q=value))
            elif op == "LOCAL":
                source, destination = roles
                # Pullback of(s,d)->(D*s,D*(d+Q^-1*s)), using snapshots.
                old_source, old_destination = weights[source], weights[destination]
                scaled_source = algebra.shift(old_source, stages=(value,))
                scaled_destination = algebra.shift(old_destination, stages=(value,))
                weights[source] = algebra.add(scaled_source, algebra.shift(scaled_destination, q=-1))
                weights[destination] = scaled_destination
            elif op == "Q_POWER":
                r = roles[0]
                weights[r] = algebra.shift(weights[r], q=value)
            elif op == "LAMBDA":
                r = roles[0]
                weights[r] = algebra.normalizer(weights[r], value)
            else:
                for r in roles:
                    weights[r] = algebra.shift(weights[r], stages=value)
            algebra.observe(weights)
        algebra.observe(weights)
        rows.append(weights)
    return rows, {"outputs_replayed": 34, "literal_events_per_output": len(ops), "event_applications": 34*len(ops),
                  "max_cell_terms": algebra.max_cell_terms, "max_functional_terms": algebra.max_functional_terms,
                  "max_observed_stage_exponent": algebra.max_stage_exponent}


def complex_payload(matrix):
    return [[[[list(key), str(value[0]), str(value[1])] for key, value in sorted(cell.items())] for cell in row] for row in matrix]


def real_payload(matrix):
    result = [[[] for _ in range(68)] for _ in range(68)]
    for r, row in enumerate(matrix):
        for c, cell in enumerate(row):
            blocks = [[], [], [], []]
            for key, (a, b) in sorted(cell.items()):
                for block, coefficient in zip(blocks, (a, -b, b, a)):
                    if coefficient:
                        block.append([list(key), str(coefficient)])
            result[2*r][2*c], result[2*r][2*c+1] = blocks[:2]
            result[2*r+1][2*c], result[2*r+1][2*c+1] = blocks[2:]
    return result


def digest(value):
    return hashlib.sha256((canonical(value)+"\n").encode()).hexdigest()


def verify_endpoint(matrix, targets):
    for output in range(34):
        for source in range(34):
            expected = {targets[output]: ONE} if source == output else {}
            require(matrix[output][source] == expected,
                    "Actual caller polynomial coefficient mismatch at output" + str(output)+",input"+str(source))
    return {"complex_cells_compared": 34*34, "off_diagonal_complex_cells_zero": 34*33,
            "nonzero_complex_cells": 34, "complex_monomial_terms": sum(len(cell) for row in matrix for cell in row)}


def first_residual(actual, baseline):
    for output in range(34):
        for source in range(34):
            a, b = actual[output][source], baseline[output][source]
            for key in sorted(a.keys() | b.keys()):
                x, y = a.get(key, ZERO), b.get(key, ZERO)
                residual = x[0]-y[0], x[1]-y[1]
                if residual != ZERO:
                    return {"output": output, "input": source, "exponents_Q_D1_to_D18": list(key),
                            "residual_Gaussian_pair": list(map(str, residual)),
                            "actual_Gaussian_pair": list(map(str, x)), "expected_Gaussian_pair": list(map(str, y))}
    return None


def character_residual(actual, baseline, character):
    powers = [ONE]
    for _ in range(3):
        powers.append(zmul(powers[-1], character))
    for output in range(34):
        for source in range(34):
            accumulated = {}
            for scale, cell in ((F(1), actual[output][source]), (F(-1), baseline[output][source])):
                for key, coefficient in cell.items():
                    value = zmul(coefficient, powers[key[0]])
                    value = value[0]*scale, value[1]*scale
                    stages = key[1:]
                    total = zadd(accumulated.get(stages, ZERO), value)
                    if total != ZERO:
                        accumulated[stages] = total
                    else:
                        accumulated.pop(stages, None)
            if accumulated:
                stages = min(accumulated)
                return {"output": output, "input": source, "stage_exponents_D1_to_D18": list(stages),
                        "residual_Gaussian_pair": list(map(str, accumulated[stages]))}
    return None


def counterfactuals(controller, baseline, budget):
    def clone():
        return decode(canonical(controller))
    tests = []
    bad = clone()
    require(bad["events"][564] == ["LAMBDA", 0, -1], "Actual terminal normalizer564")
    bad["events"][564][2] = 1
    tests.append(("actual_lambda564_sign_flip", bad, 564))
    bad = clone()
    require(bad["events"][229] == ["IDLE_ONE", 2, [8, 9]], "Actual individual idle229")
    del bad["events"][229]
    tests.append(("omit_actual_IDLE_ONE229", bad, 229))
    bad = clone()
    index = next(i for i, e in enumerate(bad["events"]) if e[0] == "QUERY")
    bad["events"][index][3] *= -1
    tests.append(("flip_first_actual_QUERY_exponent", bad, index))
    bad = clone()
    index = next(i for i, e in enumerate(bad["events"]) if e[0] == "ADD" and rational(e[3]) != 0)
    bad["events"][index][3] = str(-rational(bad["events"][index][3]))
    tests.append(("flip_first_actual_nonzero_ADD_sign", bad, index))
    results = []
    for name, bad, index in tests:
        source_gate = None
        try:
            typed_events(bad)
        except ValueError as error:
            source_gate = str(error)
        actual, stats = pullback_all(typed_events(bad, fixed_count=False), budget)
        witness = first_residual(actual, baseline)
        require(witness is not None, "Actual counterfactual must change a full polynomial coefficient: " + name)
        record = {"control": name, "source_event_index": index, "fixed_count_gate_error": source_gate,
                  "arithmetic_counterfactual_bypass": "Only the fixed570-event/globalstage census is waived; typed opcodes/roles/stage domains remain checked. Original byte authentication is not asserted for in-memory clones.",
                  "first_coefficient_residual": witness, "changed_complex_cells": sum(a != b for rowa, rowb in zip(actual, baseline) for a, b in zip(rowa, rowb)),
                  "replay_stats": stats, "classification": "Corrupted caller coefficient witness, not a legitimate cheaper source"}
        if name == "actual_lambda564_sign_flip":
            chars = {"1": ONE, "-1": (F(-1), F(0)), "i": (F(0), F(1)), "-i": (F(0), F(-1))}
            residuals = {label: character_residual(actual, baseline, value) for label, value in chars.items()}
            require(residuals["1"] is None and residuals["-1"] is None
                    and residuals["i"] is not None and residuals["-i"] is not None,
                    "Actual lambda fault invisible to real characters but visible to both imaginary characters")
            record["four_character_residuals"] = residuals
        results.append(record)
    benign = []
    modified = clone()
    index = next(i for i, event in enumerate(modified["events"]) if event[0] == "Q_POWER")
    modified["events"][index][2] *= -1
    tests = [("Q_POWER_minus2_plus2", modified, index)]
    modified = clone()
    require(sorted(e[1] for e in modified["events"][-6:]) == list(range(6))
            and all(e[0] == "LAMBDA" and e[2] == -1 for e in modified["events"][-6:]), "Six distinct terminal inverse normalizers")
    modified["events"][-6:] = list(reversed(modified["events"][-6:]))
    tests.append(("reverse_six_terminal_normalizers", modified, 564))
    for name, modified, index in tests:
        actual, stats = pullback_all(typed_events(modified), budget)
        require(actual == baseline, "Benign actual caller mutation must preserve all1156 polynomial cells")
        benign.append({"control": name, "source_event_index": index, "classification": "BENIGN exact full coefficient equality",
                       "realified_payload_sha256": digest(real_payload(actual)), "replay_stats": stats})
    return results, benign


def compute():
    data = authenticate()  # Every original byte is checked before arithmetic.
    budget = Budget()
    controller, root = data["CONTROLLER.json"], data["ROOT.json"]
    ops = typed_events(controller)
    targets = expected_targets(root, controller)
    actual, stats = pullback_all(ops, budget)
    comparison = verify_endpoint(actual, targets)
    complex_coefficients, real_coefficients = complex_payload(actual), real_payload(actual)
    controls, benign = counterfactuals(controller, actual, budget)
    budget.check()
    return {"schema_version": 1, "status": "PASS_FULL_INDEPENDENT_MIXED_ROOT_CALLER_ENDPOINT",
            "frozen_R9_scientific_sha256": FROZEN, "source_git_blobs": BLOBS,
            "method": "Backward complex-linear output functionals with independent Gaussian rational pairs and exact Qmod4/stage polynomial convolution; no inversion, adjoint or scientific imports.",
            "formal_ring": "Q(i)[Q,D1,...,D18]/(Q^4-1); only the central exponent is reduced, all18stage powers are unrestricted nonnegative integers",
            "public_arbitrary_complex_inputs": 34, "owned_or_initialized_inputs": 0,
            "comparison": comparison, "expected_target_monomials": [list(term) for term in targets],
            "replay_stats": stats, "declared_resource_caps": CAPS,
            "complex_payload_convention": "Output-major34x34; cell terms [[Qmod4,D1exp,...,D18exp],real_fraction_string,imaginary_fraction_string], lexicographic exponent order; [] is zero.",
            "actual_complex_coefficient_payload": complex_coefficients,
            "actual_complex_payload_sha256": digest(complex_coefficients),
            "realification_convention": "Complex role r uses real index2r and imaginary index2r+1; a+ib becomes blocks[[a,-b],[b,a]], with each real cell sorted [[19exponents],fraction_string]. This is an audit representation, not68physical inputs.",
            "actual_realified_coefficient_payload": real_coefficients,
            "actual_realified_payload_sha256": digest(real_coefficients),
            "realified_cells": 68*68, "counterfactual_coefficient_controls": controls, "benign_full_caller_controls": benign,
            "limits": ["This certifies the fixed6398caller570-event formal polynomial endpoint and the retained R9 local normalization specification, not a new normalization theorem or first verification.",
                       "Author exact forward quotient and four-character reverse coverage is credited; this is independently available code and exact source/control binding.",
                       "The declared Q^4=1 premise is not a nativeQ^2=X phase or physical whole-field translation proof; scalar coefficients stay outside tensor powers.",
                       "No new native/allwidth supplier, physical erasure, costs/full invoice, price optimum, compiler/outer admission, kappa or selected-frontier change is certified.",
                       "All15R9 scientific files remain authenticated unchanged; the newer6417 composition and other changed source heads are outside this fixed caller claim."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "ENDPOINT-ORACLE.json"
        require(path.is_file(), "Retained endpoint receipt ENDPOINT-ORACLE.json required")
        require(canonical(decode(path.read_bytes())) == canonical(result), "Retained endpoint receipt mismatch")
        print("PASS independent full mixed-root caller endpoint receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
