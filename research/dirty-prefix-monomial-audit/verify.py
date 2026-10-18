#!/usr/bin/env python3
"""Exact audit of PR628/905 ideal prefixes; Apache-2.0, Hanson Sun + Codex.

This does not execute a rounded cyclic inverse or certify a multiplication bound.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent


def require(ok, label):
    if not ok:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def word(n, sign=1):
    """Expand the positive tree, then reverse the literal word for a negative call."""
    require(type(n) is int and n > 0, "positive integer factor count")
    require(type(sign) is int and sign in (-1, 1), "word sign")

    def positive(lo, hi, src, dst, level):
        if hi - lo == 1:
            return [(src, dst, lo, 1)]
        mid = (lo + hi) // 2
        left = positive(lo, mid, src, level + 2, level + 1)
        right = positive(mid, hi, level + 2, dst, level + 1)
        return left + right + inverse_word(left) + inverse_word(right)

    result = positive(0, n, 0, 1, 0)
    return result if sign == 1 else inverse_word(result)


def inverse_word(instructions):
    return [(s, t, a, -v) for s, t, a, v in reversed(instructions)]


def accumulate(row, key, value):
    value += row.get(key, 0)
    if value:
        row[key] = value
    else:
        row.pop(key, None)


def identity(size):
    # (input register, ordered noncommutative factor tuple) -> integer coefficient
    return [{(i, ()): 1} for i in range(size)]


@lru_cache(None)
def ordered_distinct(term):
    return all(a > b for a, b in zip(term, term[1:]))


def check_monomials(matrix, source, target, product, sign):
    """The induction invariant, checked before any operator specialization."""
    size = len(matrix)
    require(matrix[source] == {(source, ()): 1}, "protected source row")
    for i, row in enumerate(matrix):
        ports = Counter(c for c, _ in row)
        require(all(v == 1 for v in ports.values()), "one monomial per entry")
        for (c, term), value in row.items():
            require(abs(value) == 1, "unit monomial coefficient")
            require(0 <= c < size, "register range")
            require(ordered_distinct(term), "ordered distinct factors")
        require({k: v for k, v in row.items() if k[0] == target}
                == ({(target, ()): 1} if i == target else {}), "protected target column")
    endpoint = {k: v for k, v in matrix[target].items() if k[0] == source}
    require(endpoint in ({}, {(source, product): sign}), "endpoint coefficient")


def trace(n, sign=1, instructions=None, enforce=True, observer=None):
    instructions = word(n, sign) if instructions is None else instructions
    height = (n - 1).bit_length()
    size = height + 2
    p, q = identity(size), identity(size)
    maximum = [1, 1]
    witnesses = [None, None]
    product = tuple(range(n - 1, -1, -1))
    if enforce:
        check_monomials(p, 0, 1, product, sign)
        check_monomials(q, 0, 1, product, -sign)
    for boundary, (src, dst, factor, direction) in enumerate(instructions, 1):
        require(src != dst and 0 <= factor < n, "leaf interface")
        # P <- E P: prepend the factor to the source row.
        for (col, term), value in tuple(p[src].items()):
            accumulate(p[dst], (col, (factor,) + term), direction * value)
        # Q <- Q E^-1: append the factor to the target column.
        for row in q:
            for (col, term), value in tuple(row.items()):
                if col == dst:
                    accumulate(row, (src, term + (factor,)), -direction * value)
        for index, matrix in enumerate((p, q)):
            if enforce:
                check_monomials(matrix, 0, 1, product, sign if index == 0 else -sign)
            for row_index, row in enumerate(matrix):
                norm = sum(abs(value) for value in row.values())
                if norm > maximum[index]:
                    maximum[index] = norm
                    witnesses[index] = {
                        "boundary": boundary, "row": row_index,
                        "terms": [[col, list(term), value]
                                  for (col, term), value in sorted(row.items())],
                    }
        if observer is not None:
            observer(boundary, (src, dst, factor, direction), p, q)
    wanted = identity(size)
    wanted[1][(0, product)] = sign
    wanted_inverse = identity(size)
    wanted_inverse[1][(0, product)] = -sign
    require(p == wanted and q == wanted_inverse, "complete product and restoration")
    require(max(maximum) <= size, "logarithmic coefficient bound")
    if sign == 1:
        require(maximum[0] == size, "sharp positive-prefix attainment")
    return {"n": n, "sign": sign, "leaves": len(instructions),
            "bound": size, "maximum": maximum, "witnesses": witnesses}


def polynomial_product(left, right):
    """General matrix multiplication over a free algebra, separate from trace()."""
    result = [{} for _ in left]
    for row_index, row in enumerate(left):
        for (middle, a), av in row.items():
            for (column, b), bv in right[middle].items():
                accumulate(result[row_index], (column, a + b), av * bv)
    return result


def schema_checks():
    """Check the eight induction cases with two abstract internal registers.

    Each child entry is a separate indeterminate. Its source/target endpoint
    is 0 or +/- its full product. No relation between other child entries is
    assumed, so this checks a stronger algebraic substitution contract.
    """
    # Global registers: x=0, z=1, y=2, internal registers=3,4.
    # A=(10,), B=(20,); generic child monomials have distinct symbols >=100.
    a, b, ab = (10,), (20,), (10, 20)
    u, v = identity(5), identity(5)
    ui, vi = identity(5), identity(5)
    u[1][(0, b)] = 1
    ui[1][(0, b)] = -1
    v[2][(1, a)] = 1
    vi[2][(1, a)] = -1
    count = 0
    for polarity in (1, -1):
        children = [("L", 1, u, ui), ("R", 1, v, vi),
                    ("L", -1, ui, u), ("R", -1, vi, v)] if polarity == 1 else [
                    ("R", 1, v, vi), ("L", 1, u, ui),
                    ("R", -1, vi, v), ("L", -1, ui, u)]
        c, ci = identity(5), identity(5)
        for phase, (side, child_sign, whole, whole_inverse) in enumerate(children):
            src, dst, full = (0, 1, b) if side == "L" else (1, 2, a)
            active = [src, dst, 3, 4]
            for e in (0, 1):
                for f in (0, 1):
                    matrices = []
                    for endpoint, direction, offset in ((e, child_sign, 0), (f, -child_sign, 100)):
                        r = identity(5)
                        for i in active:
                            if i == src:
                                continue
                            for j in active:
                                if j in (dst, i):
                                    continue
                                if (i, j) == (dst, src):
                                    if endpoint:
                                        r[i][(j, full)] = direction
                                else:
                                    r[i][(j, (100 + offset + 5*i+j,))] = 1
                        matrices.append(r)
                    p = polynomial_product(matrices[0], c)
                    q = polynomial_product(ci, matrices[1])
                    for matrix, sign in ((p, polarity), (q, -polarity)):
                        require(matrix[0] == {(0, ()): 1}, "schema source row")
                        for i, row in enumerate(matrix):
                            require(len({col for col, _ in row}) == len(row), "schema monomial entries")
                            require(all(abs(value) == 1 for value in row.values()), "schema unit coefficients")
                            require({k: value for k, value in row.items() if k[0] == 2}
                                    == ({(2, ()): 1} if i == 2 else {}), "schema target column")
                        endpoint = {k: value for k, value in matrix[2].items() if k[0] == 0}
                        require(endpoint in ({}, {(0, ab): sign}), "schema endpoint")
                    expected_endpoints = ([(0, 0), (e, 0), (1, -f), (1, -1)]
                                          if polarity == 1 else
                                          [(0, 0), (0, f), (-e, 1), (-1, 1)])
                    require((p[2].get((0, ab), 0), q[2].get((0, ab), 0))
                            == expected_endpoints[phase], "eight-case proof table")
                    count += 1
            c = polynomial_product(whole, c)
            ci = polynomial_product(ci, whole_inverse)
        require(polynomial_product(c, ci) == identity(5), "schema complete inverse")
    return {"abstract_cases": count, "independent_endpoint_choices": 4,
            "internal_registers": 2}


def bound_sources(root):
    data = json.loads((HERE / "SOURCES.json").read_text())
    for item in data["files"]:
        raw = (root / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"],
                "source SHA256: " + item["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == item["git_blob"],
                "source Git blob: " + item["path"])
    return data


def source_dispatcher(root, paths):
    """Execute only the pinned compose definition; leaf arithmetic is recorded."""
    tree = ast.parse((root / paths["dispatcher"]).read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name == "compose"]
    require(len(nodes) == 1, "one source dispatcher")

    class Contract:
        need = staticmethod(require)
        norm2 = staticmethod(lambda x: x * x)

    def generate(n, sign):
        arrays = [[i] for i in range(2 + (n - 1).bit_length())]
        ports = {id(value): i for i, value in enumerate(arrays)}
        emitted = []

        def leaf(x, y, factor, phases, beta, bits, direction, polarity, stats):
            emitted.append((ports[id(x)], ports[id(y)], factor, polarity))

        namespace = {"c": Contract, "leaf": leaf}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "pinned-compose", "exec"), namespace)
        namespace["compose"](arrays[0], arrays[1], list(range(n)), arrays[2:],
                             [1], Fraction(1, 2), 128, 1, sign)
        return emitted

    return generate


def load_core(root, path):
    spec = importlib.util.spec_from_file_location("pinned_905_budget", root / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mm(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    """Independent exact Gauss-Jordan inverse; no shear update formulas."""
    n = len(a)
    aug = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
           for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if aug[i][j])
        aug[j], aug[pivot] = aug[pivot], aug[j]
        scale = aug[j][j]
        aug[j] = [x / scale for x in aug[j]]
        for i in range(n):
            if i != j:
                scale = aug[i][j]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[j])]
    return [row[n:] for row in aug]


def evaluate(matrix, factors):
    size = 2 * len(matrix)
    result = [[0] * size for _ in range(size)]
    for i, row in enumerate(matrix):
        for (j, term), value in row.items():
            product = eye(2)
            for a in term:
                product = mm(product, factors[a])
            for r in range(2):
                for c in range(2):
                    result[2*i+r][2*j+c] += value * product[r][c]
    return result


def dense_checks():
    # These factors do not commute; integer arithmetic is exact.
    cases = boundaries = solves = 0
    for n in range(1, 9):
        factors = [[[1, (j % 3) - 1], [0, 1]] if j % 2 == 0
                   else [[1, 0], [1, 1]] for j in range(n)]
        blocks = 2 + (n - 1).bit_length()
        dim = 2 * blocks
        subset_norm = 1
        for mask in range(1 << n):
            value = eye(2)
            for j in range(n):
                if mask >> j & 1:
                    value = mm(factors[j], value)
            subset_norm = max(subset_norm, max(sum(abs(x) for x in row) for row in value))
        for sign in (-1, 1):
            p, q = eye(dim), eye(dim)
            instructions = word(n, sign)

            def observe(index, instruction, formal, formal_inverse):
                nonlocal p, q, boundaries, solves
                s, t, a, v = instruction
                elementary = eye(dim)
                for i in range(2):
                    for j in range(2):
                        elementary[2*t+i][2*s+j] = v * factors[a][i][j]
                p = mm(elementary, p)
                # Use a separately inverted elementary matrix on the right.
                q = mm(q, inverse(elementary))
                require(evaluate(formal, factors) == p, "independent dense prefix evaluation")
                require(evaluate(formal_inverse, factors) == q, "independent dense inverse evaluation")
                require(mm(p, q) == eye(dim) == mm(q, p), "two-sided dense inverse")
                require(max(sum(abs(x) for x in row) for matrix in (p, q) for row in matrix)
                        <= blocks * subset_norm, "operator substitution bound")
                if index in {1, len(instructions)//2, len(instructions)}:
                    require(q == inverse(p), "independent dense prefix inverse")
                    solves += 1
                boundaries += 1
            trace(n, sign, instructions, observer=observe)
            # Independent direct ordered product for the final dense map.
            product = eye(2)
            for a in factors:
                product = mm(a, product)
            expected = eye(dim)
            for i in range(2):
                for j in range(2):
                    expected[2+i][j] = sign * product[i][j]
            require(p == expected, "dense complete ordered product")
            cases += 1
    return {"cases": cases, "boundaries": boundaries, "dense_prefix_solves": solves}


@lru_cache(None)
def calls(n):
    return 1 if n == 1 else 2 * (calls(n // 2) + calls(n - n // 2))


def cl2(n):
    require(type(n) is int and n > 0, "positive integer logarithm")
    return (n - 1).bit_length()


def prime_power_phi(r):
    prime = next((p for p in range(2, r + 1) if r % p == 0), r)
    rest = r
    while rest % prime == 0:
        rest //= prime
    return r - r // prime if rest == 1 else None


def budget_checks(core):
    rows = []
    for r in range(3, 257):
        phi = prime_power_phi(r)
        if phi is None:
            continue
        n, ell, height = r - 1, cl2(r), cl2(r - 1)
        delta = 1 + 2*ell + r*n*phi
        ai = 2*delta + r + 2
        gap = delta + ell + 2*r + 2
        subset_exponent = ai + 2*r + ell
        j = subset_exponent + cl2(height + 2)
        local = 3*gap + cl2(13*(r + 1))
        require(height + 2 <= 1 << (j - subset_exponent), "prefix rounding-up")
        for p in (1, 53, 128):
            for m in (0, 20):
                for incoming in (0, p + 7, 10**9):
                    old = core.uniform(r, p, m, incoming)
                    w = max(incoming, local, 2*gap + 1,
                            p + 3 + cl2(calls(n)) + local + m + 3*j)
                    require(old["phi"] == phi and old["leaf_calls"] == calls(n), "source resources")
                    require(old["prefix_exponent"] == subset_exponent + 1 + 2*height,
                            "source prefix exponent")
                    require(w >= incoming and w >= 2*gap + 1, "grid and stable closure")
                    require(w >= 1 + cl2(calls(n)) + 2*j + local, "feedback at most one half")
                    require(w >= p + 3 + cl2(calls(n)) + local + m + 3*j, "execution error half budget")
                    require(old["coefficient_error_exponent"] >= max(delta+1, ai+1, p+2*ai+m+4),
                            "unchanged coefficient perturbation")
                    require(old["factor_bits"] >= max(n*ell, old["coefficient_error_exponent"]+r+3),
                            "unchanged factor preparation")
                    require(w <= old["working_bits"] <= max(incoming, p) + m + 16*r**3,
                            "inherited cubic majorant")
                    rows.append({"r": r, "p": p, "m": m, "incoming": incoming,
                                 "old": old["working_bits"], "new": w,
                                 "old_J": old["prefix_exponent"], "new_J": j})
    for n in range(1, 10001):
        q = 1 << (n.bit_length() - 1)
        require(calls(n) == 3*q*n - 2*q*q, "exact inherited leaf count")
        require(cl2(n) + 2 <= 2*3**cl2(n), "coefficient-bound comparison")
    return {"cases": len(rows), "resource_counts": 10000, "rows_sha256": digest(rows),
            "unchanged_grid_cases": sum(row["new"] == row["old"] for row in rows),
            "examples": [row for row in rows if row["r"] in (4, 9, 16, 64, 128, 256)
                         and row["p"] == 128 and row["m"] == 20 and row["incoming"] == 0]}


def rejected(label, action):
    try:
        action()
    except (ValueError, IndexError):
        return label
    raise ValueError("negative control accepted: " + label)


def negative_controls():
    valid = word(3)
    controls = [
        rejected("zero factors", lambda: word(0)),
        rejected("boolean factors", lambda: word(True)),
        rejected("invalid direction", lambda: word(3, 0)),
        rejected("duplicated leaf", lambda: trace(3, instructions=valid[:1] + valid)),
        rejected("omitted restoration", lambda: trace(3, instructions=valid[:-1])),
        rejected("wrong inverse order even factors", lambda: trace(2, -1, [(s,t,a,-v) for s,t,a,v in word(2)])),
        rejected("repeated factor label", lambda: trace(3, instructions=[(s,t,min(a,1),v) for s,t,a,v in valid])),
        rejected("noncommuting factor reversal", lambda: trace(3, instructions=[(s,t,2-a,v) for s,t,a,v in valid])),
        rejected("aliased leaf ports", lambda: trace(1, instructions=[(0,0,0,1)])),
    ]
    extremal = trace(74)
    controls.append(rejected("bound smaller by one", lambda: require(
        extremal["maximum"][0] <= extremal["bound"] - 1, "sharp witness")))
    return controls


def audit(root):
    sources = bound_sources(root)
    domain = json.loads((HERE / "DOMAIN.json").read_text())
    rng = random.Random(domain["assignment_seed"])
    sampled = sorted(rng.sample(list(range(65, 193, 2)), 12))
    counts = sorted(set(range(1, 65)) | set(sampled) | {72, 74, 127, 128, 129, 255, 256, 257})
    require(canonical(domain["factor_counts"]) == canonical(counts), "frozen factor domain")
    inherited = source_dispatcher(root, sources["roles"])
    records, words_checked = [], 0
    for n in counts:
        for sign in (-1, 1):
            instructions = word(n, sign)
            require(instructions == inherited(n, sign), "literal pinned dispatcher word")
            require(len(instructions) == calls(n), "literal paid leaf count")
            records.append(trace(n, sign, instructions))
            words_checked += 1
    core = load_core(root, sources["roles"]["budget"])
    return {
        "schema": "dirty-prefix-monomial-audit-v1",
        "sources_sha256": digest(sources),
        "assignment_seed": domain["assignment_seed"],
        "factor_counts": counts,
        "traces": len(records),
        "leaf_boundaries": sum(row["leaves"] for row in records),
        "prefix_and_inverse_matrices": 2*sum(row["leaves"] + 1 for row in records),
        "dispatcher_comparisons": words_checked,
        "traces_sha256": digest(records),
        "seed_witness": next(row for row in records if row["n"] == 74 and row["sign"] == 1),
        "induction_schema": schema_checks(),
        "dense": dense_checks(),
        "budgets": budget_checks(core),
        "negative_controls": negative_controls(),
        "kappa": "unchanged",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--write", type=Path, help="write a NEW receipt instead of comparing")
    args = parser.parse_args()
    receipt = audit(args.source_root.resolve())
    if args.write:
        with args.write.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        require(canonical(receipt) == canonical(expected), "complete deterministic receipt")
    print("PASS_DIRTY_PREFIX_MONOMIAL"
          f" traces={receipt['traces']} boundaries={receipt['leaf_boundaries']}"
          f" budgets={receipt['budgets']['cases']} controls={len(receipt['negative_controls'])}"
          " kappa=unchanged")


if __name__ == "__main__":
    main()
