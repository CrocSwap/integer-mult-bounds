"""Exact, offline checks for the ternary dirty-shear construction.

Two symbolic engines independently check the emitted word: a free additive
term algebra for arbitrary deterministic nonlinear leaves, and a free
noncommutative module for the ideal ordered product. Pinned PR628 arithmetic
then supplies rounded cyclic leaves and independent dense reference solves.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_check():
    pins = json.loads((ROOT / "SOURCES.json").read_text())
    for entry in pins["sources"]:
        need(hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
             "source pin mismatch: " + entry["path"])
    return {"base_commit": pins["base_commit"], "pr628_commit": pins["pr628_commit"],
            "pr673_commit": pins["pr673_commit"],
            "source_files": len(pins["sources"])}


def add_terms(target, increment, sign):
    result = target.copy()
    for term, coefficient in increment.items():
        value = result.get(term, 0) + sign * coefficient
        if value:
            result[term] = value
        else:
            result.pop(term, None)
    return result


def nonlinear_check(steps, slots, inverse):
    # Each atom is either an initial-array symbol or F_i(canonical expression).
    # Interning gives equal function calls the same atom without evaluating F_i.
    atoms = {}

    def atom(key):
        if key not in atoms:
            atoms[key] = len(atoms)
        return atoms[key]

    state = [{atom(("initial", i)): 1} for i in range(slots)]
    initial = [x.copy() for x in state]
    # An extra target translation detects an illicit target-dependent increment.
    translated = [x.copy() for x in state]
    offset = atom(("target_offset",))
    translated[1][offset] = 1

    def run(word, values):
        for factor, source, target, sign in word:
            key = ("function", factor, tuple(sorted(values[source].items())))
            values[target] = add_terms(values[target], {atom(key): 1}, sign)

    run(steps, state)
    need(all(state[i] == initial[i] for i in range(slots) if i != 1), "nonlinear restoration")
    run(steps, translated)
    need(translated[1] == add_terms(state[1], {offset: 1}, 1), "target-independent increment")
    run(inverse, state)
    need(state == initial, "nonlinear exact inverse")


def linear_check(steps, n, slots, inverse=None):
    # Terms are (ordered factor word, initial register). Multiplication is
    # concatenation on the LEFT, so factors are never silently commuted.
    state = [{((), i): 1} for i in range(slots)]
    initial = [x.copy() for x in state]

    def run(word):
        for factor, source, target, sign in word:
            increment = {((factor,) + operators, register): coefficient
                         for (operators, register), coefficient in state[source].items()}
            state[target] = add_terms(state[target], increment, sign)

    run(steps)
    expected = [x.copy() for x in initial]
    expected[1][(tuple(reversed(range(n))), 0)] = 1
    need(state == expected, "ordered linear product or dirty endpoint")
    if inverse is not None:
        run(inverse)
        need(state == initial, "linear exact inverse")


def binary_calls(n):
    q = 1 << (n.bit_length() - 1)
    return 3 * q * n - 2 * q * q


def resource_checks(t, old):
    rows = []
    symbolic_sizes = list(range(1, 65)) + [81, 128, 243]
    for n in symbolic_sizes:
        calls, scratch = t.resources(n)
        steps, inverse = list(t.word(n)), list(t.word(n, -1))
        need(len(steps) == calls, "emitted leaf count")
        need(max(max(s, d) for _, s, d, _ in steps) == scratch + 1, "emitted peak scratch")
        need(all(0 <= f < n and s != d and sg in (-1, 1) for f, s, d, sg in steps), "leaf addresses")
        need(inverse == [(f, s, d, -sg) for f, s, d, sg in reversed(steps)], "inverse ordering")
        nonlinear_check(steps, scratch + 2, inverse)
        linear_check(steps, n, scratch + 2, inverse)
        rows.append({"factors": n, "ternary_leaves": calls, "dirty_arrays": scratch,
                     "binary_leaves": binary_calls(n), "binary_dirty_arrays": (n - 1).bit_length(),
                     "word_sha256": digest(steps)})

    # Independently minimize over ALL placements of balanced child sizes.
    # This DP does not assume that the cheapest placement puts extras at ends.
    counts = [0, 1, 4]
    predecessor = [0, 1, 4]
    placements = 0
    for n in range(3, 10001):
        q, r = divmod(n, 3)
        sizes = [q + 1] * r + [q] * (3 - r)
        alternatives = set(itertools.permutations(sizes))
        counts.append(min(2 * counts[a] + 4 * counts[b] + 2 * counts[c]
                          for a, b, c in alternatives))
        placements += len(alternatives)
        a, b, c = sizes
        predecessor.append(2 * predecessor[a] + 4 * predecessor[b] + 2 * predecessor[c])
    for n in range(1, 10001):
        power, depth = 1, 0
        while 3 * power <= n:
            power *= 3
            depth += 1
        scratch = 2 * depth + (0 if n == power else 1 if n <= 2 * power else 2)
        need(t.resources(n) == (counts[n], scratch), "independent resource recurrence")
        ceiling = depth + (n != power)
        need(counts[n] <= 8 ** ceiling and scratch <= 2 * ceiling, "uniform recurrence bounds")
        need(counts[n] <= predecessor[n], "balanced split refinement increased calls")

    # Exercise the actual pinned binary dispatcher, replacing only its leaf by
    # a recorder. This verifies the credited binary count against source bytes.
    saved = old.leaf
    baseline = []
    try:
        for n in range(1, 65):
            log = []
            old.leaf = lambda x, y, factor, phases, beta, bits, d, sign, stats: log.append((factor, sign))
            scratch = [[old.c.ZERO] for _ in range((n - 1).bit_length())]
            old.compose([old.c.ONE], [old.c.ZERO], list(range(n)), scratch,
                        [old.c.ONE], F(1, 2), 128, 1)
            need(len(log) == binary_calls(n), "pinned binary dispatcher count")
            baseline.append(len(log))
    finally:
        old.leaf = saved
    return {"symbolic_words": rows, "integer_recurrence_cases": 10000,
            "balanced_size_placements": placements,
            "strict_improvements_over_pr673": sum(counts[n] < predecessor[n] for n in range(1, 10001)),
            "pinned_binary_words": len(baseline), "pinned_binary_counts_sha256": digest(baseline)}


def echo_checks(t, echo):
    """Audit the actual PR673 word and compare a partition-only specialization."""
    rows = []
    original_partition = echo.partition

    def end_placement(n, fanout):
        need(fanout == 3, "this specialization supports fanout three only")
        if n < 3:
            return [1] * n
        q, r = divmod(n, 3)
        return [q + (r > 0), q, q + (r > 1)]

    def canonical(steps):
        return [(factor, src, dst, sign) for src, dst, factor, sign in steps]

    for n in list(range(1, 65)) + [81, 127, 128, 243, 255]:
        scratch, calls = echo.resources(n, 3)
        steps = canonical(echo.instructions(0, n, 0, 1, 2, 3))
        inverse = canonical(echo.instructions(0, n, 0, 1, 2, 3, -1))
        need(len(steps) == calls, "PR673 emitted count")
        nonlinear_check(steps, scratch + 2, inverse)
        linear_check(steps, n, scratch + 2, inverse)
        try:
            # Source bytes stay unchanged. Only the partition hook is replaced
            # in this in-memory instance to isolate the split-placement effect.
            echo.partition = end_placement
            changed_scratch, changed_calls = echo.resources(n, 3)
            changed = canonical(echo.instructions(0, n, 0, 1, 2, 3))
            changed_inverse = canonical(echo.instructions(0, n, 0, 1, 2, 3, -1))
        finally:
            echo.partition = original_partition
        need((changed_calls, changed_scratch) == t.resources(n), "partition-only resources")
        need(changed == list(t.word(n)) and changed_inverse == list(t.word(n, -1)),
             "independent dispatcher differs from partition-only source")
        need(changed_scratch == scratch and changed_calls <= calls, "scratch-preserving refinement")
        rows.append({"factors": n, "dirty_arrays": scratch, "pr673_calls": calls,
                     "refined_calls": changed_calls, "pr673_word_sha256": digest(steps),
                     "refined_word_sha256": digest(changed)})

    return {"fanout": 3, "source_words": rows}


def ceil_log2(value):
    value = F(value)
    need(value > 0, "positive logarithm argument")
    ceiling = (value.numerator + value.denominator - 1) // value.denominator
    return max(0, (ceiling - 1).bit_length())


def execution_budget(calls, beta, scale_bound, initial_bound, target_bits):
    a = 13 * (scale_bound + 1) / beta ** 3
    growth = 2 + F(scale_bound) / beta
    bits = max(ceil_log2(a), ceil_log2(2 / beta ** 2),
               target_bits + 1 + ceil_log2(calls * a * (initial_bound + 1))
               + (calls - 1) * ceil_log2(growth))
    bound = calls * a * (initial_bound + 1) * F(1, 1 << bits) * growth ** (calls - 1)
    need(a <= 1 << bits and F(1, 1 << bits) <= beta ** 2 / 2, "leaf precision assumptions")
    need(bound <= F(1, 1 << (target_bits + 1)), "complete execution error budget")
    return bits, bound


def rounded_case(t, old, factors, length, direction, dirt, beta, scale_bound, kernel=None):
    c = old.c
    n = len(factors)
    calls, required = t.resources(n)
    x = [(F(i % 5 - 2, 4), F(i % 3 - 1, 8)) for i in range(length)]
    y = [(F(dirt + i, 4), F(dirt - i, 8)) for i in range(length)]
    # One additional spectator makes an off-by-one workspace use observable.
    scratch = [[(F(dirt + 2 * i + j, 4), F(dirt - 3 * i - j, 8))
                for i in range(length)] for j in range(required + 1)]
    initial = [v[:] for v in [x, y, *scratch]]
    D = max(abs(real) + abs(imag) for v in initial for real, imag in v)
    bits, bound = execution_budget(calls, beta, scale_bound, D, 128 if kernel else 64)
    units = [c.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    values = [units[(i * i + i + 1) % 4] for i in range(length)]
    need(all(c.norm2(v) == 1 for v in values), "unit phases")

    class Phases:
        reads = 0

        def __getitem__(self, index):
            self.reads += 1
            return values[index]

    phases = Phases()
    stats = {"leaves": 0, "scalar_steps": 0}

    def leaf(src, dst, factor, sign):
        old.leaf(src, dst, factor, phases, beta, bits, direction, sign, stats)

    t.compose(x, y, factors, scratch, leaf)
    need(x == initial[0] and scratch == initial[2:], "rounded source/scratch/spectator restoration")
    need(stats == {"leaves": calls, "scalar_steps": 3 * length * calls}, "all leaf passes charged")
    multiplicities = Counter(f for f, _, _, _ in t.word(n))
    phase_reads = sum(times * ((6 if factors[f][0] else 5) * length - 2)
                      for f, times in multiplicities.items())
    need(phases.reads == phase_reads, "coefficient and phase reads charged")
    net = [c.sub(v, start) for v, start in zip(y, initial[1])]
    if kernel is None:
        exact = old.exact_operator(initial[0], factors, values, direction)
    else:
        # Expand the full polynomial in the cyclic shift, then solve it once.
        # This reference does not use the factor-lifting or ternary recurrences.
        exact = old.w.solve(old.w.matrix(kernel["q"], values, direction), initial[0])
    need(all(c.norm2(c.sub(v, ref)) <= bound ** 2 for v, ref in zip(net, exact)), "dense error comparison")
    net_hash = digest([[str(a), str(b)] for a, b in net])
    t.compose(x, y, factors, scratch, leaf, -1)
    need([x, y, *scratch] == initial, "rounded exact inverse")
    need(stats["leaves"] == 2 * calls and phases.reads == 2 * phase_reads, "inverse cost")
    return {"factors": n, "length": length, "direction": direction, "dirt": dirt,
            "working_bits": bits, "target_bits": 128 if kernel else 64,
            "leaves": calls, "dirty_arrays": required, "spectator_arrays": 1,
            "phase_reads": phase_reads, "lift_loop_visits": 3 * length * calls,
            "net_sha256": net_hash}


def rounded_checks(t, old):
    cases = []
    for n in (1, 2, 3, 4, 5, 8, 9, 15, 27):
        factors = [(i % 2 == 0, (F(1, 4), F((-1) ** i, 8)), F(3 if i == 0 else 1))
                   for i in range(n)]
        for length in (1, 2, 4):
            for direction in (-1, 1):
                for dirt in (0, 7):
                    cases.append(rounded_case(t, old, factors, length, direction, dirt, F(1, 2), 3))
    n = 58
    factors = [(i % 2 == 0, (F(1, 4), F((-1) ** i, 8)), F(3 if i == 0 else 1)) for i in range(n)]
    for direction in (-1, 1):
        cases.append(rounded_case(t, old, factors, 1, direction, -13, F(1, 2), 3))
    return cases


def kernel_checks(t, old):
    rows = json.loads((ROOT / "vendor/pr628/FACTORS.json").read_text())
    cases = []
    for row in rows:
        if row["radix"] not in (4, 9, 16):
            continue
        state = old.w.k.certify(row)
        factors = [(inside, b, F(row["radix"] if i == 0 else 1))
                   for i, (inside, b) in enumerate(state["factors"])]
        for length in ((1,) if row["radix"] == 16 else (1, 3)):
            for direction in (-1, 1):
                for dirt in (-7, 11):
                    result = rounded_case(t, old, factors, length, direction, dirt,
                                          state["beta"], row["radix"], state)
                    result.update(radix=row["radix"], embedding=row["embedding"])
                    cases.append(result)
    need(cases, "missing kernel fixtures")
    return cases


def uniform_budgets(t, base):
    rows = []
    for r in range(3, 257):
        try:
            base.prime_power_data(r)
        except ValueError:
            continue
        calls, scratch = t.resources(r - 1)
        for p in (1, 128, 1048576):
            for dirt_bits in (0, 20, 1024):
                prepared = base.budgets(r, p + 1 + dirt_bits)
                base.check(prepared)
                g = prepared["g"]
                A = 3 * g + base.ceil_log2(13 * (r + 1))
                G = g + base.ceil_log2(r + 2)
                common = p + 1 + A + dirt_bits + 1

                def bits(N):
                    return max(A, 2 * g + 1, common + base.ceil_log2(N) + (N - 1) * G)

                working = bits(calls)
                # Check the exponent inequality directly, not a huge 2^w.
                need(working >= A and working >= 2 * g + 1, "uniform local precision")
                need(working - p - 1 >= base.ceil_log2(calls) + A + dirt_bits + 1 + (calls - 1) * G,
                     "uniform propagated precision")
                rows.append({"radix": r, "target_bits": p, "dirt_bits": dirt_bits,
                             "leaves": calls, "dirty_arrays": scratch, "working_bits": working,
                             "binary_exact_working_bits": bits(binary_calls(r - 1)),
                             "inherited_4n2_working_bits": bits(4 * (r - 1) ** 2),
                             "prepared_target_bits": prepared["target_bits"]})
    return {"cases": len(rows), "rows_sha256": digest(rows),
            "examples": [row for row in rows if row["radix"] in (4, 9, 16, 64, 256)
                         and row["target_bits"] == 128 and row["dirt_bits"] == 20]}


def controls(t):
    rejected = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    steps = list(t.word(9))
    slots = 2 + t.resources(9)[1]
    for i in range(len(steps)):
        reject("omit_leaf_" + str(i), lambda i=i: linear_check(steps[:i] + steps[i + 1:], 9, slots))
        f, s, d, sg = steps[i]
        changed = steps[:i] + [(f, s, d, -sg)] + steps[i + 1:]
        reject("flip_leaf_" + str(i), lambda changed=changed: linear_check(changed, 9, slots))
    reject("commute_factor_order", lambda: linear_check([(8-f, s, d, sg) for f, s, d, sg in steps], 9, slots))
    reject("negate_without_reversing", lambda: nonlinear_check(
        steps, slots, [(f, s, d, -sg) for f, s, d, sg in steps]))
    reject("alias_ternary_scratch", lambda: linear_check(
        [(f, 2 if s == 3 else s, 2 if d == 3 else d, sg) for f, s, d, sg in steps], 9, slots))

    def valid(**overrides):
        arguments = dict(source=[1], target=[2], factors=[0, 1, 2],
                         scratch=[[3], [4]], leaf=lambda x, y, f, s: None)
        arguments.update(overrides)
        t.compose(**arguments)

    shared = [1]
    reject("source_target_alias", lambda: valid(source=shared, target=shared))
    reject("scratch_source_alias", lambda: valid(source=shared, scratch=[shared, [4]]))
    reject("scratch_target_alias", lambda: valid(target=shared, scratch=[shared, [4]]))
    reject("scratch_pair_alias", lambda: valid(scratch=[shared, shared]))
    reject("insufficient_scratch", lambda: valid(scratch=[[3]]))
    reject("empty_factor_list", lambda: valid(factors=[]))
    reject("unequal_array_lengths", lambda: valid(target=[1, 2]))
    reject("empty_array", lambda: valid(source=[]))
    reject("invalid_sign", lambda: valid(sign=0))
    reject("bool_sign", lambda: valid(sign=True))

    # Concrete nonlinear example: restoration survives, but the increment may
    # depend on dirt. A(x)=x, B(u)=u^2, C(v)=v gives 2*u0*x+x^2.
    increments = []
    for dirt in (0, 1):
        source, target, u, v = [1], [0], [dirt], [7]

        def leaf(x, y, factor, sign):
            y[0] += sign * (x[0] ** 2 if factor == 1 else x[0])

        t.compose(source, target, [0, 1, 2], [u, v], leaf)
        need(source == [1] and u == [dirt] and v == [7], "nonlinear example restoration")
        increments.append(target[0])
    need(increments == [1, 3], "nonlinear dirt-dependence control")
    return {"rejected": rejected, "nonlinear_dirt_example": increments}


def verify():
    sources = source_check()
    t = module("ternary", ROOT / "ternary.py")
    old = module("pr628_dirty", ROOT / "vendor/pr628/dirty.py")
    base = module("pr628_budgets", ROOT / "vendor/pr628/check_budgets.py")
    echo = module("pr673_echo", ROOT / "vendor/pr673/echo.py")
    result = {"status": "PASS_TERNARY_DIRTY_COMPOSITION", "sources": sources,
              "resources": resource_checks(t, old), "controls": controls(t),
              "pr673_comparison": echo_checks(t, echo)}
    print("PASS symbolic endpoints, resource recurrences and negative controls", flush=True)
    result["rounded"] = rounded_checks(t, old)
    print("PASS", len(result["rounded"]), "rounded generic compositions", flush=True)
    result["kernels"] = kernel_checks(t, old)
    print("PASS", len(result["kernels"]), "certified-kernel compositions", flush=True)
    result["uniform_precision"] = uniform_budgets(t, base)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new certificate instead of comparing EXPECTED.json")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        need(result == expected, "expected certificate mismatch")
    print(result["status"])


if __name__ == "__main__":
    main()
