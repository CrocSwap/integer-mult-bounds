#!/usr/bin/env python3
"""Independent local Gaussian-pair algebra and literal caller bindings.

PARTIAL checkpoint only: this does not multiply the full570-event caller.
All source programs are authenticated as inert text, never imported/executed.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA = "c74239713cbebdea38f0cca551a17606617878a83c82d4ef0a5cb689e8ce9cb0"
PINS = {
    "CONTROLLER.json": ("4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c", "4f7d7a2f13b13966b10c7b583d28d1bed210364c"),
    "ROOT.json": ("2f25684c24ae0e1d10d4f8f29430aed3cef584f82c8ae840e82be0a72baa048d", "b59f1ea89aca17f0a76131743c12f2c724421df8"),
    "upstream-PROOF.md": ("bfbe0b872f6ff14c858bff47c6e3ac0bb8e43bc8eeaec20253744e3f44720fcd", "510bf9dba012949ea0f37d9e087ce8778b1951d0"),
    "NOTICE": ("b6026dd901f3cb2e6ec6d5f7b32a38aa998005c8a1df93392151ca1766d45b33", "03e4ac5937424ed9f0ae0e4b33d6b0df0c9ec8d9"),
    "controller-source.py": ("e5671c66a4091f1b482a750baf5bedf9ac0750e577efbe3c5b3d2860d2fa8edc", "393524f903b44be54884475d11200f06ce1dfddb"),
    "algebra-source.py": ("02eb3380715294334710edd3273f267dc048264555bd60fefb86022bc9eda835", "a06d6f641685e96b2f150ea6b741930a9ec037f8"),
    "normalization-PROOF.md": ("68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9", "f910b5fbf9a9d519fa7d7c7503de51df5a796368"),
    "author-caller-reverse.py": ("6435f092e7f435aa30db3877237056cc00fcb206fd8c87a3bddf380dbb7e80e9", "be84e58dc5c1836261441c1a58d4ffe51315c23f"),
    "headroom-NOTICE": ("87d3cf335599cec76ede9e68e58fa13b077e823004aab60ad17b22196cdc3747", "081d5cea1467c7cecfe35a37608963dda4e483b7"),
}
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
I = (F(0), F(1))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON member")
            result[key] = value
        return result
    def bad(value):
        raise ValueError("Nonfinite JSON value " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticate():
    manifest = (ROOT / "SOURCE-PINS.json").read_bytes()
    require(hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA, "Source manifest sha256 mismatch")
    data = {}
    for name, (sha, blob) in PINS.items():
        raw = (ROOT / "sources" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Source sha256 mismatch: " + name)
        require(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Source Git blob mismatch: " + name)
        data[name] = decode(raw) if name.endswith(".json") else raw.decode("utf-8")
    return data


def integer(value, low=0, high=None):
    require(type(value) is int and value >= low and (high is None or value <= high), "Strict integer domain")
    return value


def rational(value):
    require(type(value) in (int, str), "Exact rational string/integer")
    return F(value)


def zadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def zneg(a):
    return -a[0], -a[1]


def zmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def padd(a, b):
    result = dict(a)
    for k, v in b.items():
        total = zadd(result.get(k, ZERO), v)
        if total != ZERO:
            result[k] = total
        else:
            result.pop(k, None)
    return result


def pneg(a):
    return {k: zneg(v) for k, v in a.items()}


def pmul(a, b):
    result = {}
    for j, x in a.items():
        for k, y in b.items():
            q = (j+k) % 4
            total = zadd(result.get(q, ZERO), zmul(x, y))
            if total != ZERO:
                result[q] = total
            else:
                result.pop(q, None)
    return result


def pencode(a):
    return [[k, str(v[0]), str(v[1])] for k, v in sorted(a.items())]


def pevaluate(a, character):
    powers = [ONE]
    for _ in range(3):
        powers.append(zmul(powers[-1], character))
    answer = ZERO
    for k, value in a.items():
        answer = zadd(answer, zmul(value, powers[k]))
    return answer


def lam(sign):
    require(type(sign) is int and sign in (-1, 1), "Normalization sign")
    return {0: (F(1, 2), F(sign, 2)), 2: (F(1, 2), F(-sign, 2))}


def cmultiply(a, b):
    n = len(a)
    result = [[ZERO for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            value = ZERO
            for j in range(n):
                value = zadd(value, zmul(a[r][j], b[j][c]))
            result[r][c] = value
    return result


def cencoded(a):
    return [[[str(z[0]), str(z[1])] for z in row] for row in a]


def pair_operations(last_sign=-1):
    a = (F(1, 2), F(1, 2))
    return [
        [[ONE, (F(0), F(-1))], [ZERO, ONE]],
        [[a, ZERO], [ZERO, ONE]],
        [[ONE, ZERO], [ZERO, (F(1), F(1))]],
        [[ONE, ZERO], [(F(0), F(last_sign)), ONE]],
    ]


def compose_pair(operations):
    product = [[ONE, ZERO], [ZERO, ONE]]
    for operation in operations:
        product = cmultiply(operation, product)
    return product


def local_algebra(proof):
    specification = "x <- x - i*y\nx <- a*x\ny <- (1+i)*y\ny <- y - i*x."
    require(proof.count(specification) == 1 and "where a=(1+i)/2 and b=(1-i)/2" in proof,
            "Displayed four-operation source specification binding")
    one, q2, qinverse = {0: ONE}, {2: ONE}, {3: ONE}
    plus, minus = lam(1), lam(-1)
    S = pmul(plus, qinverse)
    identities = [
        ("lambda_minus_times_lambda_plus", pmul(minus, plus), one),
        ("lambda_plus_squared", pmul(plus, plus), q2),
        ("S_squared", pmul(S, S), one),
        ("lambda_minus_times_S", pmul(minus, S), qinverse),
    ]
    for name, actual, expected in identities:
        require(actual == expected, "Local quotient coefficient identity: " + name)
    require(q2 != one, "Q squared must not be collapsed to1")
    a, b = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    expected = [[a, b], [b, a]]
    operations = pair_operations()
    product = compose_pair(operations)
    inverse = compose_pair([[[conjugate(z) for z in row] for row in op] for op in operations])
    require(product == expected and inverse == [[conjugate(z) for z in row] for row in expected], "Actual four-operation Gaussian pair product")
    identity = [[ONE, ZERO], [ZERO, ONE]]
    require(cmultiply(product, inverse) == cmultiply(inverse, product) == identity, "Pair inverse/unitarity")
    require(cmultiply([[conjugate(product[c][r]) for c in range(2)] for r in range(2)], product) == identity,
            "Pair complex unitarity")
    real_bounds, complex_bounds = [], []
    for operation in operations:
        real_bound = max(sum(abs(z[0])+abs(z[1]) for z in row) for row in operation)
        real_bounds.append(real_bound)
        row_bounds = []
        for row in operation:
            total = F(0)
            for z in row:
                # Rational upper bound for complex modulus, checked by squares.
                upper = abs(z[0])+abs(z[1])
                require(z[0]**2+z[1]**2 <= upper**2, "Exact complex coefficient modulus bound")
                total += upper
            row_bounds.append(total)
        complex_bounds.append(max(row_bounds))
    require(all(bound <= 2 for bound in real_bounds+complex_bounds), "Maximum-norm step bounds at most2")
    wrong_inverse_residual = padd(pmul(plus, plus), pneg(one))
    require(wrong_inverse_residual, "Wrong inverse sign has a genuine quotient residual")
    chars = {"1": ONE, "-1": (F(-1), F(0)), "i": I, "-i": zneg(I)}
    character_residuals = {name: pevaluate(wrong_inverse_residual, char) for name, char in chars.items()}
    require(character_residuals["1"] == character_residuals["-1"] == ZERO
            and character_residuals["i"] != ZERO and character_residuals["-i"] != ZERO,
            "Wrong inverse sign is invisible only to the two real characters")
    bad_product = compose_pair(pair_operations(1))
    mismatch = next(({"row": r, "column": c, "actual": list(map(str, bad_product[r][c])), "expected": list(map(str, expected[r][c]))}
                     for r in range(2) for c in range(2) if bad_product[r][c] != expected[r][c]), None)
    require(mismatch is not None, "Wrong last ordinary coefficient changes actual pair map")
    return {"ring": "Q(i)[Q]/(Q^4-1); Q^2 is not set to1", "lambda_plus": pencode(plus), "lambda_minus": pencode(minus),
            "S": pencode(S), "identities": [{"name": name, "actual": pencode(actual), "expected": pencode(expected)} for name, actual, expected in identities],
            "displayed_source_specification": specification, "four_operation_product": cencoded(product), "inverse_product": cencoded(inverse),
            "real_component_linf_step_bounds": list(map(str, real_bounds)),
            "complex_field_max_step_upper_bounds": list(map(str, complex_bounds)),
            "unitary_pair_map": True,
            "coefficient_controls": [
                {"control": "wrong_inverse_uses_same_lambda_sign", "quotient_residual": pencode(wrong_inverse_residual),
                 "character_residuals": {name: list(map(str, z)) for name, z in character_residuals.items()}, "scope": "Local polynomial error, not a570-event endpoint replay"},
                {"control": "last_displayed_ordinary_minus_i_changed_to_plus_i", "coefficient_witness": mismatch, "scope": "Actual displayed four-operation pair product"}],
            "benign_Q_POWER_plus_minus2": {"minus2": pencode({(-2) % 4: ONE}), "plus2": pencode(q2), "equal": True}}


def reye(n):
    return [[F(int(r == c)) for c in range(n)] for r in range(n)]


def rmul(a, b):
    return [[sum((x*y for x, y in zip(row, column)), F(0)) for column in zip(*b)] for row in a]


def rmatrix(value):
    require(type(value) is list and len(value) == 6 and all(type(row) is list and len(row) == 6 for row in value), "Six-by-six rational basis")
    return [[rational(x) for x in row] for row in value]


def ordinary_block(events):
    rows = reye(6)
    for event in events:
        op = event[0]
        require(op in ("ADD", "SCALE", "SWAP"), "Root ordinary block contains only scalar basis operations")
        if op == "ADD":
            _, d, s, c = event
            require(d < 6 and s < 6, "Root ordinary block role bound")
            rows[d] = [a+rational(c)*b for a, b in zip(rows[d], rows[s])]
        elif op == "SCALE":
            _, d, c = event
            require(d < 6, "Root ordinary scale role")
            rows[d] = [rational(c)*a for a in rows[d]]
        else:
            _, a, b = event
            require(a < 6 and b < 6, "Root ordinary swap roles")
            rows[a], rows[b] = rows[b], rows[a]
    return rows


def parse_events(controller):
    require(type(controller) is dict and set(controller) == {"schema", "roles", "stages", "ambient_rank", "nodes", "events", "diagonal"}, "Controller schema object")
    require(controller["schema"] == "mixed-projector-query-root/2" and type(controller["roles"]) is int and controller["roles"] == 34
            and type(controller["stages"]) is int and controller["stages"] == 18
            and type(controller["ambient_rank"]) is int and controller["ambient_rank"] == 153, "Frozen schema/role/stage/ambient dimensions")
    events = controller["events"]
    require(type(events) is list and len(events) == 570, "Literal570-event source binding")
    for event in events:
        require(type(event) is list and event and type(event[0]) is str, "Event list/opcode")
        op = event[0]
        require(op in ("ADD", "SCALE", "SWAP", "LOCAL", "QUERY", "Q_POWER", "LAMBDA", "IDLE", "IDLE_ONE"), "No initialization/owned/unknown caller opcode")
        require(len(event) == {"ADD": 4, "SCALE": 3, "SWAP": 3, "LOCAL": 4, "QUERY": 4, "Q_POWER": 3, "LAMBDA": 3, "IDLE": 4, "IDLE_ONE": 3}[op], "Event arity")
        if op == "LOCAL":
            integer(event[1], 1, 18)
            roles = event[2:4]
        elif op in ("ADD", "SWAP", "QUERY", "IDLE"):
            roles = event[1:3]
        else:
            roles = [event[1]]
        require(all(type(r) is int and 0 <= r < 34 for r in roles) and len(roles) == len(set(roles)), "Distinct valid event roles")
        if op == "ADD":
            rational(event[3])
        elif op == "SCALE":
            require(rational(event[2]) != 0, "Invertible ordinary SCALE")
        elif op in ("QUERY", "LAMBDA"):
            value = event[3] if op == "QUERY" else event[2]
            require(type(value) is int and value in (-1, 1), "Strict query/normalizer sign")
        elif op == "Q_POWER":
            require(type(event[2]) is int and event[2] in (-2, 2), "Ordinary central translation power")
        elif op in ("IDLE", "IDLE_ONE"):
            stages = event[-1]
            require(type(stages) is list and stages and all(type(s) is int and 1 <= s <= 18 for s in stages)
                    and stages == sorted(set(stages)), "Distinct ordered whole-idle stage labels")
    return events


def derive_root(root):
    require(type(root) is dict and root["schema"] == "mixed-projector-query-root/2"
            and type(root["fields"]) is int and root["fields"] == 6, "ROOT schema/fields")
    masks, sites = root["masks"], root["sites"]
    require(type(masks) is list and len(masks) == 6 and all(type(row) is list and len(row) == 4 and all(type(b) is int and b in (0, 1) for b in row) for row in masks), "ROOT six-by-four masks")
    require(type(sites) is list and len(sites) == 7 and all(type(site["site"]) is int and site["site"] == i and type(site["full"]) is bool for i, site in enumerate(sites)), "Seven ordered root sites")
    full_indices = [i for i, site in enumerate(sites) if site["full"]]
    thin_indices = [i for i, site in enumerate(sites) if not site["full"]]
    require(full_indices == root["full_sites"] == [0, 1, 5, 6] and thin_indices == root["thin_sites"] == [2, 3, 4], "Full/thin site source allocation")
    children = root["children"]
    require(type(children) is list and len(children) == 4, "Four independent root children")
    next_stage = 1
    def label(tree):
        nonlocal next_stage
        if type(tree) is int:
            require(tree == 1, "Binary leaf is exactly1")
            result = {"stage": next_stage, "stages": [next_stage]}
            next_stage += 1
            return result
        require(type(tree) is list and len(tree) == 2, "Binary child shape")
        left, right = label(tree[0]), label(tree[1])
        return {"left": left, "right": right, "stages": left["stages"]+right["stages"]}
    roots = [label(tree) for tree in children]
    require(next_stage == 19 and [len(t["stages"]) for t in roots] == root["child_sizes"] == [7, 2, 2, 7], "All18 distinct native labels/four child sizes")
    nodes, leaves = [], []
    next_role = 6
    def visit(tree, root_index, x, y, sign):
        nonlocal next_role
        if "stage" in tree:
            leaves.append({"stage": tree["stage"], "roles": [x, y], "exponent": sign, "root_index": root_index})
            return
        pair = [next_role, next_role+1]
        next_role += 2
        nodes.append({"roles": pair, "stages": tree["stages"], "exponent": sign, "root_index": root_index})
        visit(tree["left"], root_index, y, x, -sign)
        visit(tree["right"], root_index, x, y, sign)
    for k, tree in enumerate(roots):
        visit(tree, k, 0, 1, 1)
    require(next_role == 34 and len(nodes) == 14 and len(leaves) == 18, "Fourteen independent node role pairs")
    target = [None]*34
    for role, mask in enumerate(masks):
        stages = [s for bit, tree in zip(mask, roots) if bit for s in tree["stages"]]
        target[role] = [-1, 0]+[int(s in stages) for s in range(1, 19)]
    for node in nodes:
        a, b = node["roles"]
        e, stages = node["exponent"], node["stages"]
        target[a] = [-e, 0]+[int(s in stages) for s in range(1, 19)]
        target[b] = [e, 0]+[int(s in stages) for s in range(1, 19)]
    require(all(term is not None for term in target), "Every arbitrary caller input has an independently declared target")
    for k, site_index in enumerate(full_indices):
        support = [r for r in range(6) if masks[r][k]]
        require(sites[site_index]["support"] == support and type(sites[site_index]["stage_rank"]) is int
                and sites[site_index]["stage_rank"] == len(support), "ROOT mask/projector support/rank binding")
    return roots, nodes, leaves, target


def bind_source(controller, root):
    events = parse_events(controller)
    trees, nodes, leaves, target = derive_root(root)
    simple_nodes = [{k: node[k] for k in ("roles", "stages", "exponent")} for node in nodes]
    require(canonical(controller["nodes"]) == canonical(simple_nodes), "Actual14 node records match independent ROOT tree traversal")
    require(type(controller["diagonal"]) is list and len(controller["diagonal"]) == 34
            and all(type(row) is list and len(row) == 20 and all(type(x) is int for x in row) and row[1] == 0 for row in controller["diagonal"]), "Diagonal integer/dummy-stage schema")
    require(controller["diagonal"] == target, "Independent ROOT/node target monomial binding")
    lambdas = [(i, e) for i, e in enumerate(events) if e[0] == "LAMBDA"]
    require(len(lambdas) == 20, "All20 normalization occurrences")
    terminal = lambdas[-6:]
    require([i for i, _ in terminal] == list(range(len(events)-6, len(events)))
            and sorted(e[1] for _, e in terminal) == list(range(6)) and all(e[2] == -1 for _, e in terminal),
            "Six distinct terminal inverse-normalizer fields")
    windows = []
    for j in range(7):
        left, right = lambdas[2*j], lambdas[2*j+1]
        require(left[1] == ["LAMBDA", 0, -1] and right[1] == ["LAMBDA", 0, 1]
                and left[0] < right[0], "Seven alternating role0 normalization wrappers")
        if windows:
            require(windows[-1]["close_index"] < left[0], "Disjoint ordered site intervals")
        require(events[right[0]+1] == ["ADD", 0, 1, -1], "Actual post-wrapper U(-1) ordinary correction")
        windows.append({"site": j, "open_index": left[0], "close_index": right[0], "full": root["sites"][j]["full"]})
    full_sites = [w for w in windows if w["full"]]
    seen_local, all_node_queries, all_idles, all_single_idles = [], [], [], []
    for w in windows:
        inside = list(enumerate(events[w["open_index"]+1:w["close_index"]], w["open_index"]+1))
        local = [(i, e) for i, e in inside if e[0] == "LOCAL"]
        queries = [(i, e) for i, e in inside if e[0] == "QUERY"]
        idles = [(i, e) for i, e in inside if e[0] == "IDLE"]
        single = [(i, e) for i, e in inside if e[0] == "IDLE_ONE"]
        if not w["full"]:
            require([e for _, e in inside] == [["QUERY", 0, 1, -1]], "Three exact one-query thin-site source intervals")
            w["stages"] = []
            continue
        k = full_sites.index(w)
        stages = trees[k]["stages"]
        require(sorted(e[1] for _, e in local) == stages, "Full-site native stage interval binding")
        expected_nodes = [n for n in nodes if n["root_index"] == k]
        require(sorted(canonical(e) for _, e in queries) == sorted(canonical(["QUERY", *n["roles"], -n["exponent"]]) for n in expected_nodes), "Node query role/sign binding")
        require(sorted(canonical(e) for _, e in idles) == sorted(canonical(["IDLE", *n["roles"], n["stages"]]) for n in expected_nodes), "Node paired-whole-idle binding")
        rank = root["sites"][w["site"]]["stage_rank"]
        require([e for _, e in single] == [["IDLE_ONE", r, stages] for r in range(2, rank)], "Actual individual-whole-idle stage/role binding")
        for i, e in local:
            leaf = next(leaf for leaf in leaves if leaf["stage"] == e[1])
            x, y = leaf["roles"]
            require(e == ["LOCAL", leaf["stage"], x, y] and events[i-1] == events[i+1] == ["SWAP", x, y], "Native leaf role/swap binding")
            if leaf["exponent"] == -1:
                require(events[i-2][:2] == events[i+2][:2] == ["Q_POWER", x]
                        and events[i-2][2] in (-2, 2) and events[i+2][2] in (-2, 2), "Negative leaf ordinary central translations")
        seen_local.extend(e[1] for _, e in local)
        all_node_queries.extend(i for i, _ in queries)
        all_idles.extend(i for i, _ in idles)
        all_single_idles.extend({"event_index": i, "role": e[1], "stages": e[2]} for i, e in single)
        w["stages"] = stages
    counts = Counter(e[0] for e in events)
    require(sorted(seen_local) == list(range(1, 19)) and counts["LOCAL"] == 18 and counts["QUERY"] == 17
            and counts["IDLE"] == 14 and counts["IDLE_ONE"] == 2
            and counts["Q_POWER"] == 2*sum(leaf["exponent"] == -1 for leaf in leaves), "Complete source primitive occurrence census")
    # Small root-only scalar blocks: this is not the34-field caller transfer.
    bases = [rmatrix(site["basis"]) for site in root["sites"]]
    inverses = [rmatrix(site["inverse"]) for site in root["sites"]]
    entry, exit_basis = rmatrix(root["input_basis"]), rmatrix(root["output_basis"])
    require(rmul(entry, exit_basis) == rmul(exit_basis, entry) == reye(6), "ROOT entry/exit inverse bases")
    require(all(rmul(a, b) == rmul(b, a) == reye(6) for a, b in zip(bases, inverses)), "Seven ordinary source basis inverses")
    shear = reye(6); shear[0][1] = F(-1)
    blocks = [(0, windows[0]["open_index"], rmul(inverses[0], entry))]
    for j in range(6):
        blocks.append((windows[j]["close_index"]+1, windows[j+1]["open_index"], rmul(inverses[j+1], rmul(bases[j], shear))))
    blocks.append((windows[-1]["close_index"]+1, len(events)-6, rmul(exit_basis, rmul(bases[-1], shear))))
    for start, stop, expected in blocks:
        require(ordinary_block(events[start:stop]) == expected, "Actual emitted root-only ordinary basis block")
    expected_monomials = [[term[0] % 4]+term[2:] for term in target]
    return {"schema": controller["schema"], "roles": 34, "stages": 18, "ambient_rank": 153,
            "events": len(events), "opcode_counts": dict(sorted(counts.items())), "site_windows": windows,
            "terminal_normalizer_role_order": [e[1] for _, e in terminal], "individual_whole_idles": all_single_idles,
            "independently_derived_nodes": simple_nodes, "leaf_bindings": leaves,
            "expected_diagonal_source_convention": target, "expected_target_monomials_mod_Q4": expected_monomials,
            "expected_target_sha256": hashlib.sha256((canonical(expected_monomials)+"\n").encode()).hexdigest(),
            "root_output_stage_supports": [[s for s, e in enumerate(term[1:], 1) if e] for term in expected_monomials[:6]],
            "root_only_scalar_basis_blocks": [{"start": a, "stop_exclusive": b} for a, b, _ in blocks],
            "arbitrary_complex_inputs": 34, "initialization_or_owned_fields_introduced": False}


def source_controls(controller, root):
    def copied():
        return decode(canonical(controller))
    results = []
    bad = copied()
    index = next(i for i, e in enumerate(bad["events"]) if e[0] == "IDLE_ONE")
    del bad["events"][index]
    variants = [("missing_actual_IDLE_ONE", bad, index)]
    bad = copied()
    index = next(i for i, e in enumerate(bad["events"]) if e[0] == "IDLE_ONE")
    bad["events"][index][-1] = [1, 2]
    variants.append(("wrong_individual_idle_stage_set", bad, index))
    bad = copied()
    index = next(i for i, e in enumerate(bad["events"]) if e[0] == "LAMBDA")
    bad["events"][index][1] = 1
    variants.append(("wrong_wrapper_role", bad, index))
    bad = copied()
    bad["diagonal"][4][2:] = bad["diagonal"][5][2:]
    variants.append(("role4_C_target_replaced_with_role5_B", bad, None))
    for name, bad, index in variants:
        error = None
        try:
            bind_source(bad, root)
        except ValueError as exc:
            error = str(exc)
        require(error is not None, "Source binding mutation must reject: " + name)
        results.append({"control": name, "event_index": index, "observed_error": error,
                        "classification": "Local source/declaration binding failure; no full570-event polynomial error computed"})
    benign = copied()
    qindex = next(i for i, e in enumerate(benign["events"]) if e[0] == "Q_POWER")
    benign["events"][qindex][2] *= -1
    bind_source(benign, root)
    results.append({"control": "Q_POWER_minus2_plus2_swap", "event_index": qindex, "classification": "BENIGN in the quotientQ^4=1; local semantic binding accepts"})
    benign = copied()
    benign["events"][-6:] = list(reversed(benign["events"][-6:]))
    bind_source(benign, root)
    # Exact per-role products demonstrate commutation without using a caller
    # endpoint: every distinct field receives the same one local polynomial.
    normal = [{0: ONE} for _ in range(6)]
    reverse = [{0: ONE} for _ in range(6)]
    for event in controller["events"][-6:]:
        normal[event[1]] = pmul(lam(event[2]), normal[event[1]])
    for event in benign["events"][-6:]:
        reverse[event[1]] = pmul(lam(event[2]), reverse[event[1]])
    require(normal == reverse, "Distinct terminal normalizers commute exactly")
    results.append({"control": "reverse_six_distinct_terminal_normalizers", "classification": "BENIGN: exact local per-role products and source semantic binding agree"})
    return results


def compute():
    data = authenticate()
    algebra = local_algebra(data["upstream-PROOF.md"])
    bindings = bind_source(data["CONTROLLER.json"], data["ROOT.json"])
    return {"schema_version": 1, "status": "PASS_PARTIAL_LOCAL_NORMALIZATION_AND_SOURCE_BINDING",
            "source_manifest_sha256": MANIFEST_SHA, "source_sha256": {name: pin[0] for name, pin in PINS.items()},
            "source_git_blobs": {name: pin[1] for name, pin in PINS.items()},
            "local_algebra": algebra, "source_bindings": bindings,
            "source_binding_controls": source_controls(data["CONTROLLER.json"], data["ROOT.json"]),
            "limits": ["PARTIAL local checkpoint: no full570-event34-field polynomial endpoint is multiplied or claimed.",
                       "Expected34targets are independently declared from ROOT masks/child topology/node allocation, not copied from CONTROLLER.diagonal.",
                       "The four ordinary operations check the displayed source specification on one translation orbit; CONTROLLER emits abstractLAMBDA opcodes, not a materialized address loop.",
                       "Real-component linf and complex-field maximum-norm bounds are stated separately; both per-step bounds are at most2 here.",
                       "Q^4=1 is a declared ring premise. NativeQ^2=X phase, physical translation, all-width implementation, costs and all five framework assumptions remain outside this check.",
                       "Stage labels remain distinct; no stage is evaluated at1 or reduced modulo2. All34complex caller inputs remain arbitrary.",
                       "Author forward and four-character reverse coverage is prior work; this is additional independent implementation/source binding, not first verification or newkappa."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "LOCAL-ORACLE.json"
        require(path.is_file(), "Retained local receipt LOCAL-ORACLE.json required")
        require(canonical(decode(path.read_bytes())) == canonical(result), "Retained local receipt mismatch")
        print("PASS independent local Gaussian-pair receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
