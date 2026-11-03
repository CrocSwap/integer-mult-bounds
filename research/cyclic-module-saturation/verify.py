"""Exact new-construction checks. Writes a hash-bound receipt only to stdout."""

import hashlib
import itertools
import json
from pathlib import Path

from linear import eye, mm, mv, solve, span, transpose
from model import Algebra, Module, check_part, cyclic_part, ideal_identity
from model import quotient_annihilator, saturated_ideal
from tensor import check, recognize


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def quadratic(p, alpha, beta):
    return Algebra(p, [[[1, 0], [0, 1]], [[0, 1], [alpha, beta]]], [1, 0])


def truncated(p, n):
    table = [[[int(k == i + j) for k in range(n)] for j in range(n)]
             for i in range(n)]
    return Algebra(p, table, [1] + [0] * (n - 1))


def radical(p):
    table = [[[0] * 3 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        table[0][i][i] = table[i][0][i] = 1
    return Algebra(p, table, [1, 0, 0])


def split(p, n):
    table = [[[int(i == j == k) for k in range(n)] for j in range(n)]
             for i in range(n)]
    return Algebra(p, table, [1] * n)


def direct_sum(first, second):
    a, b = first.algebra, second.algebra
    n, d, p = a.n + b.n, first.d + second.d, a.p
    require(p == b.p, "different characteristics")
    table = [[[0] * n for _ in range(n)] for _ in range(n)]
    actions = [[[0] * d for _ in range(d)] for _ in range(n)]
    for alg, module, offset, at in ((a, first, 0, 0), (b, second, a.n, first.d)):
        for i in range(alg.n):
            for j in range(alg.n):
                for k in range(alg.n):
                    table[offset + i][offset + j][offset + k] = alg.table[i][j][k]
            for j in range(module.d):
                for k in range(module.d):
                    actions[offset + i][at + j][at + k] = module.actions[i][j][k]
    return Module(Algebra(p, table, list(a.unit) + list(b.unit)), actions)


def inverse(matrix, p):
    n = len(matrix)
    columns = [solve(matrix, v, p, n) for v in eye(n)]
    require(all(v is not None for v in columns), "singular fixture map")
    return transpose(columns)


def chart(n, p, salt):
    matrix = eye(n)
    for k in range(2 * n):
        if n == 1:
            break
        i, j = k % n, (k + 1) % n
        c = (salt + k + 1) % p
        matrix[i] = [(x + c * y) % p for x, y in zip(matrix[i], matrix[j])]
    return matrix


def changed_module(module, salt):
    p, n = module.algebra.p, module.d
    q = chart(n, p, salt)
    qi = inverse(q, p)
    return Module(module.algebra, [mm(mm(qi, x, p), q, p) for x in module.actions])


def literal_cyclic_idempotent(module):
    """Independent tiny oracle: enumerate every vector and idempotent."""
    a, d, p = module.algebra, module.d, module.algebra.p
    require(a.n == d == 2 and p <= 5, "oracle domain exceeded")
    result = [0, 0]
    vectors = list(itertools.product(range(p), repeat=2))
    for e in vectors:
        if a.product(e, e) != list(e):
            continue
        image = transpose([module.act(e, col) for col in eye(d)])
        rank = len(span(image, p, d))
        generated = False
        for w in vectors:
            v = module.act(e, w)
            # A has basis (1,x). Use the literal two-column determinant.
            xv = mv(module.actions[1], v, p)
            vrank = 2 if (v[0] * xv[1] - v[1] * xv[0]) % p else int(any(v))
            generated = generated or vrank == rank
        if generated:
            product = a.product(result, e)
            result = [(x + y - z) % p for x, y, z in zip(result, e, product)]
    return result


def exhaustive_modules():
    candidates, modules, cyclic, partial, zero = 0, 0, 0, 0, 0
    for p in (2, 3, 5):
        ident = eye(2)
        for alpha, beta in itertools.product(range(p), repeat=2):
            a = quadratic(p, alpha, beta)
            for entries in itertools.product(range(p), repeat=4):
                candidates += 1
                x = [list(entries[:2]), list(entries[2:])]
                expected = [[(alpha * ident[i][j] + beta * x[i][j]) % p
                             for j in range(2)] for i in range(2)]
                if mm(x, x, p) != expected:
                    continue
                m = Module(a, [ident, x])
                v, e, _ = cyclic_part(m)
                require(e == literal_cyclic_idempotent(m), "maximal summand mismatch")
                require(check_part(m, v, e), "bad module endpoint")
                modules += 1
                cyclic += e == list(a.unit)
                partial += any(e) and e != list(a.unit)
                zero += not any(e)
    return {"candidate_actions": candidates, "valid_modules": modules,
            "cyclic_modules": cyclic, "proper_nonzero_cyclic_parts": partial,
            "zero_cyclic_parts": zero}


def module_fixtures():
    cases, basis_probes, partials = 0, 0, 0
    for p in (2, 3, 7, 257, 65537):
        r = radical(p)
        regular = Module(r, r.left)
        dual = Module(r, [transpose(x) for x in r.left])
        field = split(p, 1)
        mixed = direct_sum(Module(field, field.left), dual)
        fixtures = [(regular, list(r.unit)), (dual, [0] * 3),
                    (mixed, [1, 0, 0, 0])]
        for m, expected in fixtures:
            for salt in range(3):
                changed = changed_module(m, salt)
                v, e, trace = cyclic_part(changed)
                require(e == expected and check_part(changed, v, e), "fixture summand")
                require(trace == sorted(trace), "decreasing generated rank")
                cases += 1
                basis_probes += len(trace)
                partials += any(e) and e != list(m.algebra.unit)
        for n in (2, 3, 5, 8):
            a = split(p, n)
            _, e, trace = cyclic_part(Module(a, a.left))
            require(trace == list(range(1, n + 1)) and e == list(a.unit),
                    "sharp basis-scan fixture")
            a = truncated(p, n)
            m = Module(a, a.left)
            x = [0, 1] + [0] * (n - 2)
            ideal = quotient_annihilator(m, x)
            require(len(ideal) == n - 1 and not saturated_ideal(a, ideal),
                    "nilpotent ideal must vanish")
            require(quotient_annihilator(m, list(a.unit)) == eye(n),
                    "quotient annihilator confused with vector annihilator")
            cases += 2
            basis_probes += len(trace)
    return {"module_fixtures": cases, "basis_probes": basis_probes,
            "mixed_partial_fixtures": partials}


def transported_tensor(a, salt):
    n, p = a.n, a.p
    u, v, w = [chart(n, p, salt + k) for k in (0, 3, 7)]
    ui, vi = transpose(inverse(u, p)), transpose(inverse(v, p))
    return [[mv(w, a.product(ui[i], vi[j]), p) for j in range(n)] for i in range(n)]


def tensor_fixtures():
    presentations, products, rejections, forgeries = 0, 0, 0, 0
    for p in (2, 3, 7, 257, 65537):
        algebras = [split(p, 2), split(p, 4), truncated(p, 3), radical(p),
                    quadratic(p, 1, 1)]
        for a in algebras:
            for salt in range(3):
                t = transported_tensor(a, salt)
                cert, reason = recognize(t, p)
                require(cert is not None and reason is None and check(t, p, cert),
                        "new tensor reconstruction failed")
                presentations += 1
                products += a.n * a.n
                bad = dict(cert)
                bad["W"] = [list(row) for row in cert["W"]]
                bad["W"][0][0] = (bad["W"][0][0] + 1) % p
                require(not check(t, p, bad), "forged output map accepted")
                forgeries += 1
        a = radical(p)
        dual = [transpose(x) for x in a.left]
        base = [[mv(dual[i], col, p) for col in eye(3)] for i in range(3)]
        swapped = [[base[j][i] for j in range(3)] for i in range(3)]
        for t in (base, swapped):
            cert, reason = recognize(t, p)
            require(cert is None and reason == "noncyclic nucleus module",
                    "nonregular module accepted")
            rejections += 1
    return {"tensor_presentations": presentations, "transported_basis_products": products,
            "nonregular_rejections": rejections, "forged_map_rejections": forgeries}


def controls():
    rejected = 0
    a = quadratic(3, 0, 0)
    bad_table = [[[1, 0], [0, 1]], [[0, 1], [0, 0]]]
    calls = [lambda: Algebra(4, bad_table, [1, 0]),
             lambda: Algebra(65539, bad_table, [1, 0]),
             lambda: Algebra(3, bad_table, [0, 0]),
             lambda: Algebra(3, [[[1, 0.0]]], [1]),
             lambda: Module(a, [eye(2)]),
             lambda: Module(a, [eye(2), eye(2)]),
             lambda: Module(a, [eye(2), [[0], [0]]]),
             lambda: recognize([], 3),
             lambda: recognize([[[3]]], 3),
             lambda: ideal_identity(a, [[0, 1]])]
    for call in calls:
        try:
            call()
        except (ValueError, ArithmeticError):
            rejected += 1
        else:
            raise RuntimeError("boundary/mathematical control accepted")
    return {"explicit_rejection_controls": rejected}


def main():
    counts = {}
    for result in (exhaustive_modules(), module_fixtures(), tensor_fixtures(), controls()):
        counts.update(result)
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "linear.py", "model.py", "tensor.py", "verify.py")
    here = Path(__file__).resolve().parent
    hashes = {}
    for name in files:
        path = here / name
        require(path.stat().st_size <= 1024 * 1024, "package file exceeds one MiB")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_CYCLIC_MODULE_SATURATION", "counts": counts,
                      "source_sha256": hashes, "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
