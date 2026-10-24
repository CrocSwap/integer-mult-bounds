"""Independent physical-cut oracle around retained compiler scheduling code."""
import ast
import copy
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py"
FULL = "research/rational-unitary-fft/full.py"
spec = importlib.util.spec_from_file_location("retained_scalar", ROOT / "research/rational-unitary-fft/exact.py")
scalar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scalar)
C = scalar.C  # Only the retained exact Gaussian-rational scalar representation.


def need(ok, why):
    if not ok:
        raise ValueError(why)


class Matrix(list):
    def __init__(self, rows):
        super().__init__([[x if isinstance(x, C) else C(x) for x in row] for row in rows])
    @property
    def T(self):
        return Matrix(zip(*self))
    def __getitem__(self, key):
        if not isinstance(key, tuple):
            return super().__getitem__(key)
        i, j = key
        if isinstance(i, int) and isinstance(j, int):
            return super().__getitem__(i)[j]
        return Matrix([row[j] for row in super().__getitem__(i)])
    def __sub__(self, other):
        return Matrix([[x-y for x, y in zip(a, b)] for a, b in zip(self, other)])
    def __matmul__(self, other):
        return product(self, other)


def identity(n):
    return Matrix([[int(i == j) for j in range(n)] for i in range(n)])


def product(a, b):
    return Matrix([[sum((a[i][k]*b[k][j] for k in range(len(b))), C())
                    for j in range(len(b[0]))] for i in range(len(a))])


def solve(a, b):
    n, width = len(a), len(b[0])
    rows = [list(x)+list(y) for x, y in zip(a, b)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col] != 0), None)
        need(pivot is not None, "singular matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        q = rows[col][col]
        rows[col] = [x/q for x in rows[col]]
        for i in range(n):
            if i != col:
                q = rows[i][col]
                rows[i] = [x-q*y for x, y in zip(rows[i], rows[col])]
    return Matrix([row[n:n+width] for row in rows])


def embed(a, ids, n):
    out = identity(n)
    for i, row in enumerate(ids):
        for j, col in enumerate(ids):
            out[row][col] = a[i][j]
    return out


def operator(gates, n):
    out = identity(n)
    for ids, a in gates:
        out = product(embed(a, ids, n), out)
    return out


def reject(call, word):
    try:
        call()
    except ValueError as exc:
        need(word in str(exc), "unexpected rejection")
    else:
        raise ValueError("missed control " + word)


def retained_schedule():
    """Execute only unchanged structural definitions, not source verifiers."""
    original = ast.parse((ROOT / SOURCE).read_bytes())
    definitions = [copy.deepcopy(x) for x in original.body
                   if isinstance(x, ast.FunctionDef) and x.name in {"full_plan", "parallel", "inverse"}]
    need(len(definitions) == 3, "source schedule definitions")
    full = ast.parse((ROOT / FULL).read_bytes())
    plan = next(copy.deepcopy(x) for x in full.body if isinstance(x, ast.ClassDef) and x.name == "Plan")
    cls = next(x for x in full.body if isinstance(x, ast.ClassDef) and x.name == "Full")
    parallel = next(copy.deepcopy(x) for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == "parallel")
    parallel.name = "typed_parallel"
    tree = ast.Module(body=[plan]+definitions+[parallel], type_ignores=[])
    ast.fix_missing_locations(tree)
    env = {"need": need, "np": SimpleNamespace(linalg=SimpleNamespace(solve=solve, inv=lambda a: solve(a, identity(len(a))))),
           "STATS": {"full_nodes": 0}}
    exec(compile(tree, "<retained schedule only>", "exec", optimize=0), env)
    owner = SimpleNamespace(source_parallel=env["parallel"])
    env["parallel"] = lambda a, b: env["typed_parallel"](owner, a, b)
    return env


def fixture(matrix, reverse=False):
    n, env = len(matrix), retained_schedule()
    indices = list(reversed(range(n))) if reverse else list(range(n))
    position = {wire: i for i, wire in enumerate(indices)}
    def atom(ids, gates, kind):
        interval = min(position[i] for i in ids), max(position[i] for i in ids)+1
        name = (kind,)+interval
        row = dict(id=name, indices=ids, kind=kind, interval=interval,
                   start=0, stop=len(gates), local=gates, local_layers=[[g] for g in gates])
        return env["Plan"]([[gate] for gate in gates], [row])
    def leaf(ids, values):
        return atom(ids, [(tuple(ids), Matrix([[values[0]]]))], "D")
    def shear(target, source, k):
        ids = source+target
        nonzero = [(target[i], source[j], k[i][j]) for i in range(len(k))
                   for j in range(len(k)) if k[i][j] != 0]
        gates = []
        if nonzero:
            # Deliberately unequal noncommuting child implementations, exact endpoint retained.
            repetitions = 1 + sum(position[i] for i in ids) % 3
            for _ in range(repetitions):
                gates.append(((ids[0],), Matrix([[2]])))
            for _ in range(repetitions):
                gates.append(((ids[0],), Matrix([[Q(1, 2)]])))
            gates += [((a, b), Matrix([[1, c], [0, 1]])) for a, b, c in nonzero]
        kind = "R" if position[target[0]] < position[source[0]] else "L"
        return atom(ids, gates, kind)
    env.update(diag=leaf, lowdisp_shear=shear)
    plan = env["full_plan"](indices, matrix)
    need(len(plan.atoms) == 3*n-2, "complete source atoms")
    actual = operator([g for layer in plan for g in layer], n)
    need(actual == embed(matrix, indices, n), "source endpoint")
    inverse = env["inverse"](plan)
    need(product(operator([g for layer in inverse for g in layer], n), actual) == identity(n),
         "stored inverse order")
    return plan


def audit(plan, n):
    atoms = plan.atoms
    ids = {a["id"] for a in atoms}
    need(len(ids) == len(atoms), "unique atoms")
    endpoint = {a["id"]: operator(a["local"], n) for a in atoms}
    local_occurrences = [id(g[1]) for a in atoms for g in a["local"]]
    physical_occurrences = [id(g[1]) for layer in plan for g in layer]
    need(len(set(local_occurrences)) == len(local_occurrences), "unique gate occurrence tokens")
    need(sorted(local_occurrences) == sorted(physical_occurrences), "every physical gate owned once")
    prerequisites = {}
    for a in atoms:
        x, y = a["interval"]
        before = {b["id"] for b in atoms if b["kind"] == "R"
                  and b["interval"] != a["interval"]
                  and b["interval"][0] <= x and y <= b["interval"][1]}
        if a["kind"] == "L":
            before |= {b["id"] for b in atoms if b is not a
                       and x <= b["interval"][0] and b["interval"][1] <= y}
        prerequisites[a["id"]] = before
        need(a["stop"]-a["start"] == len(a["local_layers"]), "atom duration")
        for offset, layer in enumerate(a["local_layers"]):
            for g in layer:
                need(set(g[0]) <= set(a["indices"]), "atom owns every gate wire")
                need(any(g[0] == h[0] and g[1] is h[1] for h in plan[a["start"]+offset]),
                     "source timing ownership")
    counts = dict(cuts=0, partial_layer_cuts=0, simultaneous_active=0, simultaneous_nonempty=0,
                  zero_layer_atoms=sum(not a["local"] for a in atoms))
    seen_gates = []
    for layer_index in range(len(plan)+1):
        layer = plan[layer_index] if layer_index < len(plan) else []
        need(len({i for g in layer for i in g[0]}) == sum(len(g[0]) for g in layer), "disjoint layer")
        subsets = list(itertools.chain.from_iterable(itertools.combinations(range(len(layer)), k)
                                                     for k in range(len(layer)+1)))
        for subset in subsets:
            executed = seen_gates+[layer[j] for j in subset]
            done_ids = {id(g[1]) for g in executed}
            completed, active = set(), []
            for a in atoms:
                if a["stop"] <= layer_index:
                    completed.add(a["id"])
                elif a["start"] <= layer_index < a["stop"]:
                    active.append(a)
            active_ids = {a["id"] for a in active}
            need(all(prerequisites[x] <= completed for x in completed | active_ids), "downset predecessors")
            used = [i for a in active for i in a["indices"]]
            need(len(set(used)) == len(used), "active supports disjoint")
            done, remaining = identity(n), identity(n)
            for a in atoms:
                if a["id"] in completed:
                    done = product(endpoint[a["id"]], done)
                elif a["id"] not in active_ids:
                    remaining = product(endpoint[a["id"]], remaining)
            fragments, tails = identity(n), identity(n)
            for a in active:
                head = [g for g in a["local"] if id(g[1]) in done_ids]
                tail = [g for g in a["local"] if id(g[1]) not in done_ids]
                fragments = product(operator(head, n), fragments)
                tails = product(operator(tail, n), tails)
            unexecuted = [g for g in layer if id(g[1]) not in done_ids] + [g for later in plan[layer_index+1:] for g in later]
            prefix, suffix = operator(executed, n), operator(unexecuted, n)
            need(prefix == product(fragments, done), "prefix fragment order")
            need(suffix == product(remaining, tails), "suffix fragment order")
            need(product(suffix, prefix) == operator([g for l in plan for g in l], n), "cut endpoint")
            counts["cuts"] += 1
            counts["partial_layer_cuts"] += int(0 < len(subset) < len(layer))
            counts["simultaneous_active"] = max(counts["simultaneous_active"], len(active))
            counts["simultaneous_nonempty"] = max(counts["simultaneous_nonempty"],
                sum(any(id(g[1]) in done_ids for g in a["local"]) for a in active))
        seen_gates += layer
    return counts


def actual_source_fixture():
    # One actual Full factory, no source verifier and no full historical replay.
    sys.path.insert(0, str(ROOT / "research/rational-unitary-fft"))
    import full
    raw_paths = [SOURCE, "research/rational-unitary-fft/vendor/stein_rational.py",
                 "research/rational-unitary-fft/vendor/STEIN-PROVENANCE.json",
                 "research/cubic-cyclic-inverse/vendor/interval_kernel.py"]
    raw = {path: (ROOT/path).read_bytes() for path in raw_paths}
    matrix = full.Matrix([[full.C(1,Q(1,16)),full.C(Q(1,8),Q(1,32))],
                          [full.C(Q(1,16),Q(-1,32)),full.C(1,Q(1,16))]])
    lam, q, _ = full.admission(matrix)
    builder = full.Full(full.allocation(2,lam,q,1,2,0),raw)
    source_plan = builder.plan(matrix)
    cache = {}
    def gate(g, mapping=None):
        ids, matrix = g
        if id(matrix) not in cache:
            cache[id(matrix)] = Matrix([[C(x.re,x.im) for x in row] for row in matrix])
        return tuple(ids if mapping is None else [mapping[i] for i in ids]), cache[id(matrix)]
    plan = retained_schedule()["Plan"]([[gate(g) for g in layer] for layer in source_plan], [])
    for a in source_plan.atoms:
        layers = [[gate(g,a["indices"]) for g in layer] for layer in a["local_plan"]]
        kind = {"upper":"R","lower":"L","leaf":"D"}[a["kind"]]
        plan.atoms.append(dict(id=(kind,)+tuple(a["interval"]), kind=kind,
                               interval=a["interval"],indices=a["indices"],
                               start=a["start"],stop=a["stop"],local_layers=layers,
                               local=[g for layer in layers for g in layer]))
    return plan


def main():
    cases = [("complex_scalar", Matrix([[C(Q(2, 3), Q(1, 5))]]), False),
             ("zero_calls", identity(4), True)]
    for n in (2, 4):
        cases.append(("complex_"+str(n), Matrix([[C(2, Q(1, 8)) if i == j
                    else C(Q(1, 8*(1+abs(i-j))), Q(i-j, 64))
                    for j in range(n)] for i in range(n)]), True))
    results = {}
    for name, matrix, reverse in cases:
        plan = fixture(matrix, reverse)
        results[name] = audit(plan, len(matrix))
    results["actual_Full_complex_2"] = audit(actual_source_fixture(),2)
    need(any(v["partial_layer_cuts"] for v in results.values()), "proper partial layer coverage")
    need(any(v["simultaneous_nonempty"] >= 2 for v in results.values()), "two active fragments")
    plan = fixture(cases[-1][1])
    mutated = copy.copy(plan)
    mutated.atoms = [dict(a) for a in plan.atoms]
    mutated.atoms[1]["start"] += 1
    mutated.atoms[1]["stop"] += 1
    reject(lambda: audit(mutated, 4), "source timing ownership")
    zero = fixture(identity(4))
    zero.atoms = [dict(a) for a in zero.atoms]
    zero.atoms[0]["start"] = zero.atoms[0]["stop"] = 1
    reject(lambda: audit(zero,4), "downset predecessors")
    # A noncommuting two-factor cut rejects swapping the factorization order.
    a = Matrix([[1, 1], [0, 1]])
    b = Matrix([[2, 0], [0, 1]])
    reject(lambda: need(product(a, b) == product(b, a), "prefix fragment order"), "prefix fragment order")
    reject(lambda: need(product(solve(a, identity(2)), solve(b, identity(2))) ==
                        solve(product(a, b), identity(2)), "inverse reversal"), "inverse reversal")
    print(json.dumps(results, sort_keys=True))
    print("PASS_FULL_TOEPLITZ_CUT_AUDIT controls=4 one_actual_Full_factory no_new_kappa")


if __name__ == "__main__":
    main()
